# Enhanced DC Router for MTProto with retry logic and caching
import asyncio
import logging
import re
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

# Regex patterns for DC migration errors
STATS_MIGRATE_RE = re.compile(r"STATS_MIGRATE_(\d+)")
DC_MIGRATE_RE = re.compile(r"(\w+)_MIGRATE_(\d+)")
PEER_MIGRATE_RE = re.compile(r"PEER_ID_INVALID|CHAT_INVALID|CHANNEL_INVALID")

logger = logging.getLogger(__name__)


@dataclass
class DCCacheEntry:
    """Cache entry for DC routing information."""

    dc_id: int
    peer_id: str
    last_updated: float = field(default_factory=time.time)
    success_count: int = 0
    failure_count: int = 0

    @property
    def is_valid(self, ttl: float = 3600) -> bool:
        """Check if cache entry is still valid."""
        return time.time() - self.last_updated < ttl

    @property
    def confidence_score(self) -> float:
        """Calculate confidence score for this DC mapping."""
        total_attempts = self.success_count + self.failure_count
        if total_attempts == 0:
            return 0.5  # Neutral confidence
        return self.success_count / total_attempts


class DCRouter:
    """Enhanced DC router with caching and smart retry logic."""

    def __init__(self, cache_ttl: float = 3600, max_retries: int = 3):
        self.cache_ttl = cache_ttl
        self.max_retries = max_retries
        self._dc_cache: dict[str, DCCacheEntry] = {}
        self._client_dc_cache: dict[str, int] = {}  # client -> current_dc
        self._lock = asyncio.Lock()

    def _make_cache_key(self, peer_id: str, request_type: str = "default") -> str:
        """Create cache key for peer and request type."""
        return f"{peer_id}:{request_type}"

    async def get_cached_dc(self, peer_id: str, request_type: str = "default") -> int | None:
        """Get cached DC for peer if available and valid."""
        cache_key = self._make_cache_key(peer_id, request_type)

        async with self._lock:
            entry = self._dc_cache.get(cache_key)
            if entry and entry.is_valid(self.cache_ttl) and entry.confidence_score > 0.7:
                return entry.dc_id

        return None

    async def cache_dc_mapping(
        self, peer_id: str, dc_id: int, request_type: str = "default", success: bool = True
    ) -> None:
        """Cache DC mapping for a peer."""
        cache_key = self._make_cache_key(peer_id, request_type)

        async with self._lock:
            entry = self._dc_cache.get(cache_key)

            if entry and entry.dc_id == dc_id:
                # Update existing entry
                if success:
                    entry.success_count += 1
                else:
                    entry.failure_count += 1
                entry.last_updated = time.time()
            else:
                # Create new entry
                self._dc_cache[cache_key] = DCCacheEntry(
                    dc_id=dc_id,
                    peer_id=peer_id,
                    success_count=1 if success else 0,
                    failure_count=0 if success else 1,
                )

        logger.debug(
            f"Cached DC mapping: {peer_id} -> DC {dc_id} "
            f"(type: {request_type}, success: {success})"
        )

    def parse_migrate_error(self, error: Exception) -> tuple[str | None, int | None]:
        """Parse migration error and extract operation type and DC ID."""
        error_str = str(error)

        # Check for STATS_MIGRATE_x
        stats_match = STATS_MIGRATE_RE.search(error_str)
        if stats_match:
            return "stats", int(stats_match.group(1))

        # Check for general migration patterns
        migrate_match = DC_MIGRATE_RE.search(error_str)
        if migrate_match:
            return migrate_match.group(1).lower(), int(migrate_match.group(2))

        return None, None

    async def ensure_client_dc(
        self, client: Any, target_dc: int, client_id: str = "default"
    ) -> bool:
        """Ensure client is connected to the correct DC."""
        try:
            # Check if we already know the client's current DC
            current_dc = self._client_dc_cache.get(client_id)

            if current_dc == target_dc:
                logger.debug(f"Client {client_id} already on DC {target_dc}")
                return True

            # Try to get current DC from client if possible
            if hasattr(client, "session") and hasattr(client.session, "dc_id"):
                current_dc = client.session.dc_id
                self._client_dc_cache[client_id] = current_dc

                if current_dc == target_dc:
                    return True

            # If client supports DC switching, use it
            if hasattr(client, "connect_to_dc") or hasattr(client, "switch_dc"):
                try:
                    if hasattr(client, "connect_to_dc"):
                        await client.connect_to_dc(target_dc)
                    else:
                        await client.switch_dc(target_dc)

                    self._client_dc_cache[client_id] = target_dc
                    logger.info(f"Client {client_id} switched to DC {target_dc}")
                    return True

                except Exception as switch_error:
                    logger.warning(
                        f"Failed to switch client {client_id} to DC {target_dc}: {switch_error}"
                    )

            # Fallback: reconnect (if client supports it)
            if hasattr(client, "disconnect") and hasattr(client, "connect"):
                try:
                    await client.disconnect()
                    # Set DC before reconnecting if possible
                    if hasattr(client.session, "set_dc"):
                        client.session.set_dc(target_dc, None)  # Reset server address
                    await client.connect()

                    self._client_dc_cache[client_id] = target_dc
                    logger.info(f"Client {client_id} reconnected to DC {target_dc}")
                    return True

                except Exception as reconnect_error:
                    logger.error(
                        f"Failed to reconnect client {client_id} to DC {target_dc}: {reconnect_error}"
                    )

            logger.warning(
                f"Could not switch client {client_id} to DC {target_dc} - will retry on next request"
            )
            return False

        except Exception as e:
            logger.error(f"Error ensuring client DC: {e}")
            return False

    async def run_with_dc_retry(
        self,
        client: Any,
        request_callable: Callable,
        peer_id: str = "unknown",
        request_type: str = "default",
        client_id: str = "default",
        *args,
        **kwargs,
    ) -> Any:
        """
        Run a request with automatic DC migration and retry logic.

        Args:
            client: Telegram client instance
            request_callable: Async function to call
            peer_id: Peer identifier for caching
            request_type: Type of request (stats, messages, etc.)
            client_id: Client identifier for DC tracking

        Returns:
            Result from request_callable
        """
        last_error = None

        # Try cached DC first
        cached_dc = await self.get_cached_dc(peer_id, request_type)
        if cached_dc:
            if await self.ensure_client_dc(client, cached_dc, client_id):
                try:
                    result = await request_callable(*args, **kwargs)
                    await self.cache_dc_mapping(peer_id, cached_dc, request_type, success=True)
                    return result
                except Exception as e:
                    await self.cache_dc_mapping(peer_id, cached_dc, request_type, success=False)
                    last_error = e

        # Retry with migration handling
        for attempt in range(self.max_retries):
            try:
                result = await request_callable(*args, **kwargs)

                # Success - cache current DC if we can determine it
                if client_id in self._client_dc_cache:
                    current_dc = self._client_dc_cache[client_id]
                    await self.cache_dc_mapping(peer_id, current_dc, request_type, success=True)

                return result

            except Exception as e:
                last_error = e
                error_type, target_dc = self.parse_migrate_error(e)

                if target_dc and attempt < self.max_retries - 1:
                    logger.info(
                        f"Attempt {attempt + 1}: {error_type} migration to DC {target_dc} "
                        f"for peer {peer_id}"
                    )

                    # Try to switch to target DC
                    if await self.ensure_client_dc(client, target_dc, client_id):
                        await self.cache_dc_mapping(peer_id, target_dc, request_type, success=False)
                        # Add small delay before retry
                        await asyncio.sleep(0.5)
                        continue

                # If it's not a migration error or we can't handle it, break
                if not target_dc:
                    logger.debug(f"Non-migration error on attempt {attempt + 1}: {e}")
                    if attempt == 0:  # Only retry once for non-migration errors
                        break

        # All retries failed
        logger.error(
            f"Request failed after {self.max_retries} attempts for peer {peer_id}: {last_error}"
        )
        raise last_error

    async def run_with_stats_dc(
        self,
        client: Any,
        request_callable: Callable,
        peer_id: str = "stats",
        client_id: str = "default",
        *args,
        **kwargs,
    ) -> Any:
        """Specialized method for stats requests with STATS_MIGRATE handling."""
        return await self.run_with_dc_retry(
            client, request_callable, peer_id, "stats", client_id, *args, **kwargs
        )

    def get_cache_stats(self) -> dict[str, Any]:
        """Get DC cache statistics."""
        total_entries = len(self._dc_cache)
        valid_entries = sum(
            1 for entry in self._dc_cache.values() if entry.is_valid(self.cache_ttl)
        )

        confidence_scores = [entry.confidence_score for entry in self._dc_cache.values()]
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0

        dc_distribution = {}
        for entry in self._dc_cache.values():
            dc_distribution[entry.dc_id] = dc_distribution.get(entry.dc_id, 0) + 1

        return {
            "total_entries": total_entries,
            "valid_entries": valid_entries,
            "cache_hit_rate": valid_entries / max(1, total_entries),
            "average_confidence": avg_confidence,
            "dc_distribution": dc_distribution,
            "active_clients": len(self._client_dc_cache),
            "client_dc_mapping": self._client_dc_cache.copy(),
        }

    async def clear_cache(self, peer_id: str | None = None) -> int:
        """Clear DC cache entries. Returns number of entries cleared."""
        async with self._lock:
            if peer_id:
                # Clear entries for specific peer
                keys_to_remove = [k for k in self._dc_cache.keys() if k.startswith(f"{peer_id}:")]
                for key in keys_to_remove:
                    del self._dc_cache[key]
                return len(keys_to_remove)
            else:
                # Clear all entries
                count = len(self._dc_cache)
                self._dc_cache.clear()
                self._client_dc_cache.clear()
                return count


# Backward compatibility functions
def parse_stats_migrate(exc: Exception) -> int | None:
    """Legacy function for backward compatibility."""
    router = DCRouter()
    error_type, dc_id = router.parse_migrate_error(exc)
    return dc_id if error_type == "stats" else None


async def ensure_stats_dc(client: Any, dc_id: int) -> None:
    """Legacy function for backward compatibility."""
    router = DCRouter()
    await router.ensure_client_dc(client, dc_id)


async def run_with_stats_dc(client: Any, request_callable: Callable, *args, **kwargs):
    """Legacy function with enhanced retry logic."""
    router = DCRouter()
    return await router.run_with_stats_dc(client, request_callable, *args, **kwargs)


# Global router instance for convenience
_global_router: DCRouter | None = None


def get_global_router() -> DCRouter:
    """Get global DC router instance."""
    global _global_router
    if _global_router is None:
        _global_router = DCRouter()
    return _global_router

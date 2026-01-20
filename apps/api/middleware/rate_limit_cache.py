"""
Rate Limit Configuration Cache (Phase 2)

In-memory cache for rate limit configurations with 30-second TTL.
Enables hot-reload without API restart.

Domain: API rate limiting - dynamic configuration
"""

import asyncio
import logging
import time
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CachedConfig:
    """Single cached rate limit configuration with metadata"""

    limit: int
    period: str
    enabled: bool
    cached_at: float

    def is_expired(self, ttl: int = 30) -> bool:
        """
        Check if cache entry is older than TTL seconds

        Args:
            ttl: Time-to-live in seconds (default: 30)

        Returns:
            True if expired, False otherwise
        """
        return time.time() - self.cached_at > ttl

    def to_limit_string(self) -> str:
        """
        Convert to slowapi limit string format

        Returns:
            Limit string like "100/minute"
        """
        return f"{self.limit}/{self.period}"


class RateLimitConfigCache:
    """
    In-memory cache for rate limit configurations

    Features:
    - 30-second TTL (configurable)
    - Thread-safe with asyncio locks
    - Automatic refresh from Redis
    - Cache invalidation support

    Usage:
        cache = RateLimitConfigCache(ttl=30)
        config = await cache.get("bot_operations")
        if config:
            limit = config.to_limit_string()  # "100/minute"
    """

    def __init__(self, ttl: int = 30):
        """
        Initialize cache

        Args:
            ttl: Time-to-live for cache entries in seconds (default: 30)
        """
        self._cache: dict[str, CachedConfig] = {}
        self._lock = asyncio.Lock()
        self._ttl = ttl
        logger.info(f"Rate limit config cache initialized with {ttl}s TTL")

    async def get(self, service_key: str, force_refresh: bool = False) -> CachedConfig | None:
        """
        Get configuration from cache, refresh if expired

        Args:
            service_key: Service identifier (e.g., "bot_operations")
            force_refresh: Force refresh even if not expired

        Returns:
            Cached configuration or None if not found
        """
        async with self._lock:
            cached = self._cache.get(service_key)

            # Return if fresh and not forcing refresh
            if cached and not force_refresh and not cached.is_expired(self._ttl):
                logger.debug(
                    f"Cache HIT for {service_key} (age: {time.time() - cached.cached_at:.1f}s)"
                )
                return cached

            # Refresh if expired or forced
            logger.debug(f"Cache MISS for {service_key}, refreshing...")
            await self._refresh(service_key)
            return self._cache.get(service_key)

    async def _refresh(self, service_key: str) -> None:
        """
        Reload configuration from Redis

        Args:
            service_key: Service identifier to refresh
        """
        try:
            from core.services.system import get_rate_limit_service

            service = get_rate_limit_service()
            config = await service.get_config(service_key)

            if config and config.get("limit"):
                self._cache[service_key] = CachedConfig(
                    limit=config["limit"],
                    period=config.get("period", "minute"),
                    enabled=config.get("enabled", True),
                    cached_at=time.time(),
                )
                logger.info(
                    f"Refreshed config for {service_key}: {self._cache[service_key].to_limit_string()}"
                )
            else:
                logger.debug(f"No config found in Redis for {service_key}, using defaults")

        except Exception as e:
            logger.warning(f"Failed to refresh config for {service_key}: {e}")

    async def get_all(self, force_refresh: bool = False) -> dict[str, CachedConfig]:
        """
        Get all cached configurations

        Args:
            force_refresh: Force refresh all entries

        Returns:
            Dictionary of service_key -> CachedConfig
        """
        async with self._lock:
            if force_refresh:
                # Refresh all known services
                from core.services.system import get_rate_limit_service

                service = get_rate_limit_service()
                all_configs = await service.get_all_configs()

                for service_key, config in all_configs.items():
                    if config and config.get("limit"):
                        self._cache[service_key] = CachedConfig(
                            limit=config["limit"],
                            period=config.get("period", "minute"),
                            enabled=config.get("enabled", True),
                            cached_at=time.time(),
                        )

            return self._cache.copy()

    async def invalidate(self, service_key: str | None = None) -> None:
        """
        Clear cache for one or all services

        Args:
            service_key: Specific service to invalidate, or None for all
        """
        async with self._lock:
            if service_key:
                removed = self._cache.pop(service_key, None)
                if removed:
                    logger.info(f"Invalidated cache for {service_key}")
                else:
                    logger.debug(f"No cache entry to invalidate for {service_key}")
            else:
                count = len(self._cache)
                self._cache.clear()
                logger.info(f"Invalidated entire cache ({count} entries)")

    async def warmup(self) -> int:
        """
        Pre-load all known configurations into cache

        Returns:
            Number of configurations loaded
        """
        try:
            from core.services.system import get_rate_limit_service

            service = get_rate_limit_service()
            all_configs = await service.get_all_configs()

            count = 0
            async with self._lock:
                for service_key, config in all_configs.items():
                    if config and config.get("limit"):
                        self._cache[service_key] = CachedConfig(
                            limit=config["limit"],
                            period=config.get("period", "minute"),
                            enabled=config.get("enabled", True),
                            cached_at=time.time(),
                        )
                        count += 1

            logger.info(f"Cache warmed up with {count} configurations")
            return count

        except Exception as e:
            logger.error(f"Failed to warm up cache: {e}")
            return 0

    def get_stats(self) -> dict[str, any]:
        """
        Get cache statistics

        Returns:
            Dictionary with cache metrics
        """
        total = len(self._cache)
        expired = sum(1 for cfg in self._cache.values() if cfg.is_expired(self._ttl))
        fresh = total - expired

        return {
            "total_entries": total,
            "fresh_entries": fresh,
            "expired_entries": expired,
            "ttl_seconds": self._ttl,
        }


# === GLOBAL CACHE INSTANCE ===

# Initialize global cache with 30-second TTL
config_cache = RateLimitConfigCache(ttl=30)


# === HELPER FUNCTIONS ===


async def get_cached_limit(service_key: str, default: str = "100/minute") -> str:
    """
    Get rate limit from cache or return default

    Args:
        service_key: Service identifier
        default: Fallback limit if not found

    Returns:
        Rate limit string (e.g., "100/minute")
    """
    try:
        config = await config_cache.get(service_key)
        if config and config.enabled:
            return config.to_limit_string()
    except Exception as e:
        logger.debug(f"Error getting cached limit for {service_key}: {e}")

    return default


async def invalidate_cache(service_key: str | None = None) -> None:
    """
    Invalidate cache for one or all services

    Args:
        service_key: Specific service or None for all
    """
    await config_cache.invalidate(service_key)


async def warmup_cache() -> int:
    """
    Pre-load all configurations into cache

    Returns:
        Number of configurations loaded
    """
    return await config_cache.warmup()


# === EXPORTS ===

__all__ = [
    "CachedConfig",
    "RateLimitConfigCache",
    "config_cache",
    "get_cached_limit",
    "invalidate_cache",
    "warmup_cache",
]

"""
Idempotency utility using Redis SETNX + TTL for duplicate request prevention.

Usage:
    idempotency = IdempotencyGuard()

    # Check if operation was already performed
    if await idempotency.is_duplicate(key, ttl_seconds=300):
        return cached_result

    # Mark operation as started
    await idempotency.mark_operation_start(key, ttl_seconds=300)

    # Perform operation...
    result = await perform_operation()

    # Mark operation as completed with result
    await idempotency.mark_operation_complete(key, result, ttl_seconds=300)
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

from core.ports.security_ports import CachePort


# Redis types for backwards compatibility
class RedisProtocol(Protocol):
    async def get(self, key: str) -> str | None: ...
    async def set(
        self, key: str, value: str, ex: int | None = None, nx: bool = False
    ) -> bool | None: ...
    async def delete(self, key: str) -> int: ...
    async def keys(self, pattern: str) -> list[str]: ...
    async def ttl(self, key: str) -> int: ...
    async def close(self) -> None: ...


logger = logging.getLogger(__name__)


@dataclass
class IdempotencyStatus:
    """Idempotency operation status."""

    status: str  # 'processing', 'completed', 'failed'
    created_at: datetime
    completed_at: datetime | None = None
    result: Any | None = None
    error: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "completed_at": (self.completed_at.isoformat() if self.completed_at else None),
            "result": self.result,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "IdempotencyStatus":
        """Create from dictionary."""
        return cls(
            status=data["status"],
            created_at=datetime.fromisoformat(data["created_at"]),
            completed_at=(
                datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None
            ),
            result=data.get("result"),
            error=data.get("error"),
        )


class IdempotencyGuard:
    """Framework-independent idempotency guard using SETNX + TTL."""

    def __init__(
        self,
        cache: CachePort | None = None,
        redis_client: RedisProtocol | None = None,
        redis_url: str | None = None,
        key_prefix: str = "idempotency",
    ):
        """
        Initialize idempotency guard with flexible backend options.

        Args:
            cache: Cache port for simple operations (preferred for new code)
            redis_client: Direct Redis client for advanced operations (backwards compatibility)
            redis_url: Redis URL for creating client (fallback)
            key_prefix: Prefix for cache keys
        """
        self.cache = cache
        self.redis_client = redis_client
        self.redis_url = redis_url
        self.key_prefix = key_prefix
        self._redis: RedisProtocol | None = None

    async def get_redis(self) -> RedisProtocol:
        """Get Redis connection - requires injection."""
        if self._redis is None:
            if self.redis_client:
                self._redis = self.redis_client
            else:
                raise RuntimeError(
                    "No Redis client provided. Please inject redis_client parameter."
                )
        return self._redis

    def _make_key(self, idempotency_key: str) -> str:
        """Create full Redis key."""
        return f"{self.key_prefix}:{idempotency_key}"

    async def is_duplicate(self, idempotency_key: str) -> tuple[bool, IdempotencyStatus | None]:
        """
        Check if operation with this key already exists.

        Returns:
            (is_duplicate, status_or_none)
        """
        redis_client = await self.get_redis()
        key = self._make_key(idempotency_key)

        try:
            data = await redis_client.get(key)
            if data is None:
                return False, None

            status = IdempotencyStatus.from_dict(json.loads(data))
            logger.info(f"Idempotency check: key='{idempotency_key}', status='{status.status}'")
            return True, status

        except Exception as e:
            logger.error(f"Redis error checking idempotency key '{idempotency_key}': {e}")
            # In case of Redis failure, allow operation to proceed
            return False, None

    async def mark_operation_start(self, idempotency_key: str, ttl_seconds: int = 300) -> bool:
        """
        Mark operation as started using SETNX for atomicity.

        Returns:
            True if successfully marked (not duplicate), False if already exists
        """
        redis_client = await self.get_redis()
        key = self._make_key(idempotency_key)

        status = IdempotencyStatus(status="processing", created_at=datetime.utcnow())

        try:
            # Use SETNX (SET if Not eXists) for atomic check-and-set
            result = await redis_client.set(
                key,
                json.dumps(status.to_dict()),
                ex=ttl_seconds,
                nx=True,  # Only set if key doesn't exist
            )

            if result:
                logger.info(
                    f"Idempotency operation started: key='{idempotency_key}', ttl={ttl_seconds}s"
                )
                return True
            else:
                logger.warning(f"Idempotency key already exists: '{idempotency_key}'")
                return False

        except Exception as e:
            logger.error(f"Redis error marking operation start '{idempotency_key}': {e}")
            # In case of Redis failure, allow operation to proceed
            return True

    async def mark_operation_complete(
        self, idempotency_key: str, result: Any = None, ttl_seconds: int = 300
    ) -> None:
        """Mark operation as completed with result."""
        redis_client = await self.get_redis()
        key = self._make_key(idempotency_key)

        status = IdempotencyStatus(
            status="completed",
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            result=result,
        )

        try:
            await redis_client.set(key, json.dumps(status.to_dict()), ex=ttl_seconds)
            logger.info(f"Idempotency operation completed: key='{idempotency_key}'")

        except Exception as e:
            logger.error(f"Redis error marking operation complete '{idempotency_key}': {e}")

    async def mark_operation_failed(
        self, idempotency_key: str, error: str, ttl_seconds: int = 300
    ) -> None:
        """Mark operation as failed with error."""
        redis_client = await self.get_redis()
        key = self._make_key(idempotency_key)

        status = IdempotencyStatus(
            status="failed",
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            error=error,
        )

        try:
            await redis_client.set(key, json.dumps(status.to_dict()), ex=ttl_seconds)
            logger.warning(
                f"Idempotency operation failed: key='{idempotency_key}', error='{error}'"
            )

        except Exception as e:
            logger.error(f"Redis error marking operation failed '{idempotency_key}': {e}")

    async def cleanup_expired(self) -> int:
        """Clean up expired idempotency keys. Returns count of cleaned keys."""
        redis_client = await self.get_redis()

        try:
            pattern = f"{self.key_prefix}:*"
            keys = await redis_client.keys(pattern)

            cleaned = 0
            for key in keys:
                # Check if key has TTL
                ttl = await redis_client.ttl(key)
                if ttl == -1:  # No TTL set, clean it up
                    await redis_client.delete(key)
                    cleaned += 1

            logger.info(f"Cleaned up {cleaned} expired idempotency keys")
            return cleaned

        except Exception as e:
            logger.error(f"Error cleaning up idempotency keys: {e}")
            return 0

    async def close(self) -> None:
        """Close Redis connection if it supports closing."""
        if self._redis and hasattr(self._redis, "close"):
            try:
                await self._redis.close()
            except Exception as e:
                logger.warning(f"Error closing Redis connection: {e}")

"""Redis cache adapter implementing AsyncCachePort protocol.

Provides Redis-based implementation of the cache operations defined
in AsyncCachePort protocol with proper error handling and connection management.
"""

from typing import TYPE_CHECKING, Any

from core.ports.cache_port import AsyncCachePort

if TYPE_CHECKING:
    import redis.asyncio as redis
else:
    try:
        import redis.asyncio as redis
    except ImportError:
        redis = None  # type: ignore


class RedisCacheAdapter(AsyncCachePort):
    """Redis implementation of AsyncCachePort protocol.

    Wraps redis.asyncio.Redis client to provide cache operations
    with proper error handling and type conversion.
    """

    def __init__(self, redis_client: Any):
        """Initialize adapter with Redis client.

        Args:
            redis_client: Configured redis.asyncio.Redis instance
        """
        self._redis = redis_client

    async def sadd(self, key: str, *values: str) -> int:
        """Add values to Redis set."""
        if not values:
            return 0
        result = await self._redis.sadd(key, *values)
        return int(result) if result is not None else 0

    async def srem(self, key: str, *values: str) -> int:
        """Remove values from Redis set."""
        if not values:
            return 0
        result = await self._redis.srem(key, *values)
        return int(result) if result is not None else 0

    async def smembers(self, key: str) -> set[str]:
        """Get all members from Redis set.

        Handles byte decoding from Redis automatically.
        """
        members = await self._redis.smembers(key)
        # Decode bytes from Redis to strings
        return {
            member.decode("utf-8") if isinstance(member, bytes) else str(member)
            for member in members
        }

    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        result = await self._redis.exists(key)
        return bool(result)

    async def delete(self, *keys: str) -> int:
        """Delete keys from Redis."""
        if not keys:
            return 0
        result = await self._redis.delete(*keys)
        return int(result) if result is not None else 0

    async def close(self) -> None:
        """Close Redis connection."""
        await self._redis.aclose()


class InMemoryCacheAdapter(AsyncCachePort):
    """In-memory cache implementation for testing or when Redis unavailable.

    Provides a simple dictionary-based cache that implements AsyncCachePort
    protocol for environments where Redis is not available.
    """

    def __init__(self):
        """Initialize in-memory storage."""
        self._storage: dict[str, set[str]] = {}

    async def sadd(self, key: str, *values: str) -> int:
        """Add values to in-memory set."""
        if not values:
            return 0
        if key not in self._storage:
            self._storage[key] = set()
        before = len(self._storage[key])
        self._storage[key].update(values)
        return len(self._storage[key]) - before

    async def srem(self, key: str, *values: str) -> int:
        """Remove values from in-memory set."""
        if not values or key not in self._storage:
            return 0
        before = len(self._storage[key])
        self._storage[key].difference_update(values)
        return before - len(self._storage[key])

    async def smembers(self, key: str) -> set[str]:
        """Get all members from in-memory set."""
        return self._storage.get(key, set()).copy()

    async def exists(self, key: str) -> bool:
        """Check if key exists in memory."""
        return key in self._storage

    async def delete(self, *keys: str) -> int:
        """Delete keys from memory."""
        count = 0
        for key in keys:
            if key in self._storage:
                del self._storage[key]
                count += 1
        return count

    async def close(self) -> None:
        """No-op for in-memory storage."""


def create_redis_cache_adapter(redis_client: Any | None = None) -> AsyncCachePort:
    """Factory function to create appropriate cache adapter.

    Args:
        redis_client: Optional Redis client. If None, returns in-memory adapter.

    Returns:
        AsyncCachePort implementation (Redis or in-memory)
    """
    if redis_client is not None:
        return RedisCacheAdapter(redis_client)
    return InMemoryCacheAdapter()

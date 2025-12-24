"""
Unified Redis Cache Service
============================

This is the ONLY cache implementation to use for the application.
DO NOT create alternative cache implementations.

Usage:
    from infra.caching import CacheService, InMemoryCacheAdapter
    
    # Production - Redis
    cache = CacheService(redis_url="redis://localhost:6379")
    await cache.set("key", "value", ttl=3600)
    value = await cache.get("key")
    
    # Testing - In-memory
    cache = InMemoryCacheAdapter()
    await cache.set("key", "value")
"""

from typing import TYPE_CHECKING, Any, Optional

from core.ports.cache_port import AsyncCachePort

if TYPE_CHECKING:
    import redis.asyncio as redis
else:
    try:
        import redis.asyncio as redis
    except ImportError:
        redis = None  # type: ignore


class CacheService(AsyncCachePort):
    """
    Unified async Redis cache service implementing AsyncCachePort.
    
    This consolidates all Redis caching functionality into one class.
    Use this for all caching needs throughout the application.
    """

    def __init__(self, redis_client: Optional[Any] = None, redis_url: str = "redis://localhost:6379"):
        """
        Initialize cache service.
        
        Args:
            redis_client: Pre-configured redis client (preferred)
            redis_url: Redis connection URL (fallback if client not provided)
        """
        self._redis_client = redis_client
        self._redis_url = redis_url
        self._connected = redis_client is not None

    async def _ensure_connection(self):
        """Ensure Redis connection is established."""
        if not self._connected and redis:
            self._redis_client = await redis.from_url(
                self._redis_url, 
                encoding="utf-8",
                decode_responses=True
            )
            self._connected = True

    # AsyncCachePort protocol methods (set operations)
    
    async def sadd(self, key: str, *values: str) -> int:
        """Add values to Redis set."""
        await self._ensure_connection()
        if not values or not self._redis_client:
            return 0
        result = await self._redis_client.sadd(key, *values)
        return int(result) if result is not None else 0

    async def srem(self, key: str, *values: str) -> int:
        """Remove values from Redis set."""
        await self._ensure_connection()
        if not values or not self._redis_client:
            return 0
        result = await self._redis_client.srem(key, *values)
        return int(result) if result is not None else 0

    async def smembers(self, key: str) -> set[str]:
        """Get all members from Redis set."""
        await self._ensure_connection()
        if not self._redis_client:
            return set()
        members = await self._redis_client.smembers(key)
        return {
            member.decode("utf-8") if isinstance(member, bytes) else str(member)
            for member in members
        }

    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        await self._ensure_connection()
        if not self._redis_client:
            return False
        result = await self._redis_client.exists(key)
        return bool(result)

    async def delete(self, *keys: str) -> int:
        """Delete keys from Redis."""
        await self._ensure_connection()
        if not keys or not self._redis_client:
            return 0
        result = await self._redis_client.delete(*keys)
        return int(result) if result is not None else 0

    # Additional common cache operations
    
    async def get(self, key: str) -> Optional[str]:
        """Get value by key."""
        await self._ensure_connection()
        if not self._redis_client:
            return None
        return await self._redis_client.get(key)

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """
        Set key-value pair with optional TTL.
        
        Args:
            key: Cache key
            value: Value to store
            ttl: Time to live in seconds (optional)
        """
        await self._ensure_connection()
        if not self._redis_client:
            return False
        if ttl:
            return bool(await self._redis_client.setex(key, ttl, value))
        return bool(await self._redis_client.set(key, value))

    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis_client and self._connected:
            await self._redis_client.aclose()
            self._connected = False


class InMemoryCacheAdapter(AsyncCachePort):
    """
    In-memory cache for testing or when Redis is unavailable.
    
    Implements AsyncCachePort protocol using simple dictionary storage.
    """

    def __init__(self):
        """Initialize in-memory storage."""
        self._sets: dict[str, set[str]] = {}
        self._values: dict[str, str] = {}

    async def sadd(self, key: str, *values: str) -> int:
        """Add values to in-memory set."""
        if not values:
            return 0
        if key not in self._sets:
            self._sets[key] = set()
        before = len(self._sets[key])
        self._sets[key].update(values)
        return len(self._sets[key]) - before

    async def srem(self, key: str, *values: str) -> int:
        """Remove values from in-memory set."""
        if not values or key not in self._sets:
            return 0
        before = len(self._sets[key])
        self._sets[key].difference_update(values)
        return before - len(self._sets[key])

    async def smembers(self, key: str) -> set[str]:
        """Get all members from in-memory set."""
        return self._sets.get(key, set()).copy()

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        return key in self._sets or key in self._values

    async def delete(self, *keys: str) -> int:
        """Delete keys from memory."""
        count = 0
        for key in keys:
            if key in self._sets:
                del self._sets[key]
                count += 1
            if key in self._values:
                del self._values[key]
                count += 1
        return count

    async def get(self, key: str) -> Optional[str]:
        """Get value by key."""
        return self._values.get(key)

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Set key-value pair (TTL ignored in memory)."""
        self._values[key] = value
        return True

    async def close(self) -> None:
        """Clear in-memory storage."""
        self._sets.clear()
        self._values.clear()


# Factory function for compatibility
def create_redis_cache_adapter(redis_client: Any) -> CacheService:
    """
    Create cache adapter from Redis client.
    
    This function exists for backward compatibility with existing code.
    New code should use CacheService directly.
    """
    return CacheService(redis_client=redis_client)

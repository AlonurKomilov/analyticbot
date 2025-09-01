"""
Redis Cache Adapter for Analytics Fusion
Simple JSON caching with TTL support
"""

import hashlib
import json
import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class RedisJSONCache:
    """Redis-based JSON cache with TTL support"""

    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.enabled = redis_client is not None

    async def get_json(self, key: str) -> dict | None:
        """Get JSON data from cache"""
        if not self.enabled:
            return None

        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")

        return None

    async def set_json(self, key: str, value: dict, ttl_s: int = 60) -> None:
        """Set JSON data in cache with TTL"""
        if not self.enabled:
            return

        try:
            json_value = json.dumps(value, default=self._json_serializer)
            await self.redis.set(key, json_value, ex=ttl_s)
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")

    async def delete(self, key: str) -> None:
        """Delete key from cache"""
        if not self.enabled:
            return

        try:
            await self.redis.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.enabled:
            return False

        try:
            return bool(await self.redis.exists(key))
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False

    def generate_cache_key(self, endpoint: str, params: dict, last_updated: datetime = None) -> str:
        """Generate a consistent cache key from endpoint and parameters"""
        # Sort parameters for consistent key generation
        sorted_params = sorted(params.items())
        params_str = json.dumps(sorted_params, default=str)

        # Include last_updated in key for cache invalidation
        key_data = f"{endpoint}:{params_str}"
        if last_updated:
            key_data += f":{last_updated.isoformat()}"

        # Create hash for shorter, consistent keys
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"analytics_v2:{endpoint}:{key_hash}"

    def _json_serializer(self, obj: Any) -> str:
        """Custom JSON serializer for datetime objects"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


class NoOpCache:
    """No-operation cache for when Redis is not available"""

    async def get_json(self, key: str) -> dict | None:
        return None

    async def set_json(self, key: str, value: dict, ttl_s: int = 60) -> None:
        pass

    async def delete(self, key: str) -> None:
        pass

    async def exists(self, key: str) -> bool:
        return False

    def generate_cache_key(self, endpoint: str, params: dict, last_updated: datetime = None) -> str:
        return f"noop:{endpoint}"


def create_cache_adapter(redis_client=None) -> RedisJSONCache | NoOpCache:
    """Factory function to create appropriate cache adapter"""
    if redis_client:
        return RedisJSONCache(redis_client)
    else:
        logger.info("Redis client not provided, using no-op cache")
        return NoOpCache()

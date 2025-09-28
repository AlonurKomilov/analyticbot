# infra/cache/redis_cache_service.py
"""
Redis implementation of CacheService port.
"""

import asyncio
import json
import logging
from typing import Any

from core.ports import CacheService

logger = logging.getLogger(__name__)


class RedisCacheService(CacheService):
    """Redis implementation of cache service port."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self._client = None
        self._connected = False
    
    async def _ensure_connected(self):
        """Ensure Redis connection is established."""
        if self._connected and self._client:
            return
            
        try:
            # Import here to avoid dependency issues if redis not installed
            import redis.asyncio as redis
            self._client = redis.from_url(self.redis_url)
            await self._client.ping()
            self._connected = True
            logger.info("Redis cache service connected")
        except ImportError:
            logger.warning("Redis not installed, using in-memory fallback")
            self._client = InMemoryCache()
            self._connected = True
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._client = InMemoryCache()
            self._connected = True
    
    async def get(self, key: str) -> str | None:
        """Get value from cache."""
        await self._ensure_connected()
        try:
            if hasattr(self._client, 'get'):
                result = await self._client.get(key)
                return result.decode('utf-8') if result else None
            else:
                return self._client.get(key)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: str, ttl: int | None = None) -> bool:
        """Set value in cache with optional TTL."""
        await self._ensure_connected()
        try:
            if hasattr(self._client, 'set'):
                await self._client.set(key, value, ex=ttl)
            else:
                self._client.set(key, value, ttl)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        await self._ensure_connected()
        try:
            if hasattr(self._client, 'delete'):
                result = await self._client.delete(key)
                return bool(result)
            else:
                return self._client.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        await self._ensure_connected()
        try:
            if hasattr(self._client, 'exists'):
                result = await self._client.exists(key)
                return bool(result)
            else:
                return self._client.exists(key)
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False


class InMemoryCache:
    """Fallback in-memory cache implementation."""
    
    def __init__(self):
        self._cache = {}
        self._expiry = {}
    
    def get(self, key: str) -> str | None:
        """Get value from in-memory cache."""
        import time
        if key in self._expiry and self._expiry[key] < time.time():
            self.delete(key)
        return self._cache.get(key)
    
    def set(self, key: str, value: str, ttl: int | None = None) -> None:
        """Set value in in-memory cache."""
        self._cache[key] = value
        if ttl:
            import time
            self._expiry[key] = time.time() + ttl
    
    def delete(self, key: str) -> bool:
        """Delete key from in-memory cache."""
        deleted = key in self._cache
        self._cache.pop(key, None)
        self._expiry.pop(key, None)
        return deleted
    
    def exists(self, key: str) -> bool:
        """Check if key exists in in-memory cache."""
        import time
        if key in self._expiry and self._expiry[key] < time.time():
            self.delete(key)
        return key in self._cache
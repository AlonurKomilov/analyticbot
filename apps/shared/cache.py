# apps/shared/cache.py
"""
Cache abstraction for apps layer
Provides caching functionality without direct infra imports
"""

from __future__ import annotations

import asyncio
import functools
import hashlib
import json
import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

__all__ = ["cache_result", "MemoryCache", "create_cache_key"]

T = TypeVar("T")


@dataclass
class CacheEntry:
    """Cache entry with value and metadata"""

    value: Any
    created_at: float
    expires_at: float | None = None
    access_count: int = 0


class MemoryCache:
    """Simple in-memory cache implementation"""

    def __init__(self, max_size: int = 1000):
        self._cache: dict[str, CacheEntry] = {}
        self._max_size = max_size
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Any:
        """Get value from cache"""
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None

            # Check expiration
            import time

            if entry.expires_at and time.time() > entry.expires_at:
                del self._cache[key]
                return None

            # Update access count
            entry.access_count += 1
            return entry.value

    async def set(self, key: str, value: Any, ttl: int | None = None):
        """Set value in cache"""
        async with self._lock:
            import time

            # Evict if cache is full
            if len(self._cache) >= self._max_size and key not in self._cache:
                await self._evict_lru()

            expires_at = None
            if ttl:
                expires_at = time.time() + ttl

            self._cache[key] = CacheEntry(
                value=value, created_at=time.time(), expires_at=expires_at
            )

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        async with self._lock:
            return self._cache.pop(key, None) is not None

    async def clear(self):
        """Clear all cache entries"""
        async with self._lock:
            self._cache.clear()

    async def _evict_lru(self):
        """Evict least recently used entry"""
        if not self._cache:
            return

        # Find entry with lowest access count (simple LRU approximation)
        lru_key = min(self._cache.keys(), key=lambda k: self._cache[k].access_count)
        del self._cache[lru_key]


# Global cache instance
_global_cache = MemoryCache()


def create_cache_key(*args, **kwargs) -> str:
    """Create cache key from arguments"""
    # Create deterministic key from arguments
    key_data = {
        "args": [str(arg) for arg in args],
        "kwargs": {str(k): str(v) for k, v in sorted(kwargs.items())},
    }
    key_str = json.dumps(key_data, sort_keys=True)
    return hashlib.md5(key_str.encode()).hexdigest()


def cache_result(ttl: int = 3600, key_func: Callable | None = None, use_redis: bool = False):
    """
    Decorator for caching function results
    Provides same interface as infra.cache.advanced_decorators.cache_result
    """

    def decorator(func):
        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Create cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = (
                        f"{func.__module__}.{func.__name__}:{create_cache_key(*args, **kwargs)}"
                    )

                # Try to get from cache first
                try:
                    cached_value = await _get_cached_value(cache_key)
                    if cached_value is not None:
                        logger.debug(f"Cache hit for {func.__name__}")
                        return cached_value
                except Exception as e:
                    logger.debug(f"Cache get failed for {func.__name__}: {e}")

                # Execute function and cache result
                result = await func(*args, **kwargs)

                try:
                    await _set_cached_value(cache_key, result, ttl)
                    logger.debug(f"Cached result for {func.__name__}")
                except Exception as e:
                    logger.debug(f"Cache set failed for {func.__name__}: {e}")

                return result

            return async_wrapper

        else:

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                # For sync functions, we'll use a simpler approach
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = (
                        f"{func.__module__}.{func.__name__}:{create_cache_key(*args, **kwargs)}"
                    )

                # Simple synchronous caching (not recommended for production)
                result = func(*args, **kwargs)
                logger.debug(f"Executed {func.__name__} (sync caching not fully supported)")
                return result

            return sync_wrapper

    return decorator


async def _get_cached_value(cache_key: str) -> Any:
    """Get value from cache"""
    # Try memory cache
    value = await _global_cache.get(cache_key)
    if value is not None:
        return value

    # Could try infra cache here if available (but avoid direct import)
    logger.debug(f"Cache miss for key: {cache_key}")
    return None


async def _set_cached_value(cache_key: str, value: Any, ttl: int):
    """Set value in cache"""
    # Set in memory cache
    await _global_cache.set(cache_key, value, ttl)
    logger.debug(f"Cached value for key: {cache_key}")


# For backward compatibility
async def clear_cache():
    """Clear all cached values"""
    await _global_cache.clear()


def get_cache_stats() -> dict[str, Any]:
    """Get cache statistics"""
    return {"memory_cache_size": len(_global_cache._cache), "max_size": _global_cache._max_size}

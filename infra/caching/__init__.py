"""
Caching Infrastructure
======================

Unified caching layer for the application.

USE THIS for all caching needs:
    from infra.caching import CacheService
    
    # Production with Redis
    cache = CacheService(redis_url="redis://localhost:6379")
    await cache.set("key", "value", ttl=3600)
    
    # Testing with in-memory
    cache = InMemoryCacheAdapter()
    await cache.set("key", "value")

DO NOT:
- Create alternative cache implementations
- Import from infra.cache.* (old location)
- Use infra.security.adapters.RedisCache (moved here)

This module consolidates all caching functionality to prevent duplicates.
"""

from infra.caching.cache_service import (
    CacheService,
    InMemoryCacheAdapter,
    create_redis_cache_adapter,
)

__all__ = [
    "CacheService",  # Main cache service - USE THIS
    "InMemoryCacheAdapter",  # For testing
    "create_redis_cache_adapter",  # Compatibility function
]

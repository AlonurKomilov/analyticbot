"""
Caching Infrastructure
======================

Unified caching layer for the application.

USE THIS for all caching needs:
    from infra.cache import CacheService

    # Production with Redis
    cache = CacheService(redis_url="redis://localhost:6379")
    await cache.set("key", "value", ttl=3600)

    # Testing with in-memory
    from infra.cache import InMemoryCacheAdapter
    cache = InMemoryCacheAdapter()

This module consolidates all caching functionality.
"""

from infra.cache.cache_service import (
    CacheService,
    InMemoryCacheAdapter,
    create_redis_cache_adapter,
)

__all__ = [
    "CacheService",
    "InMemoryCacheAdapter",
    "create_redis_cache_adapter",
]

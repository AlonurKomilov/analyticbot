"""Cache adapters for infrastructure layer.

Provides implementations of caching protocols using various backends
(Redis, in-memory, etc.).
"""

from infra.cache.redis_cache_adapter import (
    InMemoryCacheAdapter,
    RedisCacheAdapter,
    create_redis_cache_adapter,
)

__all__ = [
    "RedisCacheAdapter",
    "InMemoryCacheAdapter",
    "create_redis_cache_adapter",
]

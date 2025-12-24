"""
⚠️ DEPRECATED

This module is deprecated. Use infra.caching instead.

Old import:
    from infra.cache import RedisCacheAdapter
    
New import:
    from infra.caching import CacheService

See infra/caching/README.md for migration guide.
"""

# For backward compatibility, re-export from new location
try:
    from infra.caching import CacheService as RedisCacheAdapter
    from infra.caching import InMemoryCacheAdapter, create_redis_cache_adapter
    
    __all__ = [
        "RedisCacheAdapter",
        "InMemoryCacheAdapter",
        "create_redis_cache_adapter",
    ]
except ImportError:
    # If new module doesn't exist yet, raise helpful error
    raise ImportError(
        "infra.cache is deprecated. "
        "Please update your imports to: from infra.caching import CacheService"
    )

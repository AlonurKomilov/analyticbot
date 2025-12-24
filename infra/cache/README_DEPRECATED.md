# ⚠️ DEPRECATED - Use infra/caching/ instead

This folder is deprecated and kept for reference only.

**DO NOT use files from this folder!**

## Migration

Old imports:
```python
from infra.cache.redis_cache import RedisJSONCache
from infra.cache.redis_cache_adapter import RedisCacheAdapter  
from infra.cache.redis_cache_service import RedisCacheService
```

New imports:
```python
from infra.caching import CacheService
```

## Files Archived

All `.py` files moved to `infra/_archive_old_cache/` for reference.

See `infra/caching/README.md` for the new unified cache implementation.

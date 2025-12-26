# Caching Infrastructure

## Purpose

Unified Redis caching layer for the application.

## What Goes Here

- ✅ Redis client configuration
- ✅ Cache service implementations (AsyncCachePort)
- ✅ Caching decorators (@cached, @cache_invalidate)
- ✅ Cache key generation utilities

## What Does NOT Go Here

- ❌ Database models (use `infra/database/models/`)
- ❌ Business logic (use `core/services/`)
- ❌ HTTP clients or external APIs (use `infra/adapters/`)
- ❌ Session management (that's in `infra/security/`)

## Main Components

- `cache_service.py` - **THE cache service implementation (USE THIS)**
  - `CacheService` - Redis-backed cache
  - `InMemoryCacheAdapter` - In-memory cache for testing

## Usage Example

```python
from infra.caching import CacheService

# Initialize
cache = CacheService(redis_url="redis://localhost:6379")

# Store with TTL
await cache.set("user:123", "John Doe", ttl=3600)

# Retrieve
name = await cache.get("user:123")

# Set operations
await cache.sadd("active_users", "user_123", "user_456")
users = await cache.smembers("active_users")

# Check existence
exists = await cache.exists("user:123")

# Delete
await cache.delete("user:123")
```

## Testing

```python
from infra.caching import InMemoryCacheAdapter

# Use in-memory cache for tests
cache = InMemoryCacheAdapter()
await cache.set("test_key", "test_value")
assert await cache.get("test_key") == "test_value"
```

## Related Folders

- `../database/` - For persistent storage
- `../security/` - For JWT tokens and sessions
- `core/ports/cache_port.py` - Protocol definition (AsyncCachePort)

## Migration Notes

**Old imports (DEPRECATED):**
```python
from infra.cache.redis_cache import RedisJSONCache
from infra.cache.redis_cache_adapter import RedisCacheAdapter
from infra.security.adapters import RedisCache
```

**New imports (USE THIS):**
```python
from infra.caching import CacheService
```

## Important

This is the **ONLY** place for cache implementations. Do not create:
- `infra/redis/`
- `infra/cache2/`
- Alternative cache adapters

If you need to modify caching behavior, update `cache_service.py`.

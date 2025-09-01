# Shim to keep old imports running for a cycle
import warnings

warnings.warn("`infrastructure.cache` moved to `infra.cache`.", DeprecationWarning, stacklevel=2)
from infra.cache.redis_cache import RedisJSONCache, create_cache_adapter  # re-export

__all__ = ["RedisJSONCache", "create_cache_adapter"]

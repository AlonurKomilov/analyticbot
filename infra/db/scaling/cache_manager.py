"""
Query Cache Manager
===================

For 100K+ users, caching is CRITICAL:
- Reduce database load by 70-90%
- Sub-millisecond response times
- Protect against traffic spikes

Cache Strategies by Data Type:
    - User data: 5 min TTL (changes rarely)
    - Channel stats: 1-2 min TTL (updates frequently)  
    - Marketplace: 10 min TTL (semi-static)
    - Subscription: 5 min TTL (changes on purchase)
    - Rate limits: Real-time (no cache)
"""

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import timedelta
from enum import Enum
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CacheTier(Enum):
    """Cache tier determines TTL and invalidation strategy"""
    HOT = "hot"        # 30 sec - frequently changing (live stats)
    WARM = "warm"      # 2 min - moderate changes (channel metrics)
    STANDARD = "std"   # 5 min - normal data (user info)
    COLD = "cold"      # 15 min - rarely changes (marketplace)
    STATIC = "static"  # 1 hour - almost never changes (config)


@dataclass
class CacheConfig:
    """Cache configuration per tier"""
    ttl: timedelta
    max_size: int  # Max items in local cache
    compress: bool = False  # Compress large values
    
    
TIER_CONFIGS: dict[CacheTier, CacheConfig] = {
    CacheTier.HOT: CacheConfig(ttl=timedelta(seconds=30), max_size=10000),
    CacheTier.WARM: CacheConfig(ttl=timedelta(minutes=2), max_size=50000),
    CacheTier.STANDARD: CacheConfig(ttl=timedelta(minutes=5), max_size=100000),
    CacheTier.COLD: CacheConfig(ttl=timedelta(minutes=15), max_size=50000, compress=True),
    CacheTier.STATIC: CacheConfig(ttl=timedelta(hours=1), max_size=10000, compress=True),
}


@dataclass
class CacheKey:
    """Structured cache key with namespace"""
    namespace: str
    identifier: str
    tier: CacheTier = CacheTier.STANDARD
    tags: list[str] = field(default_factory=list)
    
    @property
    def key(self) -> str:
        """Generate Redis-compatible key"""
        return f"cache:{self.namespace}:{self.identifier}"
    
    @property
    def ttl_seconds(self) -> int:
        """Get TTL in seconds for this tier"""
        return int(TIER_CONFIGS[self.tier].ttl.total_seconds())


class QueryCacheManager:
    """
    High-performance query cache manager for 100K+ users.
    
    Usage:
        cache = QueryCacheManager(redis_client)
        
        # Cache with automatic key generation
        @cache.cached(namespace="user", tier=CacheTier.STANDARD)
        async def get_user(user_id: int) -> User:
            return await db.fetch_user(user_id)
        
        # Manual caching
        await cache.set("user:123", user_data, tier=CacheTier.STANDARD)
        user = await cache.get("user:123")
        
        # Invalidation
        await cache.invalidate("user:123")
        await cache.invalidate_pattern("user:*")
        await cache.invalidate_by_tag("user_updated")
    """
    
    def __init__(self, redis_client: Any):
        self._redis = redis_client
        self._local_cache: dict[str, tuple[Any, float]] = {}  # key -> (value, expiry)
        self._tag_keys: dict[str, set[str]] = {}  # tag -> set of keys
        
    async def get(self, key: str) -> Any | None:
        """Get value from cache (local first, then Redis)"""
        # Check local cache first
        import time
        if key in self._local_cache:
            value, expiry = self._local_cache[key]
            if time.time() < expiry:
                logger.debug(f"Local cache hit: {key}")
                return value
            else:
                del self._local_cache[key]
        
        # Check Redis
        if self._redis:
            try:
                data = await self._redis.get(key)
                if data:
                    logger.debug(f"Redis cache hit: {key}")
                    return json.loads(data)
            except Exception as e:
                logger.warning(f"Redis get error: {e}")
        
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        tier: CacheTier = CacheTier.STANDARD,
        tags: list[str] | None = None,
    ) -> None:
        """Set value in cache"""
        config = TIER_CONFIGS[tier]
        ttl_seconds = int(config.ttl.total_seconds())
        
        # Store in local cache
        import time
        self._local_cache[key] = (value, time.time() + ttl_seconds)
        
        # Limit local cache size
        if len(self._local_cache) > config.max_size:
            # Remove oldest entries
            sorted_keys = sorted(
                self._local_cache.keys(),
                key=lambda k: self._local_cache[k][1]
            )
            for old_key in sorted_keys[:1000]:
                del self._local_cache[old_key]
        
        # Store in Redis
        if self._redis:
            try:
                data = json.dumps(value, default=str)
                await self._redis.setex(key, ttl_seconds, data)
            except Exception as e:
                logger.warning(f"Redis set error: {e}")
        
        # Track tags for invalidation
        if tags:
            for tag in tags:
                if tag not in self._tag_keys:
                    self._tag_keys[tag] = set()
                self._tag_keys[tag].add(key)
    
    async def invalidate(self, key: str) -> None:
        """Invalidate specific key"""
        if key in self._local_cache:
            del self._local_cache[key]
        
        if self._redis:
            try:
                await self._redis.delete(key)
            except Exception as e:
                logger.warning(f"Redis delete error: {e}")
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern"""
        count = 0
        
        # Local cache
        to_delete = [k for k in self._local_cache if self._match_pattern(k, pattern)]
        for key in to_delete:
            del self._local_cache[key]
            count += 1
        
        # Redis
        if self._redis:
            try:
                cursor = 0
                while True:
                    cursor, keys = await self._redis.scan(cursor, match=pattern, count=100)
                    if keys:
                        await self._redis.delete(*keys)
                        count += len(keys)
                    if cursor == 0:
                        break
            except Exception as e:
                logger.warning(f"Redis pattern delete error: {e}")
        
        logger.info(f"Invalidated {count} keys matching {pattern}")
        return count
    
    async def invalidate_by_tag(self, tag: str) -> int:
        """Invalidate all keys with specific tag"""
        if tag not in self._tag_keys:
            return 0
        
        count = 0
        for key in list(self._tag_keys[tag]):
            await self.invalidate(key)
            count += 1
        
        del self._tag_keys[tag]
        return count
    
    def cached(
        self,
        namespace: str,
        tier: CacheTier = CacheTier.STANDARD,
        key_builder: Callable[..., str] | None = None,
        tags: list[str] | None = None,
    ):
        """Decorator for caching async functions"""
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            import functools
            
            @functools.wraps(func)
            async def wrapper(*args, **kwargs) -> T:
                # Build cache key
                if key_builder:
                    key_suffix = key_builder(*args, **kwargs)
                else:
                    # Auto-generate key from arguments
                    key_data = json.dumps({"args": args[1:], "kwargs": kwargs}, default=str)
                    key_suffix = hashlib.md5(key_data.encode()).hexdigest()[:16]
                
                cache_key = f"cache:{namespace}:{key_suffix}"
                
                # Try cache
                cached_value = await self.get(cache_key)
                if cached_value is not None:
                    return cached_value
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Store in cache
                await self.set(cache_key, result, tier=tier, tags=tags)
                
                return result
            
            return wrapper
        return decorator
    
    @staticmethod
    def _match_pattern(key: str, pattern: str) -> bool:
        """Simple glob-style pattern matching"""
        import fnmatch
        return fnmatch.fnmatch(key, pattern)
    
    async def get_stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        stats = {
            "local_cache_size": len(self._local_cache),
            "tag_count": len(self._tag_keys),
            "total_tagged_keys": sum(len(keys) for keys in self._tag_keys.values()),
        }
        
        if self._redis:
            try:
                info = await self._redis.info("memory")
                stats["redis_used_memory"] = info.get("used_memory_human", "unknown")
            except Exception:
                pass
        
        return stats


# Cache key patterns for common queries
CACHE_PATTERNS = {
    # User data
    "user_profile": lambda user_id: CacheKey("user", str(user_id), CacheTier.STANDARD),
    "user_subscription": lambda user_id: CacheKey("sub", str(user_id), CacheTier.WARM),
    "user_credits": lambda user_id: CacheKey("credits", str(user_id), CacheTier.WARM),
    
    # Channel data
    "channel_info": lambda channel_id: CacheKey("channel", str(channel_id), CacheTier.WARM),
    "channel_stats": lambda channel_id: CacheKey("stats", str(channel_id), CacheTier.HOT),
    "channel_list": lambda user_id: CacheKey("channels", str(user_id), CacheTier.WARM),
    
    # Marketplace
    "marketplace_services": lambda: CacheKey("market", "services", CacheTier.COLD),
    "service_detail": lambda svc_id: CacheKey("market", f"svc:{svc_id}", CacheTier.COLD),
    "user_services": lambda user_id: CacheKey("market", f"user:{user_id}", CacheTier.STANDARD),
    
    # System
    "feature_flags": lambda: CacheKey("system", "flags", CacheTier.STATIC),
    "rate_limits": lambda user_id: CacheKey("limits", str(user_id), CacheTier.HOT),
}

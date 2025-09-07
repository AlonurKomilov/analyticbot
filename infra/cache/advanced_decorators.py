"""
Enhanced Caching Decorators for Performance Optimization
Provides advanced caching strategies for API endpoints and database operations
"""

import asyncio
import functools
import hashlib
import json
import logging
import time
from typing import Any, Callable, Optional

import redis.asyncio as redis
from pydantic import SecretStr

logger = logging.getLogger(__name__)


class CacheConfig:
    """Cache configuration constants"""
    
    # TTL values in seconds
    ANALYTICS_SUMMARY_TTL = 600      # 10 minutes
    USER_CHANNELS_TTL = 300          # 5 minutes  
    SUBSCRIPTION_PLANS_TTL = 3600    # 1 hour
    POST_METRICS_TTL = 180          # 3 minutes
    CHANNEL_STATS_TTL = 420         # 7 minutes
    DEFAULT_TTL = 300               # 5 minutes
    
    # Cache key prefixes
    PREFIX_ANALYTICS = "analytics"
    PREFIX_USER = "user"
    PREFIX_CHANNEL = "channel"
    PREFIX_POST = "post"
    PREFIX_SUBSCRIPTION = "subscription"


class AdvancedCache:
    """Advanced Redis cache with enhanced features"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis = redis_client
        self.enabled = redis_client is not None
        self._local_cache = {}  # Small local cache for hot data
        self._local_cache_size = 100
        
    @classmethod
    async def create(cls, redis_url: str = "redis://localhost:6379/0"):
        """Factory method to create cache with Redis connection"""
        try:
            redis_client = redis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_keepalive=True,
                retry_on_timeout=True,
                max_connections=20
            )
            await redis_client.ping()
            logger.info("✅ Advanced cache connected to Redis")
            return cls(redis_client)
        except Exception as e:
            logger.warning(f"❌ Redis connection failed, using no-op cache: {e}")
            return cls(None)
    
    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate consistent cache key"""
        key_parts = [str(arg) for arg in args]
        if kwargs:
            # Sort kwargs for consistent key generation
            sorted_kwargs = sorted(kwargs.items())
            key_parts.append(json.dumps(sorted_kwargs, default=str, sort_keys=True))
        
        key_data = f"{prefix}:{':'.join(key_parts)}"
        # Use hash for long keys
        if len(key_data) > 200:
            key_hash = hashlib.sha256(key_data.encode()).hexdigest()
            return f"{prefix}:{key_hash}"
        return key_data
    
    async def get(self, key: str) -> Any:
        """Get value from cache with local cache fallback"""
        # Check local cache first
        if key in self._local_cache:
            data, timestamp = self._local_cache[key]
            if time.time() - timestamp < 60:  # Local cache valid for 1 minute
                return data
        
        if not self.enabled or self.redis is None:
            return None
            
        try:
            value = await self.redis.get(key)
            if value:
                data = json.loads(value)
                # Store in local cache
                self._update_local_cache(key, data)
                return data
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {e}")
        
        return None
    
    async def set(self, key: str, value: Any, ttl: int = CacheConfig.DEFAULT_TTL) -> bool:
        """Set value in cache with local cache update"""
        self._update_local_cache(key, value)
        
        if not self.enabled or self.redis is None:
            return False
            
        try:
            serialized = json.dumps(value, default=str)
            await self.redis.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        # Remove from local cache
        self._local_cache.pop(key, None)
        
        if not self.enabled or self.redis is None:
            return False
            
        try:
            result = await self.redis.delete(key)
            return bool(result)
        except Exception as e:
            logger.warning(f"Cache delete error for key {key}: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self.enabled or self.redis is None:
            return 0
            
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                deleted = await self.redis.delete(*keys)
                # Clear matching keys from local cache
                for key in list(self._local_cache.keys()):
                    if any(k for k in keys if k in key):
                        self._local_cache.pop(key, None)
                logger.info(f"🗑️ Deleted {deleted} cache keys matching '{pattern}'")
                return deleted
        except Exception as e:
            logger.warning(f"Cache pattern delete error for pattern {pattern}: {e}")
        
        return 0
    
    def _update_local_cache(self, key: str, data: Any):
        """Update local cache with size limit"""
        if len(self._local_cache) >= self._local_cache_size:
            # Remove oldest entry
            oldest_key = min(self._local_cache.keys(), 
                           key=lambda k: self._local_cache[k][1])
            self._local_cache.pop(oldest_key, None)
        
        self._local_cache[key] = (data, time.time())
    
    async def get_stats(self) -> dict:
        """Get cache statistics"""
        stats = {
            "enabled": self.enabled,
            "local_cache_size": len(self._local_cache),
            "local_cache_max": self._local_cache_size
        }
        
        if self.enabled and self.redis is not None:
            try:
                info = await self.redis.info()
                stats.update({
                    "redis_memory": info.get("used_memory_human", "N/A"),
                    "redis_connections": info.get("connected_clients", 0),
                    "redis_hits": info.get("keyspace_hits", 0),
                    "redis_misses": info.get("keyspace_misses", 0)
                })
            except Exception as e:
                logger.warning(f"Error getting Redis stats: {e}")
        
        return stats


# Global cache instance
_global_cache: Optional[AdvancedCache] = None


async def get_cache() -> AdvancedCache:
    """Get global cache instance"""
    global _global_cache
    if _global_cache is None:
        # Try to get Redis URL from settings
        try:
            from config.settings import Settings
            import os
            settings = Settings(
                BOT_TOKEN=SecretStr(os.getenv("BOT_TOKEN", "test_token")),
                STORAGE_CHANNEL_ID=int(os.getenv("STORAGE_CHANNEL_ID", "0")),
                POSTGRES_USER=os.getenv("POSTGRES_USER", "test_user"),
                POSTGRES_PASSWORD=SecretStr(os.getenv("POSTGRES_PASSWORD", "test_pass")),
                POSTGRES_DB=os.getenv("POSTGRES_DB", "test_db"),
                JWT_SECRET_KEY=SecretStr(os.getenv("JWT_SECRET_KEY", "test_jwt_key"))
            )
            redis_url = str(settings.REDIS_URL) if hasattr(settings, 'REDIS_URL') else "redis://localhost:6379/0"
        except Exception:
            redis_url = "redis://localhost:6379/0"
        
        _global_cache = await AdvancedCache.create(redis_url)
    
    return _global_cache


def cache_result(prefix: str, ttl: int = CacheConfig.DEFAULT_TTL, 
                key_func: Optional[Callable] = None, 
                invalidate_on_error: bool = True):
    """
    Enhanced caching decorator with advanced features
    
    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds
        key_func: Custom function to generate cache key
        invalidate_on_error: Whether to delete cache on function error
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            cache = await get_cache()
            
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = cache._generate_cache_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            start_time = time.time()
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                cache_time = time.time() - start_time
                logger.debug(f"💾 Cache HIT for {prefix} (key: {cache_key[:50]}...) in {cache_time:.3f}s")
                return cached_result
            
            # Cache miss - execute function
            logger.debug(f"🔄 Cache MISS for {prefix} (key: {cache_key[:50]}...)")
            
            try:
                result = await func(*args, **kwargs)
                # Store in cache
                await cache.set(cache_key, result, ttl)
                execution_time = time.time() - start_time
                logger.debug(f"✅ Cached {prefix} result in {execution_time:.3f}s")
                return result
            except Exception as e:
                if invalidate_on_error:
                    await cache.delete(cache_key)
                raise e
        
        # Add cache management methods to function
        async def invalidate_cache(*args, **kwargs):
            """Invalidate cache for this function call"""
            cache = await get_cache()
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = cache._generate_cache_key(prefix, *args, **kwargs)
            return await cache.delete(cache_key)
        
        async def warm_cache(*args, **kwargs):
            """Warm cache by executing function"""
            return await wrapper(*args, **kwargs)
        
        # Add methods as attributes with proper typing
        wrapper.invalidate_cache = invalidate_cache  # type: ignore
        wrapper.warm_cache = warm_cache  # type: ignore
        wrapper.cache_prefix = prefix  # type: ignore
        
        return wrapper
    
    return decorator


def cache_analytics_summary(ttl: int = CacheConfig.ANALYTICS_SUMMARY_TTL):
    """Decorator for caching analytics summaries"""
    return cache_result(
        prefix=CacheConfig.PREFIX_ANALYTICS,
        ttl=ttl,
        key_func=lambda channel_id, period=7, **kwargs: f"summary:{channel_id}:{period}"
    )


def cache_user_channels(ttl: int = CacheConfig.USER_CHANNELS_TTL):
    """Decorator for caching user channel lists"""
    return cache_result(
        prefix=CacheConfig.PREFIX_USER,
        ttl=ttl,
        key_func=lambda user_id, **kwargs: f"channels:{user_id}"
    )


def cache_subscription_plans(ttl: int = CacheConfig.SUBSCRIPTION_PLANS_TTL):
    """Decorator for caching subscription plans"""
    return cache_result(
        prefix=CacheConfig.PREFIX_SUBSCRIPTION,
        ttl=ttl,
        key_func=lambda **kwargs: "plans:all"
    )


def cache_post_metrics(ttl: int = CacheConfig.POST_METRICS_TTL):
    """Decorator for caching post metrics"""
    return cache_result(
        prefix=CacheConfig.PREFIX_POST,
        ttl=ttl,
        key_func=lambda post_id, metric_type="all", **kwargs: f"metrics:{post_id}:{metric_type}"
    )


def cache_channel_stats(ttl: int = CacheConfig.CHANNEL_STATS_TTL):
    """Decorator for caching channel statistics"""
    return cache_result(
        prefix=CacheConfig.PREFIX_CHANNEL,
        ttl=ttl,
        key_func=lambda channel_id, period=30, **kwargs: f"stats:{channel_id}:{period}"
    )


class CacheInvalidator:
    """Utility class for cache invalidation patterns"""
    
    @staticmethod
    async def invalidate_user_data(user_id: int):
        """Invalidate all cache data for a user"""
        cache = await get_cache()
        patterns = [
            f"{CacheConfig.PREFIX_USER}:*{user_id}*",
            f"{CacheConfig.PREFIX_ANALYTICS}:*{user_id}*"
        ]
        
        total_deleted = 0
        for pattern in patterns:
            deleted = await cache.delete_pattern(pattern)
            total_deleted += deleted
        
        logger.info(f"🗑️ Invalidated {total_deleted} cache entries for user {user_id}")
        return total_deleted
    
    @staticmethod
    async def invalidate_channel_data(channel_id: int):
        """Invalidate all cache data for a channel"""
        cache = await get_cache()
        patterns = [
            f"{CacheConfig.PREFIX_CHANNEL}:*{channel_id}*",
            f"{CacheConfig.PREFIX_ANALYTICS}:*{channel_id}*",
            f"{CacheConfig.PREFIX_POST}:*{channel_id}*"
        ]
        
        total_deleted = 0
        for pattern in patterns:
            deleted = await cache.delete_pattern(pattern)
            total_deleted += deleted
        
        logger.info(f"🗑️ Invalidated {total_deleted} cache entries for channel {channel_id}")
        return total_deleted
    
    @staticmethod
    async def invalidate_analytics_data():
        """Invalidate all analytics cache data"""
        cache = await get_cache()
        deleted = await cache.delete_pattern(f"{CacheConfig.PREFIX_ANALYTICS}:*")
        logger.info(f"🗑️ Invalidated {deleted} analytics cache entries")
        return deleted

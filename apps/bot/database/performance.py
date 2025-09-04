"""
🚀 PERFORMANCE OPTIMIZATION MODULE
Enhanced database performance and caching layer using optimized connection management
"""

import asyncio
import hashlib
import json
import logging
import time
from contextlib import asynccontextmanager
from functools import wraps
from typing import Any

import redis.asyncio as redis

from apps.bot.config import settings
from infra.db.connection_manager import db_manager

logger = logging.getLogger(__name__)


class PerformanceConfig:
    """Performance optimization configuration"""

    DB_POOL_MIN_SIZE = 10
    DB_POOL_MAX_SIZE = 50
    DB_POOL_TIMEOUT = 30
    DB_POOL_COMMAND_TIMEOUT = 60
    CACHE_DEFAULT_TTL = 300
    CACHE_ANALYTICS_TTL = 600
    CACHE_USER_DATA_TTL = 1800
    CACHE_CHANNEL_DATA_TTL = 3600
    QUERY_BATCH_SIZE = 100
    QUERY_TIMEOUT = 30
    MAX_CONCURRENT_QUERIES = 20
    TASK_BATCH_SIZE = 50
    TASK_DELAY = 0.1
    MAX_RETRIES = 3
    TIMEOUT = 30  # General timeout constant


class RedisCache:
    """High-performance Redis caching layer"""

    def __init__(self):
        self._redis: redis.Redis | None = None
        self._is_connected = False

    async def connect(self):
        """Connect to Redis server"""
        try:
            redis_url = (
                str(settings.REDIS_URL)
                if hasattr(settings, "REDIS_URL")
                else "redis://localhost:6379/0"
            )
            self._redis = redis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_keepalive=True,
                socket_keepalive_options={
                    "TCP_KEEPIDLE": 600,
                    "TCP_KEEPINTVL": 30,
                    "TCP_KEEPCNT": 3,
                },
                retry_on_timeout=True,
                max_connections=20,
            )
            await self._redis.ping()
            self._is_connected = True
            logger.info("✅ Redis cache connected successfully")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            self._is_connected = False

    async def close(self):
        """Close Redis connection"""
        if self._redis:
            await self._redis.close()
            self._is_connected = False

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from prefix and parameters"""
        key_data = f"{prefix}:{':'.join(map(str, args))}"
        if kwargs:
            key_data += (
                f":{hashlib.sha256(json.dumps(kwargs, sort_keys=True).encode()).hexdigest()}"
            )
        return key_data

    async def get(self, key: str) -> Any | None:
        """Get value from cache"""
        if not self._is_connected or not self._redis:
            return None
        try:
            value = await self._redis.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {e}")
        return None

    async def set(self, key: str, value: Any, ttl: int = PerformanceConfig.CACHE_DEFAULT_TTL):
        """Set value in cache"""
        if not self._is_connected or not self._redis:
            return False
        try:
            serialized = json.dumps(value, default=str)
            await self._redis.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str):
        """Delete key from cache"""
        if not self._is_connected or not self._redis:
            return
        try:
            await self._redis.delete(key)
        except Exception as e:
            logger.warning(f"Cache delete error for key {key}: {e}")

    async def flush_pattern(self, pattern: str):
        """Delete all keys matching pattern"""
        if not self._is_connected or not self._redis:
            return
        try:
            keys = await self._redis.keys(pattern)
            if keys:
                await self._redis.delete(*keys)
                logger.info(f"🗑️ Flushed {len(keys)} cache keys matching '{pattern}'")
        except Exception as e:
            logger.warning(f"Cache flush error for pattern {pattern}: {e}")


class OptimizedPool:
    """High-performance database connection pool using optimized connection management"""

    def __init__(self):
        self._db_manager = db_manager
        self._semaphore = asyncio.Semaphore(PerformanceConfig.MAX_CONCURRENT_QUERIES)

    async def create_pool(self):
        """Use optimized database manager"""
        if not self._db_manager._pool:
            await self._db_manager.initialize()
        logger.info("✅ Using optimized database pool")
        return self._db_manager._pool

    async def _initialize_optimizations(self):
        """Optimizations are now handled by optimized connection manager"""
        logger.info("📊 Database optimizations handled by optimized connection manager")

    @asynccontextmanager
    async def acquire_connection(self):
        """Acquire database connection with concurrency control using optimized manager"""
        async with self._semaphore:
            async with self._db_manager.connection() as conn:
                yield conn

    async def close(self):
        """Close database pool using optimized manager"""
        await self._db_manager.close()


class QueryOptimizer:
    """Database query optimization utilities using optimized manager"""

    @staticmethod
    def batch_queries(
        items: list[Any], batch_size: int = PerformanceConfig.QUERY_BATCH_SIZE
    ) -> list[list[Any]]:
        """Split items into optimized batches"""
        return [items[i : i + batch_size] for i in range(0, len(items), batch_size)]

    @staticmethod
    async def execute_batched(
        query: str,
        params_list: list[tuple],
        batch_size: int = PerformanceConfig.QUERY_BATCH_SIZE,
    ):
        """Execute query in optimized batches using optimized manager"""
        results = []
        batches = QueryOptimizer.batch_queries(params_list, batch_size)
        for batch in batches:
            batch_results = await asyncio.gather(
                *[db_manager.execute_query(query, *params) for params in batch],
                return_exceptions=True,
            )
            results.extend(batch_results)
        return results

    @staticmethod
    async def fetch_in_batches(
        query: str,
        params_list: list[tuple],
        batch_size: int = PerformanceConfig.QUERY_BATCH_SIZE,
    ) -> list[list]:
        """Fetch data in optimized batches using optimized manager"""
        all_results = []
        batches = QueryOptimizer.batch_queries(params_list, batch_size)
        for batch in batches:
            batch_results = await asyncio.gather(
                *[db_manager.fetch_query(query, *params) for params in batch],
                return_exceptions=True,
            )
            for result in batch_results:
                if not isinstance(result, Exception) and isinstance(result, list):
                    all_results.extend(result)
        return all_results


def cache_result(prefix: str, ttl: int = PerformanceConfig.CACHE_DEFAULT_TTL, key_func=None):
    """Decorator for caching function results"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = performance_manager.cache
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = cache._generate_key(prefix, *args, **kwargs)
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, ttl)
            return result

        return wrapper

    return decorator


def performance_timer(operation_name: str):
    """Decorator for measuring performance"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"⚡ {operation_name} completed in {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"❌ {operation_name} failed in {duration:.3f}s: {e}")
                raise

        return wrapper

    return decorator


class PerformanceManager:
    """Centralized performance management using optimized connection management"""

    def __init__(self):
        self.pool = OptimizedPool()
        self.cache = RedisCache()
        self.query_optimizer = QueryOptimizer()

    async def initialize(self):
        """Initialize all performance components"""
        await self.cache.connect()
        await self.pool.create_pool()
        logger.info(
            "🚀 Performance optimization system initialized with optimized connection management"
        )

    async def close(self):
        """Close all performance components"""
        await self.cache.close()
        await self.pool.close()
        logger.info("🏁 Performance optimization system closed")

    async def get_performance_stats(self) -> dict[str, Any]:
        """Get performance statistics including optimized connection metrics"""
        stats = {
            "cache_connected": self.cache._is_connected,
            "phase3_optimizations": "enabled",
            "timestamp": time.time(),
        }

        # Get optimized database stats
        if self.pool._db_manager._pool:
            db_stats = self.pool._db_manager.get_stats()
            stats.update(
                {
                    "pool_size": db_stats.get("pool_size", 0),
                    "idle_connections": db_stats.get("idle_connections", 0),
                    "used_connections": db_stats.get("used_connections", 0),
                    "avg_query_time": db_stats.get("avg_query_time", 0),
                    "total_queries": db_stats.get("query_count", 0),
                    "health_status": db_stats.get("health_status", False),
                }
            )

        # Get Redis stats
        if self.cache._is_connected:
            try:
                redis_info = await self.cache._redis.info()
                if redis_info:  # Check if redis_info is not None
                    stats.update(
                        {
                            "redis_memory": redis_info.get("used_memory_human", "N/A"),
                            "redis_connections": redis_info.get("connected_clients", 0),
                            "redis_hits": redis_info.get("keyspace_hits", 0),
                            "redis_misses": redis_info.get("keyspace_misses", 0),
                        }
                )
            except Exception as e:
                logger.warning(f"Error getting Redis stats: {e}")

        return stats


performance_manager = PerformanceManager()

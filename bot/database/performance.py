"""
🚀 PHASE 1.5: PERFORMANCE OPTIMIZATION MODULE
Enhanced database performance and caching layer
"""

import asyncio
import hashlib
import json
import logging
import time
from contextlib import asynccontextmanager
from functools import wraps
from typing import Any

import asyncpg
import redis.asyncio as redis
from asyncpg.pool import Pool

from bot.config import settings

logger = logging.getLogger(__name__)


class PerformanceConfig:
    """Performance optimization configuration"""

    # Database Pool Settings
    DB_POOL_MIN_SIZE = 10
    DB_POOL_MAX_SIZE = 50
    DB_POOL_TIMEOUT = 30
    DB_POOL_COMMAND_TIMEOUT = 60

    # Redis Cache Settings
    CACHE_DEFAULT_TTL = 300  # 5 minutes
    CACHE_ANALYTICS_TTL = 600  # 10 minutes
    CACHE_USER_DATA_TTL = 1800  # 30 minutes
    CACHE_CHANNEL_DATA_TTL = 3600  # 1 hour

    # Query Performance
    QUERY_BATCH_SIZE = 100
    QUERY_TIMEOUT = 30
    MAX_CONCURRENT_QUERIES = 20

    # Background Tasks
    TASK_BATCH_SIZE = 50
    TASK_DELAY = 0.1
    MAX_RETRIES = 3


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

            # Test connection
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
            key_data += f":{hashlib.md5(json.dumps(kwargs, sort_keys=True).encode()).hexdigest()}"
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

    async def set(
        self, key: str, value: Any, ttl: int = PerformanceConfig.CACHE_DEFAULT_TTL
    ):
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
    """High-performance database connection pool"""

    def __init__(self):
        self._pool: Pool | None = None
        self._semaphore = asyncio.Semaphore(PerformanceConfig.MAX_CONCURRENT_QUERIES)

    async def create_pool(self) -> Pool:
        """Create optimized database pool"""
        dsn_string = str(settings.DATABASE_URL.unicode_string())

        self._pool = await asyncpg.create_pool(
            dsn=dsn_string,
            min_size=PerformanceConfig.DB_POOL_MIN_SIZE,
            max_size=PerformanceConfig.DB_POOL_MAX_SIZE,
            command_timeout=PerformanceConfig.DB_POOL_COMMAND_TIMEOUT,
            server_settings={
                "application_name": "analyticbot_optimized",
                "tcp_keepalives_idle": "600",
                "tcp_keepalives_interval": "30",
                "tcp_keepalives_count": "3",
                "shared_preload_libraries": "pg_stat_statements",
                "track_activity_query_size": "2048",
                "log_min_duration_statement": "1000",  # Log slow queries
                "checkpoint_completion_target": "0.9",
                "wal_buffers": "16MB",
                "effective_cache_size": "2GB",
                "random_page_cost": "1.1",
            },
        )

        # Test connection and create indexes if needed
        await self._initialize_optimizations()

        logger.info(
            f"✅ Optimized DB pool created: {PerformanceConfig.DB_POOL_MIN_SIZE}-{PerformanceConfig.DB_POOL_MAX_SIZE} connections"
        )
        return self._pool

    async def _initialize_optimizations(self):
        """Initialize database optimizations"""
        async with self._pool.acquire() as conn:
            # Create performance indexes if not exist
            optimizations = [
                # Analytics performance indexes
                """
                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analytics_channel_date 
                ON analytics(channel_id, created_at DESC);
                """,
                """
                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analytics_message_views 
                ON analytics(message_id, view_count) WHERE view_count > 0;
                """,
                # User activity indexes
                """
                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_active_plan 
                ON users(is_active, plan_id) WHERE is_active = true;
                """,
                # Channel performance indexes
                """
                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_channels_user_active 
                ON channels(user_id, is_active) WHERE is_active = true;
                """,
                # Scheduler optimization
                """
                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scheduled_posts_execution 
                ON scheduled_posts(scheduled_time) WHERE status = 'pending';
                """,
            ]

            for optimization in optimizations:
                try:
                    await conn.execute(optimization)
                except Exception as e:
                    logger.debug(f"Index creation skipped (probably exists): {e}")

    @asynccontextmanager
    async def acquire_connection(self):
        """Acquire database connection with concurrency control"""
        async with self._semaphore:
            async with self._pool.acquire(
                timeout=PerformanceConfig.DB_POOL_TIMEOUT
            ) as conn:
                yield conn

    async def close(self):
        """Close database pool"""
        if self._pool:
            await self._pool.close()


class QueryOptimizer:
    """Database query optimization utilities"""

    @staticmethod
    def batch_queries(
        items: list[Any], batch_size: int = PerformanceConfig.QUERY_BATCH_SIZE
    ) -> list[list[Any]]:
        """Split items into optimized batches"""
        return [items[i : i + batch_size] for i in range(0, len(items), batch_size)]

    @staticmethod
    async def execute_batched(
        pool: Pool,
        query: str,
        params_list: list[tuple],
        batch_size: int = PerformanceConfig.QUERY_BATCH_SIZE,
    ):
        """Execute query in optimized batches"""
        results = []
        batches = QueryOptimizer.batch_queries(params_list, batch_size)

        for batch in batches:
            async with pool.acquire() as conn:
                batch_results = await asyncio.gather(
                    *[conn.execute(query, *params) for params in batch],
                    return_exceptions=True,
                )
                results.extend(batch_results)

        return results

    @staticmethod
    async def fetch_in_batches(
        pool: Pool,
        query: str,
        params_list: list[tuple],
        batch_size: int = PerformanceConfig.QUERY_BATCH_SIZE,
    ) -> list[list]:
        """Fetch data in optimized batches"""
        all_results = []
        batches = QueryOptimizer.batch_queries(params_list, batch_size)

        for batch in batches:
            async with pool.acquire() as conn:
                batch_results = await asyncio.gather(
                    *[conn.fetch(query, *params) for params in batch],
                    return_exceptions=True,
                )

                for result in batch_results:
                    if not isinstance(result, Exception):
                        all_results.extend(result)

        return all_results


def cache_result(
    prefix: str, ttl: int = PerformanceConfig.CACHE_DEFAULT_TTL, key_func=None
):
    """Decorator for caching function results"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = performance_manager.cache

            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = cache._generate_key(prefix, *args, **kwargs)

            # Try to get from cache
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
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
    """Centralized performance management"""

    def __init__(self):
        self.pool = OptimizedPool()
        self.cache = RedisCache()
        self.query_optimizer = QueryOptimizer()

    async def initialize(self):
        """Initialize all performance components"""
        await self.cache.connect()
        await self.pool.create_pool()
        logger.info("🚀 Performance optimization system initialized")

    async def close(self):
        """Close all performance components"""
        await self.cache.close()
        await self.pool.close()
        logger.info("🏁 Performance optimization system closed")

    async def get_performance_stats(self) -> dict[str, Any]:
        """Get performance statistics"""
        stats = {
            "cache_connected": self.cache._is_connected,
            "pool_size": self.pool._pool.get_size() if self.pool._pool else 0,
            "pool_free": self.pool._pool.get_idle_size() if self.pool._pool else 0,
            "timestamp": time.time(),
        }

        # Get Redis stats if available
        if self.cache._is_connected:
            try:
                redis_info = await self.cache._redis.info()
                stats["redis_memory"] = redis_info.get("used_memory_human", "N/A")
                stats["redis_connections"] = redis_info.get("connected_clients", 0)
                stats["redis_hits"] = redis_info.get("keyspace_hits", 0)
                stats["redis_misses"] = redis_info.get("keyspace_misses", 0)
            except Exception:
                pass

        return stats


# Global performance manager instance
performance_manager = PerformanceManager()

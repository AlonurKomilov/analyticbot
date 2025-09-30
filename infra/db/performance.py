"""
Database Performance Monitoring and Optimization
Infrastructure layer database utilities
"""

import hashlib
import json
import logging
import time
from contextlib import asynccontextmanager
from functools import wraps

import redis.asyncio as redis

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
    CACHE_EXPIRE_ON_UPDATE = True
    ENABLE_QUERY_LOGGING = True
    QUERY_SLOW_THRESHOLD = 1.0  # seconds
    ENABLE_CACHING = True
    CACHE_PREFIX = "analyticsbot_v3"


class DatabasePerformanceManager:
    """Enhanced database performance manager with caching and monitoring"""

    def __init__(self, redis_url: str = None):
        self._redis_pool = None
        self._redis_url = redis_url or "redis://localhost:6379/0"
        self._query_stats = {}
        self._cache_stats = {"hits": 0, "misses": 0, "sets": 0}

    async def initialize(self):
        """Initialize Redis connection pool for caching"""
        try:
            self._redis_pool = redis.ConnectionPool.from_url(
                self._redis_url,
                max_connections=20,
                retry_on_timeout=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            logger.info("Redis connection pool initialized for performance caching")
        except Exception as e:
            logger.warning(f"Failed to initialize Redis pool: {e}, disabling caching")
            self._redis_pool = None

    async def close(self):
        """Close Redis connections"""
        if self._redis_pool:
            await self._redis_pool.disconnect()
            logger.info("Redis connection pool closed")

    @asynccontextmanager
    async def get_redis_connection(self):
        """Get Redis connection from pool"""
        if not self._redis_pool:
            yield None
            return

        conn = redis.Redis(connection_pool=self._redis_pool)
        try:
            yield conn
        finally:
            await conn.close()

    def _generate_cache_key(self, query: str, params: tuple = ()) -> str:
        """Generate cache key for query and parameters"""
        key_data = f"{query}:{str(params)}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"{PerformanceConfig.CACHE_PREFIX}:query:{key_hash}"

    async def cached_query(
        self,
        query: str,
        params: tuple = (),
        ttl: int = PerformanceConfig.CACHE_DEFAULT_TTL,
        cache_enabled: bool = True,
    ):
        """Execute query with caching support"""
        cache_key = self._generate_cache_key(query, params)

        # Try cache first
        if cache_enabled and PerformanceConfig.ENABLE_CACHING:
            async with self.get_redis_connection() as redis_conn:
                if redis_conn:
                    try:
                        cached_result = await redis_conn.get(cache_key)
                        if cached_result:
                            self._cache_stats["hits"] += 1
                            return json.loads(cached_result)
                        else:
                            self._cache_stats["misses"] += 1
                    except Exception as e:
                        logger.warning(f"Cache read error: {e}")

        # Execute query
        start_time = time.time()
        try:
            result = await db_manager.fetch_query(query, *params)
            execution_time = time.time() - start_time

            # Log slow queries
            if (
                PerformanceConfig.ENABLE_QUERY_LOGGING
                and execution_time > PerformanceConfig.QUERY_SLOW_THRESHOLD
            ):
                logger.warning(f"Slow query detected: {execution_time:.2f}s - {query[:100]}...")

            # Update query stats
            if query not in self._query_stats:
                self._query_stats[query] = {"count": 0, "total_time": 0, "avg_time": 0}

            self._query_stats[query]["count"] += 1
            self._query_stats[query]["total_time"] += execution_time
            self._query_stats[query]["avg_time"] = (
                self._query_stats[query]["total_time"] / self._query_stats[query]["count"]
            )

            # Cache result
            if cache_enabled and PerformanceConfig.ENABLE_CACHING:
                async with self.get_redis_connection() as redis_conn:
                    if redis_conn:
                        try:
                            await redis_conn.setex(cache_key, ttl, json.dumps(result, default=str))
                            self._cache_stats["sets"] += 1
                        except Exception as e:
                            logger.warning(f"Cache write error: {e}")

            return result

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Query failed after {execution_time:.2f}s: {e}")
            raise

    async def invalidate_cache_pattern(self, pattern: str):
        """Invalidate cache entries matching pattern"""
        async with self.get_redis_connection() as redis_conn:
            if redis_conn:
                try:
                    keys = await redis_conn.keys(f"{PerformanceConfig.CACHE_PREFIX}:*{pattern}*")
                    if keys:
                        await redis_conn.delete(*keys)
                        logger.info(f"Invalidated {len(keys)} cache entries for pattern: {pattern}")
                except Exception as e:
                    logger.error(f"Cache invalidation error: {e}")

    def get_performance_stats(self) -> dict:
        """Get performance statistics"""
        return {
            "cache_stats": self._cache_stats,
            "query_stats": dict(list(self._query_stats.items())[:10]),  # Top 10 queries
            "total_queries": sum(stats["count"] for stats in self._query_stats.values()),
            "cache_hit_ratio": (
                self._cache_stats["hits"]
                / (self._cache_stats["hits"] + self._cache_stats["misses"])
                if (self._cache_stats["hits"] + self._cache_stats["misses"]) > 0
                else 0
            ),
        }


# Global performance manager instance
performance_manager = DatabasePerformanceManager()


def performance_timer(func):
    """Decorator to measure function execution time"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time

            if execution_time > 1.0:  # Log slow operations
                logger.warning(f"Slow operation: {func.__name__} took {execution_time:.2f}s")

            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Operation {func.__name__} failed after {execution_time:.2f}s: {e}")
            raise

    return wrapper


async def init_performance_monitoring():
    """Initialize performance monitoring"""
    await performance_manager.initialize()
    logger.info("Database performance monitoring initialized")


async def close_performance_monitoring():
    """Close performance monitoring"""
    await performance_manager.close()
    logger.info("Database performance monitoring closed")

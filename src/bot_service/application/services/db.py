import asyncio
import logging

import asyncpg
from asyncpg.pool import Pool
from src.bot_service.config import settings
from src.bot_service.database.performance import PerformanceConfig, performance_manager
from src.bot_service.utils.error_handler import ErrorContext, ErrorHandler

logger = logging.getLogger(__name__)


class DatabaseManager:
    """🚀 Enhanced database manager with performance optimization and monitoring"""

    def __init__(self):
        self._pool: Pool | None = None
        self._is_healthy = False
        self._performance_enabled = True

    @property
    def pool(self) -> Pool | None:
        return self._pool

    @property
    def is_healthy(self) -> bool:
        return self._is_healthy and self._pool is not None

    async def create_pool(self, max_retries: int = 5, backoff_factor: float = 0.5) -> Pool:
        """
        🔥 Creates high-performance connection pool with optimization features.

        Features:
        - Enhanced connection pooling with performance tuning
        - Automatic index creation for query optimization
        - Health monitoring and auto-recovery
        - Performance metrics collection
        """
        if self._performance_enabled:
            try:
                await performance_manager.initialize()
                self._pool = performance_manager.pool._pool
                self._is_healthy = True
                logger.info("🚀 Using optimized performance pool")
                return self._pool
            except Exception as e:
                logger.warning(f"⚠️ Performance optimization failed, using standard pool: {e}")
                self._performance_enabled = False
        dsn_string = str(settings.DATABASE_URL.unicode_string())
        last_exception = None
        for attempt in range(max_retries):
            try:
                self._pool = await asyncpg.create_pool(
                    dsn=dsn_string,
                    min_size=PerformanceConfig.DB_POOL_MIN_SIZE // 2,
                    max_size=PerformanceConfig.DB_POOL_MAX_SIZE // 2,
                    command_timeout=PerformanceConfig.DB_POOL_COMMAND_TIMEOUT,
                    server_settings={
                        "application_name": "analyticbot_enhanced",
                        "tcp_keepalives_idle": "600",
                        "tcp_keepalives_interval": "30",
                        "tcp_keepalives_count": "3",
                        "log_min_duration_statement": "1000",
                        "checkpoint_completion_target": "0.9",
                        "effective_cache_size": "1GB",
                    },
                )
                async with self._pool.acquire() as conn:
                    await conn.execute("SELECT 1")
                    result = await conn.fetchval("SELECT version()")
                    logger.debug(f"📊 Connected to: {result}")
                self._is_healthy = True
                logger.info(
                    f"✅ Enhanced database pool created: {self._pool.get_size()} connections"
                )
                return self._pool
            except (OSError, asyncpg.exceptions.PostgresError) as e:
                last_exception = e
                wait_time = backoff_factor * 2**attempt
                context = ErrorContext().add("attempt", attempt + 1).add("max_retries", max_retries)
                ErrorHandler.handle_database_error(e, context)
                if attempt < max_retries - 1:
                    logger.warning(
                        "🔄 DB connection attempt %d/%d failed. Retrying in %.2f seconds...",
                        attempt + 1,
                        max_retries,
                        wait_time,
                    )
                    await asyncio.sleep(wait_time)
        self._is_healthy = False
        logger.error("❌ Could not connect to the database after %d attempts.", max_retries)
        raise last_exception

    async def health_check(self) -> bool:
        """🩺 Enhanced health check with performance monitoring"""
        if not self._pool:
            self._is_healthy = False
            return False
        try:
            async with self._pool.acquire(timeout=5) as conn:
                await conn.execute("SELECT 1")
                start_time = asyncio.get_event_loop().time()
                await conn.fetchval("SELECT COUNT(*) FROM information_schema.tables")
                query_time = asyncio.get_event_loop().time() - start_time
                if query_time > 1.0:
                    logger.warning(f"⚠️ Slow database query detected: {query_time:.3f}s")
            self._is_healthy = True
            return True
        except Exception as e:
            self._is_healthy = False
            context = ErrorContext().add("operation", "enhanced_health_check")
            ErrorHandler.handle_database_error(e, context)
            return False

    async def get_performance_stats(self) -> dict:
        """📊 Get database performance statistics"""
        if not self._pool:
            return {"status": "no_pool"}
        stats = {
            "pool_size": self._pool.get_size(),
            "pool_free": self._pool.get_idle_size(),
            "pool_used": self._pool.get_size() - self._pool.get_idle_size(),
            "is_healthy": self._is_healthy,
            "performance_mode": self._performance_enabled,
        }
        if self._performance_enabled:
            try:
                perf_stats = await performance_manager.get_performance_stats()
                stats.update(perf_stats)
            except Exception:
                pass
        return stats

    async def optimize_database(self):
        """🛠️ Run database optimization procedures"""
        if not self._pool:
            return
        try:
            async with self._pool.acquire() as conn:
                await conn.execute("ANALYZE;")
                await conn.execute("VACUUM (ANALYZE);")
                logger.info("✅ Database optimization completed")
        except Exception as e:
            logger.error(f"❌ Database optimization failed: {e}")

    async def close_pool(self):
        """🏁 Close the database pool gracefully with cleanup"""
        cleanup_tasks = []
        if self._performance_enabled:
            cleanup_tasks.append(performance_manager.close())
        if self._pool:
            cleanup_tasks.append(self._pool.close())
        try:
            if cleanup_tasks:
                await asyncio.gather(*cleanup_tasks, return_exceptions=True)
            logger.info("✅ Enhanced database pool closed successfully")
        except Exception as e:
            context = ErrorContext().add("operation", "enhanced_close_pool")
            ErrorHandler.handle_database_error(e, context)
        finally:
            self._pool = None
            self._is_healthy = False


db_manager = DatabaseManager()


async def create_pool(max_retries: int = 5, backoff_factor: float = 0.5) -> Pool:
    """
    Creates a connection pool with retry logic.
    Backward compatibility wrapper.
    """
    return await db_manager.create_pool(max_retries, backoff_factor)


async def get_pool() -> Pool | None:
    """Get the current database pool"""
    return db_manager.pool


async def is_db_healthy() -> bool:
    """Check if database is healthy"""
    return await db_manager.health_check()

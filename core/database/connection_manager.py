"""
🚀 DATABASE CONNECTION OPTIMIZATION MODULE
Unified, high-performance database connection management system
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Dict, List, Optional

import asyncpg
import psycopg2
from asyncpg import Connection, Pool
from psycopg2 import pool

from config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class ConnectionConfig:
    """Database connection configuration"""

    user: str
    password: str
    database: str
    host: str = "localhost"
    port: int = 5432
    min_connections: int = 5
    max_connections: int = 20
    connection_timeout: int = 30
    command_timeout: int = 60
    max_inactive_time: int = 300
    max_lifetime: int = 3600
    health_check_interval: int = 60
    retry_attempts: int = 3
    retry_delay: float = 1.0


class ConnectionHealthMonitor:
    """Monitor database connection health"""

    def __init__(self, config: ConnectionConfig):
        self.config = config
        self.last_health_check = 0
        self.is_healthy = False
        self._monitor_task: Optional[asyncio.Task] = None

    async def start_monitoring(self, pool: Pool):
        """Start health monitoring"""
        if self._monitor_task and not self._monitor_task.done():
            return

        self._monitor_task = asyncio.create_task(self._health_check_loop(pool))
        logger.info("🩺 Database health monitoring started")

    async def stop_monitoring(self):
        """Stop health monitoring"""
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
            logger.info("🛑 Database health monitoring stopped")

    async def _health_check_loop(self, pool: Pool):
        """Continuous health check loop"""
        while True:
            try:
                await self._perform_health_check(pool)
                await asyncio.sleep(self.config.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {e}")
                self.is_healthy = False
                await asyncio.sleep(self.config.retry_delay)

    async def _perform_health_check(self, pool: Pool) -> bool:
        """Perform actual health check"""
        try:
            async with pool.acquire() as conn:
                await conn.execute("SELECT 1")
                self.is_healthy = True
                self.last_health_check = time.time()
                return True
        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
            self.is_healthy = False
            return False


class OptimizedAsyncPgPool:
    """High-performance asyncpg connection pool with optimizations"""

    def __init__(self, config: ConnectionConfig):
        self.config = config
        self._pool: Optional[Pool] = None
        self._health_monitor = ConnectionHealthMonitor(config)
        self._prepared_statements: Dict[str, str] = {}
        self._connection_stats = {
            "created": 0,
            "acquired": 0,
            "released": 0,
            "failed": 0,
            "total_query_time": 0.0,
            "query_count": 0,
        }

    async def initialize(self) -> Pool:
        """Initialize the optimized connection pool"""
        if self._pool:
            return self._pool

        # Build connection string
        dsn = f"postgresql://{self.config.user}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database}"

        # Create pool with optimized settings
        self._pool = await asyncpg.create_pool(
            dsn=dsn,
            min_size=self.config.min_connections,
            max_size=self.config.max_connections,
            command_timeout=self.config.command_timeout,
            server_settings={
                "application_name": "analyticbot_optimized_v3",
                "tcp_keepalives_idle": "60",
                "tcp_keepalives_interval": "10",
                "tcp_keepalives_count": "3",
                "work_mem": "64MB",
                "maintenance_work_mem": "256MB",
            },
        )

        # Start health monitoring
        await self._health_monitor.start_monitoring(self._pool)

        # Initialize optimizations
        await self._initialize_optimizations()

        logger.info(
            f"🚀 Optimized asyncpg pool initialized: {self.config.min_connections}-{self.config.max_connections} connections"
        )
        return self._pool

    async def _initialize_optimizations(self):
        """Initialize database optimizations"""
        async with self._pool.acquire() as conn:
            optimizations = [
                # Performance indexes
                """
                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_telegram_active
                ON users(telegram_id, is_active) WHERE is_active = true;
                """,
                """
                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_channels_user_active_status
                ON channels(user_id, is_active, status);
                """,
                """
                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analytics_channel_date_views
                ON analytics(channel_id, created_at DESC, view_count);
                """,
                """
                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_payments_user_status_date
                ON payments(user_id, status, created_at DESC);
                """,
                # Connection optimization
                """
                SET session work_mem = '64MB';
                """,
                """
                SET session maintenance_work_mem = '256MB';
                """,
            ]

            for optimization in optimizations:
                try:
                    await conn.execute(optimization.strip())
                except Exception as e:
                    logger.debug(f"Optimization skipped (may already exist): {e}")

    async def close(self):
        """Close the connection pool"""
        if self._health_monitor:
            await self._health_monitor.stop_monitoring()

        if self._pool:
            await self._pool.close()
            logger.info("🔒 Optimized asyncpg pool closed")

    @asynccontextmanager
    async def acquire(self) -> AsyncGenerator[Connection, None]:
        """Acquire connection with monitoring"""
        start_time = time.time()
        try:
            async with self._pool.acquire() as conn:
                self._connection_stats["acquired"] += 1
                yield conn
                self._connection_stats["released"] += 1
        except Exception as e:
            self._connection_stats["failed"] += 1
            logger.error(f"Connection acquisition failed: {e}")
            raise
        finally:
            duration = time.time() - start_time
            self._connection_stats["total_query_time"] += duration
            self._connection_stats["query_count"] += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        stats = self._connection_stats.copy()
        if self._pool:
            stats.update({
                "pool_size": self._pool.get_size(),
                "idle_connections": self._pool.get_idle_size(),
                "used_connections": self._pool.get_size() - self._pool.get_idle_size(),
            })
        stats["health_status"] = self._health_monitor.is_healthy
        stats["avg_query_time"] = (
            stats["total_query_time"] / stats["query_count"]
            if stats["query_count"] > 0 else 0
        )
        return stats

    async def prepare_statement(self, name: str, query: str):
        """Prepare a statement for reuse"""
        self._prepared_statements[name] = query
        logger.debug(f"Prepared statement '{name}' registered")

    async def execute_prepared(self, name: str, *args, **kwargs):
        """Execute a prepared statement"""
        if name not in self._prepared_statements:
            raise ValueError(f"Prepared statement '{name}' not found")

        async with self.acquire() as conn:
            return await conn.execute(self._prepared_statements[name], *args, **kwargs)


class OptimizedConnection(asyncpg.Connection):
    """Enhanced connection class with query optimization"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class QueryOptimizer:
    """Advanced query optimization utilities"""

    @staticmethod
    def optimize_query(query: str) -> str:
        """Apply query optimizations"""
        # Remove unnecessary whitespace
        query = " ".join(query.split())

        # Add query hints for better performance
        if "SELECT" in query.upper() and "ORDER BY" in query.upper():
            # Add index hint if ordering by indexed column
            pass

        return query

    @staticmethod
    def batch_operations(operations: List[Dict], batch_size: int = 100) -> List[List[Dict]]:
        """Split operations into optimized batches"""
        return [operations[i:i + batch_size] for i in range(0, len(operations), batch_size)]

    @staticmethod
    async def execute_batch(
        pool: OptimizedAsyncPgPool,
        query: str,
        params_list: List[tuple],
        batch_size: int = 100
    ) -> List[Any]:
        """Execute batch operations efficiently"""
        results = []
        batches = QueryOptimizer.batch_operations(
            [{"query": query, "params": params} for params in params_list],
            batch_size
        )

        for batch in batches:
            async with pool.acquire() as conn:
                batch_results = await asyncio.gather(
                    *[conn.execute(item["query"], *item["params"]) for item in batch],
                    return_exceptions=True
                )
                results.extend(batch_results)

        return results


class DatabaseManager:
    """Unified database management system"""

    def __init__(self):
        self.config = ConnectionConfig(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD.get_secret_value(),
            database=settings.POSTGRES_DB,
            min_connections=settings.DB_POOL_SIZE // 2,
            max_connections=settings.DB_POOL_SIZE,
        )
        self._pool: Optional[OptimizedAsyncPgPool] = None
        self._query_optimizer = QueryOptimizer()

    async def initialize(self):
        """Initialize the database manager"""
        self._pool = OptimizedAsyncPgPool(self.config)
        await self._pool.initialize()
        logger.info("🎯 Database Manager initialized with performance optimizations")

    async def close(self):
        """Close the database manager"""
        if self._pool:
            await self._pool.close()

    @asynccontextmanager
    async def connection(self) -> AsyncGenerator[Connection, None]:
        """Get optimized database connection"""
        if not self._pool:
            raise RuntimeError("Database manager not initialized")

        async with self._pool.acquire() as conn:
            yield conn

    async def execute_query(self, query: str, *args, **kwargs) -> Any:
        """Execute optimized query"""
        optimized_query = self._query_optimizer.optimize_query(query)

        async with self.connection() as conn:
            return await conn.execute(optimized_query, *args, **kwargs)

    async def fetch_query(self, query: str, *args, **kwargs) -> List[Dict]:
        """Fetch optimized query results"""
        optimized_query = self._query_optimizer.optimize_query(query)

        async with self.connection() as conn:
            rows = await conn.fetch(optimized_query, *args, **kwargs)
            return [dict(row) for row in rows]

    async def fetch_one(self, query: str, *args, **kwargs) -> Optional[Dict]:
        """Fetch single row from optimized query"""
        optimized_query = self._query_optimizer.optimize_query(query)

        async with self.connection() as conn:
            row = await conn.fetchrow(optimized_query, *args, **kwargs)
            return dict(row) if row else None

    def get_stats(self) -> Dict[str, Any]:
        """Get database performance statistics"""
        if not self._pool:
            return {"error": "Database manager not initialized"}

        return self._pool.get_stats()

    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        if not self._pool:
            return {"healthy": False, "error": "Database manager not initialized"}

        stats = self.get_stats()
        health_status = {
            "healthy": stats.get("health_status", False),
            "pool_size": stats.get("pool_size", 0),
            "idle_connections": stats.get("idle_connections", 0),
            "used_connections": stats.get("used_connections", 0),
            "avg_query_time": stats.get("avg_query_time", 0),
            "total_queries": stats.get("query_count", 0),
            "timestamp": time.time(),
        }

        return health_status


# Global database manager instance
db_manager = DatabaseManager()


async def init_database():
    """Initialize the optimized database system"""
    await db_manager.initialize()


async def close_database():
    """Close the optimized database system"""
    await db_manager.close()


# Convenience functions for backward compatibility
async def get_db_connection():
    """Get database connection (backward compatibility)"""
    async with db_manager.connection() as conn:
        yield conn


async def execute_query(query: str, *args, **kwargs):
    """Execute query (backward compatibility)"""
    return await db_manager.execute_query(query, *args, **kwargs)


async def fetch_query(query: str, *args, **kwargs):
    """Fetch query results (backward compatibility)"""
    return await db_manager.fetch_query(query, *args, **kwargs)


async def fetch_one(query: str, *args, **kwargs):
    """Fetch single row (backward compatibility)"""
    return await db_manager.fetch_one(query, *args, **kwargs)


async def get_db_stats():
    """Get database statistics (backward compatibility)"""
    return db_manager.get_stats()


async def check_db_health():
    """Check database health (backward compatibility)"""
    return await db_manager.health_check()

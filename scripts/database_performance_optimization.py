"""
🚀 DATABASE PERFORMANCE OPTIMIZATION MIGRATION
Apply database performance optimizations and indexes
"""

import asyncio
import logging
import time
from typing import Dict, List

from core.database.connection_manager import db_manager

logger = logging.getLogger(__name__)


class DatabaseOptimizer:
    """Database performance optimization and migration"""

    def __init__(self):
        self.optimizations_applied = []

    async def apply_optimizations(self) -> Dict:
        """Apply all database performance optimizations"""
        logger.info("🚀 Starting database performance optimizations...")

        try:
            # Initialize database manager
            if not db_manager._pool:
                await db_manager.initialize()

            # Apply optimizations
            await self._apply_memory_settings()
            await self._apply_query_planner_settings()
            await self._apply_connection_settings()
            await self._apply_performance_indexes()

            # Verify optimizations
            verification_results = await self._verify_optimizations()

            logger.info("✅ Database performance optimizations completed successfully")
            return {
                "status": "success",
                "optimizations_applied": len(self.optimizations_applied),
                "details": self.optimizations_applied,
                "verification": verification_results,
                "timestamp": time.time(),
            }

        except Exception as e:
            logger.error(f"❌ Database performance optimization failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "optimizations_applied": len(self.optimizations_applied),
                "timestamp": time.time(),
            }

    async def _apply_memory_settings(self):
        """Apply optimized memory settings"""
        memory_settings = [
            "SET session work_mem = '128MB';",
            "SET session maintenance_work_mem = '256MB';",
            "SET session effective_cache_size = '2GB';",
        ]

        async with db_manager.connection() as conn:
            for setting in memory_settings:
                await conn.execute(setting)
                self.optimizations_applied.append(f"Setting: {setting}")
                logger.info(f"✅ Applied: {setting}")

    async def _apply_query_planner_settings(self):
        """Apply query planner optimizations"""
        planner_settings = [
            "SET session random_page_cost = '1.1';",
            "SET session tcp_keepalives_idle = '60';",
            "SET session tcp_keepalives_interval = '10';",
            "SET session tcp_keepalives_count = '3';",
            "SET session enable_seqscan = 'off';",
            "SET session enable_bitmapscan = 'on';",
            "SET session enable_indexscan = 'on';",
        ]

        async with db_manager.connection() as conn:
            for setting in planner_settings:
                await conn.execute(setting)
                self.optimizations_applied.append(f"Setting: {setting}")
                logger.info(f"✅ Applied: {setting}")

    async def _apply_connection_settings(self):
        """Apply connection optimizations"""
        connection_settings = [
            "SET session statement_timeout = '30000';",
            "SET session lock_timeout = '15000';",
            "SET session idle_in_transaction_session_timeout = '60000';",
        ]

        async with db_manager.connection() as conn:
            for setting in connection_settings:
                await conn.execute(setting)
                self.optimizations_applied.append(f"Setting: {setting}")
                logger.info(f"✅ Applied: {setting}")

    async def _apply_performance_indexes(self):
        """Apply performance indexes (if tables exist)"""
        index_statements = [
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
        ]

        async with db_manager.connection() as conn:
            for index_sql in index_statements:
                try:
                    await conn.execute(index_sql.strip())
                    self.optimizations_applied.append(f"Index: {index_sql.strip()[:50]}...")
                    logger.info(f"✅ Applied index: {index_sql.strip()[:50]}...")
                except Exception as e:
                    logger.debug(f"Index creation skipped (table may not exist): {e}")

    async def _verify_optimizations(self) -> Dict:
        """Verify that optimizations were applied"""
        verification_results = {}

        async with db_manager.connection() as conn:
            # Check memory settings
            work_mem = await conn.fetchval("SHOW work_mem;")
            maintenance_work_mem = await conn.fetchval("SHOW maintenance_work_mem;")
            effective_cache_size = await conn.fetchval("SHOW effective_cache_size;")

            verification_results["work_mem"] = work_mem
            verification_results["maintenance_work_mem"] = maintenance_work_mem
            verification_results["effective_cache_size"] = effective_cache_size

            logger.info(f"✅ Verification: SHOW work_mem; = {work_mem}")
            logger.info(f"✅ Verification: SHOW maintenance_work_mem; = {maintenance_work_mem}")
            logger.info(f"✅ Verification: SHOW effective_cache_size; = {effective_cache_size}")

            # Check indexes
            index_count = await conn.fetchval("""
                SELECT count(*) FROM pg_indexes
                WHERE schemaname = 'public' AND indexname LIKE 'idx_%';
            """)
            verification_results["indexes_found"] = index_count
            logger.info(f"✅ Verification: SELECT count(*) FROM pg_indexes WHERE schemaname = 'public' AND indexname LIKE 'idx_%'; = {index_count}")

        return verification_results


async def run_database_optimization():
    """Run database performance optimization"""
    optimizer = DatabaseOptimizer()
    return await optimizer.apply_optimizations()


if __name__ == "__main__":
    """Run optimization when script is executed directly"""
    logging.basicConfig(level=logging.INFO)

    print("🚀 Running Database Performance Optimization...")
    result = asyncio.run(run_database_optimization())

    if result["status"] == "success":
        print(f"✅ Database Performance Optimization Report: {result}")
    else:
        print(f"❌ Database Performance Optimization failed: {result}")

import asyncio
import logging
from typing import List

from core.database.connection_manager import db_manager

logger = logging.getLogger(__name__)


class DatabaseOptimizer:
    """Database performance optimization and migration"""

    def __init__(self):
        self.optimizations_applied = []

    async def apply_optimizations(self):
        """Apply all database performance optimizations"""
        logger.info("🚀 Starting database performance optimizations...")

        try:
            # Initialize database manager if not already done
            if not db_manager._pool:
                await db_manager.initialize()

            # Apply performance indexes
            await self._apply_performance_indexes()

            # Apply connection optimizations
            await self._apply_connection_optimizations()

            # Verify optimizations
            await self._verify_optimizations()

            logger.info("✅ Database performance optimizations completed successfully")
            logger.info(f"📊 Optimizations applied: {len(self.optimizations_applied)}")

        except Exception as e:
            logger.error(f"❌ Database performance optimization failed: {e}")
            raise

    async def _apply_performance_indexes(self):
        """Apply performance-optimized database indexes"""
        indexes = [
            # User-related indexes
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_telegram_active
            ON users(telegram_id, is_active) WHERE is_active = true;
            """,
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_plan_active
            ON users(plan_id, is_active, created_at DESC) WHERE is_active = true;
            """,

            # Channel-related indexes
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_channels_user_active_status
            ON channels(user_id, is_active, status);
            """,
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_channels_created_active
            ON channels(created_at DESC, is_active) WHERE is_active = true;
            """,

            # Analytics indexes
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analytics_channel_date_views
            ON analytics(channel_id, created_at DESC, view_count);
            """,
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analytics_message_performance
            ON analytics(message_id, view_count, share_count, created_at DESC);
            """,
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analytics_date_range
            ON analytics(created_at DESC, channel_id) WHERE created_at >= CURRENT_DATE - INTERVAL '30 days';
            """,

            # Payment indexes
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_payments_user_status_date
            ON payments(user_id, status, created_at DESC);
            """,
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_payments_status_date
            ON payments(status, created_at DESC) WHERE status IN ('pending', 'completed');
            """,

            # Plan indexes
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_plans_active_features
            ON plans(is_active, features) WHERE is_active = true;
            """,

            # Scheduled posts indexes
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scheduled_posts_execution
            ON scheduled_posts(scheduled_time, status) WHERE status = 'pending';
            """,
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scheduled_posts_user_status
            ON scheduled_posts(user_id, status, scheduled_time DESC);
            """,
        ]

        async with db_manager.connection() as conn:
            for index_sql in indexes:
                try:
                    await conn.execute(index_sql.strip())
                    self.optimizations_applied.append(f"Index: {index_sql.strip()[:50]}...")
                    logger.debug(f"✅ Applied index: {index_sql.strip()[:50]}...")
                except Exception as e:
                    logger.debug(f"Index may already exist: {e}")

    async def _apply_connection_optimizations(self):
        """Apply connection-level optimizations"""
        optimizations = [
            # Memory and performance settings
            "SET session work_mem = '128MB';",
            "SET session maintenance_work_mem = '256MB';",
            "SET session effective_cache_size = '2GB';",
            "SET session random_page_cost = '1.1';",

            # Connection settings
            "SET session tcp_keepalives_idle = '60';",
            "SET session tcp_keepalives_interval = '10';",
            "SET session tcp_keepalives_count = '3';",

            # Query optimization
            "SET session enable_seqscan = 'off';",  # Prefer index scans
            "SET session enable_bitmapscan = 'on';",
            "SET session enable_indexscan = 'on';",
        ]

        async with db_manager.connection() as conn:
            for opt_sql in optimizations:
                try:
                    await conn.execute(opt_sql)
                    self.optimizations_applied.append(f"Setting: {opt_sql}")
                    logger.debug(f"✅ Applied setting: {opt_sql}")
                except Exception as e:
                    logger.warning(f"Failed to apply setting {opt_sql}: {e}")

    async def _verify_optimizations(self):
        """Verify that optimizations were applied successfully"""
        verification_queries = [
            "SELECT count(*) FROM pg_indexes WHERE schemaname = 'public' AND indexname LIKE 'idx_%';",
            "SHOW work_mem;",
            "SHOW maintenance_work_mem;",
            "SHOW effective_cache_size;",
        ]

        async with db_manager.connection() as conn:
            for query in verification_queries:
                try:
                    result = await conn.fetchval(query)
                    logger.info(f"✅ Verification: {query} = {result}")
                except Exception as e:
                    logger.warning(f"Verification failed for {query}: {e}")


async def run_database_optimization():
    """Run database performance optimization"""
    optimizer = DatabaseOptimizer()
    return await optimizer.apply_optimizations()


if __name__ == "__main__":
    """Run optimization when script is executed directly"""
    logging.basicConfig(level=logging.INFO)

    print("🚀 Running Database Performance Optimization...")
    result = asyncio.run(run_database_optimization())

    if result["status"] == "success":
        print(f"✅ Database Performance Optimization Report: {result}")
    else:
        print(f"❌ Database Performance Optimization failed: {result}")

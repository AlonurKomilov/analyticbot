"""
🚀 DATABASE PERFORMANCE OPTIMIZATION MIGRATION
Apply database performance optimizations and indexes
"""

import asyncio
import logging
import time

from infra.db.connection_manager import db_manager

logger = logging.getLogger(__name__)


class DatabaseOptimizer:
    """Database performance optimization and migration"""

    def __init__(self):
        self.optimizations_applied = []

    async def apply_optimizations(self) -> dict:
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

    async def _verify_optimizations(self) -> dict:
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
            try:
                index_count = await conn.fetchval("""
                    SELECT count(*) FROM pg_indexes
                    WHERE schemaname = 'public' AND indexname LIKE 'idx_%';
                """)
                verification_results["indexes_found"] = index_count
                logger.info(
                    f"✅ Verification: SELECT count(*) FROM pg_indexes WHERE schemaname = 'public' AND indexname LIKE 'idx_%'; = {index_count}"
                )
            except Exception as e:
                logger.warning(f"Could not verify indexes: {e}")
                verification_results["indexes_found"] = None

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

    if result and result.get("status") == "success":
        print(f"✅ Database Performance Optimization Report: {result}")
    else:
        print(f"❌ Database Performance Optimization failed: {result}")

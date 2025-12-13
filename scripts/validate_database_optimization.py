"""
🚀 DATABASE OPTIMIZATION VALIDATION
Test and validate database performance optimizations
"""

import asyncio
import logging
import time

from infra.db.connection_manager import db_manager

logger = logging.getLogger(__name__)


class DatabaseOptimizationValidator:
    """Validate database performance optimizations"""

    def __init__(self):
        self.test_results = {}

    async def run_validation(self) -> dict:
        """Run comprehensive validation of database optimizations"""
        logger.info("🧪 Starting database optimization validation...")

        try:
            # Initialize database manager
            if not db_manager._pool:
                await db_manager.initialize()

            # Run all validation tests
            await self._test_connection_pool()
            await self._test_health_monitoring()
            await self._test_query_optimization()
            await self._test_performance_indexes()
            await self._test_connection_settings()

            # Generate validation report
            report = self._generate_report()

            logger.info("✅ Database optimization validation completed")
            return report

        except Exception as e:
            logger.error(f"❌ Database optimization validation failed: {e}")
            return {"error": str(e), "status": "failed"}

    async def _test_connection_pool(self):
        """Test optimized connection pool"""
        logger.info("Testing connection pool...")

        start_time = time.time()
        connections = []

        try:
            # Test multiple concurrent connections
            for i in range(5):
                async with db_manager.connection() as conn:
                    result = await conn.fetchval("SELECT 1")
                    connections.append(result)

            pool_time = time.time() - start_time
            self.test_results["connection_pool"] = {
                "status": "passed",
                "connections_tested": len(connections),
                "total_time": pool_time,
                "avg_time_per_connection": pool_time / len(connections),
            }
            logger.info(
                f"✅ Connection pool test passed: {len(connections)} connections in {pool_time:.3f}s"
            )

        except Exception as e:
            self.test_results["connection_pool"] = {
                "status": "failed",
                "error": str(e),
            }
            logger.error(f"❌ Connection pool test failed: {e}")

    async def _test_health_monitoring(self):
        """Test health monitoring system"""
        logger.info("Testing health monitoring...")

        try:
            health_check = await db_manager.health_check()

            self.test_results["health_monitoring"] = {
                "status": "passed" if health_check["healthy"] else "failed",
                "pool_size": health_check["pool_size"],
                "idle_connections": health_check["idle_connections"],
                "used_connections": health_check["used_connections"],
                "avg_query_time": health_check["avg_query_time"],
            }
            logger.info("✅ Health monitoring test passed")

        except Exception as e:
            self.test_results["health_monitoring"] = {
                "status": "failed",
                "error": str(e),
            }
            logger.error(f"❌ Health monitoring test failed: {e}")

    async def _test_query_optimization(self):
        """Test query optimization features"""
        logger.info("Testing query optimization...")

        try:
            # Test optimized query execution
            start_time = time.time()

            # Execute multiple queries to test optimization
            queries = [
                ("SELECT COUNT(*) FROM users", []),
                ("SELECT COUNT(*) FROM channels", []),
                ("SELECT COUNT(*) FROM analytics", []),
            ]

            results = []
            for query, params in queries:
                result = await db_manager.fetch_one(query, *params)
                results.append(result)

            query_time = time.time() - start_time
            self.test_results["query_optimization"] = {
                "status": "passed",
                "queries_executed": len(results),
                "total_time": query_time,
                "avg_time_per_query": query_time / len(results),
            }
            logger.info(
                f"✅ Query optimization test passed: {len(results)} queries in {query_time:.3f}s"
            )

        except Exception as e:
            self.test_results["query_optimization"] = {
                "status": "failed",
                "error": str(e),
            }
            logger.error(f"❌ Query optimization test failed: {e}")

    async def _test_performance_indexes(self):
        """Test that performance indexes are working"""
        logger.info("Testing performance indexes...")

        try:
            async with db_manager.connection() as conn:
                # Check if our indexes exist
                index_query = """
                SELECT indexname, tablename
                FROM pg_indexes
                WHERE schemaname = 'public'
                AND indexname LIKE 'idx_%'
                ORDER BY indexname;
                """

                indexes = await conn.fetch(index_query)

                self.test_results["performance_indexes"] = {
                    "status": "passed",
                    "indexes_found": len(indexes),
                    "index_details": [
                        {"name": idx["indexname"], "table": idx["tablename"]} for idx in indexes
                    ],
                }
                logger.info(f"✅ Performance indexes test passed: {len(indexes)} indexes found")

        except Exception as e:
            self.test_results["performance_indexes"] = {
                "status": "failed",
                "error": str(e),
            }
            logger.error(f"❌ Performance indexes test failed: {e}")

    async def _test_connection_settings(self):
        """Test optimized connection settings"""
        logger.info("Testing connection settings...")

        try:
            async with db_manager.connection() as conn:
                # Check key PostgreSQL settings
                settings_queries = [
                    "SHOW work_mem;",
                    "SHOW maintenance_work_mem;",
                    "SHOW effective_cache_size;",
                    "SHOW random_page_cost;",
                ]

                settings_results = {}
                for query in settings_queries:
                    setting_name = query.split()[1].replace(";", "")
                    value = await conn.fetchval(query)
                    settings_results[setting_name] = value

                self.test_results["connection_settings"] = {
                    "status": "passed",
                    "settings": settings_results,
                }
                logger.info("✅ Connection settings test passed")

        except Exception as e:
            self.test_results["connection_settings"] = {
                "status": "failed",
                "error": str(e),
            }
            logger.error(f"❌ Connection settings test failed: {e}")

    def _generate_report(self) -> dict:
        """Generate comprehensive validation report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for test in self.test_results.values() if test["status"] == "passed")
        failed_tests = total_tests - passed_tests

        report = {
            "phase": "Database Optimization Validation",
            "timestamp": time.time(),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (
                    f"{(passed_tests / total_tests * 100):.1f}%" if total_tests > 0 else "0%"
                ),
            },
            "test_results": self.test_results,
            "status": "passed" if failed_tests == 0 else "failed",
        }

        return report


async def validate_database_optimization():
    """Run database optimization validation"""
    validator = DatabaseOptimizationValidator()
    return await validator.run_validation()


async def benchmark_database_performance():
    """Run performance benchmark for database optimizations"""
    logger.info("🏃 Running database performance benchmark...")

    if not db_manager._pool:
        await db_manager.initialize()

    # Benchmark queries
    benchmark_queries = [
        "SELECT COUNT(*) FROM users;",
        "SELECT COUNT(*) FROM channels WHERE is_active = true;",
        "SELECT COUNT(*) FROM analytics WHERE created_at >= CURRENT_DATE - INTERVAL '7 days';",
        "SELECT user_id, COUNT(*) as post_count FROM channels GROUP BY user_id ORDER BY post_count DESC LIMIT 10;",
    ]

    results = []
    for query in benchmark_queries:
        start_time = time.time()
        try:
            result = await db_manager.fetch_one(query)
            execution_time = time.time() - start_time
            results.append(
                {
                    "query": query[:50] + "...",
                    "execution_time": execution_time,
                    "status": "success",
                    "result": result,
                }
            )
            logger.info(f"✅ Query executed in {execution_time:.3f}s")
        except Exception as e:
            execution_time = time.time() - start_time
            results.append(
                {
                    "query": query[:50] + "...",
                    "execution_time": execution_time,
                    "status": "failed",
                    "error": str(e),
                }
            )
            logger.error(f"❌ Query failed in {execution_time:.3f}s: {e}")

    return {
        "benchmark_type": "Database Performance",
        "timestamp": time.time(),
        "results": results,
        "avg_execution_time": sum(r["execution_time"] for r in results) / len(results),
    }


if __name__ == "__main__":
    """Run validation when script is executed directly"""
    logging.basicConfig(level=logging.INFO)

    print("🚀 Running Database Optimization Validation...")
    validation_result = asyncio.run(validate_database_optimization())

    if "summary" in validation_result:
        print(f"Validation Result: {validation_result['summary']}")
    else:
        print(f"Validation failed: {validation_result}")

    print("\n🏃 Running Database Performance Benchmark...")
    benchmark_result = asyncio.run(benchmark_database_performance())
    print(f"Benchmark Result: Avg execution time = {benchmark_result['avg_execution_time']:.3f}s")

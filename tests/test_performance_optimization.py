"""
🧪 PERFORMANCE TESTING SUITE
Comprehensive performance testing and benchmarking
"""

import asyncio
import logging
import statistics
import time
from collections.abc import Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

import pytest
import pytest_asyncio

from bot.database.db import db_manager
from bot.database.performance import performance_manager
from bot.optimized_container import container

logger = logging.getLogger(__name__)


@dataclass
class PerformanceResult:
    """Performance test result data"""

    name: str
    duration: float
    success: bool
    iterations: int
    avg_time: float
    min_time: float
    max_time: float
    std_dev: float
    throughput: float
    error_rate: float
    memory_used: int | None = None


class PerformanceTester:
    """🔥 High-performance testing framework"""

    def __init__(self):
        self.results: list[PerformanceResult] = []
        self._setup_complete = False

    async def setup(self):
        """Initialize testing environment"""
        if not self._setup_complete:
            await container.initialize()
            self._setup_complete = True
            logger.info("🧪 Performance testing environment initialized")

    async def teardown(self):
        """Clean up testing environment"""
        if self._setup_complete:
            await container.shutdown()
            self._setup_complete = False
            logger.info("🧹 Performance testing environment cleaned up")

    @asynccontextmanager
    async def measure_performance(self, test_name: str):
        """Context manager for measuring performance"""
        start_time = time.perf_counter()
        start_memory = self._get_memory_usage()

        try:
            yield
        except Exception as e:
            logger.error(f"❌ Test {test_name} failed: {e}")
            raise
        finally:
            end_time = time.perf_counter()
            end_memory = self._get_memory_usage()

            duration = end_time - start_time
            memory_used = (
                end_memory - start_memory if start_memory and end_memory else None
            )

            logger.info(
                f"⏱️ {test_name}: {duration:.3f}s (memory: {memory_used or 0}MB)"
            )

    def _get_memory_usage(self) -> int | None:
        """Get current memory usage in MB"""
        try:
            import psutil

            process = psutil.Process()
            return process.memory_info().rss // 1024 // 1024
        except:
            return None

    async def benchmark_function(
        self,
        name: str,
        func: Callable,
        iterations: int = 100,
        concurrent: bool = False,
        *args,
        **kwargs,
    ) -> PerformanceResult:
        """🏁 Benchmark a function with multiple iterations"""

        logger.info(f"🏃 Running benchmark: {name} ({iterations} iterations)")

        times: list[float] = []
        errors = 0

        start_time = time.perf_counter()

        if concurrent:
            # Concurrent execution
            tasks = []
            for _ in range(iterations):
                task = asyncio.create_task(self._timed_execution(func, *args, **kwargs))
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, Exception):
                    errors += 1
                else:
                    times.append(result)
        else:
            # Sequential execution
            for _ in range(iterations):
                try:
                    execution_time = await self._timed_execution(func, *args, **kwargs)
                    times.append(execution_time)
                except Exception:
                    errors += 1

        total_duration = time.perf_counter() - start_time

        if not times:
            # All iterations failed
            return PerformanceResult(
                name=name,
                duration=total_duration,
                success=False,
                iterations=iterations,
                avg_time=0,
                min_time=0,
                max_time=0,
                std_dev=0,
                throughput=0,
                error_rate=100.0,
            )

        # Calculate statistics
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0
        throughput = len(times) / total_duration
        error_rate = (errors / iterations) * 100

        result = PerformanceResult(
            name=name,
            duration=total_duration,
            success=errors == 0,
            iterations=iterations,
            avg_time=avg_time,
            min_time=min_time,
            max_time=max_time,
            std_dev=std_dev,
            throughput=throughput,
            error_rate=error_rate,
        )

        self.results.append(result)

        logger.info(
            f"✅ {name}: {avg_time:.3f}s avg, {throughput:.1f} ops/sec, "
            f"{error_rate:.1f}% errors"
        )

        return result

    async def _timed_execution(self, func: Callable, *args, **kwargs) -> float:
        """Execute function and return execution time"""
        start_time = time.perf_counter()

        if asyncio.iscoroutinefunction(func):
            await func(*args, **kwargs)
        else:
            func(*args, **kwargs)

        return time.perf_counter() - start_time

    def generate_report(self) -> dict[str, Any]:
        """📊 Generate comprehensive performance report"""
        if not self.results:
            return {"status": "no_results"}

        # Overall statistics
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - successful_tests

        # Performance metrics
        avg_throughput = statistics.mean([r.throughput for r in self.results])
        avg_response_time = statistics.mean([r.avg_time for r in self.results])

        # Find bottlenecks
        slowest_test = max(self.results, key=lambda r: r.avg_time)
        fastest_test = min(self.results, key=lambda r: r.avg_time)

        return {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": (successful_tests / total_tests) * 100,
                "avg_throughput": avg_throughput,
                "avg_response_time": avg_response_time,
            },
            "performance": {
                "slowest_test": {
                    "name": slowest_test.name,
                    "avg_time": slowest_test.avg_time,
                    "throughput": slowest_test.throughput,
                },
                "fastest_test": {
                    "name": fastest_test.name,
                    "avg_time": fastest_test.avg_time,
                    "throughput": fastest_test.throughput,
                },
            },
            "detailed_results": [
                {
                    "name": r.name,
                    "avg_time": r.avg_time,
                    "min_time": r.min_time,
                    "max_time": r.max_time,
                    "std_dev": r.std_dev,
                    "throughput": r.throughput,
                    "error_rate": r.error_rate,
                    "success": r.success,
                }
                for r in self.results
            ],
        }


# Test suite implementation
class TestPerformanceOptimization:
    """🧪 Performance optimization test cases"""

    @pytest_asyncio.fixture(autouse=True)
    async def setup_teardown(self):
        """Setup and teardown for each test"""
        tester = PerformanceTester()
        await tester.setup()
        yield tester
        await tester.teardown()

    async def test_database_connection_performance(self, setup_teardown):
        """Test database connection pool performance"""
        tester = setup_teardown

        async def get_connection():
            async with db_manager.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")

        result = await tester.benchmark_function(
            "database_connection", get_connection, iterations=50, concurrent=True
        )

        # Assert performance criteria
        assert result.success, "Database connection test failed"
        assert result.avg_time < 0.1, f"DB connection too slow: {result.avg_time:.3f}s"
        assert result.throughput > 10, (
            f"DB throughput too low: {result.throughput:.1f} ops/sec"
        )

    async def test_cache_performance(self, setup_teardown):
        """Test Redis cache performance"""
        tester = setup_teardown

        if not performance_manager.cache._is_connected:
            pytest.skip("Redis cache not available")

        async def cache_operations():
            cache = performance_manager.cache
            test_key = "test_performance_key"
            test_value = {"test": "data", "timestamp": time.time()}

            # Set
            await cache.set(test_key, test_value)

            # Get
            result = await cache.get(test_key)
            assert result is not None

            # Delete
            await cache.delete(test_key)

        result = await tester.benchmark_function(
            "cache_operations", cache_operations, iterations=100, concurrent=True
        )

        assert result.success, "Cache operations test failed"
        assert result.avg_time < 0.05, (
            f"Cache operations too slow: {result.avg_time:.3f}s"
        )
        assert result.throughput > 50, (
            f"Cache throughput too low: {result.throughput:.1f} ops/sec"
        )

    async def test_analytics_service_performance(self, setup_teardown):
        """Test optimized analytics service performance"""
        tester = setup_teardown

        # Get analytics service
        analytics_service = container.optimized_analytics_service()

        async def analytics_operation():
            # Test cached analytics retrieval
            return await analytics_service.get_channel_analytics_cached(
                channel_id=12345, days=7
            )

        result = await tester.benchmark_function(
            "analytics_service", analytics_operation, iterations=20, concurrent=True
        )

        assert result.success, "Analytics service test failed"
        assert result.avg_time < 0.5, f"Analytics too slow: {result.avg_time:.3f}s"

    async def test_bulk_operations_performance(self, setup_teardown):
        """Test bulk operations performance"""
        tester = setup_teardown

        async def bulk_query_simulation():
            """Simulate bulk database operations"""
            async with db_manager.pool.acquire() as conn:
                # Simulate bulk insert
                data = [(i, f"test_data_{i}") for i in range(100)]

                # Batch processing simulation
                for batch_start in range(0, len(data), 20):
                    batch = data[batch_start : batch_start + 20]
                    # Simulate batch processing
                    await asyncio.sleep(0.001)  # Minimal processing time

        result = await tester.benchmark_function(
            "bulk_operations", bulk_query_simulation, iterations=10, concurrent=False
        )

        assert result.success, "Bulk operations test failed"
        assert result.avg_time < 1.0, (
            f"Bulk operations too slow: {result.avg_time:.3f}s"
        )

    async def test_concurrent_load_performance(self, setup_teardown):
        """Test system performance under concurrent load"""
        tester = setup_teardown

        async def concurrent_mixed_operations():
            """Mixed operations simulating real load"""
            tasks = []

            # Database operations
            tasks.append(db_manager.health_check())

            # Cache operations (if available)
            if performance_manager.cache._is_connected:
                cache_key = f"load_test_{time.time()}"
                tasks.append(performance_manager.cache.set(cache_key, {"test": True}))
                tasks.append(performance_manager.cache.get(cache_key))

            # Wait for all operations
            await asyncio.gather(*tasks, return_exceptions=True)

        result = await tester.benchmark_function(
            "concurrent_load",
            concurrent_mixed_operations,
            iterations=50,
            concurrent=True,
        )

        assert result.success, "Concurrent load test failed"
        assert result.error_rate < 5.0, f"Too many errors: {result.error_rate:.1f}%"

    async def test_memory_efficiency(self, setup_teardown):
        """Test memory usage efficiency"""
        tester = setup_teardown

        initial_memory = tester._get_memory_usage()

        # Perform memory-intensive operations
        large_data = []
        for i in range(1000):
            large_data.append(
                {"id": i, "data": f"test_data_{i}" * 10, "timestamp": time.time()}
            )

        # Clear data
        del large_data

        final_memory = tester._get_memory_usage()

        if initial_memory and final_memory:
            memory_increase = final_memory - initial_memory
            assert memory_increase < 50, (
                f"Memory leak detected: {memory_increase}MB increase"
            )

        logger.info("✅ Memory efficiency test completed")


async def run_comprehensive_performance_test():
    """🚀 Run comprehensive performance test suite"""
    tester = PerformanceTester()

    try:
        await tester.setup()

        logger.info("🧪 Starting comprehensive performance tests...")

        # Test database performance
        async def db_test():
            async with db_manager.pool.acquire() as conn:
                return await conn.fetchval(
                    "SELECT COUNT(*) FROM information_schema.tables"
                )

        await tester.benchmark_function("database_query", db_test, iterations=50)

        # Test cache performance (if available)
        if performance_manager.cache._is_connected:

            async def cache_test():
                await performance_manager.cache.set("test_key", {"test": True})
                result = await performance_manager.cache.get("test_key")
                await performance_manager.cache.delete("test_key")
                return result

            await tester.benchmark_function(
                "cache_operations", cache_test, iterations=100
            )

        # Generate and display report
        report = tester.generate_report()

        logger.info("📊 PERFORMANCE TEST REPORT")
        logger.info("=" * 50)
        logger.info(f"Total Tests: {report['summary']['total_tests']}")
        logger.info(f"Success Rate: {report['summary']['success_rate']:.1f}%")
        logger.info(
            f"Average Throughput: {report['summary']['avg_throughput']:.1f} ops/sec"
        )
        logger.info(
            f"Average Response Time: {report['summary']['avg_response_time']:.3f}s"
        )

        return report

    finally:
        await tester.teardown()


if __name__ == "__main__":
    # Run performance tests
    asyncio.run(run_comprehensive_performance_test())

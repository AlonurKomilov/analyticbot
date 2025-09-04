"""
🧪 PERFORMANCE OPTIMIZATION TESTS
Comprehensive performance testing and optimization module
"""

import asyncio
import logging
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import psutil

sys.path.insert(0, str(Path(__file__).parent.parent))
from apps.bot.database.db import db_manager
from apps.bot.database.performance import performance_manager

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """Results from a performance benchmark"""

    avg_time: float
    throughput: float
    error_rate: float = 0.0
    iterations: int = 0
    min_time: float = 0.0
    max_time: float = 0.0
    std_dev: float = 0.0
    p95_time: float = 0.0
    p99_time: float = 0.0


class PerformanceTester:
    """Advanced performance testing class"""

    def __init__(self):
        self.results: dict[str, BenchmarkResult] = {}
        self.start_memory = 0
        self.process = psutil.Process()

    async def setup(self):
        """Setup performance testing environment"""
        try:
            self.start_memory = self.process.memory_info().rss / 1024 / 1024
            logger.info(
                f"Performance tester initialized - baseline memory: {self.start_memory:.1f}MB"
            )
        except Exception as e:
            logger.warning(f"Failed to get baseline memory: {e}")

    async def teardown(self):
        """Cleanup after performance testing"""
        try:
            final_memory = self.process.memory_info().rss / 1024 / 1024
            memory_diff = final_memory - self.start_memory
            logger.info(f"Performance testing complete - memory change: {memory_diff:+.1f}MB")
        except Exception as e:
            logger.warning(f"Failed to get final memory: {e}")

    def _calculate_statistics(self, times: list[float]) -> dict[str, float]:
        """Calculate statistical metrics from timing data"""
        if not times:
            return {"min": 0, "max": 0, "std_dev": 0, "p95": 0, "p99": 0}
        times_sorted = sorted(times)
        n = len(times_sorted)
        p95_idx = int(0.95 * n)
        p99_idx = int(0.99 * n)
        mean = sum(times) / len(times)
        variance = sum((t - mean) ** 2 for t in times) / len(times)
        std_dev = variance**0.5
        return {
            "min": min(times),
            "max": max(times),
            "std_dev": std_dev,
            "p95": times_sorted[min(p95_idx, n - 1)],
            "p99": times_sorted[min(p99_idx, n - 1)],
        }

    async def benchmark_function(
        self,
        name: str,
        func: Callable,
        iterations: int = 10,
        concurrent: bool = False,
        warmup_iterations: int = 2,
    ) -> BenchmarkResult:
        """Benchmark a function with advanced metrics"""
        logger.info(f"Benchmarking {name} - {iterations} iterations, concurrent: {concurrent}")
        for _ in range(warmup_iterations):
            try:
                if asyncio.iscoroutinefunction(func):
                    await func()
                else:
                    func()
            except Exception:
                pass
        times = []
        errors = 0
        if concurrent:

            async def timed_execution():
                try:
                    start = time.perf_counter()
                    if asyncio.iscoroutinefunction(func):
                        await func()
                    else:
                        func()
                    end = time.perf_counter()
                    return end - start
                except Exception as e:
                    logger.debug(f"Error in {name}: {e}")
                    raise

            tasks = [timed_execution() for _ in range(iterations)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    errors += 1
                else:
                    times.append(result)
        else:
            for i in range(iterations):
                try:
                    start = time.perf_counter()
                    if asyncio.iscoroutinefunction(func):
                        await func()
                    else:
                        func()
                    end = time.perf_counter()
                    times.append(end - start)
                except Exception as e:
                    logger.debug(f"Error in {name} iteration {i}: {e}")
                    errors += 1
        if times:
            avg_time = sum(times) / len(times)
            throughput = len(times) / sum(times) if sum(times) > 0 else 0
            stats = self._calculate_statistics(times)
        else:
            avg_time = 0
            throughput = 0
            stats = {"min": 0, "max": 0, "std_dev": 0, "p95": 0, "p99": 0}
        error_rate = errors / iterations * 100
        result = BenchmarkResult(
            avg_time=avg_time,
            throughput=throughput,
            error_rate=error_rate,
            iterations=iterations,
            min_time=stats["min"],
            max_time=stats["max"],
            std_dev=stats["std_dev"],
            p95_time=stats["p95"],
            p99_time=stats["p99"],
        )
        self.results[name] = result
        logger.info(
            f"✅ {name}: {avg_time:.3f}s avg, {throughput:.1f} ops/sec, {error_rate:.1f}% errors"
        )
        return result

    def generate_report(self) -> dict[str, Any]:
        """Generate comprehensive performance report"""
        if not self.results:
            return {"summary": {"total_tests": 0}}
        total_tests = len(self.results)
        avg_response_time = sum(r.avg_time for r in self.results.values()) / total_tests
        avg_throughput = sum(r.throughput for r in self.results.values()) / total_tests
        avg_error_rate = sum(r.error_rate for r in self.results.values()) / total_tests
        success_rate = 100 - avg_error_rate
        best_test = min(self.results.items(), key=lambda x: x[1].avg_time)
        worst_test = max(self.results.items(), key=lambda x: x[1].avg_time)
        return {
            "summary": {
                "total_tests": total_tests,
                "success_rate": success_rate,
                "avg_response_time": avg_response_time,
                "avg_throughput": avg_throughput,
                "avg_error_rate": avg_error_rate,
            },
            "best_performance": {
                "test": best_test[0],
                "avg_time": best_test[1].avg_time,
                "throughput": best_test[1].throughput,
            },
            "worst_performance": {
                "test": worst_test[0],
                "avg_time": worst_test[1].avg_time,
                "throughput": worst_test[1].throughput,
            },
            "detailed_results": {
                name: {
                    "avg_time": result.avg_time,
                    "throughput": result.throughput,
                    "error_rate": result.error_rate,
                    "p95_time": result.p95_time,
                    "p99_time": result.p99_time,
                    "std_dev": result.std_dev,
                }
                for name, result in self.results.items()
            },
        }


async def run_comprehensive_performance_test() -> dict[str, Any] | None:
    """Run comprehensive performance test suite"""
    logger.info("🚀 Starting comprehensive performance test suite...")
    tester = PerformanceTester()
    try:
        await tester.setup()
        logger.info("🔍 Testing database operations...")

        async def db_simple_query():
            if db_manager.pool:
                async with db_manager.pool.acquire() as conn:
                    return await conn.fetchval("SELECT 1")
            return None

        await tester.benchmark_function("db_simple_query", db_simple_query, iterations=50)

        async def db_complex_query():
            if db_manager.pool:
                async with db_manager.pool.acquire() as conn:
                    return await conn.fetch(
                        "\n                    SELECT \n                        generate_series(1, 100) as id,\n                        md5(random()::text) as hash_value,\n                        now() as timestamp\n                "
                    )
            return []

        await tester.benchmark_function("db_complex_query", db_complex_query, iterations=20)
        if performance_manager.cache._is_connected:
            logger.info("🔍 Testing cache operations...")

            async def cache_set_get():
                key = f"perf_test_{time.time()}_{id(asyncio.current_task())}"
                value = {
                    "test_data": "performance_test",
                    "timestamp": time.time(),
                    "complex_data": list(range(100)),
                }
                await performance_manager.cache.set(key, value, 60)
                result = await performance_manager.cache.get(key)
                await performance_manager.cache.delete(key)
                return result is not None

            await tester.benchmark_function("cache_set_get", cache_set_get, iterations=100)
            await tester.benchmark_function(
                "cache_concurrent", cache_set_get, iterations=50, concurrent=True
            )
        logger.info("🔍 Testing mixed workload...")

        async def mixed_workload():
            tasks = []
            tasks.append(db_simple_query())
            if performance_manager.cache._is_connected:

                async def cache_op():
                    key = f"mixed_test_{time.time()}"
                    await performance_manager.cache.set(key, {"mixed": True}, 30)
                    result = await performance_manager.cache.get(key)
                    await performance_manager.cache.delete(key)
                    return result

                tasks.append(cache_op())
                tasks.append(cache_op())
            results = await asyncio.gather(*tasks, return_exceptions=True)
            successful = len([r for r in results if not isinstance(r, Exception)])
            return successful >= len(tasks) // 2

        await tester.benchmark_function("mixed_workload", mixed_workload, iterations=30)
        logger.info("🔍 Running stress test...")

        async def stress_test():
            db_tasks = [db_simple_query() for _ in range(10)]
            cache_tasks = []
            if performance_manager.cache._is_connected:
                for i in range(20):

                    async def cache_stress_op():
                        key = f"stress_{i}_{time.time()}"
                        data = {"stress_test": True, "data": list(range(50))}
                        await performance_manager.cache.set(key, data, 30)
                        result = await performance_manager.cache.get(key)
                        await performance_manager.cache.delete(key)
                        return result

                    cache_tasks.append(cache_stress_op())
            all_tasks = db_tasks + cache_tasks
            results = await asyncio.gather(*all_tasks, return_exceptions=True)
            successful = len([r for r in results if not isinstance(r, Exception)])
            return successful / len(all_tasks) >= 0.8

        await tester.benchmark_function("stress_test", stress_test, iterations=10)
        report = tester.generate_report()
        logger.info("📊 Comprehensive performance test completed!")
        logger.info(f"✅ Success rate: {report['summary']['success_rate']:.1f}%")
        logger.info(f"⚡ Average throughput: {report['summary']['avg_throughput']:.1f} ops/sec")
        logger.info(f"⏱️ Average response time: {report['summary']['avg_response_time']:.3f}s")
        return report
    except Exception as e:
        logger.error(f"❌ Comprehensive performance test failed: {e}")
        return None
    finally:
        await tester.teardown()

    async def test_memory_efficiency(self, setup_teardown):
        """Test memory usage efficiency"""
        tester = setup_teardown
        initial_memory = tester._get_memory_usage()
        large_data = []
        for i in range(1000):
            large_data.append({"id": i, "data": f"test_data_{i}" * 10, "timestamp": time.time()})
        del large_data
        final_memory = tester._get_memory_usage()
        if initial_memory and final_memory:
            memory_increase = final_memory - initial_memory
            assert memory_increase < 50, f"Memory leak detected: {memory_increase}MB increase"
        logger.info("✅ Memory efficiency test completed")


if __name__ == "__main__":
    asyncio.run(run_comprehensive_performance_test())

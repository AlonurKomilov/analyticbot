"""
🧪 SIMPLIFIED PERFORMANCE TESTS
Lightweight performance testing without complex dependencies
"""

import asyncio
import logging
import statistics
import sys
import time
from pathlib import Path
from typing import Any

import psutil

sys.path.insert(0, str(Path(__file__).parent))
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class SimplifiedPerformanceTester:
    """🔥 Lightweight performance testing framework"""

    def __init__(self):
        self.results: list[dict[str, Any]] = []

    async def measure_async_function(self, name: str, func, iterations: int = 10) -> dict[str, Any]:
        """Measure performance of an async function"""
        logger.info(f"🔍 Testing {name} ({iterations} iterations)...")
        times = []
        errors = 0
        for i in range(iterations):
            try:
                start_time = time.perf_counter()
                await func()
                end_time = time.perf_counter()
                times.append(end_time - start_time)
            except Exception as e:
                errors += 1
                logger.debug(f"Error in iteration {i}: {e}")
        if not times:
            return {
                "name": name,
                "success": False,
                "error_rate": 100.0,
                "avg_time": 0,
                "throughput": 0,
            }
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0
        throughput = len(times) / sum(times) if sum(times) > 0 else 0
        error_rate = errors / iterations * 100
        result = {
            "name": name,
            "success": errors == 0,
            "iterations": iterations,
            "successful_iterations": len(times),
            "avg_time": avg_time,
            "min_time": min_time,
            "max_time": max_time,
            "std_dev": std_dev,
            "throughput": throughput,
            "error_rate": error_rate,
        }
        self.results.append(result)
        logger.info(
            f"✅ {name}: {avg_time:.3f}s avg, {throughput:.1f} ops/sec, {error_rate:.1f}% errors"
        )
        return result

    def measure_sync_function(self, name: str, func, iterations: int = 100) -> dict[str, Any]:
        """Measure performance of a sync function"""
        logger.info(f"🔍 Testing {name} ({iterations} iterations)...")
        times = []
        errors = 0
        for i in range(iterations):
            try:
                start_time = time.perf_counter()
                func()
                end_time = time.perf_counter()
                times.append(end_time - start_time)
            except Exception as e:
                errors += 1
                logger.debug(f"Error in iteration {i}: {e}")
        if not times:
            return {
                "name": name,
                "success": False,
                "error_rate": 100.0,
                "avg_time": 0,
                "throughput": 0,
            }
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0
        throughput = len(times) / sum(times) if sum(times) > 0 else 0
        error_rate = errors / iterations * 100
        result = {
            "name": name,
            "success": errors == 0,
            "iterations": iterations,
            "successful_iterations": len(times),
            "avg_time": avg_time,
            "min_time": min_time,
            "max_time": max_time,
            "std_dev": std_dev,
            "throughput": throughput,
            "error_rate": error_rate,
        }
        self.results.append(result)
        logger.info(
            f"✅ {name}: {avg_time:.3f}s avg, {throughput:.1f} ops/sec, {error_rate:.1f}% errors"
        )
        return result

    def get_system_metrics(self) -> dict[str, Any]:
        """Get current system performance metrics"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "memory_available_mb": psutil.virtual_memory().available / 1024 / 1024,
                "disk_usage_percent": psutil.disk_usage("/").percent,
                "load_average": psutil.getloadavg() if hasattr(psutil, "getloadavg") else None,
            }
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return {}

    def generate_report(self) -> dict[str, Any]:
        """Generate performance test report"""
        if not self.results:
            return {"status": "no_results"}
        successful_tests = [r for r in self.results if r["success"]]
        failed_tests = [r for r in self.results if not r["success"]]
        return {
            "summary": {
                "total_tests": len(self.results),
                "successful_tests": len(successful_tests),
                "failed_tests": len(failed_tests),
                "success_rate": len(successful_tests) / len(self.results) * 100,
                "avg_response_time": statistics.mean([r["avg_time"] for r in successful_tests])
                if successful_tests
                else 0,
                "avg_throughput": statistics.mean([r["throughput"] for r in successful_tests])
                if successful_tests
                else 0,
            },
            "detailed_results": self.results,
            "system_metrics": self.get_system_metrics(),
        }


async def test_basic_async_operations():
    """Test basic async operations performance"""

    async def async_sleep_test():
        """Test async sleep (simulates I/O wait)"""
        await asyncio.sleep(0.001)

    async def async_computation_test():
        """Test CPU computation in async context"""
        result = sum(i * i for i in range(1000))
        return result

    async def concurrent_operations_test():
        """Test concurrent operations"""
        tasks = [
            asyncio.create_task(asyncio.sleep(0.001)),
            asyncio.create_task(asyncio.sleep(0.001)),
            asyncio.create_task(asyncio.sleep(0.001)),
        ]
        await asyncio.gather(*tasks)

    tester = SimplifiedPerformanceTester()
    await tester.measure_async_function("async_sleep", async_sleep_test, 50)
    await tester.measure_async_function("async_computation", async_computation_test, 100)
    await tester.measure_async_function("concurrent_operations", concurrent_operations_test, 20)
    return tester.generate_report()


def test_memory_operations():
    """Test memory-related operations"""

    def small_memory_allocation():
        """Small memory allocation test"""
        data = [i for i in range(1000)]
        return len(data)

    def large_memory_allocation():
        """Large memory allocation test"""
        data = [{"id": i, "data": f"test_{i}" * 10} for i in range(10000)]
        return len(data)

    def memory_cleanup_test():
        """Memory allocation and cleanup test"""
        data = [i * i for i in range(50000)]
        del data
        return True

    tester = SimplifiedPerformanceTester()
    tester.measure_sync_function("small_memory_alloc", small_memory_allocation, 1000)
    tester.measure_sync_function("large_memory_alloc", large_memory_allocation, 50)
    tester.measure_sync_function("memory_cleanup", memory_cleanup_test, 100)
    return tester.generate_report()


def test_cpu_intensive_operations():
    """Test CPU-intensive operations"""

    def fibonacci_calculation():
        """Calculate fibonacci numbers (CPU intensive)"""

        def fib(n):
            if n <= 1:
                return n
            return fib(n - 1) + fib(n - 2)

        return fib(20)

    def sorting_operation():
        """Sorting operation test"""
        import random

        data = [random.randint(1, 1000) for _ in range(10000)]
        data.sort()
        return len(data)

    def string_operations():
        """String manipulation test"""
        text = "performance test " * 1000
        processed = text.upper().replace("TEST", "TESTING").split()
        return len(processed)

    tester = SimplifiedPerformanceTester()
    tester.measure_sync_function("fibonacci_calc", fibonacci_calculation, 10)
    tester.measure_sync_function("sorting_operation", sorting_operation, 50)
    tester.measure_sync_function("string_operations", string_operations, 100)
    return tester.generate_report()


async def test_database_simulation():
    """Test database-like operations (without actual DB)"""
    fake_db = {}

    async def db_insert_simulation():
        """Simulate database insert"""
        key = f"user_{time.time()}_{len(fake_db)}"
        fake_db[key] = {
            "id": len(fake_db) + 1,
            "name": f"User {len(fake_db)}",
            "created_at": time.time(),
            "metadata": {"test": True},
        }
        await asyncio.sleep(0.0001)
        return key

    async def db_query_simulation():
        """Simulate database query"""
        if not fake_db:
            return None
        await asyncio.sleep(0.0001)
        import random

        key = random.choice(list(fake_db.keys()))
        return fake_db[key]

    async def db_update_simulation():
        """Simulate database update"""
        if not fake_db:
            return False
        await asyncio.sleep(0.0001)
        import random

        key = random.choice(list(fake_db.keys()))
        fake_db[key]["updated_at"] = time.time()
        return True

    tester = SimplifiedPerformanceTester()
    for _i in range(100):
        await db_insert_simulation()
    await tester.measure_async_function("db_insert", db_insert_simulation, 100)
    await tester.measure_async_function("db_query", db_query_simulation, 200)
    await tester.measure_async_function("db_update", db_update_simulation, 100)
    logger.info(f"📊 Simulated DB contains {len(fake_db)} records")
    return tester.generate_report()


async def test_cache_simulation():
    """Test cache-like operations (without actual Redis)"""
    cache = {}
    cache_stats = {"hits": 0, "misses": 0}

    async def cache_set_operation():
        """Simulate cache set"""
        key = f"cache_key_{time.time()}_{len(cache)}"
        value = {"data": f"cached_value_{len(cache)}", "timestamp": time.time()}
        cache[key] = value
        await asyncio.sleep(5e-05)
        return True

    async def cache_get_operation():
        """Simulate cache get with hit/miss logic"""
        import random

        if not cache or random.random() < 0.1:
            cache_stats["misses"] += 1
            await asyncio.sleep(0.0001)
            return None
        else:
            cache_stats["hits"] += 1
            key = random.choice(list(cache.keys()))
            await asyncio.sleep(5e-05)
            return cache[key]

    async def cache_delete_operation():
        """Simulate cache delete"""
        if not cache:
            return False
        import random

        key = random.choice(list(cache.keys()))
        del cache[key]
        await asyncio.sleep(5e-05)
        return True

    tester = SimplifiedPerformanceTester()
    for _i in range(50):
        await cache_set_operation()
    await tester.measure_async_function("cache_set", cache_set_operation, 100)
    await tester.measure_async_function("cache_get", cache_get_operation, 200)
    await tester.measure_async_function("cache_delete", cache_delete_operation, 50)
    hit_rate = cache_stats["hits"] / (cache_stats["hits"] + cache_stats["misses"]) * 100
    logger.info(f"📦 Simulated cache hit rate: {hit_rate:.1f}%")
    return tester.generate_report()


async def main():
    """🚀 Run simplified performance tests"""
    logger.info("🚀 Starting simplified performance testing...")
    logger.info("=" * 60)
    start_time = time.time()
    all_results = {}
    try:
        logger.info("🧪 PHASE 1: BASIC ASYNC OPERATIONS")
        logger.info("-" * 40)
        async_results = await test_basic_async_operations()
        all_results["async_operations"] = async_results
        logger.info("\n🧠 PHASE 2: MEMORY OPERATIONS")
        logger.info("-" * 40)
        memory_results = test_memory_operations()
        all_results["memory_operations"] = memory_results
        logger.info("\n💻 PHASE 3: CPU INTENSIVE OPERATIONS")
        logger.info("-" * 40)
        cpu_results = test_cpu_intensive_operations()
        all_results["cpu_operations"] = cpu_results
        logger.info("\n🗄️ PHASE 4: DATABASE SIMULATION")
        logger.info("-" * 40)
        db_results = await test_database_simulation()
        all_results["database_simulation"] = db_results
        logger.info("\n📦 PHASE 5: CACHE SIMULATION")
        logger.info("-" * 40)
        cache_results = await test_cache_simulation()
        all_results["cache_simulation"] = cache_results
        total_time = time.time() - start_time
        logger.info("\n" + "=" * 80)
        logger.info("🏆 SIMPLIFIED PERFORMANCE TEST REPORT")
        logger.info("=" * 80)
        logger.info(f"⏱️ Total testing time: {total_time:.2f} seconds")
        logger.info(f"📊 Test categories: {len(all_results)}")
        for category, results in all_results.items():
            if "summary" in results:
                summary = results["summary"]
                logger.info(f"\n🔍 {category.upper().replace('_', ' ')}:")
                logger.info(f"   ✅ Success rate: {summary['success_rate']:.1f}%")
                logger.info(f"   ⚡ Avg throughput: {summary['avg_throughput']:.1f} ops/sec")
                logger.info(f"   ⏱️ Avg response: {summary['avg_response_time']:.4f}s")
                logger.info(f"   📈 Tests run: {summary['total_tests']}")
        logger.info("\n💡 PERFORMANCE ANALYSIS:")
        logger.info("-" * 40)
        recommendations = []
        for category, results in all_results.items():
            if "summary" in results:
                summary = results["summary"]
                if summary["success_rate"] < 100:
                    recommendations.append(
                        f"Check {category} - {100 - summary['success_rate']:.1f}% failure rate"
                    )
                if summary["avg_response_time"] > 0.01:
                    recommendations.append(
                        f"{category} response time high: {summary['avg_response_time']:.3f}s"
                    )
                if summary["avg_throughput"] < 100:
                    recommendations.append(
                        f"{category} throughput could be improved: {summary['avg_throughput']:.1f} ops/sec"
                    )
        if recommendations:
            logger.info("⚠️ Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                logger.info(f"   {i}. {rec}")
        else:
            logger.info("🎉 All performance metrics look excellent!")
        if all_results and "async_operations" in all_results:
            system_metrics = all_results["async_operations"].get("system_metrics", {})
            if system_metrics:
                logger.info("\n🖥️ SYSTEM HEALTH:")
                logger.info(f"   🔥 CPU Usage: {system_metrics.get('cpu_percent', 'N/A')}%")
                logger.info(f"   🧠 Memory Usage: {system_metrics.get('memory_percent', 'N/A')}%")
                logger.info(
                    f"   💾 Available Memory: {system_metrics.get('memory_available_mb', 'N/A'):.0f}MB"
                )
                logger.info(f"   💿 Disk Usage: {system_metrics.get('disk_usage_percent', 'N/A')}%")
        logger.info(f"\n✅ Simplified performance testing completed in {total_time:.2f}s!")
        return all_results
    except Exception as e:
        logger.error(f"❌ Performance testing failed: {e}")
        return None


if __name__ == "__main__":
    asyncio.run(main())

"""
🧪 PERFORMANCE TEST RUNNER
Main entry point for running performance tests
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
try:
    from tests.test_performance_optimization import (
        PerformanceTester,
        run_comprehensive_performance_test,
    )
except ImportError:
    raise ImportError(
        "Performance optimization test module not found. Please ensure tests/test_performance_optimization.py exists."
    )
from src.database.db import db_manager
from src.database.performance import performance_manager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("performance_test.log")],
)
logger = logging.getLogger(__name__)


async def setup_test_environment():
    """🔧 Setup test environment"""
    logger.info("🔧 Setting up performance test environment...")
    try:
        await performance_manager.initialize()
        logger.info("✅ Performance manager initialized")
        await db_manager.create_pool()
        health = await db_manager.health_check()
        if health:
            logger.info("✅ Database connection healthy")
        else:
            logger.warning("⚠️ Database health check failed")
        return True
    except Exception as e:
        logger.error(f"❌ Environment setup failed: {e}")
        return False


async def run_basic_performance_tests():
    """🧪 Run basic performance tests"""
    logger.info("🧪 Running basic performance tests...")
    tester = PerformanceTester()
    try:
        await tester.setup()
        logger.info("🔍 Testing database connection performance...")

        async def db_connection_test():
            if db_manager.pool:
                async with db_manager.pool.acquire() as conn:
                    result = await conn.fetchval("SELECT 1 as test_value")
                    return result
            return None

        db_result = await tester.benchmark_function(
            "database_connection_basic", db_connection_test, iterations=20, concurrent=False
        )
        logger.info(
            f"📊 DB Connection: {db_result.avg_time:.3f}s avg, {db_result.throughput:.1f} ops/sec"
        )
        if performance_manager.cache._is_connected:
            logger.info("🔍 Testing cache performance...")

            async def cache_test():
                key = f"test_key_{time.time()}"
                value = {"test": "data", "timestamp": time.time()}
                await performance_manager.cache.set(key, value)
                result = await performance_manager.cache.get(key)
                await performance_manager.cache.delete(key)
                return result is not None

            cache_result = await tester.benchmark_function(
                "cache_operations_basic", cache_test, iterations=50, concurrent=False
            )
            logger.info(
                f"📦 Cache: {cache_result.avg_time:.3f}s avg, {cache_result.throughput:.1f} ops/sec"
            )
        else:
            logger.warning("⚠️ Cache not available for testing")
        logger.info("🔍 Testing concurrent operations...")

        async def concurrent_test():
            tasks = []
            tasks.append(db_connection_test())
            if performance_manager.cache._is_connected:

                async def quick_cache():
                    key = f"concurrent_test_{time.time()}"
                    await performance_manager.cache.set(key, {"concurrent": True}, 60)
                    result = await performance_manager.cache.get(key)
                    await performance_manager.cache.delete(key)
                    return result

                tasks.append(quick_cache())
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return len([r for r in results if not isinstance(r, Exception)])

        concurrent_result = await tester.benchmark_function(
            "concurrent_operations_basic", concurrent_test, iterations=10, concurrent=False
        )
        logger.info(
            f"🔄 Concurrent: {concurrent_result.avg_time:.3f}s avg, {concurrent_result.throughput:.1f} ops/sec"
        )
        report = tester.generate_report()
        logger.info("📊 BASIC PERFORMANCE TEST RESULTS:")
        logger.info("=" * 50)
        logger.info(f"✅ Total tests: {report['summary']['total_tests']}")
        logger.info(f"✅ Success rate: {report['summary']['success_rate']:.1f}%")
        logger.info(f"⚡ Avg throughput: {report['summary']['avg_throughput']:.1f} ops/sec")
        logger.info(f"⏱️ Avg response time: {report['summary']['avg_response_time']:.3f}s")
        return report
    except Exception as e:
        logger.error(f"❌ Basic performance tests failed: {e}")
        return None
    finally:
        await tester.teardown()


async def run_load_test():
    """🔥 Run load testing"""
    logger.info("🔥 Running load testing...")
    tester = PerformanceTester()
    try:
        await tester.setup()

        async def high_load_simulation():
            """Simulate high concurrent load"""
            tasks = []
            for i in range(5):

                async def db_op():
                    if db_manager.pool:
                        async with db_manager.pool.acquire() as conn:
                            result = await conn.fetchval("SELECT pg_sleep(0.01), 1")
                            return result
                    return None

                tasks.append(db_op())
            if performance_manager.cache._is_connected:
                for i in range(10):

                    async def cache_op():
                        key = f"load_test_{i}_{time.time()}"
                        value = {"load_test": True, "iteration": i}
                        await performance_manager.cache.set(key, value, 30)
                        result = await performance_manager.cache.get(key)
                        await performance_manager.cache.delete(key)
                        return result is not None

                    tasks.append(cache_op())
            results = await asyncio.gather(*tasks, return_exceptions=True)
            successful = len([r for r in results if not isinstance(r, Exception)])
            return successful

        load_result = await tester.benchmark_function(
            "high_load_simulation", high_load_simulation, iterations=5, concurrent=True
        )
        logger.info(
            f"🔥 Load Test: {load_result.avg_time:.3f}s avg, {load_result.error_rate:.1f}% errors"
        )
        logger.info("🧠 Testing memory usage...")
        import psutil

        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024
        large_data = []
        for i in range(1000):
            large_data.append(
                {
                    "id": i,
                    "data": f"test_data_{i}" * 50,
                    "timestamp": time.time(),
                    "metadata": {"iteration": i, "test": True},
                }
            )
        peak_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = peak_memory - initial_memory
        del large_data
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_retained = final_memory - initial_memory
        logger.info("🧠 Memory Usage:")
        logger.info(f"   📈 Peak increase: {memory_increase:.1f} MB")
        logger.info(f"   📊 Retained after cleanup: {memory_retained:.1f} MB")
        if memory_retained > 20:
            logger.warning(f"⚠️ Potential memory leak detected: {memory_retained:.1f} MB retained")
        else:
            logger.info("✅ Memory usage looks healthy")
        return {
            "load_test": load_result,
            "memory": {
                "peak_increase_mb": memory_increase,
                "retained_mb": memory_retained,
                "potential_leak": memory_retained > 20,
            },
        }
    except Exception as e:
        logger.error(f"❌ Load testing failed: {e}")
        return None
    finally:
        await tester.teardown()


async def run_cache_effectiveness_test():
    """📦 Test cache effectiveness"""
    if not performance_manager.cache._is_connected:
        logger.warning("⚠️ Cache not available, skipping cache effectiveness test")
        return None
    logger.info("📦 Testing cache effectiveness...")
    try:
        cache = performance_manager.cache
        test_keys = [f"cache_test_{i}" for i in range(100)]
        test_values = [{"id": i, "data": f"test_{i}"} for i in range(100)]
        logger.info("📝 Filling cache with test data...")
        for key, value in zip(test_keys, test_values, strict=False):
            await cache.set(key, value, 300)
        logger.info("🔍 Testing cache hit rate...")
        hits = 0
        misses = 0
        start_time = time.time()
        for key in test_keys:
            result = await cache.get(key)
            if result is not None:
                hits += 1
            else:
                misses += 1
        for i in range(20):
            result = await cache.get(f"non_existent_key_{i}")
            if result is not None:
                hits += 1
            else:
                misses += 1
        cache_time = time.time() - start_time
        total_operations = hits + misses
        hit_rate = hits / total_operations * 100 if total_operations > 0 else 0
        for key in test_keys:
            await cache.delete(key)
        logger.info("📊 Cache Effectiveness Results:")
        logger.info(f"   ✅ Hit rate: {hit_rate:.1f}%")
        logger.info(f"   ⚡ Operations: {total_operations}")
        logger.info(f"   ⏱️ Total time: {cache_time:.3f}s")
        logger.info(f"   📈 Throughput: {total_operations / cache_time:.1f} ops/sec")
        return {
            "hit_rate_percent": hit_rate,
            "total_operations": total_operations,
            "total_time_seconds": cache_time,
            "throughput_ops_per_sec": total_operations / cache_time,
        }
    except Exception as e:
        logger.error(f"❌ Cache effectiveness test failed: {e}")
        return None


async def main():
    """🚀 Main performance testing function"""
    logger.info("🚀 Starting comprehensive performance testing...")
    start_time = time.time()
    setup_success = await setup_test_environment()
    if not setup_success:
        logger.error("❌ Failed to setup test environment")
        return
    try:
        results = {}
        logger.info("\n" + "=" * 60)
        logger.info("🧪 PHASE 1: BASIC PERFORMANCE TESTS")
        logger.info("=" * 60)
        basic_results = await run_basic_performance_tests()
        if basic_results:
            results["basic_tests"] = basic_results
            logger.info("✅ Basic performance tests completed")
        logger.info("\n" + "=" * 60)
        logger.info("📦 PHASE 2: CACHE EFFECTIVENESS TEST")
        logger.info("=" * 60)
        cache_results = await run_cache_effectiveness_test()
        if cache_results:
            results["cache_effectiveness"] = cache_results
            logger.info("✅ Cache effectiveness test completed")
        logger.info("\n" + "=" * 60)
        logger.info("🔥 PHASE 3: LOAD TESTING")
        logger.info("=" * 60)
        load_results = await run_load_test()
        if load_results:
            results["load_test"] = load_results
            logger.info("✅ Load testing completed")
        logger.info("\n" + "=" * 60)
        logger.info("🧪 PHASE 4: COMPREHENSIVE TEST SUITE")
        logger.info("=" * 60)
        comprehensive_results = await run_comprehensive_performance_test()
        if comprehensive_results:
            results["comprehensive"] = comprehensive_results
            logger.info("✅ Comprehensive tests completed")
        total_time = time.time() - start_time
        logger.info("\n" + "=" * 80)
        logger.info("🏆 FINAL PERFORMANCE TEST REPORT")
        logger.info("=" * 80)
        logger.info(f"⏱️ Total testing time: {total_time:.2f} seconds")
        logger.info(f"📊 Test phases completed: {len(results)}/4")
        if "basic_tests" in results:
            basic = results["basic_tests"]["summary"]
            logger.info(f"🧪 Basic Tests - Success Rate: {basic['success_rate']:.1f}%")
            logger.info(f"   ⚡ Average Throughput: {basic['avg_throughput']:.1f} ops/sec")
            logger.info(f"   ⏱️ Average Response Time: {basic['avg_response_time']:.3f}s")
        if "cache_effectiveness" in results:
            cache = results["cache_effectiveness"]
            logger.info(f"📦 Cache Effectiveness: {cache['hit_rate_percent']:.1f}% hit rate")
            logger.info(f"   ⚡ Cache Throughput: {cache['throughput_ops_per_sec']:.1f} ops/sec")
        if "load_test" in results:
            load = results["load_test"]
            if "load_test" in load:
                logger.info(f"🔥 Load Test - Error Rate: {load['load_test'].error_rate:.1f}%")
                logger.info(f"   ⏱️ Response Time: {load['load_test'].avg_time:.3f}s")
            if "memory" in load:
                mem = load["memory"]
                logger.info(f"🧠 Memory - Peak Increase: {mem['peak_increase_mb']:.1f}MB")
                logger.info(
                    f"   {('⚠️' if mem['potential_leak'] else '✅')} Memory Leak: {('Detected' if mem['potential_leak'] else 'None')}"
                )
        if "comprehensive" in results:
            comp = results["comprehensive"]["summary"]
            logger.info(f"🏆 Comprehensive Tests - Success Rate: {comp['success_rate']:.1f}%")
            logger.info(f"   📈 Total Tests: {comp['total_tests']}")
        logger.info("\n" + "=" * 60)
        logger.info("💡 PERFORMANCE RECOMMENDATIONS")
        logger.info("=" * 60)
        recommendations = []
        if "basic_tests" in results:
            if results["basic_tests"]["summary"]["avg_response_time"] > 0.1:
                recommendations.append("Consider optimizing database query performance")
        if "cache_effectiveness" in results:
            if results["cache_effectiveness"]["hit_rate_percent"] < 70:
                recommendations.append("Improve cache hit rate by optimizing cache strategy")
        if "load_test" in results and "load_test" in results["load_test"]:
            if results["load_test"]["load_test"].error_rate > 5:
                recommendations.append("Reduce error rate under high load conditions")
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                logger.info(f"{i}. {rec}")
        else:
            logger.info("🎉 All performance metrics look excellent!")
        logger.info("\n✅ Performance testing completed successfully!")
        return results
    except Exception as e:
        logger.error(f"❌ Performance testing failed: {e}")
        return None
    finally:
        try:
            await performance_manager.close()
            await db_manager.close_pool()
        except Exception as e:
            logger.debug(f"Cleanup error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
if __name__ == "__main__":
    asyncio.run(main())

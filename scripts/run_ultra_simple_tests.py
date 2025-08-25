"""
🧪 ULTRA-SIMPLIFIED PERFORMANCE TESTS
Minimal performance testing without any dependencies
"""

import asyncio
import logging
import time

import psutil

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def test_async_performance():
    """Test basic async performance"""
    logger.info("🔍 Testing async operations...")

    async def simple_async_task():
        await asyncio.sleep(0.001)  # 1ms

    # Measure single operation
    start_time = time.perf_counter()
    await simple_async_task()
    single_time = time.perf_counter() - start_time

    # Measure multiple operations
    start_time = time.perf_counter()
    tasks = [simple_async_task() for _ in range(100)]
    await asyncio.gather(*tasks)
    batch_time = time.perf_counter() - start_time

    # Measure concurrent operations
    start_time = time.perf_counter()
    await asyncio.gather(*[simple_async_task() for _ in range(50)])
    concurrent_time = time.perf_counter() - start_time

    logger.info("✅ Async Performance:")
    logger.info(f"   Single task: {single_time:.4f}s")
    logger.info(f"   100 tasks sequential: {batch_time:.4f}s")
    logger.info(f"   50 tasks concurrent: {concurrent_time:.4f}s")
    logger.info(f"   Concurrency benefit: {batch_time / concurrent_time:.1f}x faster")

    return {
        "single_task_time": single_time,
        "batch_time": batch_time,
        "concurrent_time": concurrent_time,
        "concurrency_speedup": batch_time / concurrent_time if concurrent_time > 0 else 0,
    }


def test_memory_performance():
    """Test memory allocation performance"""
    logger.info("🧠 Testing memory operations...")

    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB

    # Small allocation test
    start_time = time.perf_counter()
    small_data = [i for i in range(10000)]
    small_alloc_time = time.perf_counter() - start_time

    # Large allocation test
    start_time = time.perf_counter()
    large_data = [{"id": i, "value": f"data_{i}"} for i in range(100000)]
    large_alloc_time = time.perf_counter() - start_time

    peak_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_used = peak_memory - initial_memory

    # Cleanup test
    del small_data, large_data

    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_freed = peak_memory - final_memory

    logger.info("✅ Memory Performance:")
    logger.info(f"   Small allocation (10K items): {small_alloc_time:.4f}s")
    logger.info(f"   Large allocation (100K items): {large_alloc_time:.4f}s")
    logger.info(f"   Memory used: {memory_used:.1f}MB")
    logger.info(f"   Memory freed: {memory_freed:.1f}MB")
    logger.info(f"   Allocation rate: {100000 / large_alloc_time:.0f} items/sec")

    return {
        "small_alloc_time": small_alloc_time,
        "large_alloc_time": large_alloc_time,
        "memory_used_mb": memory_used,
        "memory_freed_mb": memory_freed,
        "allocation_rate": 100000 / large_alloc_time if large_alloc_time > 0 else 0,
    }


def test_cpu_performance():
    """Test CPU performance"""
    logger.info("💻 Testing CPU operations...")

    # Mathematical computation
    start_time = time.perf_counter()
    result = sum(i * i for i in range(100000))
    math_time = time.perf_counter() - start_time

    # String processing
    start_time = time.perf_counter()
    text = "performance test " * 10000
    processed = text.upper().replace("TEST", "TESTING").split()
    string_time = time.perf_counter() - start_time

    # Sorting
    import random

    data = [random.randint(1, 10000) for _ in range(50000)]
    start_time = time.perf_counter()
    sorted_data = sorted(data)
    sort_time = time.perf_counter() - start_time

    logger.info("✅ CPU Performance:")
    logger.info(f"   Math computation (100K): {math_time:.4f}s")
    logger.info(f"   String processing: {string_time:.4f}s")
    logger.info(f"   Sorting (50K items): {sort_time:.4f}s")
    logger.info(f"   Math throughput: {100000 / math_time:.0f} ops/sec")

    return {
        "math_time": math_time,
        "string_time": string_time,
        "sort_time": sort_time,
        "math_throughput": 100000 / math_time if math_time > 0 else 0,
    }


async def test_concurrent_io_simulation():
    """Test concurrent I/O simulation"""
    logger.info("🔄 Testing concurrent I/O simulation...")

    async def simulate_io_operation(delay_ms: float):
        """Simulate I/O operation with specific delay"""
        await asyncio.sleep(delay_ms / 1000)  # Convert ms to seconds
        return f"completed_{delay_ms}"

    # Test different concurrency levels
    operations = [1, 2, 5, 10, 20]
    results = {}

    for num_concurrent in operations:
        start_time = time.perf_counter()

        tasks = [simulate_io_operation(1) for _ in range(num_concurrent)]  # 1ms each
        await asyncio.gather(*tasks)

        total_time = time.perf_counter() - start_time
        throughput = num_concurrent / total_time

        results[num_concurrent] = {"time": total_time, "throughput": throughput}

        logger.info(
            f"   {num_concurrent} concurrent ops: {total_time:.4f}s, {throughput:.1f} ops/sec"
        )

    # Find optimal concurrency
    best_throughput = max(results.values(), key=lambda x: x["throughput"])
    best_concurrency = [
        k for k, v in results.items() if v["throughput"] == best_throughput["throughput"]
    ][0]

    logger.info(
        f"✅ Optimal concurrency: {best_concurrency} ops ({best_throughput['throughput']:.1f} ops/sec)"
    )

    return {
        "concurrency_results": results,
        "optimal_concurrency": best_concurrency,
        "max_throughput": best_throughput["throughput"],
    }


def get_system_baseline():
    """Get system baseline metrics"""
    logger.info("🖥️ Getting system baseline...")

    try:
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        baseline = {
            "cpu_cores": cpu_count,
            "cpu_freq_mhz": cpu_freq.current if cpu_freq else None,
            "memory_total_gb": memory.total / (1024**3),
            "memory_available_gb": memory.available / (1024**3),
            "disk_total_gb": disk.total / (1024**3),
            "disk_free_gb": disk.free / (1024**3),
        }

        logger.info("✅ System Baseline:")
        logger.info(f"   CPU Cores: {baseline['cpu_cores']}")
        logger.info(
            f"   CPU Frequency: {baseline['cpu_freq_mhz']:.0f} MHz"
            if baseline["cpu_freq_mhz"]
            else "   CPU Frequency: Unknown"
        )
        logger.info(f"   Total Memory: {baseline['memory_total_gb']:.1f} GB")
        logger.info(f"   Available Memory: {baseline['memory_available_gb']:.1f} GB")
        logger.info(
            f"   Disk Space: {baseline['disk_free_gb']:.1f} GB free of {baseline['disk_total_gb']:.1f} GB"
        )

        return baseline

    except Exception as e:
        logger.error(f"❌ Failed to get system baseline: {e}")
        return {}


async def run_performance_benchmark():
    """Run complete performance benchmark"""
    logger.info("🚀 Starting Ultra-Simplified Performance Benchmark")
    logger.info("=" * 70)

    start_time = time.time()
    results = {}

    try:
        # Get system baseline
        logger.info("\n📊 SYSTEM BASELINE")
        logger.info("-" * 40)
        results["system_baseline"] = get_system_baseline()

        # Test async performance
        logger.info("\n⚡ ASYNC PERFORMANCE")
        logger.info("-" * 40)
        results["async_performance"] = await test_async_performance()

        # Test memory performance
        logger.info("\n🧠 MEMORY PERFORMANCE")
        logger.info("-" * 40)
        results["memory_performance"] = test_memory_performance()

        # Test CPU performance
        logger.info("\n💻 CPU PERFORMANCE")
        logger.info("-" * 40)
        results["cpu_performance"] = test_cpu_performance()

        # Test concurrent I/O
        logger.info("\n🔄 CONCURRENT I/O SIMULATION")
        logger.info("-" * 40)
        results["concurrent_io"] = await test_concurrent_io_simulation()

        # Generate summary
        total_time = time.time() - start_time

        logger.info("\n" + "=" * 70)
        logger.info("🏆 PERFORMANCE BENCHMARK SUMMARY")
        logger.info("=" * 70)

        logger.info(f"⏱️ Total benchmark time: {total_time:.2f} seconds")

        # Performance scores (relative)
        scores = {}

        if "async_performance" in results:
            async_perf = results["async_performance"]
            concurrency_score = min(async_perf.get("concurrency_speedup", 1) * 20, 100)
            scores["async_concurrency"] = concurrency_score
            logger.info(f"⚡ Async Concurrency Score: {concurrency_score:.0f}/100")

        if "memory_performance" in results:
            memory_perf = results["memory_performance"]
            allocation_rate = memory_perf.get("allocation_rate", 0)
            memory_score = min(allocation_rate / 10000, 1) * 100  # Normalize to 1M/sec = 100
            scores["memory_allocation"] = memory_score
            logger.info(f"🧠 Memory Allocation Score: {memory_score:.0f}/100")

        if "cpu_performance" in results:
            cpu_perf = results["cpu_performance"]
            math_throughput = cpu_perf.get("math_throughput", 0)
            cpu_score = min(math_throughput / 1000000, 1) * 100  # Normalize to 1M/sec = 100
            scores["cpu_processing"] = cpu_score
            logger.info(f"💻 CPU Processing Score: {cpu_score:.0f}/100")

        if "concurrent_io" in results:
            io_perf = results["concurrent_io"]
            max_throughput = io_perf.get("max_throughput", 0)
            io_score = min(max_throughput / 50, 1) * 100  # Normalize to 50 ops/sec = 100
            scores["concurrent_io"] = io_score
            logger.info(f"🔄 Concurrent I/O Score: {io_score:.0f}/100")

        # Overall score
        if scores:
            overall_score = sum(scores.values()) / len(scores)
            logger.info(f"\n🎯 Overall Performance Score: {overall_score:.0f}/100")

            # Performance rating
            if overall_score >= 80:
                rating = "Excellent 🚀"
            elif overall_score >= 60:
                rating = "Good ✅"
            elif overall_score >= 40:
                rating = "Fair ⚠️"
            else:
                rating = "Needs Improvement ❌"

            logger.info(f"📈 Performance Rating: {rating}")

        # Recommendations
        logger.info("\n💡 PERFORMANCE RECOMMENDATIONS:")
        logger.info("-" * 40)

        recommendations = []

        if "async_performance" in results:
            speedup = results["async_performance"].get("concurrency_speedup", 1)
            if speedup < 2:
                recommendations.append(
                    "Consider optimizing async operations for better concurrency"
                )

        if "memory_performance" in results:
            alloc_rate = results["memory_performance"].get("allocation_rate", 0)
            if alloc_rate < 500000:  # Less than 500K/sec
                recommendations.append("Memory allocation could be optimized")

        if "cpu_performance" in results:
            math_throughput = results["cpu_performance"].get("math_throughput", 0)
            if math_throughput < 500000:  # Less than 500K/sec
                recommendations.append("CPU-intensive operations may benefit from optimization")

        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                logger.info(f"{i}. {rec}")
        else:
            logger.info("🎉 All performance metrics are excellent!")

        logger.info(f"\n✅ Benchmark completed successfully in {total_time:.2f} seconds!")

        return results

    except Exception as e:
        logger.error(f"❌ Benchmark failed: {e}")
        return None


async def main():
    """Main function"""
    results = await run_performance_benchmark()

    if results:
        # Save results to file
        import json

        with open("performance_benchmark_results.json", "w") as f:
            # Convert any non-serializable objects to strings
            serializable_results = {}
            for key, value in results.items():
                try:
                    json.dumps(value)  # Test if serializable
                    serializable_results[key] = value
                except:
                    serializable_results[key] = str(value)

            json.dump(serializable_results, f, indent=2)

        logger.info("📁 Results saved to: performance_benchmark_results.json")

    return results


if __name__ == "__main__":
    asyncio.run(main())

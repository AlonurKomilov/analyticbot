"""
Performance and stress testing for MTProto Phase 4.6 scaling components.
Tests reliability under load, horizontal scaling, and observability.
"""

import asyncio
import logging
import time
import statistics
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import json
import os
from pathlib import Path

# Import MTProto components
from apps.mtproto.config import MTProtoSettings
from apps.mtproto.di import initialize_application, shutdown_application, MTProtoApplication
from infra.common.faults import initialize_fault_injection

logger = logging.getLogger(__name__)


@dataclass
class TestMetrics:
    """Performance test metrics."""
    test_name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    response_times: List[float] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    @property
    def duration(self) -> float:
        """Test duration in seconds."""
        end = self.end_time or time.time()
        return end - self.start_time
    
    @property
    def requests_per_second(self) -> float:
        """Requests per second."""
        duration = self.duration
        return self.total_requests / duration if duration > 0 else 0
    
    @property
    def success_rate(self) -> float:
        """Success rate as percentage."""
        return (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0
    
    @property
    def avg_response_time(self) -> float:
        """Average response time in seconds."""
        return statistics.mean(self.response_times) if self.response_times else 0
    
    @property
    def p95_response_time(self) -> float:
        """95th percentile response time in seconds."""
        return statistics.quantiles(self.response_times, n=20)[18] if len(self.response_times) >= 20 else 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "test_name": self.test_name,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "duration_seconds": self.duration,
            "requests_per_second": self.requests_per_second,
            "success_rate_percent": self.success_rate,
            "avg_response_time_ms": self.avg_response_time * 1000,
            "p95_response_time_ms": self.p95_response_time * 1000,
            "error_count": len(self.errors),
            "unique_errors": len(set(self.errors))
        }


class MTProtoPerformanceTest:
    """Performance test suite for MTProto scaling components."""
    
    def __init__(self, settings: MTProtoSettings):
        self.settings = settings
        self.results: List[TestMetrics] = []
        
        # Test configuration
        self.slos = {
            "min_success_rate": 99.0,  # 99% success rate
            "max_p95_latency_ms": 600,  # 600ms p95 latency
            "min_rps": 1.0,  # Minimum 1 RPS
            "max_queue_drop_rate": 0.5,  # Max 0.5% queue drops
            "max_graceful_shutdown_time": 25  # 25 seconds max shutdown
        }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all performance tests."""
        logger.info("Starting MTProto performance test suite")
        
        # Test 1: Account pool performance
        await self.test_account_pool_performance()
        
        # Test 2: Rate limiting accuracy
        await self.test_rate_limiting()
        
        # Test 3: Proxy failover
        await self.test_proxy_failover()
        
        # Test 4: DC migration handling
        await self.test_dc_migration()
        
        # Test 5: Concurrent request handling
        await self.test_concurrent_requests()
        
        # Test 6: Graceful shutdown
        await self.test_graceful_shutdown()
        
        # Test 7: Fault injection resilience
        await self.test_fault_resilience()
        
        # Analyze results
        return await self.analyze_results()
    
    async def test_account_pool_performance(self) -> None:
        """Test account pool load balancing and performance."""
        if not self.settings.MTPROTO_POOL_ENABLED or not self.settings.MTPROTO_ACCOUNTS:
            logger.info("Skipping account pool test - pool not enabled")
            return
        
        metrics = TestMetrics("account_pool_performance")
        logger.info("Testing account pool performance...")
        
        async with MTProtoApplication(self.settings) as scaling_container:
            if not scaling_container.account_pool:
                logger.warning("Account pool not available")
                return
            
            # Simulate concurrent requests across accounts
            async def make_request() -> bool:
                try:
                    start_time = time.time()
                    async with scaling_container.account_pool.lease() as client:
                        # Simulate work
                        await asyncio.sleep(0.1)  # 100ms simulated work
                    end_time = time.time()
                    
                    metrics.response_times.append(end_time - start_time)
                    return True
                    
                except Exception as e:
                    metrics.errors.append(str(e))
                    return False
            
            # Run concurrent requests
            tasks = [make_request() for _ in range(50)]  # 50 concurrent requests
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Update metrics
            metrics.total_requests = len(results)
            metrics.successful_requests = sum(1 for r in results if r is True)
            metrics.failed_requests = metrics.total_requests - metrics.successful_requests
            
        metrics.end_time = time.time()
        self.results.append(metrics)
        logger.info(f"Account pool test completed: {metrics.success_rate:.1f}% success rate")
    
    async def test_rate_limiting(self) -> None:
        """Test rate limiting accuracy and backpressure."""
        metrics = TestMetrics("rate_limiting_accuracy")
        logger.info("Testing rate limiting accuracy...")
        
        async with MTProtoApplication(self.settings) as scaling_container:
            if not scaling_container.rate_limiter:
                logger.warning("Rate limiter not available")
                return
            
            # Test global rate limiting
            target_rps = self.settings.MTPROTO_GLOBAL_RPS
            test_duration = 10  # 10 seconds
            expected_requests = int(target_rps * test_duration * 1.1)  # Allow 10% overhead
            
            async def rate_limited_request() -> bool:
                try:
                    start_time = time.time()
                    await scaling_container.rate_limiter.acquire_with_delay("test_account")
                    end_time = time.time()
                    
                    metrics.response_times.append(end_time - start_time)
                    return True
                    
                except Exception as e:
                    metrics.errors.append(str(e))
                    return False
            
            # Start requests and measure actual RPS
            start_time = time.time()
            tasks = [rate_limited_request() for _ in range(expected_requests)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            actual_duration = time.time() - start_time
            
            metrics.total_requests = len(results)
            metrics.successful_requests = sum(1 for r in results if r is True)
            metrics.failed_requests = metrics.total_requests - metrics.successful_requests
            
            actual_rps = metrics.successful_requests / actual_duration
            rps_accuracy = abs(actual_rps - target_rps) / target_rps * 100
            
            logger.info(f"Rate limiting test: target={target_rps:.1f} RPS, "
                       f"actual={actual_rps:.1f} RPS, accuracy={100-rps_accuracy:.1f}%")
        
        metrics.end_time = time.time()
        self.results.append(metrics)
    
    async def test_proxy_failover(self) -> None:
        """Test proxy pool failover behavior."""
        if not self.settings.MTPROTO_PROXY_ENABLED or not self.settings.MTPROTO_PROXIES:
            logger.info("Skipping proxy test - proxy pool not enabled")
            return
        
        metrics = TestMetrics("proxy_failover")
        logger.info("Testing proxy failover...")
        
        async with MTProtoApplication(self.settings) as scaling_container:
            if not scaling_container.proxy_pool:
                logger.warning("Proxy pool not available")
                return
            
            # Simulate proxy failures and measure failover time
            initial_proxy = await scaling_container.proxy_pool.get_current_proxy()
            
            # Report failures for current proxy
            for _ in range(self.settings.MTPROTO_PROXY_FAIL_SCORE_LIMIT):
                await scaling_container.proxy_pool.report_failure(
                    initial_proxy, Exception("Simulated proxy failure")
                )
            
            # Measure failover time
            start_time = time.time()
            new_proxy = await scaling_container.proxy_pool.get_current_proxy()
            failover_time = time.time() - start_time
            
            metrics.response_times.append(failover_time)
            metrics.total_requests = 1
            
            if new_proxy != initial_proxy:
                metrics.successful_requests = 1
                logger.info(f"Proxy failover successful in {failover_time*1000:.1f}ms")
            else:
                metrics.failed_requests = 1
                metrics.errors.append("Proxy did not change after failures")
        
        metrics.end_time = time.time()
        self.results.append(metrics)
    
    async def test_dc_migration(self) -> None:
        """Test DC migration handling."""
        metrics = TestMetrics("dc_migration_handling")
        logger.info("Testing DC migration handling...")
        
        async with MTProtoApplication(self.settings) as scaling_container:
            # Simulate DC migration errors and measure retry behavior
            async def simulate_dc_request() -> bool:
                try:
                    start_time = time.time()
                    
                    # Use DC router to handle simulated migration
                    router = scaling_container.dc_router
                    
                    async def failing_request():
                        # Simulate STATS_MIGRATE_3 error on first call
                        if not hasattr(failing_request, 'called'):
                            failing_request.called = True
                            raise Exception("STATS_MIGRATE_3")
                        return "success"
                    
                    result = await router.run_with_dc_retry(
                        client=None,  # Mock client
                        request_callable=failing_request,
                        peer_id="test_peer",
                        request_type="stats"
                    )
                    
                    end_time = time.time()
                    metrics.response_times.append(end_time - start_time)
                    return result == "success"
                    
                except Exception as e:
                    metrics.errors.append(str(e))
                    return False
            
            # Test DC migration handling
            tasks = [simulate_dc_request() for _ in range(10)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            metrics.total_requests = len(results)
            metrics.successful_requests = sum(1 for r in results if r is True)
            metrics.failed_requests = metrics.total_requests - metrics.successful_requests
        
        metrics.end_time = time.time()
        self.results.append(metrics)
    
    async def test_concurrent_requests(self) -> None:
        """Test concurrent request handling under load."""
        metrics = TestMetrics("concurrent_requests")
        logger.info("Testing concurrent request handling...")
        
        async with MTProtoApplication(self.settings) as scaling_container:
            async def concurrent_request() -> bool:
                try:
                    start_time = time.time()
                    
                    # Simulate request processing with fault injection
                    await scaling_container.fault_injector.inject_fault("concurrent_test")
                    await asyncio.sleep(0.05)  # 50ms simulated work
                    
                    end_time = time.time()
                    metrics.response_times.append(end_time - start_time)
                    return True
                    
                except Exception as e:
                    metrics.errors.append(str(e))
                    return False
            
            # Run high concurrency test
            concurrency = 100
            tasks = [concurrent_request() for _ in range(concurrency)]
            
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            metrics.total_requests = len(results)
            metrics.successful_requests = sum(1 for r in results if r is True)
            metrics.failed_requests = metrics.total_requests - metrics.successful_requests
        
        metrics.end_time = time.time()
        self.results.append(metrics)
        logger.info(f"Concurrent requests test: {concurrency} requests, "
                   f"{metrics.success_rate:.1f}% success rate")
    
    async def test_graceful_shutdown(self) -> None:
        """Test graceful shutdown behavior."""
        metrics = TestMetrics("graceful_shutdown")
        logger.info("Testing graceful shutdown...")
        
        # Create app instance
        scaling_container = await initialize_application(self.settings)
        
        # Start some background work
        async def background_work():
            await asyncio.sleep(5)  # 5 seconds of work
            return True
        
        work_tasks = [asyncio.create_task(background_work()) for _ in range(3)]
        
        # Start shutdown after 1 second
        await asyncio.sleep(1)
        start_time = time.time()
        
        # Shutdown and measure time
        await shutdown_application(scaling_container)
        shutdown_time = time.time() - start_time
        
        metrics.response_times.append(shutdown_time)
        metrics.total_requests = 1
        
        if shutdown_time <= self.slos["max_graceful_shutdown_time"]:
            metrics.successful_requests = 1
            logger.info(f"Graceful shutdown completed in {shutdown_time:.1f}s")
        else:
            metrics.failed_requests = 1
            metrics.errors.append(f"Shutdown took {shutdown_time:.1f}s, exceeds {self.slos['max_graceful_shutdown_time']}s SLO")
        
        # Clean up remaining tasks
        for task in work_tasks:
            if not task.done():
                task.cancel()
        
        metrics.end_time = time.time()
        self.results.append(metrics)
    
    async def test_fault_resilience(self) -> None:
        """Test resilience under fault injection."""
        metrics = TestMetrics("fault_resilience")
        logger.info("Testing fault injection resilience...")
        
        # Enable fault injection for testing
        fault_injector = initialize_fault_injection(enabled=True)
        
        async with MTProtoApplication(self.settings) as scaling_container:
            async def resilient_request() -> bool:
                try:
                    start_time = time.time()
                    
                    # Request with fault injection
                    await fault_injector.inject_fault("resilience_test")
                    await asyncio.sleep(0.1)  # Simulated work
                    
                    end_time = time.time()
                    metrics.response_times.append(end_time - start_time)
                    return True
                    
                except Exception as e:
                    metrics.errors.append(str(e))
                    return False
            
            # Run requests with fault injection
            tasks = [resilient_request() for _ in range(100)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            metrics.total_requests = len(results)
            metrics.successful_requests = sum(1 for r in results if r is True)
            metrics.failed_requests = metrics.total_requests - metrics.successful_requests
        
        metrics.end_time = time.time()
        self.results.append(metrics)
        logger.info(f"Fault resilience test: {metrics.success_rate:.1f}% success rate under fault injection")
    
    async def analyze_results(self) -> Dict[str, Any]:
        """Analyze test results against SLOs."""
        logger.info("Analyzing performance test results...")
        
        analysis = {
            "timestamp": time.time(),
            "slos": self.slos,
            "test_results": [metrics.to_dict() for metrics in self.results],
            "slo_compliance": {},
            "overall_status": "PASS"
        }
        
        # Check SLO compliance
        for metrics in self.results:
            test_name = metrics.test_name
            compliance = {}
            
            # Success rate SLO
            if metrics.success_rate < self.slos["min_success_rate"]:
                compliance["success_rate"] = f"FAIL: {metrics.success_rate:.1f}% < {self.slos['min_success_rate']}%"
                analysis["overall_status"] = "FAIL"
            else:
                compliance["success_rate"] = f"PASS: {metrics.success_rate:.1f}%"
            
            # P95 latency SLO
            if metrics.p95_response_time * 1000 > self.slos["max_p95_latency_ms"]:
                compliance["p95_latency"] = f"FAIL: {metrics.p95_response_time*1000:.1f}ms > {self.slos['max_p95_latency_ms']}ms"
                analysis["overall_status"] = "FAIL"
            else:
                compliance["p95_latency"] = f"PASS: {metrics.p95_response_time*1000:.1f}ms"
            
            # RPS SLO
            if metrics.requests_per_second < self.slos["min_rps"]:
                compliance["rps"] = f"FAIL: {metrics.requests_per_second:.1f} < {self.slos['min_rps']}"
                analysis["overall_status"] = "FAIL"
            else:
                compliance["rps"] = f"PASS: {metrics.requests_per_second:.1f}"
            
            analysis["slo_compliance"][test_name] = compliance
        
        # Generate summary
        total_requests = sum(m.total_requests for m in self.results)
        total_successful = sum(m.successful_requests for m in self.results)
        overall_success_rate = (total_successful / total_requests * 100) if total_requests > 0 else 0
        
        analysis["summary"] = {
            "total_tests": len(self.results),
            "total_requests": total_requests,
            "overall_success_rate": overall_success_rate,
            "tests_passed": sum(1 for test_name, compliance in analysis["slo_compliance"].items() 
                              if all("PASS" in v for v in compliance.values())),
            "tests_failed": sum(1 for test_name, compliance in analysis["slo_compliance"].items() 
                              if any("FAIL" in v for v in compliance.values()))
        }
        
        # Save results to file
        await self.save_results(analysis)
        
        logger.info(f"Performance test analysis complete: {analysis['overall_status']}")
        logger.info(f"Overall success rate: {overall_success_rate:.1f}%")
        
        return analysis
    
    async def save_results(self, analysis: Dict[str, Any]) -> None:
        """Save test results to file."""
        results_dir = Path("test_results")
        results_dir.mkdir(exist_ok=True)
        
        timestamp = int(time.time())
        filename = results_dir / f"mtproto_perf_test_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        logger.info(f"Test results saved to {filename}")


async def main():
    """Run performance tests."""
    logging.basicConfig(level=logging.INFO)
    
    # Load settings
    settings = MTProtoSettings()
    
    # Override settings for testing
    settings.MTPROTO_ENABLED = True
    settings.MTPROTO_POOL_ENABLED = True
    settings.MTPROTO_ACCOUNTS = ["test_session1", "test_session2"]
    settings.MTPROTO_RPS_PER_ACCOUNT = 1.0
    settings.MTPROTO_GLOBAL_RPS = 2.0
    settings.OBS_PROMETHEUS_ENABLED = False  # Disable for testing
    
    # Enable fault injection for resilience testing
    os.environ["FAULT_INJECTION_ENABLED"] = "true"
    os.environ["ENVIRONMENT"] = "test"
    
    # Run tests
    test_suite = MTProtoPerformanceTest(settings)
    results = await test_suite.run_all_tests()
    
    print("\n" + "="*50)
    print("MTProto Performance Test Results")
    print("="*50)
    print(f"Overall Status: {results['overall_status']}")
    print(f"Tests Passed: {results['summary']['tests_passed']}/{results['summary']['total_tests']}")
    print(f"Overall Success Rate: {results['summary']['overall_success_rate']:.1f}%")
    print("="*50)
    
    return results


if __name__ == "__main__":
    asyncio.run(main())

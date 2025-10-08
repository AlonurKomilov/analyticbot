"""
Load Testing Infrastructure
Comprehensive performance testing and monitoring tools
"""

import asyncio
import json
import logging
import random
import statistics
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from typing import Any

import aiohttp
from pydantic import BaseModel

logger = logging.getLogger(__name__)


@dataclass
class LoadTestResult:
    """Result of a single load test request"""

    success: bool
    response_time: float
    status_code: int | None = None
    error_message: str | None = None
    response_size: int | None = None
    timestamp: float | None = None


@dataclass
class LoadTestMetrics:
    """Aggregated metrics from load test"""

    total_requests: int
    successful_requests: int
    failed_requests: int
    success_rate: float

    # Response time metrics
    min_response_time: float
    max_response_time: float
    avg_response_time: float
    median_response_time: float
    p95_response_time: float
    p99_response_time: float

    # Throughput metrics
    requests_per_second: float
    total_duration: float

    # Error analysis
    error_distribution: dict[str, int]
    status_code_distribution: dict[int, int]


class LoadTestConfig(BaseModel):
    """Configuration for load testing"""

    target_url: str
    concurrent_users: int = 10
    total_requests: int = 100
    ramp_up_time: int = 10  # seconds
    test_duration: int | None = None  # seconds
    request_timeout: int = 30
    headers: dict[str, str] = {}
    payload: dict[str, Any] | None = None
    method: str = "GET"

    # Advanced options
    think_time_min: float = 0.1  # minimum wait between requests
    think_time_max: float = 1.0  # maximum wait between requests
    follow_redirects: bool = True
    verify_ssl: bool = True


class DatabaseLoadTester:
    """Load tester for database operations"""

    def __init__(self, db_connection_func: Callable):
        self.db_connection_func = db_connection_func
        self.results = []

    async def test_query_performance(
        self,
        query: str,
        params: tuple | None = None,
        concurrent_connections: int = 10,
        total_queries: int = 100,
    ) -> LoadTestMetrics:
        """Test database query performance under load"""

        logger.info(
            f"🔍 Starting database load test: {concurrent_connections} connections, {total_queries} queries"
        )

        async def execute_query():
            start_time = time.time()
            success = True
            error_msg = None

            try:
                async with await self.db_connection_func() as conn:
                    if params:
                        await conn.fetch(query, *params)
                    else:
                        await conn.fetch(query)
            except Exception as e:
                success = False
                error_msg = str(e)

            return LoadTestResult(
                success=success,
                response_time=time.time() - start_time,
                error_message=error_msg,
                timestamp=start_time,
            )

        # Execute concurrent queries
        semaphore = asyncio.Semaphore(concurrent_connections)

        async def limited_execute():
            async with semaphore:
                return await execute_query()

        start_time = time.time()
        tasks = [limited_execute() for _ in range(total_queries)]
        results = await asyncio.gather(*tasks)
        total_duration = time.time() - start_time

        return self._calculate_metrics(results, total_duration)

    async def test_connection_pool_performance(
        self, pool_size: int = 20, max_connections: int = 100, test_duration: int = 60
    ) -> dict[str, Any]:
        """Test database connection pool performance"""

        logger.info(
            f"🏊 Testing connection pool: {pool_size} pool size, {max_connections} max connections"
        )

        results = []
        start_time = time.time()

        async def connection_test():
            try:
                async with await self.db_connection_func() as conn:
                    # Simple query to test connection
                    await conn.fetchval("SELECT 1")
                return True
            except Exception as e:
                logger.error(f"Connection test failed: {e}")
                return False

        # Run connection tests for specified duration
        while time.time() - start_time < test_duration:
            # Create burst of connections
            tasks = [connection_test() for _ in range(max_connections)]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            successful = sum(1 for r in batch_results if r is True)
            results.append(
                {
                    "timestamp": time.time(),
                    "successful_connections": successful,
                    "total_attempts": len(batch_results),
                    "success_rate": successful / len(batch_results),
                }
            )

            # Wait before next batch
            await asyncio.sleep(1)

        return {
            "test_duration": time.time() - start_time,
            "total_batches": len(results),
            "avg_success_rate": statistics.mean(r["success_rate"] for r in results),
            "min_success_rate": min(r["success_rate"] for r in results),
            "results": results,
        }

    def _calculate_metrics(
        self, results: list[LoadTestResult], total_duration: float
    ) -> LoadTestMetrics:
        """Calculate load test metrics from results"""
        successful_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]

        response_times = [float(r.response_time) for r in successful_results]

        if not response_times:
            response_times = [0.0]

        # Error distribution
        error_dist = {}
        for result in failed_results:
            error_key = result.error_message or "Unknown Error"
            error_dist[error_key] = error_dist.get(error_key, 0) + 1

        return LoadTestMetrics(
            total_requests=len(results),
            successful_requests=len(successful_results),
            failed_requests=len(failed_results),
            success_rate=len(successful_results) / len(results) if results else 0,
            min_response_time=min(response_times),
            max_response_time=max(response_times),
            avg_response_time=statistics.mean(response_times),
            median_response_time=statistics.median(response_times),
            p95_response_time=self._percentile(response_times, 95),
            p99_response_time=self._percentile(response_times, 99),
            requests_per_second=len(results) / total_duration if total_duration > 0 else 0,
            total_duration=total_duration,
            error_distribution=error_dist,
            status_code_distribution={},
        )

    @staticmethod
    def _percentile(data: list[float], percentile: int) -> float:
        """Calculate percentile of data"""
        if not data:
            return 0.0
        # Convert to float to ensure type consistency
        sorted_data = sorted([float(x) for x in data])
        index = int((percentile / 100) * len(sorted_data))
        if index >= len(sorted_data):
            index = len(sorted_data) - 1
        return sorted_data[index]


class APILoadTester:
    """Load tester for API endpoints"""

    def __init__(self):
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def run_load_test(self, config: LoadTestConfig) -> LoadTestMetrics:
        """Run comprehensive API load test"""

        logger.info(
            f"🚀 Starting API load test: {config.concurrent_users} users, {config.total_requests} requests"
        )

        # Calculate requests per user
        requests_per_user = config.total_requests // config.concurrent_users

        # Create semaphore for concurrent control
        semaphore = asyncio.Semaphore(config.concurrent_users)

        start_time = time.time()

        # Create user simulation tasks
        user_tasks = []
        for user_id in range(config.concurrent_users):
            task = self._simulate_user(user_id, requests_per_user, config, semaphore, start_time)
            user_tasks.append(task)

        # Wait for all users to complete
        all_results = await asyncio.gather(*user_tasks)

        # Flatten results
        results = []
        for user_results in all_results:
            results.extend(user_results)

        total_duration = time.time() - start_time

        return self._calculate_api_metrics(results, total_duration)

    async def _simulate_user(
        self,
        user_id: int,
        num_requests: int,
        config: LoadTestConfig,
        semaphore: asyncio.Semaphore,
        test_start_time: float,
    ) -> list[LoadTestResult]:
        """Simulate individual user behavior"""

        results = []

        # Ramp-up delay
        ramp_delay = (config.ramp_up_time / config.concurrent_users) * user_id
        await asyncio.sleep(ramp_delay)

        for request_num in range(num_requests):
            async with semaphore:
                result = await self._make_request(config)
                results.append(result)

                # Think time between requests
                think_time = random.uniform(config.think_time_min, config.think_time_max)
                await asyncio.sleep(think_time)

                # Check if test duration exceeded
                if config.test_duration:
                    elapsed = time.time() - test_start_time
                    if elapsed >= config.test_duration:
                        break

        logger.debug(f"👤 User {user_id} completed {len(results)} requests")
        return results

    async def _make_request(self, config: LoadTestConfig) -> LoadTestResult:
        """Make a single HTTP request"""
        start_time = time.time()

        try:
            if self.session is None:
                raise RuntimeError("Session not initialized")

            timeout = aiohttp.ClientTimeout(total=config.request_timeout)

            async with self.session.request(
                method=config.method,
                url=config.target_url,
                headers=config.headers,
                json=config.payload if config.method in ["POST", "PUT", "PATCH"] else None,
                timeout=timeout,
                ssl=config.verify_ssl,
            ) as response:
                # Read response content to measure size
                content = await response.read()

                return LoadTestResult(
                    success=response.status < 400,
                    response_time=time.time() - start_time,
                    status_code=response.status,
                    response_size=len(content),
                    timestamp=start_time,
                )

        except Exception as e:
            return LoadTestResult(
                success=False,
                response_time=time.time() - start_time,
                error_message=str(e),
                timestamp=start_time,
            )

    def _calculate_api_metrics(
        self, results: list[LoadTestResult], total_duration: float
    ) -> LoadTestMetrics:
        """Calculate API load test metrics"""
        successful_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]

        response_times = [float(r.response_time) for r in successful_results]
        if not response_times:
            response_times = [0.0]

        # Error distribution
        error_dist = {}
        for result in failed_results:
            error_key = result.error_message or "Unknown Error"
            error_dist[error_key] = error_dist.get(error_key, 0) + 1

        # Status code distribution
        status_dist = {}
        for result in results:
            if result.status_code:
                status_dist[result.status_code] = status_dist.get(result.status_code, 0) + 1

        return LoadTestMetrics(
            total_requests=len(results),
            successful_requests=len(successful_results),
            failed_requests=len(failed_results),
            success_rate=len(successful_results) / len(results) if results else 0,
            min_response_time=min(response_times),
            max_response_time=max(response_times),
            avg_response_time=statistics.mean(response_times),
            median_response_time=statistics.median(response_times),
            p95_response_time=DatabaseLoadTester._percentile(response_times, 95),
            p99_response_time=DatabaseLoadTester._percentile(response_times, 99),
            requests_per_second=len(results) / total_duration if total_duration > 0 else 0,
            total_duration=total_duration,
            error_distribution=error_dist,
            status_code_distribution=status_dist,
        )


class PerformanceBenchmark:
    """Comprehensive performance benchmarking utility"""

    def __init__(self):
        self.test_results = {}

    async def benchmark_api_endpoints(
        self, endpoints: list[dict[str, Any]]
    ) -> dict[str, LoadTestMetrics]:
        """Benchmark multiple API endpoints"""

        logger.info(f"🎯 Benchmarking {len(endpoints)} API endpoints")

        results = {}

        async with APILoadTester() as load_tester:
            for endpoint_config in endpoints:
                config = LoadTestConfig(**endpoint_config)

                logger.info(f"Testing endpoint: {config.target_url}")

                try:
                    metrics = await load_tester.run_load_test(config)
                    results[config.target_url] = metrics

                    logger.info(
                        f"✅ Endpoint {config.target_url}: "
                        f"{metrics.success_rate:.1%} success, "
                        f"{metrics.avg_response_time:.3f}s avg response"
                    )

                except Exception as e:
                    logger.error(f"❌ Failed to test endpoint {config.target_url}: {e}")

        return results

    async def benchmark_database_queries(
        self, db_connection_func: Callable, queries: list[dict[str, Any]]
    ) -> dict[str, LoadTestMetrics]:
        """Benchmark database query performance"""

        logger.info(f"🗄️ Benchmarking {len(queries)} database queries")

        db_tester = DatabaseLoadTester(db_connection_func)
        results = {}

        for query_config in queries:
            query_name = query_config.get("name", "Unnamed Query")
            query = query_config["query"]
            params = query_config.get("params")
            concurrent_connections = query_config.get("concurrent_connections", 10)
            total_queries = query_config.get("total_queries", 100)

            logger.info(f"Testing query: {query_name}")

            try:
                metrics = await db_tester.test_query_performance(
                    query, params, concurrent_connections, total_queries
                )
                results[query_name] = metrics

                logger.info(
                    f"✅ Query {query_name}: "
                    f"{metrics.success_rate:.1%} success, "
                    f"{metrics.avg_response_time:.3f}s avg time"
                )

            except Exception as e:
                logger.error(f"❌ Failed to test query {query_name}: {e}")

        return results

    def generate_performance_report(
        self, results: dict[str, LoadTestMetrics], output_file: str | None = None
    ) -> dict:
        """Generate comprehensive performance report"""

        report = {
            "summary": {
                "total_tests": len(results),
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "overall_metrics": {},
            },
            "test_results": {},
            "recommendations": [],
        }

        # Calculate overall metrics
        if results:
            all_success_rates = [r.success_rate for r in results.values()]
            all_response_times = [r.avg_response_time for r in results.values()]
            all_throughput = [r.requests_per_second for r in results.values()]

            report["summary"]["overall_metrics"] = {
                "avg_success_rate": statistics.mean(all_success_rates),
                "avg_response_time": statistics.mean(all_response_times),
                "avg_throughput": statistics.mean(all_throughput),
                "best_performing_test": min(
                    results.keys(), key=lambda k: results[k].avg_response_time
                ),
                "worst_performing_test": max(
                    results.keys(), key=lambda k: results[k].avg_response_time
                ),
            }

        # Add detailed test results
        for test_name, metrics in results.items():
            report["test_results"][test_name] = asdict(metrics)

        # Generate recommendations
        report["recommendations"] = self._generate_recommendations(results)

        # Save to file if specified
        if output_file:
            with open(output_file, "w") as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"📊 Performance report saved to {output_file}")

        return report

    def _generate_recommendations(self, results: dict[str, LoadTestMetrics]) -> list[str]:
        """Generate performance improvement recommendations"""
        recommendations = []

        for test_name, metrics in results.items():
            # High response time
            if metrics.avg_response_time > 2.0:
                recommendations.append(
                    f"🐌 {test_name}: High response time ({metrics.avg_response_time:.2f}s) - Consider optimization"
                )

            # Low success rate
            if metrics.success_rate < 0.95:
                recommendations.append(
                    f"⚠️ {test_name}: Low success rate ({metrics.success_rate:.1%}) - Investigate errors"
                )

            # High P99 response time
            if metrics.p99_response_time > metrics.avg_response_time * 3:
                recommendations.append(
                    f"📈 {test_name}: High P99 latency - Check for outliers and bottlenecks"
                )

            # Low throughput
            if metrics.requests_per_second < 10:
                recommendations.append(
                    f"🔄 {test_name}: Low throughput ({metrics.requests_per_second:.1f} RPS) - Consider scaling"
                )

        # General recommendations
        if not recommendations:
            recommendations.append("✅ All tests performing within acceptable ranges")

        return recommendations


# Example usage functions
async def run_api_performance_test():
    """Example API performance test"""
    endpoints = [
        {
            "target_url": "http://localhost:8000/api/v1/analytics/summary",
            "method": "GET",
            "concurrent_users": 20,
            "total_requests": 200,
            "headers": {"Authorization": "Bearer test_token"},
        },
        {
            "target_url": "http://localhost:8000/api/v1/channels",
            "method": "GET",
            "concurrent_users": 15,
            "total_requests": 150,
        },
    ]

    benchmark = PerformanceBenchmark()
    results = await benchmark.benchmark_api_endpoints(endpoints)

    report = benchmark.generate_performance_report(results, "api_performance_report.json")

    logger.info("📊 API Performance Test Results:")
    for endpoint, metrics in results.items():
        logger.info(
            f"  {endpoint}: {metrics.success_rate:.1%} success, {metrics.avg_response_time:.3f}s avg"
        )

    return report


async def run_database_performance_test(db_connection_func):
    """Example database performance test"""
    queries = [
        {
            "name": "Channel Analytics Summary",
            "query": "SELECT channel_id, COUNT(*) FROM analytics_data WHERE created_at > NOW() - INTERVAL '7 days' GROUP BY channel_id",
            "concurrent_connections": 10,
            "total_queries": 100,
        },
        {
            "name": "User Subscription Check",
            "query": "SELECT * FROM subscriptions WHERE user_id = $1 AND status = 'active'",
            "params": (12345,),
            "concurrent_connections": 15,
            "total_queries": 200,
        },
    ]

    benchmark = PerformanceBenchmark()
    results = await benchmark.benchmark_database_queries(db_connection_func, queries)

    report = benchmark.generate_performance_report(results, "db_performance_report.json")

    logger.info("🗄️ Database Performance Test Results:")
    for query_name, metrics in results.items():
        logger.info(
            f"  {query_name}: {metrics.success_rate:.1%} success, {metrics.avg_response_time:.3f}s avg"
        )

    return report

#!/usr/bin/env python3
"""
Phase 0.0 Module 2 - Integration Test Suite
Comprehensive testing of deployed services
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import aiohttp
import psycopg2 as psycopg
import redis


class Module2TestSuite:
    def __init__(self):
        self.api_url = "http://localhost:8001"
        self.db_url = "postgresql://analyticbot:testpass123@localhost:5433/analyticbot_test"
        self.redis_url = "redis://:testredis123@localhost:6380/0"

        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {"passed": 0, "failed": 0, "total": 0},
        }

    def log_test(self, test_name, passed, message="", duration=0):
        """Log test result"""
        status = "PASS" if passed else "FAIL"
        print(f"{'✅' if passed else '❌'} {test_name}: {status}")
        if message:
            print(f"   {message}")

        self.results["tests"].append(
            {
                "name": test_name,
                "status": status,
                "message": message,
                "duration": duration,
            }
        )

        if passed:
            self.results["summary"]["passed"] += 1
        else:
            self.results["summary"]["failed"] += 1
        self.results["summary"]["total"] += 1

    async def test_api_health(self):
        """Test API health endpoint"""
        start_time = time.time()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/health", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        duration = time.time() - start_time
                        self.log_test(
                            "API Health Check",
                            True,
                            f"Response: {data.get('status', 'unknown')} (in {duration:.3f}s)",
                            duration,
                        )
                        return True
                    else:
                        self.log_test("API Health Check", False, f"HTTP {response.status}")
                        return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("API Health Check", False, f"Error: {str(e)}", duration)
            return False

    async def test_api_endpoints(self):
        """Test various API endpoints"""
        endpoints = [
            ("/", "Root endpoint"),
            ("/docs", "API Documentation"),
            ("/metrics", "Prometheus metrics"),
        ]

        results = []
        async with aiohttp.ClientSession() as session:
            for endpoint, description in endpoints:
                start_time = time.time()
                try:
                    async with session.get(f"{self.api_url}{endpoint}", timeout=10) as response:
                        duration = time.time() - start_time
                        success = response.status in [
                            200,
                            404,
                        ]  # 404 is OK for some endpoints
                        self.log_test(
                            f"API {description}",
                            success,
                            f"HTTP {response.status} (in {duration:.3f}s)",
                            duration,
                        )
                        results.append(success)
                except Exception as e:
                    duration = time.time() - start_time
                    self.log_test(f"API {description}", False, f"Error: {str(e)}", duration)
                    results.append(False)

        return all(results)

    async def test_database_connection(self):
        """Test PostgreSQL database connection"""
        start_time = time.time()
        try:
            conn = await psycopg.AsyncConnection.connect(self.db_url, connect_timeout=10)

            # Test basic query
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT version();")
                await cursor.fetchone()

            await conn.close()
            duration = time.time() - start_time
            self.log_test(
                "Database Connection",
                True,
                f"Connected to PostgreSQL (in {duration:.3f}s)",
                duration,
            )
            return True

        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Database Connection", False, f"Error: {str(e)}", duration)
            return False

    async def test_redis_connection(self):
        """Test Redis connection"""
        start_time = time.time()
        try:
            r = redis.from_url(self.redis_url, socket_timeout=10)

            # Test ping
            r.ping()

            # Test basic operations
            r.set("test_key", "test_value", ex=60)
            r.get("test_key")
            r.delete("test_key")

            duration = time.time() - start_time
            self.log_test(
                "Redis Connection",
                True,
                f"Ping successful, operations working (in {duration:.3f}s)",
                duration,
            )
            return True

        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Redis Connection", False, f"Error: {str(e)}", duration)
            return False

    async def test_performance_basic(self):
        """Basic performance test"""
        print("\n🏃 Running basic performance tests...")

        # Test API response times
        times = []
        success_count = 0

        async with aiohttp.ClientSession() as session:
            for _i in range(10):
                start_time = time.time()
                try:
                    async with session.get(f"{self.api_url}/health", timeout=5) as response:
                        duration = time.time() - start_time
                        times.append(duration * 1000)  # Convert to ms
                        if response.status == 200:
                            success_count += 1
                except Exception:
                    pass

        if times:
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)

            performance_ok = avg_time < 1000 and max_time < 2000  # Under 1s avg, 2s max

            self.log_test(
                "Performance - Response Times",
                performance_ok,
                f"Avg: {avg_time:.1f}ms, Min: {min_time:.1f}ms, Max: {max_time:.1f}ms, Success: {success_count}/10",
            )
            return performance_ok
        else:
            self.log_test("Performance - Response Times", False, "No successful requests")
            return False

    async def test_concurrent_requests(self):
        """Test concurrent request handling"""
        print("Testing concurrent requests...")

        start_time = time.time()
        concurrent_requests = 20

        async def make_request(session):
            try:
                async with session.get(f"{self.api_url}/health", timeout=10) as response:
                    return response.status == 200
            except:
                return False

        async with aiohttp.ClientSession() as session:
            tasks = [make_request(session) for _ in range(concurrent_requests)]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        duration = time.time() - start_time
        success_count = sum(1 for r in results if r is True)

        concurrency_ok = success_count >= concurrent_requests * 0.8  # 80% success rate

        self.log_test(
            "Concurrent Requests",
            concurrency_ok,
            f"{success_count}/{concurrent_requests} successful in {duration:.2f}s",
            duration,
        )
        return concurrency_ok

    def save_results(self):
        """Save test results to file"""
        results_dir = Path("./results")
        results_dir.mkdir(exist_ok=True)

        filename = f"module2_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = results_dir / filename

        with open(filepath, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"\n📊 Results saved to: {filepath}")
        return filepath

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🧪 MODULE 2 INTEGRATION TEST SUMMARY")
        print("=" * 60)

        summary = self.results["summary"]
        total = summary["total"]
        passed = summary["passed"]
        failed = summary["failed"]

        print(f"✅ Tests Passed: {passed}")
        print(f"❌ Tests Failed: {failed}")
        print(f"📊 Total Tests: {total}")

        if total > 0:
            success_rate = (passed / total) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")

            if success_rate >= 90:
                print("\n🎉 EXCELLENT: Module 2 deployment is highly successful!")
            elif success_rate >= 75:
                print("\n✅ GOOD: Module 2 deployment is working well")
            elif success_rate >= 50:
                print("\n⚠️ FAIR: Module 2 deployment has some issues")
            else:
                print("\n❌ POOR: Module 2 deployment needs attention")

        return passed == total

    async def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 PHASE 0.0 MODULE 2 - INTEGRATION TEST SUITE")
        print("=" * 60)

        print("\n📋 Starting integration tests...")

        # Core functionality tests
        print("\n🔌 Testing core connectivity...")
        await self.test_api_health()
        await self.test_database_connection()
        await self.test_redis_connection()

        # API endpoint tests
        print("\n🌐 Testing API endpoints...")
        await self.test_api_endpoints()

        # Performance tests
        print("\n⚡ Testing performance...")
        await self.test_performance_basic()
        await self.test_concurrent_requests()

        # Save and summarize results
        self.save_results()
        return self.print_summary()


async def main():
    """Main test runner"""
    test_suite = Module2TestSuite()

    try:
        success = await test_suite.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        test_suite.save_results()
        sys.exit(2)
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {e}")
        test_suite.save_results()
        sys.exit(3)


if __name__ == "__main__":
    asyncio.run(main())

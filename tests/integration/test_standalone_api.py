"""
🧪 Standalone AI/ML API Test Script

Tests all endpoints of the standalone AI/ML API
"""

import asyncio
import json
import logging
import time

import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:8002"


class APITester:
    """Test client for standalone AI/ML API"""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def test_endpoint(self, method: str, endpoint: str, data=None, expected_status=200):
        """Test a single API endpoint"""
        url = f"{self.base_url}{endpoint}"

        try:
            start_time = time.time()

            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    response_data = await response.json()
                    status = response.status
            else:  # POST
                async with self.session.post(url, json=data) as response:
                    response_data = await response.json()
                    status = response.status

            response_time = (time.time() - start_time) * 1000  # ms

            success = status == expected_status

            logger.info(f"{'✅' if success else '❌'} {method} {endpoint}")
            logger.info(f"   Status: {status} (expected {expected_status})")
            logger.info(f"   Response time: {response_time:.1f}ms")

            if not success:
                logger.error(f"   Response: {response_data}")

            return success, response_data, response_time

        except Exception as e:
            logger.error(f"❌ {method} {endpoint} - Error: {e}")
            return False, {"error": str(e)}, 0


async def run_api_tests():
    """Run comprehensive API tests"""

    print("🧪 Starting Standalone AI/ML API Tests")
    print("=" * 50)

    test_results = {
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "test_details": [],
    }

    async with APITester() as tester:
        # Test 1: Root endpoint
        print("\n📍 Testing Root Endpoint")
        success, response, time_ms = await tester.test_endpoint("GET", "/")
        test_results["total_tests"] += 1
        if success:
            test_results["passed_tests"] += 1
            print(f"   ✅ Service: {response.get('service', 'N/A')}")
            print(f"   ✅ Version: {response.get('version', 'N/A')}")
        else:
            test_results["failed_tests"] += 1

        test_results["test_details"].append(
            {"test": "Root endpoint", "success": success, "response_time_ms": time_ms}
        )

        # Test 2: Health check
        print("\n🏥 Testing Health Check")
        success, response, time_ms = await tester.test_endpoint("GET", "/health")
        test_results["total_tests"] += 1
        if success:
            test_results["passed_tests"] += 1
            print(f"   ✅ Status: {response.get('status', 'N/A')}")
            services = response.get("services", {})
            for service_name, service_status in services.items():
                print(f"   ✅ {service_name}: {service_status.get('status', 'N/A')}")
        else:
            test_results["failed_tests"] += 1

        test_results["test_details"].append(
            {"test": "Health check", "success": success, "response_time_ms": time_ms}
        )

        # Test 3: Content Analysis
        print("\n🎯 Testing Content Analysis")
        content_data = {
            "text": "🚀 Exciting news! Our new AI platform is revolutionizing content creation. Join thousands of creators who are already boosting their engagement by 50%+ with our smart analytics. #AI #content #growth #innovation #success",
            "target_audience": "tech",
        }

        success, response, time_ms = await tester.test_endpoint(
            "POST", "/analyze/content", content_data
        )
        test_results["total_tests"] += 1
        if success:
            test_results["passed_tests"] += 1
            print(f"   ✅ Overall Score: {response.get('overall_score', 'N/A'):.3f}")
            print(
                f"   ✅ Sentiment: {response.get('sentiment_label', 'N/A')} ({response.get('sentiment_score', 0):.3f})"
            )
            print(f"   ✅ Word Count: {response.get('word_count', 'N/A')}")
            print(f"   ✅ Hashtag Count: {response.get('hashtag_count', 'N/A')}")
            tips = response.get("optimization_tips", [])
            if tips:
                print(f"   💡 Tips: {tips[0]}")
        else:
            test_results["failed_tests"] += 1

        test_results["test_details"].append(
            {
                "test": "Content analysis",
                "success": success,
                "response_time_ms": time_ms,
            }
        )

        # Test 4: Real-time Scoring
        print("\n⚡ Testing Real-time Scoring")
        realtime_data = {"text": "Great product! Love the new features 😍 #amazing #product #love"}

        success, response, time_ms = await tester.test_endpoint(
            "POST", "/score/realtime", realtime_data
        )
        test_results["total_tests"] += 1
        if success:
            test_results["passed_tests"] += 1
            print(f"   ✅ Overall Score: {response.get('overall_score', 'N/A'):.3f}")
            print(f"   ✅ Length Score: {response.get('length_score', 'N/A'):.3f}")
            print(f"   ✅ Hashtag Score: {response.get('hashtag_score', 'N/A'):.3f}")
            print(f"   ✅ Sentiment Score: {response.get('sentiment_score', 'N/A'):.3f}")
        else:
            test_results["failed_tests"] += 1

        test_results["test_details"].append(
            {
                "test": "Real-time scoring",
                "success": success,
                "response_time_ms": time_ms,
            }
        )

        # Test 5: Demo Analysis
        print("\n🎬 Testing Demo Analysis")
        success, response, time_ms = await tester.test_endpoint("GET", "/demo/analyze")
        test_results["total_tests"] += 1
        if success:
            test_results["passed_tests"] += 1
            print(f"   ✅ Demo: {response.get('demo', False)}")
            analysis = response.get("analysis", {})
            print(f"   ✅ Demo Score: {analysis.get('overall_score', 'N/A')}")
        else:
            test_results["failed_tests"] += 1

        test_results["test_details"].append(
            {"test": "Demo analysis", "success": success, "response_time_ms": time_ms}
        )

        # Test 6: API Stats
        print("\n📊 Testing API Stats")
        success, response, time_ms = await tester.test_endpoint("GET", "/stats")
        test_results["total_tests"] += 1
        if success:
            test_results["passed_tests"] += 1
            print(f"   ✅ API Version: {response.get('api_version', 'N/A')}")
            capabilities = response.get("capabilities", {})
            print(f"   ✅ Content Analysis: {capabilities.get('content_analysis', False)}")
            print(f"   ✅ Real-time Scoring: {capabilities.get('real_time_scoring', False)}")
        else:
            test_results["failed_tests"] += 1

        test_results["test_details"].append(
            {"test": "API stats", "success": success, "response_time_ms": time_ms}
        )

    # Test Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)

    success_rate = (test_results["passed_tests"] / test_results["total_tests"]) * 100

    print(f"Total Tests: {test_results['total_tests']}")
    print(f"✅ Passed: {test_results['passed_tests']}")
    print(f"❌ Failed: {test_results['failed_tests']}")
    print(f"🎯 Success Rate: {success_rate:.1f}%")

    # Detailed results
    print("\n📊 DETAILED RESULTS:")
    avg_response_time = 0
    for detail in test_results["test_details"]:
        status_icon = "✅" if detail["success"] else "❌"
        print(f"{status_icon} {detail['test']}: {detail['response_time_ms']:.1f}ms")
        avg_response_time += detail["response_time_ms"]

    avg_response_time /= len(test_results["test_details"])
    print(f"\n⚡ Average Response Time: {avg_response_time:.1f}ms")

    # Verdict
    if success_rate >= 100:
        print("\n🎉 ALL TESTS PASSED! API is fully operational.")
    elif success_rate >= 80:
        print(f"\n✅ MOSTLY WORKING! {success_rate:.1f}% success rate.")
    else:
        print(f"\n⚠️  NEEDS ATTENTION! Only {success_rate:.1f}% success rate.")

    return test_results


if __name__ == "__main__":
    print("🤖 Standalone AI/ML API Test Suite")
    print("Please ensure the API server is running on http://localhost:8002")
    print("Start server with: python standalone_ai_api.py")
    print()

    # Run tests
    results = asyncio.run(run_api_tests())

    # Save results to file
    with open("api_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    print("\n💾 Test results saved to: api_test_results.json")

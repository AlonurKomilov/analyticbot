"""
🧪 Pure AI/ML API Test Script - Updated for port 8003

Tests all endpoints of the pure AI/ML API
"""

import asyncio
import json
import logging
import time
from datetime import datetime

import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:8003"


class APITester:
    """Test client for pure AI/ML API"""

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


async def run_comprehensive_tests():
    """Run comprehensive API tests with detailed analysis"""

    print("🧪 Starting Pure AI/ML API Comprehensive Tests")
    print("=" * 60)

    test_results = {
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "test_details": [],
        "performance_metrics": {},
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
            print(f"   ✅ Status: {response.get('status', 'N/A')}")
            capabilities = response.get("capabilities", [])
            print(f"   ✅ Capabilities: {len(capabilities)} features")
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
                if "test_score" in service_status:
                    print(f"   🎯 Test Score: {service_status['test_score']:.3f}")
            print(f"   ⚡ Dependencies: {response.get('dependencies', 'N/A')}")
        else:
            test_results["failed_tests"] += 1

        test_results["test_details"].append(
            {"test": "Health check", "success": success, "response_time_ms": time_ms}
        )

        # Test 3: Comprehensive Content Analysis
        print("\n🎯 Testing Comprehensive Content Analysis")
        content_data = {
            "text": """🚀 Revolutionary breakthrough! Our AI-powered platform is transforming the digital landscape!
            
            Key benefits:
            • Boost engagement rates by 50-75%
            • Predict viral content with 85% accuracy
            • Real-time performance optimization
            • Smart hashtag recommendations
            • Advanced sentiment analysis
            
            Join 10,000+ creators who've already seen amazing results! ✨
            
            #AI #innovation #contentcreation #socialmedia #analytics #growth #technology #breakthrough""",
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
            print(f"   ✅ Readability: {response.get('readability_score', 'N/A'):.1f}/100")
            print(f"   ✅ Word Count: {response.get('word_count', 'N/A')}")
            print(f"   ✅ Hashtag Count: {response.get('hashtag_count', 'N/A')}")
            tips = response.get("optimization_tips", [])
            if tips:
                print(f"   💡 First Tip: {tips[0]}")
            hashtags = response.get("hashtag_suggestions", [])
            if hashtags:
                print(f"   🏷️  Suggested Hashtags: {', '.join(hashtags[:3])}")
        else:
            test_results["failed_tests"] += 1

        test_results["test_details"].append(
            {
                "test": "Comprehensive content analysis",
                "success": success,
                "response_time_ms": time_ms,
            }
        )

        # Test 4: Real-time Scoring (Multiple scenarios)
        print("\n⚡ Testing Real-time Scoring - Multiple Scenarios")

        scenarios = [
            {"name": "Short positive", "text": "Great product! Love it 😍 #amazing"},
            {
                "name": "Long technical",
                "text": "This comprehensive analysis of machine learning algorithms demonstrates the significant impact of neural networks on predictive modeling accuracy across multiple industry verticals. #ML #AI #tech #data",
            },
            {
                "name": "Optimal content",
                "text": "🎯 Exciting update! Our new features are boosting user engagement significantly. Try them today! #update #features #engagement",
            },
        ]

        for scenario in scenarios:
            print(f"\n   🧪 Testing: {scenario['name']}")
            realtime_data = {"text": scenario["text"]}

            success, response, time_ms = await tester.test_endpoint(
                "POST", "/score/realtime", realtime_data
            )
            test_results["total_tests"] += 1
            if success:
                test_results["passed_tests"] += 1
                print(f"      ✅ Overall Score: {response.get('overall_score', 'N/A'):.3f}")
                print(f"      ✅ Length Score: {response.get('length_score', 'N/A'):.3f}")
                print(f"      ✅ Hashtag Score: {response.get('hashtag_score', 'N/A'):.3f}")
                print(f"      ✅ Sentiment Score: {response.get('sentiment_score', 'N/A'):.3f}")
                print(f"      ✅ Emoji Score: {response.get('emoji_score', 'N/A'):.3f}")
            else:
                test_results["failed_tests"] += 1

            test_results["test_details"].append(
                {
                    "test": f"Real-time scoring - {scenario['name']}",
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
            print(f"   ✅ Demo Score: {analysis.get('overall_score', 'N/A'):.3f}")
            print(f"   📝 Sample Content Length: {len(response.get('sample_content', ''))}")
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
            print(f"   ✅ Architecture: {response.get('architecture', 'N/A')}")
            capabilities = response.get("capabilities", {})
            enabled_features = sum(1 for v in capabilities.values() if v)
            print(f"   ✅ Active Features: {enabled_features}/{len(capabilities)}")
            performance = response.get("performance", {})
            print(f"   ⚡ Analysis Time: {performance.get('avg_analysis_time', 'N/A')}")
            print(f"   🎯 Accuracy: {performance.get('accuracy', 'N/A')}")
            print(f"   📦 Dependencies: {performance.get('dependencies', 'N/A')}")
        else:
            test_results["failed_tests"] += 1

        test_results["test_details"].append(
            {"test": "API stats", "success": success, "response_time_ms": time_ms}
        )

    # Performance Analysis
    response_times = [detail["response_time_ms"] for detail in test_results["test_details"]]
    test_results["performance_metrics"] = {
        "avg_response_time": sum(response_times) / len(response_times),
        "min_response_time": min(response_times),
        "max_response_time": max(response_times),
        "total_test_time": sum(response_times),
    }

    # Test Summary
    print("\n" + "=" * 60)
    print("📋 COMPREHENSIVE TEST SUMMARY")
    print("=" * 60)

    success_rate = (test_results["passed_tests"] / test_results["total_tests"]) * 100

    print(f"Total Tests: {test_results['total_tests']}")
    print(f"✅ Passed: {test_results['passed_tests']}")
    print(f"❌ Failed: {test_results['failed_tests']}")
    print(f"🎯 Success Rate: {success_rate:.1f}%")

    # Performance Metrics
    metrics = test_results["performance_metrics"]
    print("\n⚡ PERFORMANCE METRICS:")
    print(f"Average Response Time: {metrics['avg_response_time']:.1f}ms")
    print(f"Fastest Response: {metrics['min_response_time']:.1f}ms")
    print(f"Slowest Response: {metrics['max_response_time']:.1f}ms")
    print(f"Total Test Duration: {metrics['total_test_time']:.1f}ms")

    # Detailed Results
    print("\n📊 DETAILED TEST RESULTS:")
    for detail in test_results["test_details"]:
        status_icon = "✅" if detail["success"] else "❌"
        print(f"{status_icon} {detail['test']}: {detail['response_time_ms']:.1f}ms")

    # Final Verdict
    if success_rate >= 100:
        print("\n🎉 PERFECT SCORE! All tests passed - API is fully operational!")
        verdict = "EXCELLENT"
    elif success_rate >= 90:
        print(f"\n🚀 EXCELLENT! {success_rate:.1f}% success rate - API is production ready!")
        verdict = "EXCELLENT"
    elif success_rate >= 80:
        print(f"\n✅ GOOD! {success_rate:.1f}% success rate - Minor issues detected.")
        verdict = "GOOD"
    else:
        print(f"\n⚠️  NEEDS ATTENTION! Only {success_rate:.1f}% success rate.")
        verdict = "NEEDS_WORK"

    test_results["verdict"] = verdict

    return test_results


if __name__ == "__main__":
    print("🤖 Pure AI/ML API Comprehensive Test Suite")
    print("Please ensure the API server is running on http://localhost:8003")
    print("Start server with: python pure_ai_api.py")
    print()

    # Run comprehensive tests
    results = asyncio.run(run_comprehensive_tests())

    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"pure_api_test_results_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n💾 Detailed test results saved to: {filename}")

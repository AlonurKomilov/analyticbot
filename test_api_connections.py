#!/usr/bin/env python3
"""
API Connection Testing Script
Tests both real API mode and demo mode endpoints
"""

from datetime import datetime

import requests

# Configuration
API_BASE_URL = "http://localhost:11400"
DEMO_CHANNEL_ID = "demo_channel"
TEST_TIMEOUT = 5


# Colors for output
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")


def print_success(text: str):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")


def print_error(text: str):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")


def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")


def print_info(text: str):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")


def test_endpoint(
    method: str,
    path: str,
    expected_status: list[int] = [200],
    data: dict = None,
    description: str = "",
) -> tuple[bool, str]:
    """Test a single endpoint"""
    url = f"{API_BASE_URL}{path}"

    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=TEST_TIMEOUT)
        elif method.upper() == "POST":
            response = requests.post(url, json=data or {}, timeout=TEST_TIMEOUT)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data or {}, timeout=TEST_TIMEOUT)
        elif method.upper() == "DELETE":
            response = requests.delete(url, timeout=TEST_TIMEOUT)
        else:
            return False, f"Unsupported method: {method}"

        status = response.status_code

        # Check if status is expected
        if status in expected_status:
            return True, f"Status: {status}"
        elif status == 404:
            return False, f"Status: {status} - Endpoint not found!"
        elif status == 401:
            return True, f"Status: {status} - Auth required (endpoint exists)"
        elif status == 403:
            return True, f"Status: {status} - Forbidden (endpoint exists)"
        elif status == 422:
            return False, f"Status: {status} - Validation error (check request data)"
        else:
            return False, f"Status: {status} - Unexpected"

    except requests.exceptions.Timeout:
        return False, "Timeout"
    except requests.exceptions.ConnectionError:
        return False, "Connection failed - is backend running?"
    except Exception as e:
        return False, f"Error: {str(e)}"


def main():
    print_header("🧪 API Connection Testing Suite")
    print(f"Testing against: {API_BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    total_tests = 0
    passed_tests = 0
    failed_tests = 0

    # Test 1: Health Check
    print_header("1️⃣  Health Check")
    success, msg = test_endpoint("GET", "/health", [200])
    total_tests += 1
    if success:
        print_success(f"Health endpoint: {msg}")
        passed_tests += 1
    else:
        print_error(f"Health endpoint: {msg}")
        failed_tests += 1
        print_warning("Backend may not be running!")
        return

    # Test 2: Analytics Endpoints (Real API Mode)
    print_header("2️⃣  Analytics Endpoints (Real API Mode)")

    analytics_tests = [
        ("GET", f"/analytics/historical/overview/{DEMO_CHANNEL_ID}", "Historical Overview"),
        ("GET", f"/analytics/realtime/metrics/{DEMO_CHANNEL_ID}", "Real-time Metrics"),
        ("GET", f"/analytics/posts/dynamics/top-posts/{DEMO_CHANNEL_ID}", "Top Posts"),
        ("GET", f"/analytics/predictive/best-times/{DEMO_CHANNEL_ID}", "Best Times"),
        ("GET", f"/analytics/alerts/channel/{DEMO_CHANNEL_ID}", "Alerts"),
    ]

    for method, path, desc in analytics_tests:
        success, msg = test_endpoint(method, path, [200, 401, 403])
        total_tests += 1
        if success:
            print_success(f"{desc}: {msg}")
            passed_tests += 1
        else:
            print_error(f"{desc}: {msg}")
            failed_tests += 1

    # Test 3: AI Services Endpoints
    print_header("3️⃣  AI Services Endpoints")

    ai_tests = [
        (
            "POST",
            "/ai/services/content/analyze",
            "Content Analyzer",
            {"content": "Test content", "channel_id": DEMO_CHANNEL_ID},
        ),
        (
            "POST",
            "/ai/services/churn/analyze",
            "Churn Predictor",
            {"user_id": DEMO_CHANNEL_ID, "channel_id": DEMO_CHANNEL_ID},
        ),
        ("POST", "/ai/services/security/analyze", "Security Monitor", {"content": "Test content"}),
        ("GET", "/ai/services/churn/stats", "Churn Stats"),
    ]

    for method, path, desc, *data in ai_tests:
        request_data = data[0] if data else None
        success, msg = test_endpoint(method, path, [200, 401, 403, 422], request_data)
        total_tests += 1
        if success:
            print_success(f"{desc}: {msg}")
            passed_tests += 1
        else:
            print_error(f"{desc}: {msg}")
            failed_tests += 1

    # Test 4: Demo Mode Endpoints
    print_header("4️⃣  Demo Mode Endpoints")

    demo_tests = [
        ("GET", "/demo/analytics/top-posts", "Demo Top Posts"),
        ("GET", "/unified-analytics/demo/top-posts", "Unified Demo Top Posts"),
        ("GET", "/unified-analytics/demo/best-time", "Demo Best Time"),
    ]

    for method, path, desc in demo_tests:
        success, msg = test_endpoint(method, path, [200, 401, 403])
        total_tests += 1
        if success:
            print_success(f"{desc}: {msg}")
            passed_tests += 1
        else:
            print_error(f"{desc}: {msg}")
            failed_tests += 1

    # Test 5: Payment Endpoints
    print_header("5️⃣  Payment Endpoints")

    payment_tests = [
        ("GET", "/payments/plans", "Subscription Plans"),
        ("GET", "/payments/stats/payments", "Payment Stats"),
    ]

    for method, path, desc in payment_tests:
        success, msg = test_endpoint(method, path, [200, 401, 403])
        total_tests += 1
        if success:
            print_success(f"{desc}: {msg}")
            passed_tests += 1
        else:
            print_error(f"{desc}: {msg}")
            failed_tests += 1

    # Test 6: Content Protection Endpoints
    print_header("6️⃣  Content Protection Endpoints")

    protection_tests = [
        (
            "POST",
            "/content/protection/detection/scan",
            "Theft Detection",
            {"channel_id": DEMO_CHANNEL_ID},
        ),
        ("POST", "/content/protection/watermark/text", "Text Watermark", {"text": "Test text"}),
    ]

    for method, path, desc, *data in protection_tests:
        request_data = data[0] if data else None
        success, msg = test_endpoint(method, path, [200, 401, 403, 422], request_data)
        total_tests += 1
        if success:
            print_success(f"{desc}: {msg}")
            passed_tests += 1
        else:
            print_error(f"{desc}: {msg}")
            failed_tests += 1

    # Test 7: Verify Wrong Paths Don't Work
    print_header("7️⃣  Verify Wrong Paths (Should Fail)")

    wrong_paths = [
        ("GET", "/api/v2/analytics/channels/123/overview", "Old API v2 path"),
        ("GET", "/ai/content/optimize", "Wrong AI path (missing /services/)"),
        ("GET", "/statistics/core/overview/123", "Old statistics path"),
    ]

    for method, path, desc in wrong_paths:
        success, msg = test_endpoint(method, path, [404])
        total_tests += 1
        # Invert success - we WANT 404 here
        if "404" in msg:
            print_success(f"{desc}: Correctly returns 404 ✓")
            passed_tests += 1
        else:
            print_warning(f"{desc}: {msg} (expected 404)")
            # Don't count as failed since it might be a backward compatibility route

    # Final Summary
    print_header("📊 Test Results Summary")
    print(f"Total Tests:  {total_tests}")
    print(f"{Colors.GREEN}Passed:       {passed_tests}{Colors.RESET}")
    print(f"{Colors.RED}Failed:       {failed_tests}{Colors.RESET}")

    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"\n{Colors.BOLD}Success Rate: {success_rate:.1f}%{Colors.RESET}")

    if success_rate >= 80:
        print(
            f"\n{Colors.GREEN}{Colors.BOLD}✅ EXCELLENT - API connections are working well!{Colors.RESET}"
        )
    elif success_rate >= 60:
        print(
            f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  GOOD - Most connections work, some issues to fix{Colors.RESET}"
        )
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ NEEDS WORK - Many connections failing{Colors.RESET}")

    print(f"\n{Colors.BLUE}📖 For detailed API docs, visit: {API_BASE_URL}/docs{Colors.RESET}\n")


if __name__ == "__main__":
    main()

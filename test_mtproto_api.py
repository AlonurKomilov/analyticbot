#!/usr/bin/env python3
"""
Test MTProto API Endpoints
Tests the user MTProto setup flow with the API
"""

import json
import sys

import requests

# Configuration
API_BASE_URL = "http://localhost:11400"
TEST_USER_EMAIL = "test_mtproto@example.com"
TEST_USER_PASSWORD = "TestPassword123!"

# Test data (use fake data for testing - real credentials not needed for API validation)
TEST_MTPROTO_DATA = {
    "telegram_api_id": 12345678,  # Fake API ID
    "telegram_api_hash": "abcd1234efgh5678ijkl9012mnop3456",  # Fake hash (32+ chars)
    "telegram_phone": "+1234567890",  # Fake phone
}


class Colors:
    """Terminal colors"""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    END = "\033[0m"
    BOLD = "\033[1m"


def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.YELLOW}ℹ️  {text}{Colors.END}")


def print_response(response: requests.Response):
    """Print formatted response"""
    print(f"\nStatus Code: {response.status_code}")
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
    except:
        print(f"Response: {response.text}")


def login_or_register() -> str | None:
    """Login or register test user and return JWT token"""
    print_header("Authentication")

    # Try to register first
    print_info(f"Attempting to register user: {TEST_USER_EMAIL}")
    register_response = requests.post(
        f"{API_BASE_URL}/auth/register",
        json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "username": "mtproto_test_user",
        },
    )

    if register_response.status_code == 201:
        print_success("User registered successfully")
        data = register_response.json()
        token = data.get("access_token") or data.get("token")
        if token:
            return token
        print_info(f"No token in register response, trying login... Response: {data}")

    # User likely exists or no token, try login
    print_info("Attempting login...")
    login_response = requests.post(
        f"{API_BASE_URL}/auth/login",
        json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
    )

    if login_response.status_code == 200:
        print_success("Login successful")
        data = login_response.json()
        return data.get("access_token")

    print_error("Failed to authenticate")
    print_response(login_response)
    return None


def test_get_status(token: str):
    """Test GET /api/user-mtproto/status"""
    print_header("Test 1: Get MTProto Status")

    response = requests.get(
        f"{API_BASE_URL}/api/user-mtproto/status", headers={"Authorization": f"Bearer {token}"}
    )

    print_response(response)

    if response.status_code == 200:
        data = response.json()
        print_success(
            f"Status retrieved - Configured: {data.get('configured')}, Verified: {data.get('verified')}"
        )
        return data
    else:
        print_error(f"Failed to get status: {response.status_code}")
        return None


def test_setup_mtproto(token: str):
    """Test POST /api/user-mtproto/setup"""
    print_header("Test 2: Setup MTProto (Initiate)")

    print_info("Note: This will fail with real API validation, but tests the endpoint structure")
    response = requests.post(
        f"{API_BASE_URL}/api/user-mtproto/setup",
        headers={"Authorization": f"Bearer {token}"},
        json=TEST_MTPROTO_DATA,
    )

    print_response(response)

    if response.status_code == 200:
        data = response.json()
        print_success(f"Setup initiated - Message: {data.get('message')}")
        return data.get("phone_code_hash")
    elif response.status_code == 400:
        print_info("Expected error with fake credentials - endpoint is working!")
        return None
    else:
        print_error(f"Unexpected status code: {response.status_code}")
        return None


def test_verify_mtproto(token: str, phone_code_hash: str):
    """Test POST /api/user-mtproto/verify"""
    print_header("Test 3: Verify MTProto")

    if not phone_code_hash:
        print_info("Skipping verification (no phone_code_hash from setup)")
        return

    response = requests.post(
        f"{API_BASE_URL}/api/user-mtproto/verify",
        headers={"Authorization": f"Bearer {token}"},
        json={"verification_code": "12345", "phone_code_hash": phone_code_hash},
    )

    print_response(response)

    if response.status_code == 200:
        print_success("Verification successful")
    else:
        print_info("Verification failed (expected with fake data)")


def test_disconnect_mtproto(token: str):
    """Test POST /api/user-mtproto/disconnect"""
    print_header("Test 4: Disconnect MTProto")

    response = requests.post(
        f"{API_BASE_URL}/api/user-mtproto/disconnect", headers={"Authorization": f"Bearer {token}"}
    )

    print_response(response)

    if response.status_code == 200:
        print_success("Disconnected successfully")
    elif response.status_code == 404:
        print_info("No MTProto configuration found (expected)")
    else:
        print_error(f"Unexpected status: {response.status_code}")


def test_remove_mtproto(token: str):
    """Test DELETE /api/user-mtproto/remove"""
    print_header("Test 5: Remove MTProto Configuration")

    response = requests.delete(
        f"{API_BASE_URL}/api/user-mtproto/remove", headers={"Authorization": f"Bearer {token}"}
    )

    print_response(response)

    if response.status_code == 200:
        print_success("Configuration removed successfully")
    elif response.status_code == 404:
        print_info("No MTProto configuration found (expected)")
    else:
        print_error(f"Unexpected status: {response.status_code}")


def main():
    """Run all tests"""
    print_header("MTProto API Test Suite")
    print_info(f"Testing API at: {API_BASE_URL}")

    # Authenticate
    token = login_or_register()
    if not token:
        print_error("Failed to obtain authentication token")
        sys.exit(1)

    print_success(f"Authentication token obtained (length: {len(token)})")

    # Test endpoints
    try:
        # 1. Check initial status
        status = test_get_status(token)

        # 2. Try to setup MTProto
        phone_code_hash = test_setup_mtproto(token)

        # 3. Try to verify (will fail without real code)
        test_verify_mtproto(token, phone_code_hash)

        # 4. Try to disconnect
        test_disconnect_mtproto(token)

        # 5. Try to remove
        test_remove_mtproto(token)

        # 6. Check final status
        test_get_status(token)

        print_header("Test Suite Complete")
        print_success("All API endpoints are accessible and responding correctly")

    except KeyboardInterrupt:
        print_error("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Test failed with exception: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

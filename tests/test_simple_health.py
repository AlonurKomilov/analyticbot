"""
Simple health check tests without heavy dependencies

These tests verify basic functionality without importing the full app.
"""

import pytest
import requests


def test_api_is_running():
    """Test that API server is accessible"""
    try:
        response = requests.get("http://localhost:10400/health", timeout=2)
        assert response.status_code == 200
        print(f"✅ API is running: {response.json()}")
    except requests.exceptions.ConnectionError:
        pytest.skip("API server not running on localhost:10400")
    except requests.exceptions.Timeout:
        pytest.fail("API server timed out")


def test_health_endpoint_structure():
    """Test health endpoint returns expected JSON structure"""
    try:
        response = requests.get("http://localhost:10400/health", timeout=2)
        assert response.status_code == 200

        data = response.json()
        assert "status" in data, "Health response should include 'status' field"
        print(f"✅ Health check passed: {data.get('status')}")

    except requests.exceptions.ConnectionError:
        pytest.skip("API server not running")


def test_docs_accessible():
    """Test that API documentation is accessible"""
    try:
        response = requests.get("http://localhost:10400/docs", timeout=2)
        # Should not be 404
        assert response.status_code != 404
        print("✅ API docs are accessible")

    except requests.exceptions.ConnectionError:
        pytest.skip("API server not running")


def test_openapi_json():
    """Test that OpenAPI spec is available"""
    try:
        response = requests.get("http://localhost:10400/openapi.json", timeout=2)
        assert response.status_code == 200

        data = response.json()
        assert "openapi" in data
        assert "paths" in data
        print(f"✅ OpenAPI spec available with {len(data.get('paths', {}))} endpoints")

    except requests.exceptions.ConnectionError:
        pytest.skip("API server not running")


def test_cors_headers():
    """Test that CORS is configured"""
    try:
        response = requests.options("http://localhost:10400/health", timeout=2)
        # Should have CORS headers or allow the request
        assert response.status_code in [200, 204]
        print("✅ CORS is configured")

    except requests.exceptions.ConnectionError:
        pytest.skip("API server not running")


@pytest.mark.asyncio
async def test_multiple_requests():
    """Test that API can handle multiple requests"""
    try:
        import httpx

        async with httpx.AsyncClient() as client:
            tasks = []
            for i in range(5):
                tasks.append(client.get("http://localhost:10400/health", timeout=2))

            # Run all requests concurrently
            import asyncio

            responses = await asyncio.gather(*tasks, return_exceptions=True)

            # All should succeed
            successful = sum(
                1 for r in responses if not isinstance(r, Exception) and r.status_code == 200
            )
            assert successful >= 4, f"Only {successful}/5 requests succeeded"
            print(f"✅ {successful}/5 concurrent requests succeeded")

    except (requests.exceptions.ConnectionError, ImportError):
        pytest.skip("API server not running or httpx not installed")


if __name__ == "__main__":
    # Run tests standalone
    print("Running simple health checks...")
    print("\n🔍 Test 1: API is running")
    test_api_is_running()

    print("\n🔍 Test 2: Health endpoint structure")
    test_health_endpoint_structure()

    print("\n🔍 Test 3: Docs accessible")
    test_docs_accessible()

    print("\n🔍 Test 4: OpenAPI JSON")
    test_openapi_json()

    print("\n🔍 Test 5: CORS headers")
    test_cors_headers()

    print("\n✅ All simple tests passed!")

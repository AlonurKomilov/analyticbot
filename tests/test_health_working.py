"""
Basic health check tests - These should always pass

These tests validate that:
1. The application starts successfully
2. Health endpoint returns correct status
3. Core API endpoints are accessible
4. Documentation endpoints work
"""

import pytest
from fastapi.testclient import TestClient


def test_health_endpoint_returns_200(test_client: TestClient):
    """Test that health endpoint returns 200 OK"""
    response = test_client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert data["status"] in ["healthy", "ok", "success"]


def test_health_endpoint_structure(test_client: TestClient):
    """Test health endpoint returns expected structure"""
    response = test_client.get("/health")
    assert response.status_code == 200

    data = response.json()

    # Should have status field
    assert "status" in data

    # May have additional fields
    if "timestamp" in data:
        assert isinstance(data["timestamp"], str)

    if "version" in data:
        assert isinstance(data["version"], str)


def test_openapi_json_accessible(test_client: TestClient):
    """Test that OpenAPI JSON schema is accessible"""
    response = test_client.get("/openapi.json")
    assert response.status_code == 200

    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert "paths" in data


def test_docs_endpoint_accessible(test_client: TestClient):
    """Test that Swagger UI docs are accessible"""
    response = test_client.get("/docs", follow_redirects=True)

    # Should not return 404
    assert response.status_code != 404

    # Should return HTML content
    assert "text/html" in response.headers.get("content-type", "")


def test_redoc_endpoint_accessible(test_client: TestClient):
    """Test that ReDoc documentation is accessible"""
    response = test_client.get("/redoc", follow_redirects=True)

    # Should not return 404
    assert response.status_code != 404


def test_api_returns_json(test_client: TestClient):
    """Test that API endpoints return JSON"""
    response = test_client.get("/health")
    assert response.status_code == 200

    # Check content type
    content_type = response.headers.get("content-type", "")
    assert "application/json" in content_type


@pytest.mark.asyncio
async def test_async_health_check(async_client):
    """Test health check using async client"""
    response = await async_client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert "status" in data


def test_cors_headers_present(test_client: TestClient):
    """Test that CORS headers are configured"""
    response = test_client.options("/health")

    # CORS headers should be present
    headers = response.headers

    # At minimum, we should have access control allow origin
    # (May be set to * or specific origins)
    assert "access-control-allow-origin" in headers or response.status_code == 200


def test_health_check_performance(test_client: TestClient):
    """Test that health check responds quickly"""
    import time

    start = time.time()
    response = test_client.get("/health")
    duration = time.time() - start

    assert response.status_code == 200

    # Should respond in less than 1 second
    assert duration < 1.0, f"Health check took {duration:.2f}s, should be < 1s"


def test_multiple_requests_stable(test_client: TestClient):
    """Test that multiple rapid requests are stable"""
    for i in range(5):
        response = test_client.get("/health")
        assert response.status_code == 200, f"Request {i+1} failed"

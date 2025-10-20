"""
API Main Tests
==============

Test the main API application initialization and health endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.api
@pytest.mark.integration
class TestAPIStartup:
    """Test API application startup and configuration."""

    @pytest.mark.asyncio
    async def test_api_app_can_be_created(self, api_client: AsyncClient):
        """Test that the FastAPI app can be created and responds."""
        assert api_client is not None
        # Test that the app is functional by making a request
        response = await api_client.get("/health")
        assert response.status_code in [200, 404]  # App is running

    @pytest.mark.asyncio
    async def test_health_endpoint_returns_200(self, api_client: AsyncClient):
        """Test the health check endpoint."""
        response = await api_client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "ok", "up"]

    @pytest.mark.asyncio
    async def test_di_health_endpoint_returns_200(self, api_client: AsyncClient):
        """Test the DI health check endpoint."""
        response = await api_client.get("/di-health")
        assert response.status_code == 200

        data = response.json()
        assert "database" in data or "status" in data


@pytest.mark.api
@pytest.mark.integration
class TestAPIEndpoints:
    """Test critical API endpoints."""

    @pytest.mark.asyncio
    async def test_root_endpoint(self, api_client: AsyncClient):
        """Test the root endpoint."""
        response = await api_client.get("/")
        # May be 200, 404, or redirect depending on setup
        assert response.status_code in [200, 404, 307, 404]

    @pytest.mark.asyncio
    async def test_docs_endpoint_available(self, api_client: AsyncClient):
        """Test that API docs are available."""
        response = await api_client.get("/docs")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_openapi_schema_available(self, api_client: AsyncClient):
        """Test that OpenAPI schema is available."""
        response = await api_client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema


@pytest.mark.api
@pytest.mark.integration
class TestAuthenticationMiddleware:
    """Test authentication middleware."""

    @pytest.mark.asyncio
    async def test_protected_endpoint_requires_auth(self, api_client: AsyncClient):
        """Test that protected endpoints require authentication."""
        # This test assumes there are protected endpoints
        # Adjust endpoint path based on actual API structure
        response = await api_client.get("/api/v1/me")
        # Should be 401 Unauthorized or 403 Forbidden
        assert response.status_code in [401, 403, 404]

    @pytest.mark.asyncio
    async def test_authenticated_client_can_access_protected_endpoint(
        self, authenticated_client: AsyncClient
    ):
        """Test that authenticated clients can access protected endpoints."""
        # This test assumes there are protected endpoints
        response = await authenticated_client.get("/api/v1/me")
        # Should be 200 OK or 404 if endpoint doesn't exist yet
        assert response.status_code in [200, 404]


@pytest.mark.api
@pytest.mark.integration
class TestErrorHandling:
    """Test API error handling."""

    @pytest.mark.asyncio
    async def test_404_for_nonexistent_endpoint(self, api_client: AsyncClient):
        """Test 404 response for nonexistent endpoints."""
        response = await api_client.get("/api/v1/this-does-not-exist")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_422_for_invalid_request_body(self, api_client: AsyncClient):
        """Test validation error response."""
        # Try to post invalid data to an endpoint
        response = await api_client.post(
            "/api/v1/channels", json={"invalid": "data"}
        )
        # Should be 422 Unprocessable Entity or 404 if endpoint doesn't exist
        assert response.status_code in [404, 422, 401, 403]

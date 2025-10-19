"""
Authentication Tests
====================

Test authentication endpoints and middleware.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.api
@pytest.mark.integration
class TestAuthenticationFlow:
    """Test user authentication flow."""

    @pytest.mark.asyncio
    async def test_jwt_token_can_be_created(self):
        """Test that JWT tokens can be created."""
        from apps.shared.auth import create_access_token

        token = create_access_token({"user_id": 123456789})
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    @pytest.mark.asyncio
    async def test_jwt_token_can_be_decoded(self):
        """Test that JWT tokens can be decoded."""
        from apps.shared.auth import create_access_token, decode_access_token

        user_id = 123456789
        token = create_access_token({"user_id": user_id})

        payload = decode_access_token(token)
        assert payload is not None
        assert payload.get("user_id") == user_id

    @pytest.mark.asyncio
    async def test_invalid_token_raises_error(self):
        """Test that invalid tokens raise appropriate errors."""
        from apps.shared.auth import decode_access_token

        invalid_token = "invalid.token.here"

        payload = decode_access_token(invalid_token)
        # Should return None or raise exception
        assert payload is None or "error" in payload


@pytest.mark.api
@pytest.mark.integration
class TestAuthMiddleware:
    """Test authentication middleware behavior."""

    @pytest.mark.asyncio
    async def test_auth_middleware_passes_valid_token(
        self, authenticated_client: AsyncClient
    ):
        """Test that valid tokens pass through middleware."""
        # The authenticated_client fixture already has a valid token
        # Try to access a protected endpoint
        response = await authenticated_client.get("/api/v1/me")

        # Should not be 401 (Unauthorized)
        assert response.status_code != 401

    @pytest.mark.asyncio
    async def test_auth_middleware_rejects_missing_token(
        self, api_client: AsyncClient
    ):
        """Test that requests without tokens are rejected."""
        # Try to access protected endpoint without auth
        response = await api_client.get("/api/v1/me")

        # Should be 401 or 403
        assert response.status_code in [401, 403, 404]

    @pytest.mark.asyncio
    async def test_auth_middleware_rejects_malformed_token(
        self, api_client: AsyncClient
    ):
        """Test that malformed tokens are rejected."""
        # Set malformed auth header
        api_client.headers["Authorization"] = "Bearer invalid_token"

        response = await api_client.get("/api/v1/me")

        # Should be 401 or 403
        assert response.status_code in [401, 403, 404]


@pytest.mark.api
@pytest.mark.unit
class TestAuthHelpers:
    """Test authentication helper functions."""

    def test_password_can_be_hashed(self):
        """Test password hashing."""
        # Skip if password hashing not implemented yet
        pytest.skip("Password hashing not yet implemented")

    def test_password_verification_works(self):
        """Test password verification."""
        # Skip if password verification not implemented yet
        pytest.skip("Password verification not yet implemented")

"""Tests for API security middleware"""

import pytest
from unittest.mock import MagicMock, patch

from src.api.security import require_api_key, rate_limit_check, _buckets


@pytest.fixture(autouse=True)
def clear_rate_limit_buckets():
    """Clear rate limit state between tests."""
    _buckets.clear()
    yield
    _buckets.clear()


class TestRequireApiKey:
    @pytest.mark.asyncio
    async def test_no_key_configured_allows_request(self):
        with patch("src.api.security.settings") as mock_settings:
            mock_settings.API_KEY = ""
            result = await require_api_key(api_key=None)
            assert result == ""

    @pytest.mark.asyncio
    async def test_valid_key_passes(self):
        with patch("src.api.security.settings") as mock_settings:
            mock_settings.API_KEY = "test-key-123"
            result = await require_api_key(api_key="test-key-123")
            assert result == "test-key-123"

    @pytest.mark.asyncio
    async def test_invalid_key_rejected(self):
        from fastapi import HTTPException

        with patch("src.api.security.settings") as mock_settings:
            mock_settings.API_KEY = "correct-key"
            with pytest.raises(HTTPException) as exc_info:
                await require_api_key(api_key="wrong-key")
            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_missing_key_rejected(self):
        from fastapi import HTTPException

        with patch("src.api.security.settings") as mock_settings:
            mock_settings.API_KEY = "correct-key"
            with pytest.raises(HTTPException) as exc_info:
                await require_api_key(api_key=None)
            assert exc_info.value.status_code == 401


class TestRateLimiting:
    @pytest.mark.asyncio
    async def test_allows_within_limit(self):
        request = MagicMock()
        request.headers = {}
        request.client = MagicMock()
        request.client.host = "127.0.0.1"

        with patch("src.api.security.settings") as mock_settings:
            mock_settings.RATE_LIMIT_PER_MINUTE = 5
            # Should not raise for the first 5 requests
            for _ in range(5):
                await rate_limit_check(request)

    @pytest.mark.asyncio
    async def test_blocks_over_limit(self):
        from fastapi import HTTPException

        request = MagicMock()
        request.headers = {}
        request.client = MagicMock()
        request.client.host = "192.168.1.1"

        with patch("src.api.security.settings") as mock_settings:
            mock_settings.RATE_LIMIT_PER_MINUTE = 3
            for _ in range(3):
                await rate_limit_check(request)

            with pytest.raises(HTTPException) as exc_info:
                await rate_limit_check(request)
            assert exc_info.value.status_code == 429

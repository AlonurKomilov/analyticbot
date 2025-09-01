"""
Tests for Analytics V2 ETag/Cache functionality
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock

import pytest
from httpx import AsyncClient

from apps.api.main import app


@pytest.fixture
async def client():
    """Create test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_fusion_service():
    """Mock analytics fusion service"""
    service = Mock()
    service.get_last_updated_at = AsyncMock(
        return_value=datetime(2025, 8, 31, 12, 0, 0, tzinfo=UTC)
    )
    service.get_overview = AsyncMock(
        return_value={
            "channel_id": 123,
            "period": {"from": "2025-08-30T00:00:00Z", "to": "2025-08-31T23:59:59Z"},
            "metrics": {
                "total_posts": 50,
                "total_views": 15000,
                "avg_engagement_rate": 3.2,
                "growth_rate": 5.5,
            },
            "meta": {"cache_hit": False},
        }
    )
    return service


@pytest.fixture
def mock_cache():
    """Mock cache"""
    cache = Mock()
    cache.generate_cache_key = Mock(return_value="test_cache_key")
    cache.get_json = AsyncMock(return_value=None)  # No cache initially
    cache.set_json = AsyncMock()
    return cache


class TestAnalyticsV2ETag:
    """Test ETag and caching functionality for Analytics V2"""

    async def test_etag_generated_correctly(
        self, client: AsyncClient, mock_fusion_service, mock_cache, monkeypatch
    ):
        """Test that ETag is generated and included in response headers"""
        # Mock the dependencies
        monkeypatch.setattr(
            "apps.api.di_analytics_v2.get_analytics_fusion_service",
            lambda: mock_fusion_service,
        )
        monkeypatch.setattr("apps.api.di_analytics_v2.get_cache", lambda: mock_cache)

        response = await client.get(
            "/api/v2/analytics/channels/123/overview",
            params={"from": "2025-08-30T00:00:00Z", "to": "2025-08-31T23:59:59Z"},
        )

        assert response.status_code == 200
        assert "ETag" in response.headers
        assert response.headers["ETag"].startswith('"')
        assert response.headers["ETag"].endswith('"')
        assert "Cache-Control" in response.headers
        assert response.headers["Cache-Control"] == "public, max-age=60"

    async def test_304_response_with_matching_etag(
        self, client: AsyncClient, mock_fusion_service, mock_cache, monkeypatch
    ):
        """Test that 304 is returned when If-None-Match header matches ETag"""
        # Mock the dependencies
        monkeypatch.setattr(
            "apps.api.di_analytics_v2.get_analytics_fusion_service",
            lambda: mock_fusion_service,
        )
        monkeypatch.setattr("apps.api.di_analytics_v2.get_cache", lambda: mock_cache)

        # First request to get ETag
        response1 = await client.get(
            "/api/v2/analytics/channels/123/overview",
            params={"from": "2025-08-30T00:00:00Z", "to": "2025-08-31T23:59:59Z"},
        )

        assert response1.status_code == 200
        etag = response1.headers["ETag"]

        # Second request with If-None-Match header
        response2 = await client.get(
            "/api/v2/analytics/channels/123/overview",
            params={"from": "2025-08-30T00:00:00Z", "to": "2025-08-31T23:59:59Z"},
            headers={"If-None-Match": etag},
        )

        assert response2.status_code == 304
        assert "ETag" in response2.headers
        assert response2.headers["ETag"] == etag
        assert response2.content == b""  # No body for 304 response

    async def test_200_response_with_different_etag(
        self, client: AsyncClient, mock_fusion_service, mock_cache, monkeypatch
    ):
        """Test that 200 is returned when If-None-Match header doesn't match current ETag"""
        # Mock the dependencies
        monkeypatch.setattr(
            "apps.api.di_analytics_v2.get_analytics_fusion_service",
            lambda: mock_fusion_service,
        )
        monkeypatch.setattr("apps.api.di_analytics_v2.get_cache", lambda: mock_cache)

        response = await client.get(
            "/api/v2/analytics/channels/123/overview",
            params={"from": "2025-08-30T00:00:00Z", "to": "2025-08-31T23:59:59Z"},
            headers={"If-None-Match": '"different-etag"'},
        )

        assert response.status_code == 200
        assert "ETag" in response.headers
        assert response.headers["ETag"] != '"different-etag"'
        assert response.json()["data"]["channel_id"] == 123

    async def test_cache_control_header_present(
        self, client: AsyncClient, mock_fusion_service, mock_cache, monkeypatch
    ):
        """Test that Cache-Control header is present and correct"""
        # Mock the dependencies
        monkeypatch.setattr(
            "apps.api.di_analytics_v2.get_analytics_fusion_service",
            lambda: mock_fusion_service,
        )
        monkeypatch.setattr("apps.api.di_analytics_v2.get_cache", lambda: mock_cache)

        response = await client.get(
            "/api/v2/analytics/channels/123/overview",
            params={"from": "2025-08-30T00:00:00Z", "to": "2025-08-31T23:59:59Z"},
        )

        assert response.status_code == 200
        assert response.headers["Cache-Control"] == "public, max-age=60"

    async def test_etag_changes_with_different_params(
        self, client: AsyncClient, mock_fusion_service, mock_cache, monkeypatch
    ):
        """Test that ETag changes when request parameters change"""
        # Mock the dependencies
        monkeypatch.setattr(
            "apps.api.di_analytics_v2.get_analytics_fusion_service",
            lambda: mock_fusion_service,
        )
        monkeypatch.setattr("apps.api.di_analytics_v2.get_cache", lambda: mock_cache)

        # First request
        response1 = await client.get(
            "/api/v2/analytics/channels/123/overview",
            params={"from": "2025-08-30T00:00:00Z", "to": "2025-08-31T23:59:59Z"},
        )

        # Second request with different date range
        response2 = await client.get(
            "/api/v2/analytics/channels/123/overview",
            params={"from": "2025-08-29T00:00:00Z", "to": "2025-08-31T23:59:59Z"},
        )

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.headers["ETag"] != response2.headers["ETag"]

    async def test_etag_includes_last_updated_timestamp(
        self, client: AsyncClient, mock_cache, monkeypatch
    ):
        """Test that ETag incorporates last_updated timestamp"""
        # Mock fusion service with different last_updated times
        service1 = Mock()
        service1.get_last_updated_at = AsyncMock(
            return_value=datetime(2025, 8, 31, 12, 0, 0, tzinfo=UTC)
        )
        service1.get_overview = AsyncMock(
            return_value={"channel_id": 123, "meta": {"cache_hit": False}}
        )

        service2 = Mock()
        service2.get_last_updated_at = AsyncMock(
            return_value=datetime(2025, 8, 31, 13, 0, 0, tzinfo=UTC)
        )
        service2.get_overview = AsyncMock(
            return_value={"channel_id": 123, "meta": {"cache_hit": False}}
        )

        monkeypatch.setattr("apps.api.di_analytics_v2.get_cache", lambda: mock_cache)

        # First request
        monkeypatch.setattr(
            "apps.api.di_analytics_v2.get_analytics_fusion_service", lambda: service1
        )
        response1 = await client.get(
            "/api/v2/analytics/channels/123/overview",
            params={"from": "2025-08-30T00:00:00Z", "to": "2025-08-31T23:59:59Z"},
        )

        # Second request with updated timestamp
        monkeypatch.setattr(
            "apps.api.di_analytics_v2.get_analytics_fusion_service", lambda: service2
        )
        response2 = await client.get(
            "/api/v2/analytics/channels/123/overview",
            params={"from": "2025-08-30T00:00:00Z", "to": "2025-08-31T23:59:59Z"},
        )

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.headers["ETag"] != response2.headers["ETag"]

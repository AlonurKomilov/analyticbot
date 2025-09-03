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
            "posts": 10,
            "views": 1000,
            "avg_reach": 100.0,
            "err": None,
            "followers": 500,
            "period": {"from": "2025-08-30T00:00:00", "to": "2025-08-31T23:59:59"}
        }
    )
    return service


@pytest.fixture
def mock_cache():
    """Mock cache"""
    cache = Mock()
    
    def mock_generate_cache_key(endpoint: str, params: dict, last_updated=None):
        """Mock cache key generation that mimics real behavior"""
        import hashlib
        import json
        from datetime import datetime
        
        # Sort parameters for consistent key generation
        sorted_params = sorted(params.items())
        
        # Convert datetime objects to isoformat for consistency with router
        def datetime_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return str(obj)
        
        params_str = json.dumps(sorted_params, default=datetime_serializer)
        
        # Include last_updated in key for cache invalidation
        key_data = f"{endpoint}:{params_str}"
        if last_updated:
            if isinstance(last_updated, datetime):
                key_data += f":{last_updated.isoformat()}"
            else:
                key_data += f":{last_updated}"
        
        # Create hash for shorter, consistent keys
        key_hash = hashlib.sha256(key_data.encode()).hexdigest()
        return f"analytics_v2:{endpoint}:{key_hash}"
    
    cache.generate_cache_key = Mock(side_effect=mock_generate_cache_key)
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
            "apps.api.di_analytics_v2.get_analytics_fusion_service", lambda: mock_fusion_service
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
            "apps.api.di_analytics_v2.get_analytics_fusion_service", lambda: mock_fusion_service
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
            "apps.api.di_analytics_v2.get_analytics_fusion_service", lambda: mock_fusion_service
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
        # Check that we have overview data (posts field exists)
        assert "posts" in response.json()["data"]

    async def test_cache_control_header_present(
        self, client: AsyncClient, mock_fusion_service, mock_cache, monkeypatch
    ):
        """Test that Cache-Control header is present and correct"""
        # Mock the dependencies
        monkeypatch.setattr(
            "apps.api.di_analytics_v2.get_analytics_fusion_service", lambda: mock_fusion_service
        )
        monkeypatch.setattr("apps.api.di_analytics_v2.get_cache", lambda: mock_cache)

        response = await client.get(
            "/api/v2/analytics/channels/123/overview",
            params={"from": "2025-08-30T00:00:00Z", "to": "2025-08-31T23:59:59Z"},
        )

        assert response.status_code == 200
        assert response.headers["Cache-Control"] == "public, max-age=60"

    async def test_etag_changes_with_different_params(
        self, client: AsyncClient, monkeypatch
    ):
        """Test that ETag changes when request parameters change"""
        # Mock fusion service
        service = Mock()
        service.get_last_updated_at = AsyncMock(
            return_value=datetime(2025, 8, 31, 12, 0, 0, tzinfo=UTC)
        )
        service.get_overview = AsyncMock(
            return_value={
                "posts": 10,
                "views": 1000,
                "avg_reach": 100.0,
                "err": None,
                "followers": 500,
                "period": {"from": "2025-08-30T00:00:00", "to": "2025-08-31T23:59:59"}
            }
        )

        # Mock cache with proper key generation matching router
        cache = Mock()
        def mock_generate_cache_key(endpoint: str, params: dict, last_updated=None):
            """Mock cache key generation that matches router implementation"""
            import hashlib
            import json
            from datetime import datetime
            
            # Sort parameters for consistent key generation (matches router)
            sorted_params = sorted(params.items())
            
            # Convert datetime objects to isoformat for consistency with router
            def datetime_serializer(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return str(obj)
            
            params_str = json.dumps(sorted_params, default=datetime_serializer)
            
            # Include last_updated in key for cache invalidation
            key_data = f"{endpoint}:{params_str}"
            if last_updated:
                if isinstance(last_updated, datetime):
                    key_data += f":{last_updated.isoformat()}"
                else:
                    key_data += f":{last_updated}"
            
            # Create hash for shorter, consistent keys
            key_hash = hashlib.sha256(key_data.encode()).hexdigest()
            return f"analytics_v2:{endpoint}:{key_hash}"
        
        cache.generate_cache_key = Mock(side_effect=mock_generate_cache_key)
        cache.get_json = AsyncMock(return_value=None)  # No cache initially
        cache.set_json = AsyncMock()

        # Mock the dependencies
        monkeypatch.setattr(
            "apps.api.di_analytics_v2.get_analytics_fusion_service", lambda: service
        )
        monkeypatch.setattr("apps.api.di_analytics_v2.get_cache", lambda: cache)

        # First request with one date range
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
        # ETags should be different because parameters are different
        assert response1.headers["ETag"] != response2.headers["ETag"]

    async def test_etag_changes_with_different_last_updated(
        self, client: AsyncClient, monkeypatch
    ):
        """Test that ETag changes when last_updated timestamp changes"""
        # Reset global cache adapter before test
        import apps.api.di_analytics_v2 as di
        di._cache_adapter = None
        
        # Mock fusion service with different last_updated times
        service1 = Mock()
        service1.get_last_updated_at = AsyncMock(
            return_value=datetime(2025, 8, 31, 12, 0, 0, tzinfo=UTC)
        )
        service1.get_overview = AsyncMock(
            return_value={
                "posts": 10,
                "views": 1000,
                "avg_reach": 100.0,
                "err": None,
                "followers": 500,
                "period": {"from": "2025-08-30T00:00:00", "to": "2025-08-31T23:59:59"}
            }
        )

        service2 = Mock()
        service2.get_last_updated_at = AsyncMock(
            return_value=datetime(2025, 8, 31, 13, 0, 0, tzinfo=UTC)  # Different timestamp
        )
        service2.get_overview = AsyncMock(
            return_value={
                "posts": 10,
                "views": 1000,
                "avg_reach": 100.0,
                "err": None,
                "followers": 500,
                "period": {"from": "2025-08-30T00:00:00", "to": "2025-08-31T23:59:59"}
            }
        )

        # Mock cache
        cache = Mock()
        def mock_generate_cache_key(endpoint: str, params: dict, last_updated=None):
            """Mock cache key generation that mimics real behavior"""
            import hashlib
            import json
            from datetime import datetime
            
            print(f"DEBUG cache: endpoint={endpoint}, params={params}, last_updated={last_updated}")
            
            # Sort parameters for consistent key generation
            sorted_params = sorted(params.items())
            
            # Convert datetime objects to isoformat for consistency with router
            def datetime_serializer(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return str(obj)
            
            params_str = json.dumps(sorted_params, default=datetime_serializer)
            
            # Include last_updated in key for cache invalidation - THIS IS THE KEY CHANGE
            key_data = f"{endpoint}:{params_str}"
            if last_updated:
                if isinstance(last_updated, datetime):
                    key_data += f":{last_updated.isoformat()}"
                else:
                    key_data += f":{last_updated}"
            
            print(f"DEBUG cache: key_data={key_data}")
            
            # Create hash for shorter, consistent keys
            key_hash = hashlib.sha256(key_data.encode()).hexdigest()
            result = f"analytics_v2:{endpoint}:{key_hash}"
            print(f"DEBUG cache: result={result}")
            return result
        
        cache.generate_cache_key = Mock(side_effect=mock_generate_cache_key)
        cache.get_json = AsyncMock(return_value=None)  # No cache initially
        cache.set_json = AsyncMock()

        # Mock create_cache_adapter to return our mock cache instead of NoOpCache
        monkeypatch.setattr(
            "infra.cache.redis_cache.create_cache_adapter", lambda redis_client=None: cache
        )

        # First request
        monkeypatch.setattr(
            "apps.api.di_analytics_v2.get_analytics_fusion_service", lambda: service1
        )
        monkeypatch.setattr("apps.api.di_analytics_v2.get_cache", lambda: cache)

        response1 = await client.get(
            "/api/v2/analytics/channels/123/overview",
            params={"from": "2025-08-30T00:00:00Z", "to": "2025-08-31T23:59:59Z"},
        )

        # Second request with different last_updated
        monkeypatch.setattr(
            "apps.api.di_analytics_v2.get_analytics_fusion_service", lambda: service2
        )

        response2 = await client.get(
            "/api/v2/analytics/channels/123/overview",
            params={"from": "2025-08-30T00:00:00Z", "to": "2025-08-31T23:59:59Z"},
        )

        assert response1.status_code == 200
        assert response2.status_code == 200
        # ETags should be different because last_updated timestamps are different
        assert response1.headers["ETag"] != response2.headers["ETag"]

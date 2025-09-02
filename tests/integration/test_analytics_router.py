"""
Integration tests for Analytics Router API endpoints.

Tests cover FastAPI route handlers with mocked dependencies to achieve coverage
without requiring full database/external service setup.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Mock all the problematic imports first
with (
    patch("apps.bot.analytics.AdvancedDataProcessor"),
    patch("apps.bot.analytics.AIInsightsGenerator"),
    patch("apps.bot.analytics.DashboardFactory"),
    patch("apps.bot.analytics.PredictiveAnalyticsEngine"),
    patch("apps.bot.container.container"),
    patch("apps.bot.services.analytics_service.AnalyticsService"),
    patch("infra.db.repositories.analytics_repository.AsyncpgAnalyticsRepository"),
    patch("infra.db.repositories.channel_repository.AsyncpgChannelRepository"),
):
    from apps.api.routers.analytics_router import router as analytics_router


@pytest.fixture
def app():
    """Create FastAPI test application."""
    test_app = FastAPI()
    test_app.include_router(analytics_router)
    return test_app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_channel_repository():
    """Mock channel repository."""
    repo = AsyncMock()
    repo.get_channels.return_value = [
        MagicMock(
            id=1,
            name="Test Channel",
            telegram_id=12345,
            description="Test Description",
            created_at=datetime(2024, 1, 1),
            is_active=True,
        )
    ]
    repo.create_channel.return_value = MagicMock(
        id=1,
        name="New Channel",
        telegram_id=67890,
        description="New Description",
        created_at=datetime(2024, 1, 1),
        is_active=True,
    )
    repo.get_channel_by_id.return_value = MagicMock(
        id=1,
        name="Test Channel",
        telegram_id=12345,
        description="Test Description",
        created_at=datetime(2024, 1, 1),
        is_active=True,
    )
    return repo


@pytest.fixture
def mock_analytics_repository():
    """Mock analytics repository."""
    repo = AsyncMock()
    repo.get_metrics.return_value = [
        {
            "channel_id": 1,
            "date": "2024-01-01",
            "views": 1000,
            "subscribers": 500,
            "engagement_rate": 0.1,
        }
    ]
    return repo


class TestAnalyticsHealthEndpoints:
    """Test health and status endpoints."""

    def test_health_check(self, client):
        """Test analytics health check endpoint."""
        response = client.get("/analytics/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "analytics"
        assert data["version"] == "2.0.0"
        assert "timestamp" in data
        assert isinstance(data["modules"], list)
        assert len(data["modules"]) == 5

    def test_status_endpoint_success(self, client):
        """Test analytics status endpoint with successful import."""
        with patch("apps.bot.analytics.__all__", ["DataProcessor", "AIInsights"]):
            response = client.get("/analytics/status")

            assert response.status_code == 200
            data = response.json()
            assert data["module"] == "bot.analytics"
            assert data["version"] == "2.0.0"
            assert data["components"] == 2
            assert data["status"] == "operational"
            assert "timestamp" in data

    def test_status_endpoint_failure(self, client):
        """Test analytics status endpoint with import error."""
        with patch("apps.bot.analytics.__all__", side_effect=ImportError("Module not found")):
            response = client.get("/analytics/status")

            assert response.status_code == 500
            data = response.json()
            assert "Failed to get analytics status" in data["detail"]


class TestChannelEndpoints:
    """Test channel management endpoints."""

    @patch("apps.api.routers.analytics_router.get_channel_repository")
    def test_get_channels(self, mock_get_repo, client, mock_channel_repository):
        """Test get channels endpoint."""
        mock_get_repo.return_value = mock_channel_repository

        response = client.get("/analytics/channels")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Channel"
        assert data[0]["telegram_id"] == 12345
        mock_channel_repository.get_channels.assert_called_once_with(skip=0, limit=100)

    @patch("apps.api.routers.analytics_router.get_channel_repository")
    def test_get_channels_with_pagination(self, mock_get_repo, client, mock_channel_repository):
        """Test get channels with pagination parameters."""
        mock_get_repo.return_value = mock_channel_repository

        response = client.get("/analytics/channels?skip=10&limit=50")

        assert response.status_code == 200
        mock_channel_repository.get_channels.assert_called_once_with(skip=10, limit=50)

    @patch("apps.api.routers.analytics_router.get_channel_repository")
    def test_create_channel(self, mock_get_repo, client, mock_channel_repository):
        """Test create channel endpoint."""
        mock_get_repo.return_value = mock_channel_repository

        channel_data = {
            "name": "New Channel",
            "telegram_id": 67890,
            "description": "New Description",
        }

        response = client.post("/analytics/channels", json=channel_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Channel"
        assert data["telegram_id"] == 67890
        mock_channel_repository.create_channel.assert_called_once()

    @patch("apps.api.routers.analytics_router.get_channel_repository")
    def test_get_channel_by_id(self, mock_get_repo, client, mock_channel_repository):
        """Test get channel by ID endpoint."""
        mock_get_repo.return_value = mock_channel_repository

        response = client.get("/analytics/channels/1")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Test Channel"
        mock_channel_repository.get_channel_by_id.assert_called_once_with(1)

    @patch("apps.api.routers.analytics_router.get_channel_repository")
    def test_get_channel_by_id_not_found(self, mock_get_repo, client, mock_channel_repository):
        """Test get channel by ID when channel not found."""
        mock_channel_repository.get_channel_by_id.return_value = None
        mock_get_repo.return_value = mock_channel_repository

        response = client.get("/analytics/channels/999")

        assert response.status_code == 404
        data = response.json()
        assert "Channel not found" in data["detail"]


class TestMetricsEndpoints:
    """Test metrics-related endpoints."""

    @patch("apps.api.routers.analytics_router.get_analytics_repository")
    def test_get_metrics(self, mock_get_repo, client, mock_analytics_repository):
        """Test get global metrics endpoint."""
        mock_get_repo.return_value = mock_analytics_repository

        response = client.get("/analytics/metrics")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["channel_id"] == 1
        assert data[0]["views"] == 1000
        mock_analytics_repository.get_metrics.assert_called_once()

    @patch("apps.api.routers.analytics_router.get_analytics_repository")
    def test_get_channel_metrics(self, mock_get_repo, client, mock_analytics_repository):
        """Test get channel-specific metrics endpoint."""
        mock_get_repo.return_value = mock_analytics_repository

        response = client.get("/analytics/channels/1/metrics")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["channel_id"] == 1
        mock_analytics_repository.get_metrics.assert_called_once()

    @patch("apps.api.routers.analytics_router.get_analytics_repository")
    def test_get_metrics_with_date_range(self, mock_get_repo, client, mock_analytics_repository):
        """Test get metrics with date range parameters."""
        mock_get_repo.return_value = mock_analytics_repository

        start_date = "2024-01-01"
        end_date = "2024-01-31"

        response = client.get(f"/analytics/metrics?start_date={start_date}&end_date={end_date}")

        assert response.status_code == 200
        mock_analytics_repository.get_metrics.assert_called_once()


class TestDemoEndpoints:
    """Test demo data endpoints."""

    def test_demo_post_dynamics(self, client):
        """Test demo post dynamics endpoint."""
        response = client.get("/analytics/demo/post-dynamics")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 7  # One week of data

        # Verify data structure
        for item in data:
            assert "date" in item
            assert "views" in item
            assert "engagement_rate" in item
            assert isinstance(item["views"], int)
            assert isinstance(item["engagement_rate"], (int, float))

    def test_demo_top_posts(self, client):
        """Test demo top posts endpoint."""
        response = client.get("/analytics/demo/top-posts")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 5  # Top 5 posts

        # Verify data structure
        for item in data:
            assert "title" in item
            assert "views" in item
            assert "engagement_rate" in item
            assert "date" in item

    def test_demo_best_times(self, client):
        """Test demo best times endpoint."""
        response = client.get("/analytics/demo/best-times")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3  # Best 3 time slots

        # Verify data structure
        for item in data:
            assert "hour" in item
            assert "engagement_score" in item
            assert "confidence" in item
            assert 0 <= item["hour"] <= 23

    def test_demo_ai_recommendations(self, client):
        """Test demo AI recommendations endpoint."""
        response = client.get("/analytics/demo/ai-recommendations")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3  # 3 recommendations

        # Verify data structure
        for item in data:
            assert "recommendation" in item
            assert "impact" in item
            assert "priority" in item
            assert item["priority"] in ["high", "medium", "low"]


class TestDataProcessingEndpoints:
    """Test data processing endpoints."""

    @patch("apps.api.routers.analytics_router.get_analytics_service")
    def test_analyze_data(self, mock_get_service, client):
        """Test data analysis endpoint."""
        mock_service = AsyncMock()
        mock_service.analyze_data.return_value = {
            "status": "completed",
            "processed_records": 1000,
            "insights": ["High engagement on weekends"],
        }
        mock_get_service.return_value = mock_service

        request_data = {
            "channel_id": 1,
            "analysis_type": "engagement",
            "date_range": {"start": "2024-01-01", "end": "2024-01-31"},
        }

        response = client.post("/analytics/data-processing/analyze", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["processed_records"] == 1000
        mock_service.analyze_data.assert_called_once()

    @patch("apps.api.routers.analytics_router.get_analytics_service")
    def test_forecast_predictions(self, mock_get_service, client):
        """Test prediction forecast endpoint."""
        mock_service = AsyncMock()
        mock_service.generate_forecast.return_value = {
            "forecast_period": "30_days",
            "predicted_growth": 15.5,
            "confidence": 0.85,
            "predictions": [{"date": "2024-02-01", "value": 1500}],
        }
        mock_get_service.return_value = mock_service

        request_data = {"channel_id": 1, "metric": "subscribers", "forecast_days": 30}

        response = client.post("/analytics/predictions/forecast", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["forecast_period"] == "30_days"
        assert data["predicted_growth"] == 15.5
        mock_service.generate_forecast.assert_called_once()


class TestChannelInsightsEndpoints:
    """Test channel-specific insights endpoints."""

    @patch("apps.api.routers.analytics_router.get_analytics_service")
    def test_get_insights(self, mock_get_service, client):
        """Test get insights for channel."""
        mock_service = AsyncMock()
        mock_service.get_insights.return_value = {
            "channel_id": 1,
            "insights": [
                {"type": "growth", "value": "20% increase"},
                {"type": "engagement", "value": "High interaction rate"},
            ],
            "generated_at": datetime.now().isoformat(),
        }
        mock_get_service.return_value = mock_service

        response = client.get("/analytics/insights/1")

        assert response.status_code == 200
        data = response.json()
        assert data["channel_id"] == 1
        assert len(data["insights"]) == 2
        mock_service.get_insights.assert_called_once_with(1)

    @patch("apps.api.routers.analytics_router.get_analytics_service")
    def test_get_dashboard(self, mock_get_service, client):
        """Test get dashboard data for channel."""
        mock_service = AsyncMock()
        mock_service.get_dashboard_data.return_value = {
            "channel_id": 1,
            "summary": {"views": 5000, "subscribers": 1200},
            "charts": ["growth_chart", "engagement_chart"],
            "last_updated": datetime.now().isoformat(),
        }
        mock_get_service.return_value = mock_service

        response = client.get("/analytics/dashboard/1")

        assert response.status_code == 200
        data = response.json()
        assert data["channel_id"] == 1
        assert data["summary"]["views"] == 5000
        mock_service.get_dashboard_data.assert_called_once_with(1)

    @patch("apps.api.routers.analytics_router.get_analytics_service")
    def test_refresh_channel_data(self, mock_get_service, client):
        """Test refresh channel data endpoint."""
        mock_service = AsyncMock()
        mock_service.refresh_channel_data.return_value = {
            "status": "success",
            "message": "Data refreshed successfully",
            "last_refresh": datetime.now().isoformat(),
        }
        mock_get_service.return_value = mock_service

        response = client.post("/analytics/refresh/1")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        mock_service.refresh_channel_data.assert_called_once_with(1)

    @patch("apps.api.routers.analytics_router.get_analytics_service")
    def test_get_channel_summary(self, mock_get_service, client):
        """Test get channel summary endpoint."""
        mock_service = AsyncMock()
        mock_service.get_channel_summary.return_value = {
            "channel_id": 1,
            "total_views": 50000,
            "total_subscribers": 2500,
            "avg_engagement_rate": 0.125,
            "top_post": {"title": "Best Post", "views": 5000},
        }
        mock_get_service.return_value = mock_service

        response = client.get("/analytics/summary/1")

        assert response.status_code == 200
        data = response.json()
        assert data["channel_id"] == 1
        assert data["total_views"] == 50000
        mock_service.get_channel_summary.assert_called_once_with(1)


class TestErrorHandling:
    """Test error handling in analytics router."""

    @patch("apps.api.routers.analytics_router.get_channel_repository")
    def test_channel_repository_error(self, mock_get_repo, client):
        """Test handling of repository errors."""
        mock_repo = AsyncMock()
        mock_repo.get_channels.side_effect = Exception("Database connection failed")
        mock_get_repo.return_value = mock_repo

        response = client.get("/analytics/channels")

        assert response.status_code == 500

    @patch("apps.api.routers.analytics_router.get_analytics_service")
    def test_service_error(self, mock_get_service, client):
        """Test handling of service layer errors."""
        mock_service = AsyncMock()
        mock_service.get_insights.side_effect = Exception("Service unavailable")
        mock_get_service.return_value = mock_service

        response = client.get("/analytics/insights/1")

        # The exact error code depends on implementation
        assert response.status_code in [404, 500]

    def test_invalid_channel_id(self, client):
        """Test handling of invalid channel ID."""
        response = client.get("/analytics/channels/invalid")

        assert response.status_code == 422  # Validation error

    def test_invalid_json_payload(self, client):
        """Test handling of invalid JSON payloads."""
        response = client.post("/analytics/data-processing/analyze", json={"invalid": "data"})

        # Response depends on validation logic
        assert response.status_code in [400, 422, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

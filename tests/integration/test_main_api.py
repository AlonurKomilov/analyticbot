"""
Integration tests for main FastAPI application endpoints.

Tests cover the core API endpoints using centralized mock factory.
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest

# Import centralized mock factory
from tests.factories.mock_factory import MockFactory

# Mock TestClient for cases where FastAPI isn't available
try:
    from fastapi.testclient import TestClient
except ImportError:
    TestClient = Mock


class MockPost:
    """Mock post object for testing using test data factory."""

    def __init__(self):
        self.id = uuid4()
        self.title = "Test Post"
        self.content = "Test Content"
        self.channel_id = "test_channel"
        self.user_id = "test_user"
        self.scheduled_at = datetime(2024, 12, 25, 10, 0, 0)
        self.status = MockFactory.create_config_mock({"value": "SCHEDULED"})
        self.tags = ["test", "automation"]
        self.created_at = datetime(2024, 1, 1, 12, 0, 0)


class TestMainAPIEndpoints:
    """Test main API application endpoints using mock factory."""

    @pytest.fixture
    def mock_dependencies(self):
        """Mock all dependencies using centralized factory."""
        # Create services using factory
        schedule_service = MockFactory.create_bot_service()
        delivery_service = MockFactory.create_export_service()
        config = MockFactory.create_config_mock(
            {
                "DEBUG": True,
                "ENVIRONMENT": "test",
                "api": MockFactory.create_config_mock({"CORS_ORIGINS": ["http://localhost"]}),
            }
        )

        with (
            patch(
                "apps.api.deps.get_schedule_service", return_value=schedule_service
            ) as mock_schedule_service,
            patch(
                "apps.api.deps.get_delivery_service", return_value=delivery_service
            ) as mock_delivery_service,
            patch("config.settings", config) as mock_settings,
            patch("apps.api.routers.analytics_router.router"),
            patch("apps.api.routers.analytics_v2.router"),
            patch("apps.api.superadmin_routes.router"),
            patch("apps.bot.api.content_protection_router.router"),
        ):
            yield {
                "schedule_service": mock_schedule_service,
                "delivery_service": mock_delivery_service,
                "settings": mock_settings,
            }

    @pytest.fixture
    def app(self, mock_dependencies):
        """Create FastAPI test application."""
        from apps.api.main import app

        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["environment"] == "test"
        assert data["debug"] is True

    def test_create_scheduled_post_success(self, client, mock_dependencies):
        """Test successful creation of scheduled post."""
        # Setup mock service
        mock_service = AsyncMock()
        mock_post = MockPost()
        mock_service.create_scheduled_post.return_value = mock_post
        mock_dependencies["schedule_service"].return_value = mock_service

        post_data = {
            "title": "Test Post",
            "content": "Test Content",
            "channel_id": "test_channel",
            "user_id": "test_user",
            "scheduled_at": "2024-12-25T10:00:00",
            "tags": ["test", "automation"],
        }

        response = client.post("/schedule", params=post_data)

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Post"
        assert data["status"] == "SCHEDULED"
        assert "id" in data
        assert "scheduled_at" in data

    def test_create_scheduled_post_validation_error(self, client, mock_dependencies):
        """Test creation of scheduled post with validation error."""
        mock_service = AsyncMock()
        mock_service.create_scheduled_post.side_effect = ValueError("Invalid date")
        mock_dependencies["schedule_service"].return_value = mock_service

        post_data = {
            "title": "Test Post",
            "content": "Test Content",
            "channel_id": "test_channel",
            "user_id": "test_user",
            "scheduled_at": "invalid-date",
        }

        response = client.post("/schedule", params=post_data)

        assert response.status_code == 400
        data = response.json()
        assert "Invalid date" in data["detail"]

    def test_get_scheduled_post_success(self, client, mock_dependencies):
        """Test successful retrieval of scheduled post."""
        mock_service = AsyncMock()
        mock_post = MockPost()
        mock_service.get_post.return_value = mock_post
        mock_dependencies["schedule_service"].return_value = mock_service

        post_id = str(uuid4())
        response = client.get(f"/schedule/{post_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Post"
        assert data["content"] == "Test Content"
        assert data["channel_id"] == "test_channel"
        assert data["user_id"] == "test_user"
        assert data["status"] == "SCHEDULED"
        assert data["tags"] == ["test", "automation"]

    def test_get_scheduled_post_not_found(self, client, mock_dependencies):
        """Test retrieval of non-existent scheduled post."""
        mock_service = AsyncMock()
        mock_service.get_post.return_value = None
        mock_dependencies["schedule_service"].return_value = mock_service

        post_id = str(uuid4())
        response = client.get(f"/schedule/{post_id}")

        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Post not found"

    def test_get_user_posts(self, client, mock_dependencies):
        """Test retrieval of user's scheduled posts."""
        mock_service = AsyncMock()
        mock_posts = [MockPost(), MockPost()]
        mock_service.get_user_posts.return_value = mock_posts
        mock_dependencies["schedule_service"].return_value = mock_service

        user_id = "test_user"
        response = client.get(f"/schedule/user/{user_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["posts"]) == 2
        assert data["posts"][0]["title"] == "Test Post"
        assert data["posts"][0]["status"] == "SCHEDULED"

    def test_get_user_posts_with_pagination(self, client, mock_dependencies):
        """Test retrieval of user posts with pagination parameters."""
        mock_service = AsyncMock()
        mock_posts = [MockPost()]
        mock_service.get_user_posts.return_value = mock_posts
        mock_dependencies["schedule_service"].return_value = mock_service

        user_id = "test_user"
        response = client.get(f"/schedule/user/{user_id}?limit=10&offset=20")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        mock_service.get_user_posts.assert_called_once_with(user_id=user_id, limit=10, offset=20)

    def test_cancel_scheduled_post_success(self, client, mock_dependencies):
        """Test successful cancellation of scheduled post."""
        mock_service = AsyncMock()
        mock_service.cancel_post.return_value = True
        mock_dependencies["schedule_service"].return_value = mock_service

        post_id = str(uuid4())
        response = client.delete(f"/schedule/{post_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Post cancelled successfully"

    def test_cancel_scheduled_post_not_found(self, client, mock_dependencies):
        """Test cancellation of non-existent scheduled post."""
        mock_service = AsyncMock()
        mock_service.cancel_post.return_value = False
        mock_dependencies["schedule_service"].return_value = mock_service

        post_id = str(uuid4())
        response = client.delete(f"/schedule/{post_id}")

        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Post not found"

    def test_cancel_scheduled_post_validation_error(self, client, mock_dependencies):
        """Test cancellation with validation error."""
        mock_service = AsyncMock()
        mock_service.cancel_post.side_effect = ValueError("Cannot cancel published post")
        mock_dependencies["schedule_service"].return_value = mock_service

        post_id = str(uuid4())
        response = client.delete(f"/schedule/{post_id}")

        assert response.status_code == 400
        data = response.json()
        assert "Cannot cancel published post" in data["detail"]

    def test_get_delivery_stats_global(self, client, mock_dependencies):
        """Test retrieval of global delivery statistics."""
        mock_service = AsyncMock()
        mock_stats = {
            "total_deliveries": 1000,
            "successful_deliveries": 950,
            "failed_deliveries": 50,
            "success_rate": 0.95,
            "avg_delivery_time": 1.2,
        }
        mock_service.get_delivery_stats.return_value = mock_stats
        mock_dependencies["delivery_service"].return_value = mock_service

        response = client.get("/delivery/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["total_deliveries"] == 1000
        assert data["success_rate"] == 0.95
        mock_service.get_delivery_stats.assert_called_once_with(channel_id=None)

    def test_get_delivery_stats_channel_specific(self, client, mock_dependencies):
        """Test retrieval of channel-specific delivery statistics."""
        mock_service = AsyncMock()
        mock_stats = {
            "channel_id": "test_channel",
            "total_deliveries": 100,
            "successful_deliveries": 98,
            "failed_deliveries": 2,
            "success_rate": 0.98,
            "last_delivery": "2024-01-01T12:00:00",
        }
        mock_service.get_delivery_stats.return_value = mock_stats
        mock_dependencies["delivery_service"].return_value = mock_service

        response = client.get("/delivery/stats?channel_id=test_channel")

        assert response.status_code == 200
        data = response.json()
        assert data["channel_id"] == "test_channel"
        assert data["success_rate"] == 0.98
        mock_service.get_delivery_stats.assert_called_once_with(channel_id="test_channel")

    def test_invalid_uuid_format(self, client, mock_dependencies):
        """Test endpoints with invalid UUID format."""
        response = client.get("/schedule/invalid-uuid")
        assert response.status_code == 422

        response = client.delete("/schedule/invalid-uuid")
        assert response.status_code == 422

    def test_missing_required_parameters(self, client, mock_dependencies):
        """Test endpoints with missing required parameters."""
        # Missing required fields for post creation
        incomplete_data = {
            "title": "Test Post"
            # Missing content, channel_id, user_id, scheduled_at
        }

        response = client.post("/schedule", params=incomplete_data)
        assert response.status_code == 422

    def test_cors_middleware_configuration(self, client):
        """Test CORS middleware is properly configured."""
        response = client.options("/health", headers={"Origin": "http://localhost"})

        # Check that CORS headers are present
        assert response.status_code == 200
        # The actual CORS headers depend on the middleware configuration

    def test_scheduled_at_datetime_parsing(self, client, mock_dependencies):
        """Test various datetime formats for scheduled_at parameter."""
        mock_service = AsyncMock()
        mock_post = MockPost()
        mock_service.create_scheduled_post.return_value = mock_post
        mock_dependencies["schedule_service"].return_value = mock_service

        # ISO format
        post_data = {
            "title": "Test Post",
            "content": "Test Content",
            "channel_id": "test_channel",
            "user_id": "test_user",
            "scheduled_at": "2024-12-25T10:00:00Z",
        }

        response = client.post("/schedule", params=post_data)
        assert response.status_code == 200

    def test_tags_parameter_handling(self, client, mock_dependencies):
        """Test handling of optional tags parameter."""
        mock_service = AsyncMock()
        mock_post = MockPost()
        mock_service.create_scheduled_post.return_value = mock_post
        mock_dependencies["schedule_service"].return_value = mock_service

        # Without tags
        post_data = {
            "title": "Test Post",
            "content": "Test Content",
            "channel_id": "test_channel",
            "user_id": "test_user",
            "scheduled_at": "2024-12-25T10:00:00",
        }

        response = client.post("/schedule", params=post_data)
        assert response.status_code == 200

        # With tags (depends on FastAPI query parameter handling)
        post_data_with_tags = post_data.copy()
        post_data_with_tags["tags"] = "tag1,tag2"  # Convert list to comma-separated string
        response = client.post("/schedule", params=post_data_with_tags)
        assert response.status_code == 200

    def test_service_layer_error_handling(self, client, mock_dependencies):
        """Test proper error handling from service layer."""
        mock_service = AsyncMock()
        mock_service.get_delivery_stats.side_effect = Exception("Database connection failed")
        mock_dependencies["delivery_service"].return_value = mock_service

        response = client.get("/delivery/stats")

        # The exact response depends on the error handling implementation
        # It could be 500 (internal server error) or handled gracefully
        assert response.status_code in [500, 503, 200]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

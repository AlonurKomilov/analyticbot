"""
Centralized Mock Factory for Python Tests
Provides consistent, reusable mocks for all test files
"""

from datetime import datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, Mock


class MockFactory:
    """
    Centralized factory for creating consistent test mocks
    Eliminates duplicate mock creation across test files
    """

    @staticmethod
    def create_analytics_service(
        analytics_data: dict[str, Any] | None = None,
        channels_data: list[dict] | None = None,
    ) -> AsyncMock:
        """
        Create consistently configured analytics service mock

        Args:
            analytics_data: Custom analytics data to return
            channels_data: Custom channels data to return

        Returns:
            AsyncMock: Configured analytics service mock
        """
        mock_service = AsyncMock()

        # Default analytics data
        default_analytics = {
            "channel_id": "test_channel",
            "total_views": 15420,
            "total_posts": 145,
            "avg_engagement": 5.2,
            "growth_rate": 12.5,
            "top_posts": [
                {"id": 1, "title": "Top Post", "views": 2500, "engagement": 8.5},
                {"id": 2, "title": "Second Post", "views": 1800, "engagement": 6.2},
            ],
            "engagement_metrics": {"reactions": 4.2, "comments": 2.1, "shares": 1.8},
            "generated_at": datetime.now().isoformat(),
        }

        # Default channels data
        default_channels = [
            {"id": 1, "name": "Test Channel 1", "member_count": 1250, "active": True},
            {"id": 2, "name": "Test Channel 2", "member_count": 980, "active": True},
        ]

        # Configure mock responses
        mock_service.get_analytics.return_value = analytics_data or default_analytics
        mock_service.get_channels.return_value = channels_data or default_channels
        mock_service.process_data.return_value = True
        mock_service.update_analytics.return_value = {
            "success": True,
            "updated_at": datetime.now().isoformat(),
        }

        return mock_service

    @staticmethod
    def create_db_pool(query_results: dict[str, Any] | None = None) -> AsyncMock:
        """
        Create consistently configured database pool mock

        Args:
            query_results: Custom query results to return

        Returns:
            AsyncMock: Configured database pool mock
        """
        pool = AsyncMock()

        # Default query results
        default_results = {
            "fetchrow": {"id": 1, "name": "test_record", "created_at": datetime.now()},
            "fetchval": 42,
            "fetch": [{"id": 1, "value": "test1"}, {"id": 2, "value": "test2"}],
        }

        results = query_results or default_results

        # Configure mock responses
        pool.fetchrow.return_value = results.get("fetchrow")
        pool.fetchval.return_value = results.get("fetchval")
        pool.fetch.return_value = results.get("fetch", [])
        pool.execute.return_value = None
        pool.executemany.return_value = None

        return pool

    @staticmethod
    def create_channel_repository(channels: list[dict] | None = None) -> AsyncMock:
        """
        Create channel repository mock with default data

        Args:
            channels: Custom channels data

        Returns:
            AsyncMock: Configured channel repository mock
        """
        mock_repo = AsyncMock()

        default_channels = [
            {
                "id": 1,
                "name": "Test Channel",
                "member_count": 1000,
                "description": "Test channel description",
                "active": True,
                "created_at": datetime.now() - timedelta(days=30),
            },
            {
                "id": 2,
                "name": "Demo Channel",
                "member_count": 750,
                "description": "Demo channel for testing",
                "active": True,
                "created_at": datetime.now() - timedelta(days=15),
            },
        ]

        channel_data = channels or default_channels

        # Configure mock responses
        mock_repo.get_all.return_value = channel_data
        mock_repo.get_by_id.return_value = channel_data[0] if channel_data else None
        mock_repo.create.return_value = channel_data[0] if channel_data else None
        mock_repo.update.return_value = channel_data[0] if channel_data else None
        mock_repo.delete.return_value = True
        mock_repo.count.return_value = len(channel_data)

        return mock_repo

    @staticmethod
    def create_bot_service(commands_data: list[dict] | None = None) -> AsyncMock:
        """
        Create bot service mock with command responses

        Args:
            commands_data: Custom command responses

        Returns:
            AsyncMock: Configured bot service mock
        """
        mock_service = AsyncMock()

        default_commands = [
            {"command": "/start", "response": "Bot started successfully"},
            {"command": "/analytics", "response": "Analytics data retrieved"},
            {
                "command": "/help",
                "response": "Available commands: /start, /analytics, /help",
            },
        ]

        commands = commands_data or default_commands

        # Configure mock responses
        mock_service.process_command.return_value = commands[0]["response"]
        mock_service.get_available_commands.return_value = [cmd["command"] for cmd in commands]
        mock_service.is_running.return_value = True
        mock_service.start.return_value = True
        mock_service.stop.return_value = True

        return mock_service

    @staticmethod
    def create_export_service(export_data: dict[str, Any] | None = None) -> AsyncMock:
        """
        Create export service mock

        Args:
            export_data: Custom export results

        Returns:
            AsyncMock: Configured export service mock
        """
        mock_service = AsyncMock()

        default_export = {
            "export_id": "test_export_123",
            "status": "completed",
            "file_path": "/tmp/test_export.csv",
            "file_size": 1024,
            "created_at": datetime.now().isoformat(),
            "row_count": 100,
        }

        export_result = export_data or default_export

        # Configure mock responses
        mock_service.create_export.return_value = export_result
        mock_service.get_export_status.return_value = export_result["status"]
        mock_service.download_export.return_value = b"test,data,content"
        mock_service.delete_export.return_value = True

        return mock_service

    @staticmethod
    def create_payment_service(payment_data: dict[str, Any] | None = None) -> AsyncMock:
        """
        Create payment service mock

        Args:
            payment_data: Custom payment data

        Returns:
            AsyncMock: Configured payment service mock
        """
        mock_service = AsyncMock()

        default_payment = {
            "payment_id": "pay_test_123",
            "amount": 1000,  # in cents
            "currency": "USD",
            "status": "succeeded",
            "customer_id": "cust_test_123",
            "created_at": datetime.now().isoformat(),
        }

        payment_result = payment_data or default_payment

        # Configure mock responses
        mock_service.create_payment.return_value = payment_result
        mock_service.get_payment.return_value = payment_result
        mock_service.process_payment.return_value = {
            "success": True,
            "payment_id": payment_result["payment_id"],
        }
        mock_service.refund_payment.return_value = {
            "success": True,
            "refund_id": "ref_test_123",
        }

        return mock_service

    @staticmethod
    def create_dashboard_service(
        dashboard_data: dict[str, Any] | None = None,
    ) -> AsyncMock:
        """
        Create dashboard service mock

        Args:
            dashboard_data: Custom dashboard data

        Returns:
            AsyncMock: Configured dashboard service mock
        """
        mock_service = AsyncMock()

        default_dashboard = {
            "metrics": {
                "total_users": 1250,
                "active_channels": 45,
                "total_posts": 8900,
                "avg_engagement": 4.7,
            },
            "recent_activity": [
                {"action": "post_created", "timestamp": datetime.now().isoformat()},
                {
                    "action": "user_joined",
                    "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(),
                },
            ],
            "top_channels": [
                {"name": "Channel A", "members": 500},
                {"name": "Channel B", "members": 350},
            ],
        }

        dashboard_result = dashboard_data or default_dashboard

        # Configure mock responses
        mock_service.get_dashboard_data.return_value = dashboard_result
        mock_service.get_metrics.return_value = dashboard_result["metrics"]
        mock_service.get_recent_activity.return_value = dashboard_result["recent_activity"]
        mock_service.refresh_data.return_value = True

        return mock_service

    @staticmethod
    def create_http_client(responses: dict[str, Any] | None = None) -> Mock:
        """
        Create HTTP client mock for external API calls

        Args:
            responses: Custom HTTP responses by URL pattern

        Returns:
            Mock: Configured HTTP client mock
        """
        mock_client = Mock()

        default_responses = {
            "get": {"status_code": 200, "json": {"success": True, "data": []}},
            "post": {"status_code": 201, "json": {"success": True, "id": 123}},
            "put": {"status_code": 200, "json": {"success": True, "updated": True}},
            "delete": {"status_code": 204, "json": {}},
        }

        response_data = responses or default_responses

        # Create response mock
        response_mock = Mock()
        response_mock.status_code = response_data.get("get", {}).get("status_code", 200)
        response_mock.json.return_value = response_data.get("get", {}).get("json", {})
        response_mock.text = '{"success": true}'
        response_mock.headers = {"content-type": "application/json"}

        # Configure HTTP methods
        mock_client.get.return_value = response_mock
        mock_client.post.return_value = response_mock
        mock_client.put.return_value = response_mock
        mock_client.delete.return_value = response_mock

        return mock_client

    @staticmethod
    def create_config_mock(config_values: dict[str, Any] | None = None) -> Mock:
        """
        Create configuration mock

        Args:
            config_values: Custom configuration values

        Returns:
            Mock: Configured config mock
        """
        mock_config = Mock()

        default_config = {
            "database_url": "postgresql://test:test@localhost/test_db",
            "redis_url": "redis://localhost:6379",
            "api_key": "test_api_key_123",
            "debug": True,
            "log_level": "INFO",
            "max_connections": 10,
        }

        config_data = config_values or default_config

        # Configure as attribute access
        for key, value in config_data.items():
            setattr(mock_config, key, value)

        return mock_config


class TestDataFactory:
    """
    Factory for creating test data objects
    Complements MockFactory with actual data structures
    """

    @staticmethod
    def create_analytics_data(
        channel_id: str = "test_channel", days_back: int = 30
    ) -> dict[str, Any]:
        """Create realistic analytics test data"""
        base_date = datetime.now() - timedelta(days=days_back)

        return {
            "channel_id": channel_id,
            "period": f"{days_back}d",
            "total_views": 15420,
            "total_posts": 145,
            "avg_engagement": 5.2,
            "growth_rate": 12.5,
            "timeline": [
                {
                    "date": (base_date + timedelta(days=i)).strftime("%Y-%m-%d"),
                    "views": 400 + (i * 10),
                    "posts": 3 + (i % 7),
                    "engagement": 4.0 + (i * 0.1),
                }
                for i in range(days_back)
            ],
            "top_posts": [
                {
                    "id": i,
                    "title": f"Test Post {i}",
                    "views": 2500 - (i * 200),
                    "engagement": 8.5 - (i * 0.5),
                    "created_at": (base_date + timedelta(days=i)).isoformat(),
                }
                for i in range(1, 6)
            ],
            "generated_at": datetime.now().isoformat(),
        }

    @staticmethod
    def create_user_data(user_id: int = 1, username: str = "testuser") -> dict[str, Any]:
        """Create test user data"""
        return {
            "id": user_id,
            "username": username,
            "email": f"{username}@test.com",
            "created_at": datetime.now() - timedelta(days=30),
            "last_active": datetime.now() - timedelta(hours=2),
            "is_active": True,
            "role": "user",
            "preferences": {"notifications": True, "theme": "light", "language": "en"},
        }

    @staticmethod
    def create_channel_data(channel_id: int = 1, name: str = "test_channel") -> dict[str, Any]:
        """Create test channel data"""
        return {
            "id": channel_id,
            "name": name,
            "description": f"Test channel {name}",
            "member_count": 1000,
            "active": True,
            "created_at": datetime.now() - timedelta(days=60),
            "updated_at": datetime.now() - timedelta(days=1),
            "settings": {"public": True, "auto_analytics": True, "retention_days": 90},
        }

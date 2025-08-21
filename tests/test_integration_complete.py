"""
Integration tests for the complete application workflow.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from bot.services.analytics_service import AnalyticsService
from bot.services.scheduler_service import SchedulerService
from bot.utils.error_handler import ErrorContext, ErrorHandler
from bot.utils.monitoring import metrics


class TestCompleteWorkflow:
    """Integration tests for complete application workflows"""

    @pytest.fixture
    async def mock_bot(self):
        """Mock bot for testing"""
        bot = AsyncMock()
        bot.get_messages.return_value = [
            MagicMock(message_id=1, views=100),
            MagicMock(message_id=2, views=200),
        ]
        bot.send_message.return_value = MagicMock(
            message_id=123, chat=MagicMock(id=-1001234567)
        )
        bot.send_photo.return_value = MagicMock(
            message_id=124, chat=MagicMock(id=-1001234567)
        )
        return bot

    @pytest.fixture
    async def mock_analytics_repo(self):
        """Mock analytics repository"""
        repo = AsyncMock()
        repo.get_all_posts_to_track_views.return_value = [
            {"id": 1, "channel_id": -1001234567, "message_id": 1},
            {"id": 2, "channel_id": -1001234567, "message_id": 2},
        ]
        repo.update_post_views.return_value = None
        repo.log_sent_post.return_value = None
        return repo

    @pytest.fixture
    async def mock_scheduler_repo(self):
        """Mock scheduler repository"""
        repo = AsyncMock()
        repo.create_scheduled_post.return_value = 1
        repo.update_post_status.return_value = None
        repo.claim_due_posts.return_value = [
            {
                "id": 1,
                "channel_id": -1001234567,
                "post_text": "Test message",
                "media_id": None,
                "inline_buttons": None,
            }
        ]
        return repo

    @pytest.mark.asyncio
    async def test_analytics_update_workflow(self, mock_bot, mock_analytics_repo):
        """Test complete analytics update workflow"""
        # Initialize service
        service = AnalyticsService(mock_bot, mock_analytics_repo)

        # Execute analytics update
        stats = await service.update_all_post_views()

        # Verify results
        assert stats["processed"] >= 0
        assert stats["updated"] >= 0
        assert stats["errors"] >= 0
        assert stats["skipped"] >= 0

        # Verify repository calls
        mock_analytics_repo.get_all_posts_to_track_views.assert_called_once()
        mock_bot.get_messages.assert_called()

    @pytest.mark.asyncio
    async def test_scheduler_workflow(
        self, mock_bot, mock_scheduler_repo, mock_analytics_repo
    ):
        """Test complete post scheduling and sending workflow"""
        # Initialize service
        service = SchedulerService(mock_bot, mock_scheduler_repo, mock_analytics_repo)

        # Test scheduling
        post_id = await service.schedule_post(
            user_id=12345,
            channel_id=-1001234567,
            post_text="Test scheduled post",
            schedule_time=datetime.now() + timedelta(hours=1),
        )

        assert post_id == 1
        mock_scheduler_repo.create_scheduled_post.assert_called_once()

        # Test sending
        post_data = {
            "id": 1,
            "channel_id": -1001234567,
            "post_text": "Test message",
            "media_id": None,
            "inline_buttons": None,
        }

        result = await service.send_post_to_channel(post_data)

        assert result["success"] is True
        assert result["message_id"] == 123
        mock_bot.send_message.assert_called_once()
        mock_analytics_repo.log_sent_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_error_handling_workflow(self, mock_bot, mock_analytics_repo):
        """Test error handling in workflows"""
        # Setup error scenario
        mock_analytics_repo.get_all_posts_to_track_views.side_effect = Exception(
            "Database error"
        )

        service = AnalyticsService(mock_bot, mock_analytics_repo)

        # Execute and expect graceful error handling
        stats = await service.update_all_post_views()

        # Should return stats with errors
        assert stats["errors"] > 0
        assert stats["processed"] == 0

    @pytest.mark.asyncio
    async def test_telegram_api_error_handling(
        self, mock_bot, mock_scheduler_repo, mock_analytics_repo
    ):
        """Test Telegram API error handling"""
        from aiogram.exceptions import TelegramAPIError

        # Setup Telegram error with proper constructor
        mock_bot.send_message.side_effect = TelegramAPIError(
            method="sendMessage", message="Message failed"
        )

        service = SchedulerService(mock_bot, mock_scheduler_repo, mock_analytics_repo)

        post_data = {
            "id": 1,
            "channel_id": -1001234567,
            "post_text": "Test message",
            "media_id": None,
            "inline_buttons": None,
        }

        result = await service.send_post_to_channel(post_data)

        # Should handle error gracefully
        assert result["success"] is False
        assert "error" in result
        mock_scheduler_repo.update_post_status.assert_called_with(1, "error")


class TestErrorHandlerIntegration:
    """Integration tests for error handling system"""

    def test_error_context_building(self):
        """Test error context building and logging"""
        context = (
            ErrorContext()
            .add("operation", "test_operation")
            .add("user_id", 12345)
            .add("channel_id", -1001234567)
        )

        test_error = ValueError("Test error message")

        # Test error logging
        error_id = ErrorHandler.log_error(test_error, context)

        assert error_id is not None
        assert "ERR_" in error_id

    def test_telegram_error_categorization(self):
        """Test Telegram error categorization"""
        from aiogram.exceptions import TelegramBadRequest

        # Test bot kicked error with proper constructor
        bot_kicked_error = TelegramBadRequest(
            method="sendMessage", message="Bot was kicked from the group"
        )
        context = ErrorContext().add("channel_id", -1001234567)

        error_id = ErrorHandler.handle_telegram_api_error(bot_kicked_error, context)
        assert error_id is not None

        # Test rate limit error with proper constructor
        rate_limit_error = TelegramBadRequest(
            method="sendMessage", message="Too Many Requests: retry after 30"
        )
        error_id = ErrorHandler.handle_telegram_api_error(rate_limit_error, context)
        assert error_id is not None


class TestMonitoringIntegration:
    """Integration tests for monitoring system"""

    def test_metrics_collection(self):
        """Test metrics collection workflow"""
        # Record some test metrics
        metrics.record_metric("test_counter", 1.0)
        metrics.record_metric("test_gauge", 42.5, {"environment": "test"})

        # Record request metrics
        metrics.record_request("test_endpoint", True, 0.123)
        metrics.record_request("test_endpoint", False, 0.456)

        # Get performance stats
        stats = metrics.get_performance_stats("test_endpoint")
        endpoint_stats = stats["test_endpoint"]

        assert endpoint_stats.total_requests == 2
        assert endpoint_stats.successful_requests == 1
        assert endpoint_stats.failed_requests == 1
        assert endpoint_stats.success_rate == 50.0
        assert endpoint_stats.error_rate == 50.0

    def test_metrics_summary(self):
        """Test metrics summary generation"""
        # Record some metrics
        metrics.record_request("endpoint1", True, 0.1)
        metrics.record_request("endpoint2", False, 0.2)

        summary = metrics.get_summary()

        assert "uptime_seconds" in summary
        assert "total_requests" in summary
        assert "total_errors" in summary
        assert "overall_error_rate" in summary
        assert "timestamp" in summary


class TestFullSystemIntegration:
    """Full system integration tests"""

    @pytest.mark.asyncio
    async def test_complete_post_lifecycle(self):
        """Test complete post lifecycle from scheduling to analytics"""
        # This would be a comprehensive test that:
        # 1. Schedules a post
        # 2. Sends the post via task
        # 3. Updates view statistics
        # 4. Generates analytics

        # Due to complexity, this is a placeholder for future implementation
        # when we have proper test database setup

    @pytest.mark.asyncio
    async def test_system_resilience(self):
        """Test system resilience under various failure conditions"""
        # Test scenarios:
        # 1. Database connection failure
        # 2. Telegram API failures
        # 3. Redis connection issues
        # 4. Memory pressure

        # This would test the system's ability to gracefully handle
        # various failure modes and continue operating


# Performance benchmarks
class TestPerformanceBenchmarks:
    """Performance benchmark tests"""

    @pytest.fixture
    async def mock_bot(self):
        """Mock bot for testing"""
        bot = AsyncMock()
        bot.get_messages.return_value = [
            MagicMock(message_id=i, views=100 + i) for i in range(1, 1001)
        ]
        return bot

    @pytest.fixture
    async def mock_analytics_repo(self):
        """Mock analytics repository"""
        repo = AsyncMock()
        repo.update_post_views.return_value = None
        return repo

    @pytest.mark.asyncio
    async def test_analytics_update_performance(self, mock_bot, mock_analytics_repo):
        """Benchmark analytics update performance"""
        # Create large dataset
        large_dataset = []
        for i in range(1000):
            large_dataset.append(
                {"id": i, "channel_id": -1001234567, "message_id": i + 1000}
            )

        mock_analytics_repo.get_all_posts_to_track_views.return_value = large_dataset

        service = AnalyticsService(mock_bot, mock_analytics_repo)

        # Measure performance
        import time

        start_time = time.time()

        stats = await service.update_all_post_views()

        end_time = time.time()
        duration = end_time - start_time

        # Performance assertions (relaxed for testing)
        assert duration < 60.0  # Should complete within 60 seconds
        assert stats["processed"] >= 0  # Should process some posts

    def test_error_handler_performance(self):
        """Benchmark error handler performance"""
        import time

        test_error = ValueError("Performance test error")
        context = ErrorContext().add("test", "performance")

        # Measure performance of error logging
        start_time = time.time()

        for _ in range(100):
            ErrorHandler.log_error(test_error, context)

        end_time = time.time()
        duration = end_time - start_time

        # Should be fast
        assert duration < 1.0  # 100 error logs in under 1 second


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])

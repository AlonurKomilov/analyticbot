"""
Tests for Telegram Alert Delivery Service
==========================================

Tests alert formatting, delivery, retry logic, and error handling.
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from infra.adapters.telegram_alert_delivery import TelegramAlertDeliveryService


class TestTelegramAlertDeliveryService:
    """Test cases for TelegramAlertDeliveryService"""

    @pytest.fixture
    def mock_bot(self):
        """Create mock bot client"""
        bot = AsyncMock()
        bot.send_message = AsyncMock()

        # Mock successful message send
        mock_result = Mock()
        mock_result.message_id = 12345
        bot.send_message.return_value = mock_result

        return bot

    @pytest.fixture
    def delivery_service(self, mock_bot):
        """Create delivery service with mock bot"""
        return TelegramAlertDeliveryService(mock_bot)

    @pytest.fixture
    def spike_alert_data(self):
        """Sample spike alert data"""
        return {
            "alert_type": "spike",
            "channel_name": "Test Channel",
            "channel_id": 123456,
            "current_value": 500,
            "baseline": 100,
            "increase_pct": 400.0,
            "timestamp": datetime(2025, 10, 20, 12, 0, 0),
            "recommended_action": "Check for viral content",
        }

    @pytest.fixture
    def quiet_alert_data(self):
        """Sample quiet alert data"""
        return {
            "alert_type": "quiet",
            "channel_name": "Silent Channel",
            "channel_id": 789012,
            "current_value": 10,
            "baseline": 100,
            "decrease_pct": 90.0,
            "timestamp": datetime(2025, 10, 20, 14, 30, 0),
        }

    @pytest.fixture
    def growth_alert_data(self):
        """Sample growth alert data"""
        return {
            "alert_type": "growth",
            "channel_name": "Growing Channel",
            "channel_id": 345678,
            "milestone": "10,000 subscribers",
            "current_count": 10000,
            "previous_count": 9500,
            "timestamp": datetime(2025, 10, 20, 16, 15, 0),
        }

    async def test_send_alert_success(self, delivery_service, mock_bot, spike_alert_data):
        """Test successful alert delivery"""
        chat_id = 987654

        result = await delivery_service.send_alert(chat_id, spike_alert_data, max_retries=1)

        assert result["status"] == "sent"
        assert result["message_id"] == 12345
        assert result["chat_id"] == chat_id
        assert result["attempts"] == 1

        mock_bot.send_message.assert_called_once()
        call_args = mock_bot.send_message.call_args
        assert call_args.kwargs["chat_id"] == chat_id
        assert "SPIKE" in call_args.kwargs["text"]
        assert "Test Channel" in call_args.kwargs["text"]

    async def test_send_alert_with_retries(self, delivery_service, mock_bot, spike_alert_data):
        """Test alert delivery with retries on failure"""
        chat_id = 987654

        # First call fails, second succeeds
        mock_bot.send_message.side_effect = [
            Exception("Network error"),
            Mock(message_id=12345),
        ]

        with patch("asyncio.sleep", new_callable=AsyncMock):  # Speed up test
            result = await delivery_service.send_alert(chat_id, spike_alert_data, max_retries=2)

        assert result["status"] == "sent"
        assert result["attempts"] == 2
        assert mock_bot.send_message.call_count == 2

    async def test_send_alert_max_retries_exceeded(
        self, delivery_service, mock_bot, spike_alert_data
    ):
        """Test alert delivery fails after max retries"""
        chat_id = 987654

        # All calls fail
        mock_bot.send_message.side_effect = Exception("Persistent error")

        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await delivery_service.send_alert(chat_id, spike_alert_data, max_retries=2)

        assert result["status"] == "failed"
        assert "Persistent error" in result["error"]
        assert result["attempts"] == 3  # Initial + 2 retries
        assert mock_bot.send_message.call_count == 3

    async def test_send_alert_without_bot(self, spike_alert_data):
        """Test alert delivery when bot is not available"""
        delivery_service = TelegramAlertDeliveryService(None)
        chat_id = 987654

        result = await delivery_service.send_alert(chat_id, spike_alert_data)

        assert result["status"] == "failed"
        assert "Bot client not initialized" in result["error"]

    def test_format_spike_alert_message(self, delivery_service, spike_alert_data):
        """Test spike alert message formatting"""
        message = delivery_service._format_alert_message(spike_alert_data)

        assert "🚀" in message  # Spike emoji
        assert "ALERT: SPIKE" in message
        assert "Test Channel" in message
        assert "123456" in message
        assert "500" in message
        assert "100" in message
        assert "+400.0%" in message
        assert "2025-10-20 12:00:00 UTC" in message
        assert "Check for viral content" in message

    def test_format_quiet_alert_message(self, delivery_service, quiet_alert_data):
        """Test quiet alert message formatting"""
        message = delivery_service._format_alert_message(quiet_alert_data)

        assert "😴" in message  # Quiet emoji
        assert "ALERT: QUIET" in message
        assert "Silent Channel" in message
        assert "Unusual low activity" in message
        assert "10" in message
        assert "100" in message
        assert "-90.0%" in message

    def test_format_growth_alert_message(self, delivery_service, growth_alert_data):
        """Test growth alert message formatting"""
        message = delivery_service._format_alert_message(growth_alert_data)

        assert "📈" in message  # Growth emoji
        assert "ALERT: GROWTH" in message
        assert "Growing Channel" in message
        assert "Growth milestone reached" in message
        assert "10,000 subscribers" in message
        assert "10000" in message
        assert "9500" in message

    def test_format_alert_with_html_escaping(self, delivery_service):
        """Test alert formatting handles special characters"""
        alert_data = {
            "alert_type": "spike",
            "channel_name": "Test & <Special> Channel",
            "channel_id": 123,
            "current_value": 100,
            "baseline": 50,
            "increase_pct": 100.0,
            "timestamp": datetime(2025, 10, 20, 12, 0, 0),
        }

        message = delivery_service._format_alert_message(alert_data)

        # Message should still be generated (HTML entities handled by Telegram)
        assert "Test & <Special> Channel" in message
        assert "ALERT: SPIKE" in message

    async def test_send_test_alert(self, delivery_service, mock_bot):
        """Test sending test alert"""
        chat_id = 987654

        result = await delivery_service.send_test_alert(chat_id)

        assert result["status"] == "sent"
        assert result["chat_id"] == chat_id

        mock_bot.send_message.assert_called_once()
        call_args = mock_bot.send_message.call_args
        assert "Test Channel" in call_args.kwargs["text"]
        assert "SPIKE" in call_args.kwargs["text"]

    def test_retry_delays_exponential_backoff(self, delivery_service):
        """Test retry delays follow exponential-ish backoff"""
        delays = delivery_service._retry_delays

        assert len(delays) >= 3
        assert delays[0] < delays[1] < delays[2]
        assert delays[-1] >= 30  # Final delay should be substantial

    async def test_message_formatting_with_string_timestamp(self, delivery_service):
        """Test alert formatting handles string timestamps"""
        alert_data = {
            "alert_type": "spike",
            "channel_name": "Test",
            "channel_id": 123,
            "current_value": 100,
            "baseline": 50,
            "increase_pct": 100.0,
            "timestamp": "2025-10-20 15:30:00",
        }

        message = delivery_service._format_alert_message(alert_data)

        assert "2025-10-20 15:30:00" in message

    async def test_message_formatting_with_missing_fields(self, delivery_service):
        """Test alert formatting handles missing optional fields"""
        minimal_alert = {
            "alert_type": "spike",
            "channel_id": 123,
        }

        message = delivery_service._format_alert_message(minimal_alert)

        assert "ALERT: SPIKE" in message
        assert "Unknown Channel" in message  # Default value
        assert "123" in message

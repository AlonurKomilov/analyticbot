"""
Alert Notification Module
Handles Telegram delivery of alert notifications
"""

from datetime import datetime
from typing import Any

from apps.jobs.alerts.runner.base import logger


class AlertNotifier:
    """Service for sending alert notifications via Telegram"""

    def __init__(self, telegram_delivery_service=None):
        self.telegram_delivery = telegram_delivery_service

    async def create_telegram_delivery_service(self):
        """Create Telegram delivery service with bot client"""
        try:
            from apps.di import get_container

            container = get_container()

            # Get bot client from DI container
            bot_client = container.bot.bot_client()

            if bot_client is None:
                logger.warning("Bot client not available, alert delivery will be logged only")
                return None

            # Create delivery service
            from infra.adapters.telegram_alert_delivery import (
                TelegramAlertDeliveryService,
            )

            return TelegramAlertDeliveryService(bot_client)

        except Exception as e:
            logger.warning(f"Failed to create Telegram delivery service: {e}")
            return None

    def generate_alert_key(self, alert_data: dict[str, Any]) -> str:
        """
        Generate unique key for alert instance

        Args:
            alert_data: Alert information

        Returns:
            Unique alert key (e.g., "spike_2025-10-20_1000")
        """
        alert_type = alert_data.get("alert_type", "unknown")
        timestamp = alert_data.get("timestamp", datetime.utcnow())

        if isinstance(timestamp, str):
            time_str = timestamp
        else:
            # Use hour precision for grouping similar alerts
            time_str = timestamp.strftime("%Y-%m-%d_%H00")

        # Include metric value for additional uniqueness
        value = alert_data.get("current_value", "")

        return f"{alert_type}_{time_str}_{value}"

    async def send_alert_notification(
        self, user_id: int, alert_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Send alert notification to user via Telegram

        Args:
            user_id: Telegram user/chat ID
            alert_data: Alert information dictionary

        Returns:
            Delivery result with status, message_id, error
        """
        # Check if Telegram delivery service is available
        if self.telegram_delivery is None:
            logger.warning("Telegram delivery service not available, logging alert only")
            message = alert_data.get("message", "Alert triggered!")
            logger.info(f"ALERT for user {user_id}: {message}")

            return {
                "status": "logged",
                "error": "Telegram delivery not configured",
                "chat_id": user_id,
            }

        # Send via Telegram with retry logic
        try:
            result = await self.telegram_delivery.send_alert(
                chat_id=user_id,
                alert_data=alert_data,
                max_retries=3,
            )

            return result

        except Exception as e:
            logger.error(f"Failed to send alert notification to user {user_id}: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "chat_id": user_id,
            }

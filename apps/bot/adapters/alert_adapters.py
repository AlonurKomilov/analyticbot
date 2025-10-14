"""
Alert Adapters

Clean Architecture: Adapters connecting core alert services to Telegram
Framework-specific implementations for sending alerts via Telegram
"""

import logging
from typing import Any

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from core.services.bot.alerts.protocols import AlertNotificationPort

logger = logging.getLogger(__name__)


class TelegramAlertNotifier(AlertNotificationPort):
    """
    Telegram implementation of alert notification

    Responsibilities:
    - Send alert messages via Telegram
    - Format alerts for Telegram display
    - Handle Telegram-specific errors
    """

    # Severity emoji mapping
    SEVERITY_EMOJIS = {
        "critical": "🚨",
        "high": "⚠️",
        "medium": "⚡",
        "low": "ℹ️",
        "info": "📊",
    }

    def __init__(self, bot: Bot):
        """
        Initialize the Telegram alert notifier

        Args:
            bot: Aiogram Bot instance
        """
        self._bot = bot
        self._logger = logging.getLogger(__name__)

    async def send_alert(
        self,
        channel_id: str,
        alert: dict[str, Any],
    ) -> bool:
        """
        Send an alert notification via Telegram

        Args:
            channel_id: Telegram channel/chat ID
            alert: Alert event dictionary

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            message = self._format_alert_message(alert)

            await self._bot.send_message(
                chat_id=channel_id,
                text=message,
                parse_mode="HTML",
                disable_web_page_preview=True,
            )

            self._logger.info(
                f"Alert sent to channel {channel_id}: {alert.get('rule_name')}"
            )
            return True

        except TelegramAPIError as e:
            self._logger.error(f"Telegram API error sending alert to {channel_id}: {e}")
            return False

        except Exception as e:
            self._logger.error(f"Unexpected error sending alert to {channel_id}: {e}")
            return False

    async def send_bulk_alerts(
        self,
        channel_id: str,
        alerts: list[dict[str, Any]],
    ) -> int:
        """
        Send multiple alerts to a channel

        Args:
            channel_id: Telegram channel/chat ID
            alerts: List of alert event dictionaries

        Returns:
            Number of alerts successfully sent
        """
        success_count = 0

        for alert in alerts:
            if await self.send_alert(channel_id, alert):
                success_count += 1

        self._logger.info(
            f"Sent {success_count}/{len(alerts)} alerts to channel {channel_id}"
        )

        return success_count

    def _format_alert_message(self, alert: dict[str, Any]) -> str:
        """
        Format an alert as a Telegram message

        Args:
            alert: Alert event dictionary

        Returns:
            Formatted message string with HTML markup
        """
        severity = alert.get("severity", "info")
        emoji = self.SEVERITY_EMOJIS.get(severity, "📌")

        rule_name = alert.get("rule_name", "Unknown Alert")
        metric = alert.get("metric_name", "N/A")
        value = alert.get("metric_value", "N/A")
        threshold = alert.get("threshold", "N/A")
        condition = alert.get("condition", "N/A")
        message = alert.get("message", "No details available")

        # Format severity with bold
        severity_text = f"<b>{severity.upper()}</b>"

        # Build message
        lines = [
            f"{emoji} <b>ALERT: {rule_name}</b>",
            "",
            f"Severity: {severity_text}",
            f"Metric: <code>{metric}</code>",
            f"Value: <b>{value}</b>",
            f"Condition: {condition} {threshold}",
            "",
            f"📝 {message}",
        ]

        # Add timestamp if available
        if "triggered_at" in alert:
            lines.append("")
            lines.append(f"🕐 {alert['triggered_at']}")

        return "\n".join(lines)

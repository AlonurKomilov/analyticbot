"""
Telegram Alert Delivery Service
================================

Infrastructure adapter for sending alerts via Telegram.
Handles message formatting, delivery, and error handling.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class TelegramAlertDeliveryService:
    """Service for delivering alerts via Telegram"""

    def __init__(self, bot_client):
        """
        Initialize Telegram alert delivery service

        Args:
            bot_client: aiogram Bot instance or compatible bot client
        """
        self.bot = bot_client
        self._retry_delays = [1, 5, 15, 30, 60]  # Exponential-ish backoff in seconds

    async def send_alert(
        self,
        chat_id: int,
        alert_data: dict[str, Any],
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """
        Send alert notification to user via Telegram with retry logic

        Args:
            chat_id: Telegram chat ID
            alert_data: Alert information dictionary
            max_retries: Maximum number of retry attempts

        Returns:
            Result dictionary with status, message_id, error
        """
        if not self.bot:
            logger.error("Bot client not available, cannot send alert")
            return {
                "status": "failed",
                "error": "Bot client not initialized",
                "chat_id": chat_id,
            }

        message = self._format_alert_message(alert_data)

        # Try sending with retries
        for attempt in range(max_retries + 1):
            try:
                result = await self._send_message(chat_id, message)

                logger.info(
                    f"Alert sent successfully to chat {chat_id} "
                    f"(attempt {attempt + 1}/{max_retries + 1})"
                )

                return {
                    "status": "sent",
                    "message_id": (result.message_id if hasattr(result, "message_id") else None),
                    "chat_id": chat_id,
                    "attempts": attempt + 1,
                }

            except Exception as e:
                logger.warning(
                    f"Failed to send alert to chat {chat_id} "
                    f"(attempt {attempt + 1}/{max_retries + 1}): {e}"
                )

                if attempt < max_retries:
                    # Calculate delay with exponential backoff
                    delay = self._retry_delays[min(attempt, len(self._retry_delays) - 1)]
                    logger.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    # Final failure
                    logger.error(
                        f"Failed to send alert to chat {chat_id} after {max_retries + 1} attempts"
                    )
                    return {
                        "status": "failed",
                        "error": str(e),
                        "chat_id": chat_id,
                        "attempts": attempt + 1,
                    }

        return {
            "status": "failed",
            "error": "Max retries exceeded",
            "chat_id": chat_id,
            "attempts": max_retries + 1,
        }

    async def _send_message(self, chat_id: int, text: str) -> Any:
        """
        Send message via bot client (aiogram-specific)

        Args:
            chat_id: Telegram chat ID
            text: Message text

        Returns:
            Message object from bot API
        """
        try:
            # Try aiogram Bot interface
            return await self.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
        except AttributeError:
            # Fallback: try alternative interface
            return await self.bot.send_message(chat_id, text)

    def _format_alert_message(self, alert_data: dict[str, Any]) -> str:
        """
        Format alert data into user-friendly Telegram message

        Args:
            alert_data: Alert information

        Returns:
            Formatted message text with HTML markup
        """
        alert_type = alert_data.get("alert_type", "unknown").upper()
        channel_name = alert_data.get("channel_name", "Unknown Channel")
        channel_id = alert_data.get("channel_id", "N/A")

        # Alert type emoji mapping
        emoji_map = {
            "SPIKE": "🚀",
            "QUIET": "😴",
            "GROWTH": "📈",
            "SUCCESS": "🎉",
        }
        emoji = emoji_map.get(alert_type, "🔔")

        # Build message header
        message_parts = [
            f"{emoji} <b>ALERT: {alert_type}</b>",
            "",
            f"📢 <b>Channel:</b> {channel_name}",
            f"🆔 <b>ID:</b> {channel_id}",
        ]

        # Add alert-specific details
        if alert_type == "SUCCESS":
            message = alert_data.get("message", "Success!")
            success_type = alert_data.get("success_type", "unknown")
            current_value = alert_data.get("current_value", "N/A")

            message_parts.extend(
                [
                    "",
                    f"<b>{message}</b>",
                    "",
                ]
            )

            if success_type == "subscribers":
                milestone = alert_data.get("milestone_value", 0)
                message_parts.append(f"🎯 Milestone: {milestone:,} subscribers")
            elif success_type == "engagement_boost":
                improvement = alert_data.get("improvement_pct", 0)
                message_parts.append(f"📈 Improvement: +{improvement:.0f}%")
            elif success_type == "viral_content":
                multiplier = alert_data.get("multiplier", 0)
                message_parts.append(f"🔥 {multiplier:.1f}x normal views!")
            elif success_type == "high_growth":
                growth_rate = alert_data.get("growth_rate", 0)
                message_parts.append(f"📊 Growth Rate: {growth_rate:.1f}%/day")

        elif alert_type == "SPIKE":
            current_value = alert_data.get("current_value", "N/A")
            baseline = alert_data.get("baseline", "N/A")
            increase = alert_data.get("increase_pct", 0)

            message_parts.extend(
                [
                    "",
                    "⚠️ <b>Unusual high activity detected!</b>",
                    f"📊 Current: {current_value}",
                    f"📏 Baseline: {baseline}",
                    f"📈 Increase: +{increase:.1f}%",
                ]
            )

        elif alert_type == "QUIET":
            current_value = alert_data.get("current_value", "N/A")
            baseline = alert_data.get("baseline", "N/A")
            decrease = alert_data.get("decrease_pct", 0)

            message_parts.extend(
                [
                    "",
                    "⚠️ <b>Unusual low activity detected!</b>",
                    f"📊 Current: {current_value}",
                    f"📏 Baseline: {baseline}",
                    f"📉 Decrease: -{decrease:.1f}%",
                ]
            )

        elif alert_type == "GROWTH":
            milestone = alert_data.get("milestone", "N/A")
            current_count = alert_data.get("current_count", "N/A")
            previous_count = alert_data.get("previous_count", "N/A")

            message_parts.extend(
                [
                    "",
                    "🎉 <b>Growth milestone reached!</b>",
                    f"🎯 Milestone: {milestone}",
                    f"👥 Current: {current_count}",
                    f"📊 Previous: {previous_count}",
                ]
            )

        # Add timestamp
        timestamp = alert_data.get("timestamp", datetime.utcnow())
        if isinstance(timestamp, str):
            message_parts.append(f"\n🕐 <i>{timestamp}</i>")
        else:
            message_parts.append(f"\n🕐 <i>{timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</i>")

        # Add action recommendation if available
        action = alert_data.get("recommended_action")
        if action:
            message_parts.append(f"\n💡 <b>Recommendation:</b> {action}")

        return "\n".join(message_parts)

    async def send_test_alert(self, chat_id: int) -> dict[str, Any]:
        """
        Send test alert for verification

        Args:
            chat_id: Telegram chat ID

        Returns:
            Delivery result
        """
        test_alert = {
            "alert_type": "spike",
            "channel_name": "Test Channel",
            "channel_id": "test_123",
            "current_value": 150,
            "baseline": 100,
            "increase_pct": 50.0,
            "timestamp": datetime.utcnow(),
            "recommended_action": "Check content for viral posts",
        }

        return await self.send_alert(chat_id, test_alert, max_retries=1)

"""
Aiogram Telegram Bot Adapter
Implements TelegramBotPort using Aiogram framework
"""

import logging
from typing import Any

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest

from core.ports.telegram_port import TelegramBotPort

logger = logging.getLogger(__name__)


class AiogramBotAdapter(TelegramBotPort):
    """
    Aiogram implementation of TelegramBotPort
    Adapts Aiogram Bot to our Clean Architecture port
    """

    def __init__(self, bot: Bot):
        """
        Initialize adapter with Aiogram bot

        Args:
            bot: Aiogram Bot instance
        """
        self.bot = bot

    async def get_post_views(self, channel_id: int, message_id: int) -> int | None:
        """
        Fetch view count for a specific post in a channel

        Note: Direct view fetching is not supported by Telegram Bot API.
        This returns None to signal that views should be tracked differently.

        Args:
            channel_id: Telegram channel ID
            message_id: Message ID within the channel

        Returns:
            None (view fetching not supported via Bot API)
        """
        try:
            # Telegram Bot API doesn't provide direct access to view counts
            # Views are only available via MTProto API or through forwarded messages
            logger.debug(
                f"View fetching not available via Bot API for message {message_id} "
                f"in channel {channel_id}"
            )
            return None
        except TelegramBadRequest as e:
            if "message not found" in str(e).lower():
                return 0  # Message deleted, return 0 views
            logger.error(f"Telegram API error fetching views: {e}")
            return None
        except TelegramAPIError as e:
            logger.error(f"Telegram API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching views: {e}")
            return None

    async def send_message(self, chat_id: int, text: str) -> dict[str, Any]:
        """
        Send a message to a chat

        Args:
            chat_id: Target chat ID
            text: Message text

        Returns:
            Message info dict with message_id, date, etc.
        """
        try:
            message = await self.bot.send_message(chat_id=chat_id, text=text)
            return {
                "message_id": message.message_id,
                "chat_id": message.chat.id,
                "date": message.date,
                "text": message.text,
            }
        except TelegramAPIError as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")
            raise

    async def get_chat(self, chat_id: int) -> dict[str, Any]:
        """
        Get chat information

        Args:
            chat_id: Chat ID

        Returns:
            Chat information dict
        """
        try:
            chat = await self.bot.get_chat(chat_id)
            return {
                "id": chat.id,
                "type": chat.type,
                "title": getattr(chat, "title", None),
                "username": getattr(chat, "username", None),
                "description": getattr(chat, "description", None),
            }
        except TelegramAPIError as e:
            logger.error(f"Failed to get chat info for {chat_id}: {e}")
            raise


class MockTelegramBotAdapter(TelegramBotPort):
    """
    Mock implementation for testing without real Telegram bot
    """

    async def get_post_views(self, channel_id: int, message_id: int) -> int | None:
        """Return mock view count"""
        return 100  # Mock value for testing

    async def send_message(self, chat_id: int, text: str) -> dict[str, Any]:
        """Mock send message"""
        return {
            "message_id": 12345,
            "chat_id": chat_id,
            "date": "2025-10-10T00:00:00Z",
            "text": text,
        }

    async def get_chat(self, chat_id: int) -> dict[str, Any]:
        """Mock get chat"""
        return {
            "id": chat_id,
            "type": "channel",
            "title": "Mock Channel",
            "username": "mock_channel",
            "description": "Mock channel for testing",
        }

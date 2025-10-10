"""
Telegram Bot Port - Abstraction for Telegram operations
This allows business logic to be independent of Aiogram framework
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class TelegramBotPort(Protocol):
    """Protocol for Telegram bot operations"""

    async def get_post_views(self, channel_id: int, message_id: int) -> int | None:
        """
        Fetch view count for a specific post in a channel

        Args:
            channel_id: Telegram channel ID
            message_id: Message ID within the channel

        Returns:
            View count or None if unavailable
        """
        ...

    async def send_message(self, chat_id: int, text: str) -> dict:
        """
        Send a message to a chat

        Args:
            chat_id: Target chat ID
            text: Message text

        Returns:
            Message info dict
        """
        ...

    async def get_chat(self, chat_id: int) -> dict:
        """
        Get chat information

        Args:
            chat_id: Chat ID

        Returns:
            Chat information dict
        """
        ...

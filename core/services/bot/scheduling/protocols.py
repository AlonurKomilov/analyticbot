"""
Scheduling Service Protocols

Clean Architecture: Define interfaces for external dependencies
These protocols allow core services to remain framework-agnostic
"""

from datetime import datetime
from typing import Any, Protocol


class ScheduleRepository(Protocol):
    """
    Protocol for scheduled posts repository

    Defines interface for persistence operations without coupling to specific implementation
    """

    async def create_scheduled_post(
        self,
        user_id: int,
        channel_id: int,
        post_text: str,
        schedule_time: datetime,
        media_id: str | None = None,
        media_type: str | None = None,
        inline_buttons: dict | None = None,
    ) -> int:
        """
        Create a new scheduled post

        Args:
            user_id: User who scheduled the post
            channel_id: Target channel ID
            post_text: Post content text
            schedule_time: When to send the post
            media_id: Optional media file ID
            media_type: Optional media type (photo, video, document)
            inline_buttons: Optional inline keyboard buttons

        Returns:
            Created post ID
        """
        ...

    async def update_post_status(self, post_id: int, status: str) -> None:
        """
        Update the status of a scheduled post

        Args:
            post_id: Post ID to update
            status: New status (pending, sent, error)
        """
        ...

    async def get_pending_posts(self, limit: int = 50) -> list[dict]:
        """
        Get posts that are ready to be sent

        Args:
            limit: Maximum number of posts to retrieve

        Returns:
            List of pending post dictionaries
        """
        ...


class AnalyticsRepository(Protocol):
    """
    Protocol for analytics logging

    Allows tracking of sent posts without coupling to analytics implementation
    """

    async def log_sent_post(
        self,
        scheduled_post_id: int,
        channel_id: int,
        message_id: int,
    ) -> None:
        """
        Log a successfully sent post to analytics

        Args:
            scheduled_post_id: ID of the scheduled post
            channel_id: Channel where post was sent
            message_id: Telegram message ID
        """
        ...


class MessageSenderPort(Protocol):
    """
    Protocol for sending messages (Telegram abstraction)

    Core services use this port to send messages without depending on Telegram framework
    Adapters implement this port using actual Telegram API
    """

    async def send_text(
        self,
        channel_id: int,
        text: str,
        reply_markup: Any | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Send a text message

        Args:
            channel_id: Target channel ID
            text: Message text
            reply_markup: Optional inline keyboard
            **kwargs: Additional parameters

        Returns:
            Dict with message_id, chat_id, success status
        """
        ...

    async def send_media(
        self,
        channel_id: int,
        media_id: str,
        media_type: str,
        caption: str | None = None,
        reply_markup: Any | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Send a media message (photo, video, document)

        Args:
            channel_id: Target channel ID
            media_id: Telegram file ID
            media_type: Type of media (photo, video, document)
            caption: Optional caption text
            reply_markup: Optional inline keyboard
            **kwargs: Additional parameters

        Returns:
            Dict with message_id, chat_id, success status
        """
        ...


class MarkupBuilderPort(Protocol):
    """
    Protocol for building message markup (inline keyboards)

    Abstracts Telegram-specific keyboard building from core logic
    """

    def build_inline_keyboard(self, buttons_data: dict | None) -> Any:
        """
        Build an inline keyboard from button data

        Args:
            buttons_data: Button configuration dictionary

        Returns:
            Framework-specific keyboard markup object (or None)
        """
        ...

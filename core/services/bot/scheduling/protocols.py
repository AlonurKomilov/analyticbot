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

    async def get_post_by_id(self, post_id: int) -> Any | None:
        """
        Get a scheduled post by ID

        Args:
            post_id: Post ID to retrieve

        Returns:
            Post object or None if not found
        """
        ...

    async def store_error_message(self, post_id: int, error_message: str) -> None:
        """
        Store error message for a failed post

        Args:
            post_id: Post ID
            error_message: Error message to store
        """
        ...

    async def store_message_id(self, post_id: int, message_id: int) -> None:
        """
        Store Telegram message ID for a delivered post

        Args:
            post_id: Scheduled post ID
            message_id: Telegram message ID
        """
        ...

    async def count_posts(
        self, user_id: int | None = None, channel_id: int | None = None
    ) -> int:
        """
        Count total posts with optional filters

        Args:
            user_id: Optional user ID filter
            channel_id: Optional channel ID filter

        Returns:
            Total post count
        """
        ...

    async def count_posts_by_status(
        self,
        status: str,
        user_id: int | None = None,
        channel_id: int | None = None,
    ) -> int:
        """
        Count posts by status with optional filters

        Args:
            status: Post status to count
            user_id: Optional user ID filter
            channel_id: Optional channel ID filter

        Returns:
            Count of posts with given status
        """
        ...

    async def get_failed_posts_with_errors(
        self, user_id: int | None = None, limit: int = 10
    ) -> list[tuple[int, str]]:
        """
        Get recently failed posts with error messages

        Args:
            user_id: Optional user ID filter
            limit: Maximum number of posts

        Returns:
            List of (post_id, error_message) tuples
        """
        ...

    async def delete_old_posts(self, days_old: int, statuses: list[str]) -> int:
        """
        Delete old posts in specified statuses

        Args:
            days_old: Delete posts older than this many days
            statuses: List of statuses to delete

        Returns:
            Number of posts deleted
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

    async def record_post_delivery(
        self,
        post_id: int,
        message_id: int,
        channel_id: int,
        delivered_at: datetime,
    ) -> None:
        """
        Record post delivery in analytics

        Args:
            post_id: Scheduled post ID
            message_id: Telegram message ID
            channel_id: Channel ID
            delivered_at: Delivery timestamp
        """
        ...


class MessageSenderPort(Protocol):
    """
    Protocol for sending messages (Telegram abstraction)

    Core services use this port to send messages without depending on Telegram framework
    Adapters implement this port using actual Telegram API
    """

    async def send_text_message(
        self,
        channel_id: int,
        text: str,
        reply_markup: Any | None = None,
    ) -> int:
        """
        Send a text message

        Args:
            channel_id: Target channel ID
            text: Message text
            reply_markup: Optional inline keyboard

        Returns:
            Sent message ID
        """
        ...

    async def send_media_message(
        self,
        channel_id: int,
        media_id: str,
        media_type: str,
        caption: str | None = None,
        reply_markup: Any | None = None,
    ) -> int:
        """
        Send a media message (photo, video, document)

        Args:
            channel_id: Target channel ID
            media_id: Telegram file ID
            media_type: Type of media (photo, video, document)
            caption: Optional caption text
            reply_markup: Optional inline keyboard

        Returns:
            Sent message ID
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

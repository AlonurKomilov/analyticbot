"""
Post Delivery Service

Clean Architecture: Core business logic for delivering scheduled posts
Orchestrates the delivery process with reliability guards and error handling
"""

import logging
from datetime import datetime
from typing import Any

from .models import DeliveryResult, ScheduledPost
from .protocols import (
    AnalyticsRepository,
    MarkupBuilderPort,
    MessageSenderPort,
    ScheduleRepository,
)

logger = logging.getLogger(__name__)


class PostDeliveryService:
    """
    Service for delivering scheduled posts to channels

    Responsibilities:
    - Orchestrate message delivery via MessageSenderPort
    - Build inline keyboards via MarkupBuilderPort
    - Track analytics via AnalyticsRepository
    - Handle delivery errors with graceful degradation
    - Return detailed delivery results
    """

    def __init__(
        self,
        message_sender: MessageSenderPort,
        markup_builder: MarkupBuilderPort,
        schedule_repo: ScheduleRepository,
        analytics_repo: AnalyticsRepository,
    ):
        """
        Initialize delivery service

        Args:
            message_sender: Port for sending messages to Telegram
            markup_builder: Port for building inline keyboards
            schedule_repo: Repository for scheduled posts
            analytics_repo: Repository for post analytics
        """
        self._message_sender = message_sender
        self._markup_builder = markup_builder
        self._schedule_repo = schedule_repo
        self._analytics_repo = analytics_repo

    async def deliver_post(self, post: ScheduledPost) -> DeliveryResult:
        """
        Deliver a scheduled post to its target channel

        This is the main orchestration method that:
        1. Validates the post
        2. Builds inline keyboard if needed
        3. Sends the message via the appropriate port
        4. Records analytics
        5. Returns detailed delivery result

        Args:
            post: The scheduled post to deliver

        Returns:
            DeliveryResult with success status and details

        Raises:
            ValueError: If post is invalid
        """
        if not post.is_valid():
            error_msg = "Post must have text or media"
            logger.error(f"Invalid post {post.id}: {error_msg}")
            return DeliveryResult(
                post_id=post.id,
                success=False,
                error_message=error_msg,
                delivered_at=datetime.now(),
                message_id=None,
            )

        try:
            # Build inline keyboard if buttons are present
            reply_markup = None
            if post.has_buttons():
                reply_markup = self._markup_builder.build_inline_keyboard(post.inline_buttons)

            # Deliver the message via appropriate method
            message_id = await self._send_message(post, reply_markup)

            # Record analytics for successful delivery
            await self._record_analytics(post.id, message_id, post.channel_id)

            logger.info(f"Successfully delivered post {post.id} to channel {post.channel_id}")

            return DeliveryResult(
                post_id=post.id,
                success=True,
                error_message=None,
                delivered_at=datetime.now(),
                message_id=message_id,
            )

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to deliver post {post.id}: {error_msg}", exc_info=True)

            return DeliveryResult(
                post_id=post.id,
                success=False,
                error_message=error_msg,
                delivered_at=datetime.now(),
                message_id=None,
            )

    async def _send_message(self, post: ScheduledPost, reply_markup: Any | None) -> int:
        """
        Send message using the appropriate method based on content type

        Args:
            post: The post to send
            reply_markup: Optional inline keyboard markup

        Returns:
            Sent message ID

        Raises:
            Exception: If sending fails
        """
        # Text-only message
        if post.has_text() and not post.has_media():
            return await self._message_sender.send_text_message(
                channel_id=post.channel_id,
                text=post.post_text,
                reply_markup=reply_markup,
            )

        # Media with caption
        if post.has_media():
            return await self._message_sender.send_media_message(
                channel_id=post.channel_id,
                media_id=post.media_id,
                media_type=post.media_type,
                caption=post.post_text,
                reply_markup=reply_markup,
            )

        # This should never happen due to is_valid() check
        raise ValueError("Post has neither text nor media")

    async def _record_analytics(self, post_id: int, message_id: int, channel_id: int) -> None:
        """
        Record post analytics for tracking

        Args:
            post_id: Scheduled post ID
            message_id: Telegram message ID
            channel_id: Channel ID where post was sent
        """
        try:
            await self._analytics_repo.record_post_delivery(
                post_id=post_id,
                message_id=message_id,
                channel_id=channel_id,
                delivered_at=datetime.now(),
            )
        except Exception as e:
            # Don't fail delivery if analytics recording fails
            logger.warning(
                f"Failed to record analytics for post {post_id}: {e}",
                exc_info=True,
            )

    async def deliver_batch(self, posts: list[ScheduledPost]) -> list[DeliveryResult]:
        """
        Deliver multiple posts in batch

        Each post is delivered independently - one failure won't affect others

        Args:
            posts: List of scheduled posts to deliver

        Returns:
            List of delivery results for each post
        """
        results = []
        for post in posts:
            result = await self.deliver_post(post)
            results.append(result)

        return results

    async def retry_failed_delivery(self, post: ScheduledPost) -> DeliveryResult:
        """
        Retry delivery of a previously failed post

        Args:
            post: The post to retry

        Returns:
            DeliveryResult with retry outcome
        """
        logger.info(f"Retrying delivery of post {post.id}")
        return await self.deliver_post(post)

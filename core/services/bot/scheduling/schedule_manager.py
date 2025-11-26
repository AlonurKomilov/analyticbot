"""
Schedule Manager - Core Scheduling Business Logic

Clean Architecture: Framework-agnostic scheduling service
Handles creation and validation of scheduled posts
"""

import logging
from datetime import UTC, datetime

from .protocols import ScheduleRepository

logger = logging.getLogger(__name__)


class ScheduleManager:
    """
    Core service for managing post schedules

    Single Responsibility: Create and manage scheduled posts
    No framework dependencies - pure business logic
    """

    def __init__(self, schedule_repository: ScheduleRepository):
        """
        Initialize schedule manager

        Args:
            schedule_repository: Repository for schedule persistence
        """
        self.schedule_repo = schedule_repository

    async def create_scheduled_post(
        self,
        user_id: int,
        channel_id: int,
        post_text: str | None,
        schedule_time: datetime,
        media_id: str | None = None,
        media_type: str | None = None,
        inline_buttons: dict | None = None,
    ) -> int | None:
        """
        Create a new scheduled post with validation

        Args:
            user_id: User scheduling the post
            channel_id: Target channel ID
            post_text: Post text content
            schedule_time: When to send the post
            media_id: Optional media file ID
            media_type: Optional media type
            inline_buttons: Optional button configuration

        Returns:
            Post ID if successful, None if validation fails
        """
        try:
            # Validate content
            if not self._validate_content(post_text, media_id):
                logger.warning(
                    f"Invalid post content: user_id={user_id}, "
                    f"has_text={bool(post_text)}, has_media={bool(media_id)}"
                )
                return None

            # Validate schedule time
            if not self._validate_schedule_time(schedule_time):
                logger.warning(
                    f"Invalid schedule time: {schedule_time} (must be in future)"
                )
                return None

            # Validate inline buttons if provided
            if inline_buttons and not self._validate_buttons(inline_buttons):
                logger.warning(f"Invalid button configuration: {inline_buttons}")
                return None

            # Create post in repository
            post_id = await self.schedule_repo.create_scheduled_post(
                user_id=user_id,
                channel_id=channel_id,
                post_text=post_text or "",
                schedule_time=schedule_time,
                media_id=media_id,
                media_type=media_type,
                inline_buttons=inline_buttons,
            )

            logger.info(
                f"Scheduled post {post_id} for {schedule_time} "
                f"(user={user_id}, channel={channel_id})"
            )
            return post_id

        except Exception as e:
            logger.error(
                f"Failed to create scheduled post: {e}",
                exc_info=True,
                extra={
                    "user_id": user_id,
                    "channel_id": channel_id,
                    "schedule_time": schedule_time,
                },
            )
            return None

    async def get_pending_posts(self, limit: int = 50) -> list[dict]:
        """
        Get posts that are ready to be sent

        Args:
            limit: Maximum number of posts to retrieve

        Returns:
            List of pending post dictionaries
        """
        try:
            posts = await self.schedule_repo.get_pending_posts(limit=limit)
            logger.debug(f"Retrieved {len(posts)} pending posts (limit={limit})")
            return posts
        except Exception as e:
            logger.error(f"Failed to get pending posts: {e}", exc_info=True)
            return []

    def _validate_content(self, post_text: str | None, media_id: str | None) -> bool:
        """
        Validate that post has required content

        Business Rule: Post must have either text or media

        Args:
            post_text: Post text
            media_id: Media file ID

        Returns:
            True if valid, False otherwise
        """
        has_text = post_text is not None and len(post_text.strip()) > 0
        has_media = media_id is not None and len(media_id.strip()) > 0
        return has_text or has_media

    def _validate_schedule_time(self, schedule_time: datetime) -> bool:
        """
        Validate schedule time is in the future

        Business Rule: Cannot schedule posts in the past

        Args:
            schedule_time: Proposed schedule time

        Returns:
            True if valid, False otherwise
        """
        # Ensure both datetimes are timezone-aware for comparison
        now = datetime.now(UTC)

        # If schedule_time is naive, assume UTC
        if schedule_time.tzinfo is None:
            schedule_time = schedule_time.replace(tzinfo=UTC)

        return schedule_time > now

    def _validate_buttons(self, buttons_data: dict) -> bool:
        """
        Validate inline buttons configuration

        Basic validation - detailed validation done by domain model

        Args:
            buttons_data: Button configuration dictionary

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(buttons_data, dict):
            return False

        # Check if buttons key exists and is a list
        if "buttons" not in buttons_data:
            return False

        buttons = buttons_data["buttons"]
        if not isinstance(buttons, list):
            return False

        # Validate at least one button exists
        return len(buttons) > 0

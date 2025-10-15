"""
Delivery Status Tracker Service

Clean Architecture: Core business logic for tracking delivery status
Manages post lifecycle and status transitions
"""

import logging

from .models import DeliveryResult, DeliveryStats
from .protocols import AnalyticsRepository, ScheduleRepository

logger = logging.getLogger(__name__)


class DeliveryStatusTracker:
    """
    Service for tracking and managing scheduled post statuses

    Responsibilities:
    - Update post status based on delivery results
    - Track delivery statistics
    - Handle status transitions (pending -> delivered/failed)
    - Provide delivery metrics and reports
    """

    # Valid status transitions
    VALID_TRANSITIONS = {
        "pending": ["delivered", "failed", "cancelled"],
        "failed": ["pending", "cancelled"],  # Allow retry
        "delivered": [],  # Terminal state
        "cancelled": [],  # Terminal state
    }

    def __init__(
        self,
        schedule_repo: ScheduleRepository,
        analytics_repo: AnalyticsRepository,
    ):
        """
        Initialize status tracker

        Args:
            schedule_repo: Repository for scheduled posts
            analytics_repo: Repository for post analytics
        """
        self._schedule_repo = schedule_repo
        self._analytics_repo = analytics_repo

    async def update_from_delivery_result(self, result: DeliveryResult) -> None:
        """
        Update post status based on delivery result

        Args:
            result: Delivery result containing success status and details
        """
        new_status = "delivered" if result.success else "failed"

        await self.update_status(
            post_id=result.post_id,
            new_status=new_status,
            error_message=result.error_message,
            message_id=result.message_id,
        )

    async def update_status(
        self,
        post_id: int,
        new_status: str,
        error_message: str | None = None,
        message_id: int | None = None,
    ) -> bool:
        """
        Update post status with validation

        Args:
            post_id: Post ID to update
            new_status: New status value
            error_message: Optional error message for failed status
            message_id: Optional Telegram message ID for delivered status

        Returns:
            True if status was updated, False if transition is invalid

        Raises:
            ValueError: If new_status is not recognized
        """
        valid_statuses = {"pending", "delivered", "failed", "cancelled"}
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status: {new_status}. Must be one of {valid_statuses}")

        # Get current status to validate transition
        current_post = await self._schedule_repo.get_post_by_id(post_id)
        if not current_post:
            logger.error(f"Cannot update status: post {post_id} not found")
            return False

        # Validate state transition
        if not self._is_valid_transition(current_post.status, new_status):
            logger.warning(
                f"Invalid status transition for post {post_id}: "
                f"{current_post.status} -> {new_status}"
            )
            return False

        # Update status in repository
        await self._schedule_repo.update_post_status(post_id=post_id, status=new_status)

        # Store additional metadata for failed posts
        if new_status == "failed" and error_message:
            await self._schedule_repo.store_error_message(post_id, error_message)

        # Store message ID for delivered posts
        if new_status == "delivered" and message_id:
            await self._schedule_repo.store_message_id(post_id, message_id)

        logger.info(f"Updated post {post_id} status: {current_post.status} -> {new_status}")
        return True

    async def mark_as_cancelled(self, post_id: int, reason: str | None = None) -> bool:
        """
        Cancel a scheduled post

        Args:
            post_id: Post ID to cancel
            reason: Optional cancellation reason

        Returns:
            True if post was cancelled, False otherwise
        """
        success = await self.update_status(post_id, "cancelled")

        if success and reason:
            await self._schedule_repo.store_error_message(post_id, f"Cancelled: {reason}")

        return success

    async def get_delivery_stats(
        self, user_id: int | None = None, channel_id: int | None = None
    ) -> DeliveryStats:
        """
        Get delivery statistics

        Args:
            user_id: Optional filter by user ID
            channel_id: Optional filter by channel ID

        Returns:
            DeliveryStats with aggregated metrics
        """
        # Fetch counts from repository
        total_posts = await self._schedule_repo.count_posts(user_id=user_id, channel_id=channel_id)

        delivered_count = await self._schedule_repo.count_posts_by_status(
            status="delivered", user_id=user_id, channel_id=channel_id
        )

        failed_count = await self._schedule_repo.count_posts_by_status(
            status="failed", user_id=user_id, channel_id=channel_id
        )

        pending_count = await self._schedule_repo.count_posts_by_status(
            status="pending", user_id=user_id, channel_id=channel_id
        )

        cancelled_count = await self._schedule_repo.count_posts_by_status(
            status="cancelled", user_id=user_id, channel_id=channel_id
        )

        return DeliveryStats(
            total_posts=total_posts,
            delivered_count=delivered_count,
            failed_count=failed_count,
            pending_count=pending_count,
            cancelled_count=cancelled_count,
        )

    async def get_failed_posts(
        self, user_id: int | None = None, limit: int = 10
    ) -> list[tuple[int, str]]:
        """
        Get recently failed posts with error messages

        Args:
            user_id: Optional filter by user ID
            limit: Maximum number of posts to return

        Returns:
            List of (post_id, error_message) tuples
        """
        return await self._schedule_repo.get_failed_posts_with_errors(user_id=user_id, limit=limit)

    def _is_valid_transition(self, current_status: str, new_status: str) -> bool:
        """
        Check if status transition is valid

        Args:
            current_status: Current post status
            new_status: Requested new status

        Returns:
            True if transition is allowed, False otherwise
        """
        if current_status == new_status:
            return True  # No-op transitions are valid

        allowed_transitions = self.VALID_TRANSITIONS.get(current_status, [])
        return new_status in allowed_transitions

    async def cleanup_old_posts(self, days_old: int = 30, statuses: list[str] | None = None) -> int:
        """
        Clean up old posts in terminal states

        Args:
            days_old: Delete posts older than this many days
            statuses: Optional list of statuses to delete (default: delivered, cancelled)

        Returns:
            Number of posts deleted
        """
        if statuses is None:
            statuses = ["delivered", "cancelled"]

        deleted_count = await self._schedule_repo.delete_old_posts(
            days_old=days_old, statuses=statuses
        )

        logger.info(f"Cleaned up {deleted_count} old posts (>{days_old} days)")
        return deleted_count

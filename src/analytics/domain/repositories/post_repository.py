"""
Post Repository Interface - Analytics Domain
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from ....shared_kernel.domain.value_objects import UserId
from ..entities.post import Post, PostStatus, PostType
from ..value_objects.analytics_value_objects import ChannelId, MessageId, PostId


class IPostRepository(ABC):
    """
    Repository interface for Post aggregate

    Defines contract for persisting and retrieving Post entities
    following Repository pattern and Clean Architecture principles.
    """

    @abstractmethod
    async def save(self, post: Post) -> None:
        """
        Save post aggregate (create or update)

        Args:
            post: Post aggregate to persist

        Raises:
            RepositoryError: If save operation fails
        """

    @abstractmethod
    async def get_by_id(self, post_id: PostId) -> Post | None:
        """
        Retrieve post by ID

        Args:
            post_id: Unique post identifier

        Returns:
            Post aggregate if found, None otherwise
        """

    @abstractmethod
    async def get_by_message_id(self, channel_id: ChannelId, message_id: MessageId) -> Post | None:
        """
        Retrieve post by Telegram message ID within a channel

        Args:
            channel_id: Channel identifier
            message_id: Telegram message identifier

        Returns:
            Post aggregate if found, None otherwise
        """

    @abstractmethod
    async def get_by_channel_id(
        self, channel_id: ChannelId, limit: int = 100, offset: int = 0
    ) -> list[Post]:
        """
        Get posts by channel ID with pagination

        Args:
            channel_id: Channel identifier
            limit: Maximum posts to return
            offset: Results offset for pagination

        Returns:
            List of Post aggregates in the channel
        """

    @abstractmethod
    async def get_by_user_id(
        self, user_id: UserId, limit: int = 100, offset: int = 0
    ) -> list[Post]:
        """
        Get posts by user ID with pagination

        Args:
            user_id: User identifier
            limit: Maximum posts to return
            offset: Results offset for pagination

        Returns:
            List of Post aggregates owned by the user
        """

    @abstractmethod
    async def get_by_status(
        self,
        status: PostStatus,
        user_id: UserId | None = None,
        channel_id: ChannelId | None = None,
        limit: int = 100,
    ) -> list[Post]:
        """
        Get posts by status with optional filtering

        Args:
            status: Post status to filter by
            user_id: Optional user filter
            channel_id: Optional channel filter
            limit: Maximum posts to return

        Returns:
            List of Post aggregates with specified status
        """

    @abstractmethod
    async def get_scheduled_posts_ready_for_publishing(self) -> list[Post]:
        """
        Get scheduled posts that are ready to be published

        Returns:
            List of Post aggregates ready for publishing
        """

    @abstractmethod
    async def get_published_posts_needing_view_update(
        self, last_update_before: datetime, limit: int = 100
    ) -> list[Post]:
        """
        Get published posts that need view count updates

        Args:
            last_update_before: Posts updated before this time
            limit: Maximum posts to return

        Returns:
            List of Post aggregates needing view updates
        """

    @abstractmethod
    async def search_posts(
        self,
        user_id: UserId,
        search_query: str | None = None,
        channel_id: ChannelId | None = None,
        post_type: PostType | None = None,
        status: PostStatus | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Post]:
        """
        Search posts with multiple filters

        Args:
            user_id: User identifier
            search_query: Text search in content
            channel_id: Filter by channel
            post_type: Filter by post type
            status: Filter by status
            date_from: Filter posts from this date
            date_to: Filter posts until this date
            limit: Maximum results to return
            offset: Results offset for pagination

        Returns:
            List of matching Post aggregates
        """

    @abstractmethod
    async def get_top_performing_posts(
        self,
        user_id: UserId,
        metric: str = "views",
        period_start: datetime | None = None,
        period_end: datetime | None = None,
        channel_id: ChannelId | None = None,
        limit: int = 10,
    ) -> list[Post]:
        """
        Get top performing posts by metric

        Args:
            user_id: User identifier
            metric: Metric to rank by (views, performance_score, etc.)
            period_start: Optional start date for filtering
            period_end: Optional end date for filtering
            channel_id: Optional channel filter
            limit: Number of top posts to return

        Returns:
            List of top performing Post aggregates
        """

    @abstractmethod
    async def get_post_analytics_summary(self, post_id: PostId) -> dict[str, Any]:
        """
        Get comprehensive analytics summary for a post

        Args:
            post_id: Post identifier

        Returns:
            Dictionary with detailed analytics data
        """

    @abstractmethod
    async def get_channel_post_statistics(
        self, channel_id: ChannelId, period_start: datetime, period_end: datetime
    ) -> dict[str, Any]:
        """
        Get aggregated post statistics for a channel in a period

        Args:
            channel_id: Channel identifier
            period_start: Start of statistics period
            period_end: End of statistics period

        Returns:
            Dictionary with aggregated post statistics
        """

    @abstractmethod
    async def bulk_update_views(self, view_updates: list[dict[str, Any]]) -> int:
        """
        Bulk update view counts for multiple posts

        Args:
            view_updates: List of dicts with post_id and new_view_count

        Returns:
            Number of posts successfully updated

        Raises:
            RepositoryError: If bulk update operation fails
        """

    @abstractmethod
    async def get_posts_by_date_range(
        self,
        user_id: UserId,
        start_date: datetime,
        end_date: datetime,
        channel_id: ChannelId | None = None,
        status: PostStatus | None = None,
    ) -> list[Post]:
        """
        Get posts within a date range

        Args:
            user_id: User identifier
            start_date: Start of date range
            end_date: End of date range
            channel_id: Optional channel filter
            status: Optional status filter

        Returns:
            List of Post aggregates in date range
        """

    @abstractmethod
    async def count_posts(
        self,
        user_id: UserId | None = None,
        channel_id: ChannelId | None = None,
        status: PostStatus | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> int:
        """
        Count posts with optional filters

        Args:
            user_id: Optional user filter
            channel_id: Optional channel filter
            status: Optional status filter
            date_from: Optional start date filter
            date_to: Optional end date filter

        Returns:
            Total number of matching posts
        """

    @abstractmethod
    async def get_user_post_summary(self, user_id: UserId) -> dict[str, Any]:
        """
        Get summary statistics for all user's posts

        Args:
            user_id: User identifier

        Returns:
            Dictionary with aggregated statistics across all user posts
        """

    @abstractmethod
    async def get_failed_posts(self, user_id: UserId | None = None, limit: int = 50) -> list[Post]:
        """
        Get posts that failed to publish

        Args:
            user_id: Optional user filter
            limit: Maximum posts to return

        Returns:
            List of failed Post aggregates
        """

    @abstractmethod
    async def delete(self, post_id: PostId) -> bool:
        """
        Delete post (hard delete)

        Args:
            post_id: Post identifier

        Returns:
            True if post was deleted, False if not found

        Note:
            This is hard delete. For soft delete, use Post.delete_post()
        """

    @abstractmethod
    async def exists(self, post_id: PostId) -> bool:
        """
        Check if post exists

        Args:
            post_id: Post identifier

        Returns:
            True if post exists, False otherwise
        """

    @abstractmethod
    async def cleanup_old_posts(
        self, older_than: datetime, status: PostStatus = PostStatus.DELETED
    ) -> int:
        """
        Clean up old posts (hard delete)

        Args:
            older_than: Delete posts older than this date
            status: Only delete posts with this status

        Returns:
            Number of posts deleted
        """

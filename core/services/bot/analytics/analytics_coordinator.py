"""
Analytics Coordinator - Unified API for Analytics Operations
Orchestrates all analytics modules and provides high-level business API
"""

import logging
from typing import Any

from core.services.bot.analytics.analytics_batch_processor import AnalyticsBatchProcessor
from core.services.bot.analytics.cache_manager import AnalyticsCacheManager
from core.services.bot.analytics.data_aggregator import AnalyticsDataAggregator
from core.services.bot.analytics.post_tracker import AnalyticsPostTracker
from core.services.bot.analytics.stream_processor import AnalyticsStreamProcessor

logger = logging.getLogger(__name__)


class AnalyticsCoordinator:
    """
    🚀 UNIFIED ANALYTICS SERVICE - High-level coordinator for all analytics operations
    Provides clean API for analytics features with proper separation of concerns

    This replaces the monolithic AnalyticsService with a modular architecture:
    - Batch processing → AnalyticsBatchProcessor
    - Streaming → AnalyticsStreamProcessor
    - Caching → AnalyticsCacheManager
    - Grouping/Stats → AnalyticsDataAggregator
    - View Tracking → AnalyticsPostTracker
    """

    def __init__(
        self,
        analytics_repository: Any,
        telegram_port: Any | None = None,
        cache: Any | None = None,
        batch_size: int = 50,
        concurrent_limit: int = 10,
        rate_limit_delay: float = 0.1,
    ):
        """
        Initialize analytics coordinator with all sub-modules

        Args:
            analytics_repository: Repository for analytics data persistence
            telegram_port: Optional telegram abstraction for view fetching
            cache: Optional cache backend (Redis, in-memory, etc.)
            batch_size: Number of posts per batch
            concurrent_limit: Maximum concurrent operations
            rate_limit_delay: Delay between batches (seconds)
        """
        self.analytics_repository = analytics_repository
        self.telegram_port = telegram_port

        # Initialize all sub-modules
        self.cache_manager = AnalyticsCacheManager(cache=cache, default_ttl=300)
        self.data_aggregator = AnalyticsDataAggregator()

        self.batch_processor = AnalyticsBatchProcessor(
            analytics_repository=analytics_repository,
            telegram_port=telegram_port,
            batch_size=batch_size,
            concurrent_limit=concurrent_limit,
            rate_limit_delay=rate_limit_delay,
        )

        self.stream_processor = AnalyticsStreamProcessor(
            analytics_repository=analytics_repository,
            batch_processor=self.batch_processor,
            max_concurrent_batches=5,
            stream_batch_size=100,
        )

        self.post_tracker = AnalyticsPostTracker(
            analytics_repository=analytics_repository,
            batch_processor=self.batch_processor,
            cache_manager=self.cache_manager,
            data_aggregator=self.data_aggregator,
            concurrent_limit=concurrent_limit,
            batch_size=batch_size,
            rate_limit_delay=rate_limit_delay,
        )

        # Configuration
        self._batch_size = batch_size
        self._concurrent_limit = concurrent_limit
        self._rate_limit_delay = rate_limit_delay

    # ============================================================================
    # HIGH-LEVEL API - Main Business Operations
    # ============================================================================

    async def update_all_post_views(self) -> dict[str, int | float]:
        """
        🔥 MAIN API: Update all post views with full optimization stack

        This is the primary method for updating view counts across all posts.
        Uses caching, batching, concurrency control, and intelligent error handling.

        Returns:
            Comprehensive statistics dictionary
        """
        return await self.post_tracker.update_all_post_views()

    async def update_posts_views_batch(
        self, posts_data: list[dict], batch_size: int | None = None
    ) -> dict[str, int]:
        """
        🚀 OPTIMIZED BATCH PROCESSING
        Process view updates for a specific list of posts

        Args:
            posts_data: List of post dictionaries
            batch_size: Optional batch size override

        Returns:
            Statistics dictionary
        """
        return await self.batch_processor.update_posts_views_batch(
            posts_data=posts_data, batch_size=batch_size
        )

    async def stream_process_large_channel(self, channel_id: int) -> dict[str, int]:
        """
        🌊 STREAMING API: Process large channel with memory optimization
        Perfect for channels with thousands of posts

        Args:
            channel_id: Channel ID to process

        Returns:
            Statistics dictionary
        """
        return await self.stream_processor.stream_process_large_channel(channel_id)

    async def process_all_posts_memory_optimized(
        self, max_concurrent_batches: int | None = None
    ) -> dict[str, int]:
        """
        🧠 MEMORY-OPTIMIZED API: Process all posts using async generators
        Uses generators to minimize memory footprint

        Args:
            max_concurrent_batches: Optional concurrency override

        Returns:
            Statistics dictionary
        """
        return await self.stream_processor.process_all_posts_memory_optimized(
            max_concurrent_batches=max_concurrent_batches
        )

    # ============================================================================
    # DATA GROUPING AND AGGREGATION
    # ============================================================================

    def simple_group_posts(self, posts: list[dict]) -> dict[int, list[dict]]:
        """
        Simple post grouping by channel ID

        Args:
            posts: List of posts

        Returns:
            Dictionary mapping channel_id to posts
        """
        return self.data_aggregator.simple_group_posts(posts)

    async def smart_group_posts(self, posts: list[dict]) -> dict[int, list[dict]]:
        """
        🧠 Intelligent post grouping with priority optimization

        Args:
            posts: List of posts

        Returns:
            Prioritized dictionary mapping channel_id to posts
        """
        return await self.data_aggregator.smart_group_posts(posts)

    # ============================================================================
    # CACHE OPERATIONS
    # ============================================================================

    async def get_cached_posts(self) -> list[dict] | None:
        """Get cached posts list"""
        return await self.cache_manager.get_cached_posts()

    async def cache_posts(self, posts: list[dict], ttl: int | None = None) -> None:
        """Cache posts list"""
        await self.cache_manager.cache_posts(posts, ttl=ttl)

    async def cache_performance_stats(self, stats: dict[str, int | float]) -> None:
        """Cache performance statistics"""
        await self.cache_manager.cache_performance_stats(stats)

    async def get_performance_stats(self) -> dict[str, int | float] | None:
        """Get cached performance statistics"""
        return await self.cache_manager.get_performance_stats()

    # ============================================================================
    # API COMPATIBILITY METHODS (for FastAPI routers)
    # ============================================================================

    async def get_analytics_data(self, channel_id: int, **kwargs) -> dict[str, Any]:
        """
        Get analytics data for API endpoints

        Args:
            channel_id: Channel ID
            **kwargs: Additional parameters

        Returns:
            Analytics data dictionary
        """
        # Try to get from cache first
        cache_key = f"channel_analytics:{channel_id}"
        cached_data = await self.cache_manager.get_analytics_data(cache_key)
        if cached_data:
            return cached_data

        # Generate fresh data
        data = {
            "channel_id": channel_id,
            "views": 0,
            "subscribers": 0,
            "posts": 0,
            "message": "Analytics data - implement specific logic as needed",
        }

        # Cache for future requests
        await self.cache_manager.cache_analytics_data(cache_key, data, ttl=600)

        return data

    async def get_dashboard_data(self, channel_id: int) -> dict[str, Any]:
        """
        Get dashboard data for API endpoints

        Args:
            channel_id: Channel ID

        Returns:
            Dashboard data dictionary
        """
        return {
            "channel_id": channel_id,
            "dashboard_data": {},
            "message": "Dashboard data - implement specific logic as needed",
        }

    async def refresh_channel_analytics(self, channel_id: int) -> dict[str, Any]:
        """
        Refresh channel analytics

        Args:
            channel_id: Channel ID

        Returns:
            Refresh result dictionary
        """
        return {
            "channel_id": channel_id,
            "refreshed": True,
            "message": "Analytics refresh - implement specific logic as needed",
        }

    async def get_analytics_summary(self, **kwargs) -> dict[str, Any]:
        """
        Get analytics summary

        Args:
            **kwargs: Filter parameters

        Returns:
            Summary data dictionary
        """
        # Get cached performance stats
        stats = await self.get_performance_stats()

        return {
            "summary": stats or {},
            "message": "Analytics summary",
        }

    async def get_post_views(self, post_id: int, user_id: int) -> int | None:
        """
        Get views for a specific post

        Args:
            post_id: Post ID
            user_id: User ID (for permissions)

        Returns:
            View count or None if not available
        """
        try:
            # This would need repository implementation
            logger.debug(f"Get post views for post {post_id}")
            return None
        except Exception as e:
            logger.error(f"Failed to get post views for post {post_id}: {e}")
            return None

    async def create_views_chart(self, channel_id: int) -> bytes | None:
        """
        Create views chart for a channel

        Args:
            channel_id: Channel ID

        Returns:
            Chart image bytes or None if not available
        """
        try:
            # This would need chart generation implementation
            logger.debug(f"Create views chart for channel {channel_id}")
            return None
        except Exception as e:
            logger.error(f"Failed to create views chart for channel {channel_id}: {e}")
            return None


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================


def create_analytics_coordinator(
    analytics_repository: Any,
    telegram_port: Any | None = None,
    cache: Any | None = None,
    batch_size: int = 50,
    concurrent_limit: int = 10,
    rate_limit_delay: float = 0.1,
) -> AnalyticsCoordinator:
    """
    Factory function to create fully configured analytics coordinator

    Args:
        analytics_repository: Repository for analytics data persistence
        telegram_port: Optional telegram abstraction
        cache: Optional cache backend
        batch_size: Number of posts per batch
        concurrent_limit: Maximum concurrent operations
        rate_limit_delay: Delay between batches

    Returns:
        Configured AnalyticsCoordinator instance
    """
    return AnalyticsCoordinator(
        analytics_repository=analytics_repository,
        telegram_port=telegram_port,
        cache=cache,
        batch_size=batch_size,
        concurrent_limit=concurrent_limit,
        rate_limit_delay=rate_limit_delay,
    )


# Backward compatibility alias
AnalyticsService = AnalyticsCoordinator

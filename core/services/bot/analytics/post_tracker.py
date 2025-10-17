"""
Analytics Post Tracker - View Tracking Orchestration
Handles high-level orchestration of post view tracking and updates
"""

import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)


class AnalyticsPostTracker:
    """
    Orchestrates post view tracking with caching, batching, and error handling
    Provides high-level API for view update operations
    """

    def __init__(
        self,
        analytics_repository: Any,
        batch_processor: Any,
        cache_manager: Any,
        data_aggregator: Any,
        concurrent_limit: int = 10,
        batch_size: int = 50,
        rate_limit_delay: float = 0.1,
    ):
        """
        Initialize post tracker

        Args:
            analytics_repository: Repository for data access
            batch_processor: Batch processor for processing operations
            cache_manager: Cache manager for caching operations
            data_aggregator: Data aggregator for grouping and stats
            concurrent_limit: Maximum concurrent operations
            batch_size: Default batch size
            rate_limit_delay: Delay between batches
        """
        self.analytics_repository = analytics_repository
        self.batch_processor = batch_processor
        self.cache_manager = cache_manager
        self.data_aggregator = data_aggregator
        self._concurrent_limit = concurrent_limit
        self._batch_size = batch_size
        self._rate_limit_delay = rate_limit_delay
        self._semaphore = asyncio.Semaphore(concurrent_limit)

    async def update_all_post_views(self) -> dict[str, int | float]:
        """
        🔥 OPTIMIZED: Update all post views with concurrent processing and intelligent caching
        Combines modern concurrency patterns with intelligent error handling

        Returns:
            Statistics dictionary with comprehensive metrics
        """
        stats: dict[str, int | float] = {
            "processed": 0,
            "updated": 0,
            "errors": 0,
            "skipped": 0,
            "cached": 0,
            "duration": 0.0,
            "batch_size": self._batch_size,
            "concurrency_limit": self._concurrent_limit,
        }

        start_time = asyncio.get_event_loop().time()

        try:
            # Fetch posts with caching
            posts = await self._get_posts_to_track_cached()
            if not posts:
                logger.info("📊 No posts found for view tracking.")
                return stats

            logger.info(f"🚀 Starting optimized concurrent view update for {len(posts)} posts")

            # Use optimized batch processing method
            batch_stats = await self.batch_processor.update_posts_views_batch(
                posts_data=posts,
                batch_size=min(self._batch_size, 25),  # Smaller batches for better concurrency
            )

            # Merge statistics
            for key in ["processed", "updated", "errors", "skipped"]:
                stats[key] = batch_stats.get(key, 0)

            stats["duration"] = asyncio.get_event_loop().time() - start_time

            # Log comprehensive performance metrics
            success_rate = self.data_aggregator.calculate_success_rate(stats)
            throughput = self.data_aggregator.calculate_throughput(stats)

            logger.info(
                f"⚡ Optimized view update completed in {stats['duration']:.2f}s. "
                f"Processed: {stats['processed']}, Updated: {stats['updated']}, "
                f"Success rate: {success_rate:.1f}%, Throughput: {throughput:.1f} posts/sec, "
                f"Concurrent batches: {batch_stats.get('concurrent_batches', 0)}"
            )

            # Cache performance stats
            await self.cache_manager.cache_performance_stats(stats)

        except Exception as e:
            logger.error(f"❌ Failed to update all post views: {e}")
            stats["errors"] += 1
            stats["duration"] = asyncio.get_event_loop().time() - start_time

        return stats

    async def _get_posts_to_track_cached(self) -> list[dict]:
        """
        📦 Cached posts retrieval with fallback to direct call

        Returns:
            List of posts to track views for
        """
        # Try to get from cache first
        cached_posts = await self.cache_manager.get_cached_posts()
        if cached_posts is not None:
            logger.debug(f"Using {len(cached_posts)} cached posts for tracking")
            return cached_posts

        # Fetch from repository
        try:
            posts = await self.analytics_repository.get_all_posts_to_track_views()

            # Cache for future use
            await self.cache_manager.cache_posts(posts)

            return posts
        except Exception as e:
            logger.error(f"Failed to fetch posts to track: {e}")
            return []

    async def process_channels_concurrent(
        self, grouped: dict[int, list[dict]], stats: dict[str, int | float]
    ) -> None:
        """
        Process channels concurrently with rate limiting

        Args:
            grouped: Dictionary mapping channel_id to posts
            stats: Statistics dictionary (modified in place)
        """
        tasks = []

        for channel_id, channel_posts in grouped.items():
            task = asyncio.create_task(self._process_channel_optimized(channel_id, channel_posts))
            tasks.append(task)

            # Process in batches to avoid overwhelming system
            if len(tasks) >= self._concurrent_limit:
                completed_stats = await asyncio.gather(*tasks, return_exceptions=True)
                self.data_aggregator.merge_stats(stats, completed_stats)
                tasks = []
                await asyncio.sleep(self._rate_limit_delay)

        # Process remaining tasks
        if tasks:
            completed_stats = await asyncio.gather(*tasks, return_exceptions=True)
            self.data_aggregator.merge_stats(stats, completed_stats)

    async def process_channels_sequential(
        self, grouped: dict[int, list[dict]], stats: dict[str, int | float]
    ) -> None:
        """
        Process channels sequentially for maximum reliability

        Args:
            grouped: Dictionary mapping channel_id to posts
            stats: Statistics dictionary (modified in place)
        """
        for channel_id, channel_posts in grouped.items():
            channel_stats = await self._process_channel_posts(channel_id, channel_posts)

            # Merge channel stats into main stats
            for key in stats:
                stats[key] = stats.get(key, 0) + channel_stats.get(key, 0)

            await asyncio.sleep(self._rate_limit_delay)

    async def _process_channel_optimized(
        self, channel_id: int, posts: list[dict]
    ) -> dict[str, int | float]:
        """
        ⚡ High-performance channel processing with concurrency control

        Args:
            channel_id: Channel ID to process
            posts: List of posts for this channel

        Returns:
            Statistics dictionary
        """
        async with self._semaphore:
            stats: dict[str, int | float] = {
                "processed": 0,
                "updated": 0,
                "errors": 0,
                "skipped": 0,
                "cached": 0,
            }

            # Check if channel is marked as problematic
            if await self.cache_manager.is_channel_problematic(channel_id):
                logger.debug(f"⚠️ Skipping problematic channel {channel_id}")
                stats["skipped"] = len(posts)
                return stats

            try:
                # Process in micro-batches for better control
                micro_batch_size = min(10, len(posts) // 4 + 1)

                for i in range(0, len(posts), micro_batch_size):
                    micro_batch = posts[i : i + micro_batch_size]
                    batch_stats = await self.batch_processor._process_post_batch(
                        channel_id, micro_batch
                    )

                    # Merge batch stats
                    for key in stats:
                        stats[key] = stats.get(key, 0) + batch_stats.get(key, 0)

                    # Calculate adaptive delay based on success rate
                    batch_success_rate = (
                        batch_stats.get("updated", 0) / len(micro_batch) if micro_batch else 1.0
                    )
                    delay = self.data_aggregator.calculate_adaptive_delay(batch_success_rate)
                    await asyncio.sleep(delay)

            except Exception as e:
                # Mark channel as problematic
                await self.cache_manager.mark_channel_problematic(channel_id)
                logger.error(f"❌ Channel {channel_id} processing failed: {e}")
                stats["errors"] += len(posts)

            return stats

    async def _process_channel_posts(
        self, channel_id: int, posts: list[dict]
    ) -> dict[str, int | float]:
        """
        Process posts for a specific channel (legacy reliable method)

        Args:
            channel_id: Channel ID to process
            posts: List of posts for this channel

        Returns:
            Statistics dictionary
        """
        stats: dict[str, int | float] = {"processed": 0, "updated": 0, "errors": 0, "skipped": 0}

        for i in range(0, len(posts), self._batch_size):
            batch = posts[i : i + self._batch_size]
            batch_stats = await self.batch_processor._process_post_batch(channel_id, batch)

            # Merge stats
            for key in stats:
                stats[key] = stats.get(key, 0) + batch_stats.get(key, 0)

            # Rate limiting
            if i + self._batch_size < len(posts):
                await asyncio.sleep(self._rate_limit_delay)

        return stats


def create_post_tracker(
    analytics_repository: Any,
    batch_processor: Any,
    cache_manager: Any,
    data_aggregator: Any,
    concurrent_limit: int = 10,
    batch_size: int = 50,
    rate_limit_delay: float = 0.1,
) -> AnalyticsPostTracker:
    """
    Factory function to create post tracker instance

    Args:
        analytics_repository: Repository for data access
        batch_processor: Batch processor instance
        cache_manager: Cache manager instance
        data_aggregator: Data aggregator instance
        concurrent_limit: Maximum concurrent operations
        batch_size: Default batch size
        rate_limit_delay: Delay between batches

    Returns:
        Configured AnalyticsPostTracker instance
    """
    return AnalyticsPostTracker(
        analytics_repository=analytics_repository,
        batch_processor=batch_processor,
        cache_manager=cache_manager,
        data_aggregator=data_aggregator,
        concurrent_limit=concurrent_limit,
        batch_size=batch_size,
        rate_limit_delay=rate_limit_delay,
    )

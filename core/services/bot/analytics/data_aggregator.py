"""
Analytics Data Aggregator - Smart Grouping and Transformation
Handles intelligent post grouping, priority calculation, and data transformations
"""

import logging
from collections import defaultdict
from collections.abc import Mapping
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class AnalyticsDataAggregator:
    """
    Pure business logic for data aggregation and intelligent grouping
    Provides smart algorithms for priority-based processing
    """

    def __init__(self):
        """Initialize data aggregator"""
        pass

    def simple_group_posts(self, posts: list[dict]) -> dict[int, list[dict]]:
        """
        Simple post grouping by channel ID for reliable processing

        Args:
            posts: List of post dictionaries

        Returns:
            Dictionary mapping channel_id to list of posts
        """
        grouped: dict[int, list[dict]] = defaultdict(list)
        for post in posts:
            grouped[post["channel_id"]].append(post)
        return dict(grouped)

    async def smart_group_posts(self, posts: list[dict]) -> dict[int, list[dict]]:
        """
        🧠 Intelligent post grouping with priority optimization
        Prioritizes posts based on time since last update

        Priority calculation:
        - Posts not updated recently get higher priority
        - Channels with many high-priority posts processed first
        - Within each channel, posts sorted by priority (highest first)

        Args:
            posts: List of post dictionaries with optional updated_at field

        Returns:
            Dictionary mapping channel_id to prioritized list of posts
        """
        grouped = defaultdict(list)

        # Step 1: Calculate priority for each post and group by channel
        for post in posts:
            channel_id = post["channel_id"]
            priority = self._calculate_post_priority(post)
            post["_priority"] = priority
            grouped[channel_id].append(post)

        # Step 2: Sort posts within each channel by priority (highest first)
        sorted_grouped = {}
        for channel_id, channel_posts in grouped.items():
            sorted_posts = sorted(channel_posts, key=lambda x: x["_priority"], reverse=True)
            sorted_grouped[channel_id] = sorted_posts

        # Step 3: Sort channels by total priority (sum of all post priorities)
        prioritized_channels = dict(
            sorted(
                sorted_grouped.items(),
                key=lambda x: sum(p["_priority"] for p in x[1]),
                reverse=True,
            )
        )

        logger.debug(f"Smart grouped {len(posts)} posts into {len(prioritized_channels)} channels")

        return prioritized_channels

    def _calculate_post_priority(self, post: dict) -> float:
        """
        Calculate priority score for a post based on update recency

        Args:
            post: Post dictionary with optional updated_at field

        Returns:
            Priority score (0-24, higher = more urgent)
        """
        last_update = post.get("updated_at")

        if last_update is None:
            # Never updated - highest priority
            return 24.0

        try:
            # Calculate hours since last update (capped at 24 hours)
            hours_since_update = (datetime.now() - last_update).total_seconds() / 3600
            return min(hours_since_update, 24.0)
        except Exception as e:
            logger.debug(f"Failed to calculate priority for post {post.get('id')}: {e}")
            return 12.0  # Default medium priority

    def merge_stats(self, stats: dict[str, int], completed_stats: list) -> None:
        """
        Merge completed task stats into main statistics dictionary

        Args:
            stats: Main statistics dictionary (modified in place)
            completed_stats: List of completed task results (dicts or exceptions)
        """
        for result in completed_stats:
            if isinstance(result, dict):
                for key, value in result.items():
                    if isinstance(value, (int, float)):
                        stats[key] = int(stats.get(key, 0) + value)
            elif isinstance(result, Exception):
                logger.debug(f"Skipping exception result in stats merge: {result}")
                stats["errors"] = stats.get("errors", 0) + 1

    def calculate_success_rate(self, stats: Mapping[str, int | float]) -> float:
        """
        Calculate success rate from statistics

        Args:
            stats: Statistics dictionary with 'updated' and 'processed' keys

        Returns:
            Success rate as percentage (0-100)
        """
        processed = int(stats.get("processed", 0))
        if processed == 0:
            return 0.0

        updated = int(stats.get("updated", 0))
        return (updated / processed) * 100

    def calculate_throughput(self, stats: Mapping[str, int | float]) -> float:
        """
        Calculate processing throughput

        Args:
            stats: Statistics dictionary with 'processed' and 'duration' keys

        Returns:
            Throughput in posts per second
        """
        duration = float(stats.get("duration", 0))
        if duration == 0:
            return 0.0

        processed = float(stats.get("processed", 0))
        return processed / duration

    def prepare_performance_summary(self, stats: dict[str, int | float]) -> dict[str, Any]:
        """
        Prepare comprehensive performance summary

        Args:
            stats: Raw statistics dictionary

        Returns:
            Enhanced statistics with calculated metrics
        """
        summary = dict(stats)

        # Calculate derived metrics
        if "processed" in stats and "duration" in stats:
            summary["success_rate"] = self.calculate_success_rate(stats)
            summary["throughput"] = self.calculate_throughput(stats)

        # Calculate error rate
        if "processed" in stats and stats["processed"] > 0:
            errors = stats.get("errors", 0)
            summary["error_rate"] = (errors / stats["processed"]) * 100
        else:
            summary["error_rate"] = 0.0

        return summary

    def group_updates_by_channel(self, updates: list[dict]) -> dict[int, list[dict]]:
        """
        Group updates by channel ID for batch processing

        Args:
            updates: List of update dictionaries with channel_id field

        Returns:
            Dictionary mapping channel_id to list of updates
        """
        grouped: dict[int, list[dict]] = defaultdict(list)

        for update in updates:
            channel_id = update.get("channel_id")
            if channel_id is not None:
                grouped[channel_id].append(update)

        return dict(grouped)

    def calculate_adaptive_delay(
        self,
        success_rate: float,
        base_delay: float = 0.1,
        min_delay: float = 0.05,
        max_delay: float = 0.5,
    ) -> float:
        """
        Calculate adaptive rate limit delay based on success rate

        Lower success rate = longer delay (to reduce load)
        Higher success rate = shorter delay (to increase throughput)

        Args:
            success_rate: Success rate as decimal (0.0 to 1.0)
            base_delay: Base delay in seconds
            min_delay: Minimum delay in seconds
            max_delay: Maximum delay in seconds

        Returns:
            Adaptive delay in seconds
        """
        # Invert success rate (lower success = higher multiplier)
        multiplier = 2 - success_rate

        # Calculate adaptive delay
        adaptive_delay = base_delay * multiplier

        # Clamp to min/max bounds
        return max(min_delay, min(adaptive_delay, max_delay))


def create_data_aggregator() -> AnalyticsDataAggregator:
    """
    Factory function to create data aggregator instance

    Returns:
        Configured AnalyticsDataAggregator instance
    """
    return AnalyticsDataAggregator()

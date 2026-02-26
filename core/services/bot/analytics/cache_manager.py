"""
Analytics Cache Manager - Caching Layer for Performance
Handles caching of analytics data, view counts, and performance statistics
"""

import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class MockCache:
    """Mock cache implementation for when cache is not available"""

    async def get(self, key: str) -> Any | None:
        """Get value from cache (always returns None in mock)"""
        return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in cache (no-op in mock)"""


class AnalyticsCacheManager:
    """
    Cache management for analytics operations
    Provides intelligent caching with TTL management
    """

    def __init__(self, cache: Any | None = None, default_ttl: int = 300):
        """
        Initialize cache manager

        Args:
            cache: Cache backend (Redis, in-memory, etc.)
            default_ttl: Default time-to-live in seconds
        """
        self.cache = cache or MockCache()
        self.default_ttl = default_ttl

    async def get_cached_posts(self, cache_key: str = "posts_to_track") -> list[dict] | None:
        """
        Get cached posts list

        Args:
            cache_key: Cache key for posts

        Returns:
            List of posts or None if not cached
        """
        try:
            cached_posts = await self.cache.get(cache_key)
            if cached_posts:
                logger.debug(f"Cache hit for posts: {cache_key}")
            return cached_posts
        except Exception as e:
            logger.warning(f"Failed to get cached posts: {e}")
            return None

    async def cache_posts(
        self,
        posts: list[dict],
        cache_key: str = "posts_to_track",
        ttl: int | None = None,
    ) -> None:
        """
        Cache posts list

        Args:
            posts: List of posts to cache
            cache_key: Cache key for posts
            ttl: Optional TTL override
        """
        try:
            ttl = ttl or self.default_ttl
            await self.cache.set(cache_key, posts, ttl)
            logger.debug(f"Cached {len(posts)} posts with TTL {ttl}s")
        except Exception as e:
            logger.warning(f"Failed to cache posts: {e}")

    async def get_post_views_cached(self, channel_id: int, message_id: int) -> int | None:
        """
        Get cached view count for a post

        Args:
            channel_id: Channel ID
            message_id: Message ID

        Returns:
            View count or None if not cached
        """
        try:
            cache_key = f"post_views:{channel_id}:{message_id}"
            cached_views = await self.cache.get(cache_key)
            if cached_views is not None:
                logger.debug(f"Cache hit for post views: {cache_key}")
            return cached_views
        except Exception as e:
            logger.debug(f"Failed to get cached views: {e}")
            return None

    async def cache_post_views(
        self,
        channel_id: int,
        message_id: int,
        views: int,
        ttl: int | None = None,
    ) -> None:
        """
        Cache view count for a post

        Args:
            channel_id: Channel ID
            message_id: Message ID
            views: View count to cache
            ttl: Optional TTL override (default: 300s for views > 0, 60s for 0 views)
        """
        try:
            cache_key = f"post_views:{channel_id}:{message_id}"

            # Use shorter TTL for posts with no views (they might be deleted)
            if ttl is None:
                ttl = 300 if views > 0 else 60

            await self.cache.set(cache_key, views, ttl)
            logger.debug(f"Cached post views: {cache_key} = {views} (TTL: {ttl}s)")
        except Exception as e:
            logger.debug(f"Failed to cache post views: {e}")

    async def cache_performance_stats(self, stats: dict[str, int | float], ttl: int = 3600) -> None:
        """
        Cache performance statistics for monitoring

        Args:
            stats: Statistics dictionary to cache
            ttl: Time-to-live in seconds (default: 1 hour)
        """
        try:
            cache_key = f"performance_stats:{datetime.now().strftime('%Y%m%d_%H')}"
            await self.cache.set(cache_key, stats, ttl)
            logger.debug(f"Cached performance stats: {stats}")
        except Exception as e:
            logger.warning(f"Failed to cache performance stats: {e}")

    async def get_performance_stats(self) -> dict[str, int | float] | None:
        """
        Get cached performance statistics

        Returns:
            Statistics dictionary or None if not cached
        """
        try:
            cache_key = f"performance_stats:{datetime.now().strftime('%Y%m%d_%H')}"
            cached_stats = await self.cache.get(cache_key)
            if cached_stats:
                logger.debug("Cache hit for performance stats")
            return cached_stats
        except Exception as e:
            logger.warning(f"Failed to get cached performance stats: {e}")
            return None

    async def mark_channel_problematic(self, channel_id: int, ttl: int = 300) -> None:
        """
        Mark a channel as problematic (e.g., repeated errors)

        Args:
            channel_id: Channel ID to mark
            ttl: Time-to-live for the marker (default: 5 minutes)
        """
        try:
            cache_key = f"channel_problems:{channel_id}"
            await self.cache.set(cache_key, True, ttl)
            logger.warning(f"Marked channel {channel_id} as problematic (TTL: {ttl}s)")
        except Exception as e:
            logger.warning(f"Failed to mark channel as problematic: {e}")

    async def is_channel_problematic(self, channel_id: int) -> bool:
        """
        Check if a channel is marked as problematic

        Args:
            channel_id: Channel ID to check

        Returns:
            True if channel is problematic, False otherwise
        """
        try:
            cache_key = f"channel_problems:{channel_id}"
            is_problematic = await self.cache.get(cache_key)
            return bool(is_problematic)
        except Exception as e:
            logger.debug(f"Failed to check if channel is problematic: {e}")
            return False

    async def clear_channel_problems(self, channel_id: int) -> None:
        """
        Clear problematic status for a channel

        Args:
            channel_id: Channel ID to clear
        """
        try:
            cache_key = f"channel_problems:{channel_id}"
            await self.cache.set(cache_key, None, 0)
            logger.info(f"Cleared problematic status for channel {channel_id}")
        except Exception as e:
            logger.warning(f"Failed to clear channel problems: {e}")

    async def cache_analytics_data(
        self,
        key: str,
        data: dict[str, Any],
        ttl: int | None = None,
    ) -> None:
        """
        Cache arbitrary analytics data

        Args:
            key: Cache key (will be prefixed with 'analytics:')
            data: Data dictionary to cache
            ttl: Optional TTL override
        """
        try:
            cache_key = f"analytics:{key}"
            ttl = ttl or self.default_ttl
            await self.cache.set(cache_key, data, ttl)
            logger.debug(f"Cached analytics data: {cache_key}")
        except Exception as e:
            logger.warning(f"Failed to cache analytics data: {e}")

    async def get_analytics_data(self, key: str) -> dict[str, Any] | None:
        """
        Get cached analytics data

        Args:
            key: Cache key (without 'analytics:' prefix)

        Returns:
            Data dictionary or None if not cached
        """
        try:
            cache_key = f"analytics:{key}"
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                logger.debug(f"Cache hit for analytics data: {cache_key}")
            return cached_data
        except Exception as e:
            logger.warning(f"Failed to get cached analytics data: {e}")
            return None


def create_cache_manager(cache: Any | None = None, default_ttl: int = 300) -> AnalyticsCacheManager:
    """
    Factory function to create cache manager instance

    Args:
        cache: Optional cache backend
        default_ttl: Default time-to-live in seconds

    Returns:
        Configured AnalyticsCacheManager instance
    """
    return AnalyticsCacheManager(cache=cache, default_ttl=default_ttl)

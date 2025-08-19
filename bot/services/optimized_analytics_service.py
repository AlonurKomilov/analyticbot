"""
🚀 OPTIMIZED ANALYTICS SERVICE
High-performance analytics with caching and batch processing
"""

import asyncio
import logging
from collections import defaultdict
from datetime import datetime
from typing import Any

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

from bot.database.performance import (
    PerformanceConfig,
    cache_result,
    performance_manager,
    performance_timer,
)
from bot.database.repositories.analytics_repository import AnalyticsRepository
from bot.services.prometheus_service import prometheus_service, prometheus_timer
from bot.utils.error_handler import ErrorContext, ErrorHandler

logger = logging.getLogger(__name__)


class OptimizedAnalyticsService:
    """🚀 High-performance analytics service with advanced caching and optimization"""

    def __init__(self, bot: Bot, analytics_repository: AnalyticsRepository):
        self.analytics_repository = analytics_repository
        self.bot = bot
        self._rate_limit_delay = 0.1  # Optimized delay
        self._batch_size = PerformanceConfig.TASK_BATCH_SIZE
        self._concurrent_limit = 10  # Concurrent API calls
        self._semaphore = asyncio.Semaphore(self._concurrent_limit)

    @performance_timer("update_all_post_views")
    @prometheus_timer("telegram_api_optimized")
    async def update_all_post_views(self) -> dict[str, int]:
        """🔥 Optimized mass view update with intelligent batching"""
        stats = {
            "processed": 0,
            "updated": 0,
            "errors": 0,
            "skipped": 0,
            "cached": 0,
            "duration": 0,
        }

        start_time = asyncio.get_event_loop().time()

        try:
            # Get posts to track with caching
            posts = await self._get_posts_to_track_cached()

            if not posts:
                logger.info("📊 No posts found for view tracking.")
                return stats

            logger.info(f"🚀 Starting optimized view update for {len(posts)} posts")

            # Smart grouping by channel with priority
            grouped = await self._smart_group_posts(posts)

            # Process channels concurrently with rate limiting
            tasks = []
            for channel_id, channel_posts in grouped.items():
                task = asyncio.create_task(
                    self._process_channel_optimized(channel_id, channel_posts)
                )
                tasks.append(task)

                # Limit concurrent channel processing
                if len(tasks) >= self._concurrent_limit:
                    completed_stats = await asyncio.gather(
                        *tasks, return_exceptions=True
                    )
                    await self._merge_stats(stats, completed_stats)
                    tasks = []
                    await asyncio.sleep(self._rate_limit_delay)

            # Process remaining tasks
            if tasks:
                completed_stats = await asyncio.gather(*tasks, return_exceptions=True)
                await self._merge_stats(stats, completed_stats)

            stats["duration"] = asyncio.get_event_loop().time() - start_time

            logger.info(
                f"⚡ Optimized view update completed in {stats['duration']:.2f}s. "
                f"Processed: {stats['processed']}, Updated: {stats['updated']}, "
                f"Cached: {stats['cached']}, Errors: {stats['errors']}"
            )

            # Record enhanced metrics
            prometheus_service.record_post_views_update(stats["updated"])

            # Update cache with performance stats
            await self._cache_performance_stats(stats)

        except Exception as e:
            context = ErrorContext().add("operation", "optimized_update_all_post_views")
            ErrorHandler.log_error(e, context)
            stats["errors"] += 1

        return stats

    @cache_result("posts_to_track", ttl=PerformanceConfig.CACHE_ANALYTICS_TTL)
    async def _get_posts_to_track_cached(self) -> list[dict]:
        """📦 Cached posts retrieval with intelligent invalidation"""
        return await self.analytics_repository.get_all_posts_to_track_views()

    async def _smart_group_posts(self, posts: list[dict]) -> dict[int, list[dict]]:
        """🧠 Intelligent post grouping with priority optimization"""
        grouped = defaultdict(list)

        # Group by channel with metadata
        for post in posts:
            channel_id = post["channel_id"]

            # Add processing priority based on last update
            last_update = post.get("updated_at")
            if last_update:
                hours_since_update = (
                    datetime.now() - last_update
                ).total_seconds() / 3600
                post["_priority"] = min(hours_since_update, 24)  # Max 24 hours priority
            else:
                post["_priority"] = 24  # High priority for never updated

            grouped[channel_id].append(post)

        # Sort channels by total priority (most urgent first)
        sorted_grouped = {}
        for channel_id, channel_posts in grouped.items():
            sum(post["_priority"] for post in channel_posts)
            sorted_grouped[channel_id] = sorted(
                channel_posts, key=lambda x: x["_priority"], reverse=True
            )

        # Return channels sorted by urgency
        return dict(
            sorted(
                sorted_grouped.items(),
                key=lambda x: sum(p["_priority"] for p in x[1]),
                reverse=True,
            )
        )

    async def _process_channel_optimized(
        self, channel_id: int, posts: list[dict]
    ) -> dict[str, int]:
        """⚡ High-performance channel processing with concurrency control"""
        async with self._semaphore:
            stats = {
                "processed": 0,
                "updated": 0,
                "errors": 0,
                "skipped": 0,
                "cached": 0,
            }

            # Check if channel is cached as problematic
            cache_key = f"channel_problems:{channel_id}"
            if await performance_manager.cache.get(cache_key):
                logger.debug(f"⚠️ Skipping problematic channel {channel_id}")
                stats["skipped"] = len(posts)
                return stats

            try:
                # Process in optimized micro-batches
                micro_batch_size = min(10, len(posts) // 4 + 1)

                for i in range(0, len(posts), micro_batch_size):
                    micro_batch = posts[i : i + micro_batch_size]
                    batch_stats = await self._process_micro_batch(
                        channel_id, micro_batch
                    )

                    # Merge stats
                    for key in stats:
                        stats[key] += batch_stats.get(key, 0)

                    # Adaptive delay based on success rate
                    success_rate = (
                        batch_stats.get("updated", 0) / len(micro_batch)
                        if micro_batch
                        else 1
                    )
                    delay = self._rate_limit_delay * (
                        2 - success_rate
                    )  # Less delay for successful batches
                    await asyncio.sleep(delay)

            except Exception as e:
                # Cache problematic channels temporarily
                await performance_manager.cache.set(
                    cache_key, True, 300
                )  # 5 minute cooldown
                logger.error(f"❌ Channel {channel_id} processing failed: {e}")
                stats["errors"] += len(posts)

            return stats

    async def _process_micro_batch(
        self, channel_id: int, batch: list[dict]
    ) -> dict[str, int]:
        """⚡ Ultra-fast micro-batch processing"""
        stats = {"processed": 0, "updated": 0, "errors": 0, "skipped": 0, "cached": 0}

        # Prepare concurrent view fetching
        view_tasks = []
        for post in batch:
            task = self._get_post_views_with_cache(channel_id, post)
            view_tasks.append(task)

        # Execute all view fetches concurrently
        view_results = await asyncio.gather(*view_tasks, return_exceptions=True)

        # Batch database updates
        updates_to_execute = []
        for post, view_result in zip(batch, view_results):
            stats["processed"] += 1

            if isinstance(view_result, Exception):
                stats["errors"] += 1
                continue

            if view_result is None:
                stats["skipped"] += 1
                continue

            if view_result == -1:  # From cache
                stats["cached"] += 1
                continue

            # Prepare batch update
            if view_result != post.get("view_count", 0):
                updates_to_execute.append(
                    {
                        "post_id": post["id"],
                        "new_views": view_result,
                        "message_id": post["message_id"],
                        "channel_id": post["channel_id"],
                    }
                )

        # Execute batch database update
        if updates_to_execute:
            updated_count = await self._batch_update_views(updates_to_execute)
            stats["updated"] = updated_count

        return stats

    async def _get_post_views_with_cache(
        self, channel_id: int, post: dict
    ) -> int | None:
        """📦 Get post views with intelligent caching"""
        message_id = post["message_id"]
        post_id = post["id"]

        # Check cache first
        cache_key = f"post_views:{channel_id}:{message_id}"
        cached_views = await performance_manager.cache.get(cache_key)

        if cached_views is not None:
            return -1  # Indicate cached result

        try:
            # Fetch from Telegram API
            message = await self.bot.forward_message(
                chat_id=channel_id, from_chat_id=channel_id, message_id=message_id
            )

            # Get views (this is a simplified example - actual implementation depends on Telegram API)
            views = getattr(message, "views", 0) or 0

            # Cache the result
            cache_ttl = 300 if views > 0 else 60  # Cache hits longer than misses
            await performance_manager.cache.set(cache_key, views, cache_ttl)

            return views

        except TelegramBadRequest as e:
            if "message not found" in str(e).lower():
                # Cache negative result
                await performance_manager.cache.set(
                    cache_key, 0, 3600
                )  # 1 hour for not found
                return 0
            raise

        except Exception as e:
            logger.debug(f"⚠️ Failed to get views for post {post_id}: {e}")
            return None

    async def _batch_update_views(self, updates: list[dict]) -> int:
        """📊 High-performance batch database updates"""
        if not updates:
            return 0

        try:
            # Use optimized pool for batch updates
            async with performance_manager.pool.acquire_connection() as conn:
                # Prepare batch update query
                query = """
                    UPDATE analytics 
                    SET view_count = $2, updated_at = NOW()
                    WHERE id = $1 AND view_count != $2
                """

                # Execute batch update
                update_params = [
                    (update["post_id"], update["new_views"]) for update in updates
                ]
                results = await performance_manager.query_optimizer.execute_batched(
                    performance_manager.pool._pool, query, update_params, batch_size=50
                )

                # Count successful updates
                successful_updates = sum(
                    1 for result in results if not isinstance(result, Exception)
                )

                # Invalidate related caches
                await self._invalidate_analytics_cache(updates)

                return successful_updates

        except Exception as e:
            logger.error(f"❌ Batch update failed: {e}")
            return 0

    async def _invalidate_analytics_cache(self, updates: list[dict]):
        """🗑️ Smart cache invalidation"""
        cache_patterns = set()

        for update in updates:
            channel_id = update["channel_id"]
            # Invalidate channel-related caches
            cache_patterns.add(f"analytics:{channel_id}:*")
            cache_patterns.add(f"channel_stats:{channel_id}:*")

        # Flush matching patterns
        for pattern in cache_patterns:
            await performance_manager.cache.flush_pattern(pattern)

    async def _merge_stats(self, total_stats: dict[str, int], batch_results: list):
        """🔄 Merge statistics from concurrent operations"""
        for result in batch_results:
            if isinstance(result, dict):
                for key in total_stats:
                    if key in result:
                        total_stats[key] += result[key]

    async def _cache_performance_stats(self, stats: dict[str, Any]):
        """📈 Cache performance metrics for monitoring"""
        cache_key = "performance:analytics:last_run"
        await performance_manager.cache.set(cache_key, stats, 3600)  # 1 hour

    @cache_result("channel_analytics", ttl=PerformanceConfig.CACHE_ANALYTICS_TTL)
    async def get_channel_analytics_cached(
        self, channel_id: int, days: int = 7
    ) -> dict[str, Any]:
        """📊 Cached channel analytics with performance optimization"""
        return await self.analytics_repository.get_channel_analytics(channel_id, days)

    @cache_result("top_posts", ttl=PerformanceConfig.CACHE_ANALYTICS_TTL)
    async def get_top_posts_cached(
        self, channel_id: int, limit: int = 10
    ) -> list[dict]:
        """🏆 Cached top posts retrieval"""
        return await self.analytics_repository.get_top_posts(channel_id, limit)

    @performance_timer("bulk_analytics_processing")
    async def process_bulk_analytics(self, data: list[dict]) -> dict[str, int]:
        """⚡ Bulk analytics processing with optimization"""
        stats = {"processed": 0, "inserted": 0, "errors": 0}

        try:
            # Use query optimizer for batch processing
            batches = performance_manager.query_optimizer.batch_queries(data, 100)

            for batch in batches:
                batch_stats = await self._process_analytics_batch(batch)
                for key in stats:
                    stats[key] += batch_stats.get(key, 0)

            # Invalidate related caches
            await performance_manager.cache.flush_pattern("analytics:*")

        except Exception as e:
            logger.error(f"❌ Bulk analytics processing failed: {e}")
            stats["errors"] += len(data)

        return stats

    async def _process_analytics_batch(self, batch: list[dict]) -> dict[str, int]:
        """Process a batch of analytics data"""
        stats = {"processed": len(batch), "inserted": 0, "errors": 0}

        try:
            async with performance_manager.pool.acquire_connection() as conn:
                # Batch insert query
                query = """
                    INSERT INTO analytics (channel_id, message_id, view_count, created_at)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (channel_id, message_id) 
                    DO UPDATE SET view_count = EXCLUDED.view_count, updated_at = NOW()
                """

                insert_params = [
                    (
                        item["channel_id"],
                        item["message_id"],
                        item["view_count"],
                        item.get("created_at", datetime.now()),
                    )
                    for item in batch
                ]

                await conn.executemany(query, insert_params)
                stats["inserted"] = len(batch)

        except Exception as e:
            logger.error(f"❌ Analytics batch processing failed: {e}")
            stats["errors"] = len(batch)

        return stats

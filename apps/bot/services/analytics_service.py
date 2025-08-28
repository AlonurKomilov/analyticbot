"""
🚀 UNIFIED ANALYTICS SERVICE
High-performance analytics with caching, batch processing, and comprehensive functionality
"""

import asyncio
import logging
from collections import defaultdict
from datetime import datetime
from typing import Any

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest

from apps.bot.database.performance import (
    PerformanceConfig,
    cache_result,
    performance_manager,
    performance_timer,
)
from infra.db.repositories.analytics_repository import AsyncpgAnalyticsRepository
from apps.bot.domain.constants import DEFAULT_BATCH_SIZE, DEFAULT_CACHE_TTL
from apps.bot.services.prometheus_service import prometheus_service, prometheus_timer
from apps.bot.utils.error_handler import ErrorContext, ErrorHandler

logger = logging.getLogger(__name__)


class AnalyticsService:
    """🚀 Unified high-performance analytics service with advanced optimization"""

    def __init__(self, bot: Bot, analytics_repository: Any):
        self.analytics_repository = analytics_repository
        self.bot = bot
        self._rate_limit_delay = 0.1
        self._batch_size = getattr(PerformanceConfig, "TASK_BATCH_SIZE", 50)
        self._concurrent_limit = 10
        self._semaphore = asyncio.Semaphore(self._concurrent_limit)
        if not hasattr(PerformanceConfig, "TASK_BATCH_SIZE"):
            self._batch_size = 50

    @performance_timer("update_all_post_views")
    @prometheus_timer("telegram_api_optimized")
    async def update_all_post_views(self) -> dict[str, int]:
        """
        🔥 Unified optimized mass view update with intelligent batching
        Combines legacy reliability with modern performance optimizations
        """
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
            posts = await self._get_posts_to_track_cached()
            if not posts:
                logger.info("📊 No posts found for view tracking.")
                return stats
            logger.info(f"🚀 Starting unified view update for {len(posts)} posts")
            if hasattr(self, "_smart_group_posts"):
                grouped = await self._smart_group_posts(posts)
            else:
                grouped = self._simple_group_posts(posts)
            if self._concurrent_limit > 1:
                await self._process_channels_concurrent(grouped, stats)
            else:
                await self._process_channels_sequential(grouped, stats)
            stats["duration"] = asyncio.get_event_loop().time() - start_time
            logger.info(
                f"⚡ Unified view update completed in {stats['duration']:.2f}s. Processed: {stats['processed']}, Updated: {stats['updated']}, Cached: {stats['cached']}, Errors: {stats['errors']}"
            )
            prometheus_service.record_post_views_update(stats["updated"])
            if hasattr(self, "_cache_performance_stats"):
                await self._cache_performance_stats(stats)
        except Exception as e:
            context = ErrorContext().add("operation", "update_all_post_views")
            ErrorHandler.log_error(e, context)
            stats["errors"] += 1
        return stats

    @cache_result("posts_to_track", ttl=getattr(PerformanceConfig, "CACHE_ANALYTICS_TTL", 300))
    async def _get_posts_to_track_cached(self) -> list[dict]:
        """📦 Cached posts retrieval with fallback to direct call"""
        try:
            return await self.analytics_repository.get_all_posts_to_track_views()
        except Exception:
            return await self.analytics_repository.get_all_posts_to_track_views()

    def _simple_group_posts(self, posts: list[dict]) -> dict[int, list[dict]]:
        """Simple post grouping for reliable processing"""
        grouped: dict[int, list[dict]] = defaultdict(list)
        for post in posts:
            grouped[post["channel_id"]].append(post)
        return grouped

    async def _smart_group_posts(self, posts: list[dict]) -> dict[int, list[dict]]:
        """🧠 Intelligent post grouping with priority optimization"""
        grouped = defaultdict(list)
        for post in posts:
            channel_id = post["channel_id"]
            last_update = post.get("updated_at")
            if last_update:
                hours_since_update = (datetime.now() - last_update).total_seconds() / 3600
                post["_priority"] = min(hours_since_update, 24)
            else:
                post["_priority"] = 24
            grouped[channel_id].append(post)
        sorted_grouped = {}
        for channel_id, channel_posts in grouped.items():
            total_priority = sum(post["_priority"] for post in channel_posts)
            sorted_grouped[channel_id] = sorted(
                channel_posts, key=lambda x: x["_priority"], reverse=True
            )
        return dict(
            sorted(
                sorted_grouped.items(),
                key=lambda x: sum(p["_priority"] for p in x[1]),
                reverse=True,
            )
        )

    async def _process_channels_concurrent(
        self, grouped: dict[int, list[dict]], stats: dict[str, int]
    ):
        """Process channels concurrently with rate limiting"""
        tasks = []
        for channel_id, channel_posts in grouped.items():
            if hasattr(self, "_process_channel_optimized"):
                task = asyncio.create_task(
                    self._process_channel_optimized(channel_id, channel_posts)
                )
            else:
                task = asyncio.create_task(self._process_channel_posts(channel_id, channel_posts))
            tasks.append(task)
            if len(tasks) >= self._concurrent_limit:
                completed_stats = await asyncio.gather(*tasks, return_exceptions=True)
                await self._merge_stats(stats, completed_stats)
                tasks = []
                await asyncio.sleep(self._rate_limit_delay)
        if tasks:
            completed_stats = await asyncio.gather(*tasks, return_exceptions=True)
            await self._merge_stats(stats, completed_stats)

    async def _process_channels_sequential(
        self, grouped: dict[int, list[dict]], stats: dict[str, int]
    ):
        """Process channels sequentially for maximum reliability"""
        for channel_id, channel_posts in grouped.items():
            channel_stats = await self._process_channel_posts(channel_id, channel_posts)
            for key in stats:
                stats[key] += channel_stats.get(key, 0)
            await asyncio.sleep(self._rate_limit_delay)

    async def _process_channel_optimized(
        self, channel_id: int, posts: list[dict]
    ) -> dict[str, int]:
        """⚡ High-performance channel processing with concurrency control"""
        async with self._semaphore:
            stats = {"processed": 0, "updated": 0, "errors": 0, "skipped": 0, "cached": 0}
            if hasattr(performance_manager, "cache"):
                cache_key = f"channel_problems:{channel_id}"
                if await performance_manager.cache.get(cache_key):
                    logger.debug(f"⚠️ Skipping problematic channel {channel_id}")
                    stats["skipped"] = len(posts)
                    return stats
            try:
                micro_batch_size = min(10, len(posts) // 4 + 1)
                for i in range(0, len(posts), micro_batch_size):
                    micro_batch = posts[i : i + micro_batch_size]
                    if hasattr(self, "_process_micro_batch"):
                        batch_stats = await self._process_micro_batch(channel_id, micro_batch)
                    else:
                        batch_stats = await self._process_post_batch(channel_id, micro_batch)
                    for key in stats:
                        stats[key] += batch_stats.get(key, 0)
                    success_rate = (
                        batch_stats.get("updated", 0) / len(micro_batch) if micro_batch else 1
                    )
                    delay = self._rate_limit_delay * (2 - success_rate)
                    await asyncio.sleep(delay)
            except Exception as e:
                if hasattr(performance_manager, "cache"):
                    cache_key = f"channel_problems:{channel_id}"
                    await performance_manager.cache.set(cache_key, True, 300)
                logger.error(f"❌ Channel {channel_id} processing failed: {e}")
                stats["errors"] += len(posts)
            return stats

    async def _process_channel_posts(self, channel_id: int, posts: list[dict]) -> dict[str, int]:
        """Process posts for a specific channel (legacy reliable method)"""
        stats = {"processed": 0, "updated": 0, "errors": 0, "skipped": 0}
        for i in range(0, len(posts), self._batch_size):
            batch = posts[i : i + self._batch_size]
            batch_stats = await self._process_post_batch(channel_id, batch)
            for key in stats:
                stats[key] += batch_stats.get(key, 0)
            if i + self._batch_size < len(posts):
                await asyncio.sleep(self._rate_limit_delay)
        return stats

    async def _process_micro_batch(self, channel_id: int, batch: list[dict]) -> dict[str, int]:
        """⚡ Ultra-fast micro-batch processing"""
        stats = {"processed": 0, "updated": 0, "errors": 0, "skipped": 0, "cached": 0}
        try:
            view_tasks = []
            for post in batch:
                if hasattr(self, "_get_post_views_with_cache"):
                    task = self._get_post_views_with_cache(channel_id, post)
                else:
                    task = self._get_single_post_views(channel_id, post)
                view_tasks.append(task)
            view_results = await asyncio.gather(*view_tasks, return_exceptions=True)
            updates_to_execute = []
            for post, view_result in zip(batch, view_results, strict=False):
                stats["processed"] += 1
                if isinstance(view_result, Exception):
                    stats["errors"] += 1
                    continue
                if view_result is None:
                    stats["skipped"] += 1
                    continue
                if view_result == -1:
                    stats["cached"] += 1
                    continue
                if view_result != post.get("view_count", 0):
                    updates_to_execute.append(
                        {
                            "post_id": post["id"],
                            "new_views": view_result,
                            "message_id": post["message_id"],
                            "channel_id": post["channel_id"],
                        }
                    )
            if updates_to_execute:
                if hasattr(self, "_batch_update_views"):
                    updated_count = await self._batch_update_views(updates_to_execute)
                else:
                    updated_count = await self._sequential_update_views(updates_to_execute)
                stats["updated"] = updated_count
        except Exception as e:
            logger.error(f"❌ Micro-batch processing failed for channel {channel_id}: {e}")
            stats["errors"] += len(batch)
        return stats

    async def _process_post_batch(self, channel_id: int, batch: list[dict]) -> dict[str, int]:
        """Process a batch of posts from the same channel (legacy reliable method)"""
        stats = {"processed": 0, "updated": 0, "errors": 0, "skipped": 0}
        message_ids = [post["message_id"] for post in batch]
        try:
            messages = await self.bot.get_messages(chat_id=channel_id, message_ids=message_ids)
            msg_map = {m.message_id: m for m in messages if m}
            for post in batch:
                stats["processed"] += 1
                message = msg_map.get(post["message_id"])
                if not message:
                    stats["skipped"] += 1
                    continue
                if message.views is None:
                    stats["skipped"] += 1
                    continue
                try:
                    await self.analytics_repository.update_post_views(
                        scheduled_post_id=post["id"], views=message.views
                    )
                    stats["updated"] += 1
                except Exception as e:
                    context = (
                        ErrorContext()
                        .add("operation", "update_post_views")
                        .add("post_id", post["id"])
                        .add("channel_id", channel_id)
                    )
                    ErrorHandler.handle_database_error(e, context)
                    stats["errors"] += 1
        except TelegramBadRequest as e:
            context = (
                ErrorContext()
                .add("operation", "get_messages_batch")
                .add("channel_id", channel_id)
                .add("batch_size", len(batch))
            )
            ErrorHandler.handle_telegram_api_error(e, context)
            stats["errors"] += len(batch)
        except TelegramAPIError as e:
            context = (
                ErrorContext().add("operation", "get_messages_batch").add("channel_id", channel_id)
            )
            ErrorHandler.handle_telegram_api_error(e, context)
            stats["errors"] += len(batch)
        except Exception as e:
            context = (
                ErrorContext().add("operation", "process_post_batch").add("channel_id", channel_id)
            )
            ErrorHandler.log_error(e, context)
            stats["errors"] += len(batch)
        return stats

    async def _get_post_views_with_cache(self, channel_id: int, post: dict) -> int | None:
        """📦 Get post views with intelligent caching"""
        if not hasattr(performance_manager, "cache"):
            return await self._get_single_post_views(channel_id, post)
        message_id = post["message_id"]
        post_id = post["id"]
        cache_key = f"post_views:{channel_id}:{message_id}"
        cached_views = await performance_manager.cache.get(cache_key)
        if cached_views is not None:
            return -1
        try:
            message = await self.bot.forward_message(
                chat_id=channel_id, from_chat_id=channel_id, message_id=message_id
            )
            views = getattr(message, "views", 0) or 0
            cache_ttl = 300 if views > 0 else 60
            await performance_manager.cache.set(cache_key, views, cache_ttl)
            return views
        except TelegramBadRequest as e:
            if "message not found" in str(e).lower():
                await performance_manager.cache.set(cache_key, 0, 3600)
                return 0
            raise
        except Exception as e:
            logger.debug(f"⚠️ Failed to get views for post {post_id}: {e}")
            return None

    async def _get_single_post_views(self, channel_id: int, post: dict) -> int | None:
        """Get views for a single post without caching"""
        try:
            message = await self.bot.get_message(chat_id=channel_id, message_id=post["message_id"])
            return getattr(message, "views", 0) or 0
        except Exception as e:
            logger.debug(f"⚠️ Failed to get views for post {post['id']}: {e}")
            return None

    async def _batch_update_views(self, updates: list[dict]) -> int:
        """📊 High-performance batch database updates"""
        if not updates:
            return 0
        try:
            if hasattr(performance_manager, "pool"):
                async with performance_manager.pool.acquire_connection() as conn:
                    query = "\n                        UPDATE analytics \n                        SET view_count = $2, updated_at = NOW()\n                        WHERE id = $1 AND view_count != $2\n                    "
                    update_params = [(update["post_id"], update["new_views"]) for update in updates]
                    if hasattr(performance_manager, "query_optimizer"):
                        results = await performance_manager.query_optimizer.execute_batched(
                            performance_manager.pool._pool, query, update_params, batch_size=50
                        )
                        successful_updates = sum(
                            1 for result in results if not isinstance(result, Exception)
                        )
                    else:
                        await conn.executemany(query, update_params)
                        successful_updates = len(updates)
                    if hasattr(self, "_invalidate_analytics_cache"):
                        await self._invalidate_analytics_cache(updates)
                    return successful_updates
            else:
                return await self._sequential_update_views(updates)
        except Exception as e:
            logger.error(f"❌ Batch update failed: {e}")
            return 0

    async def _sequential_update_views(self, updates: list[dict]) -> int:
        """Sequential view updates as fallback"""
        successful_updates = 0
        for update in updates:
            try:
                await self.analytics_repository.update_post_views(
                    scheduled_post_id=update["post_id"], views=update["new_views"]
                )
                successful_updates += 1
            except Exception as e:
                logger.debug(f"Failed to update post {update['post_id']}: {e}")
        return successful_updates

    async def _invalidate_analytics_cache(self, updates: list[dict]):
        """🗑️ Smart cache invalidation"""
        if not hasattr(performance_manager, "cache"):
            return
        cache_patterns = set()
        for update in updates:
            channel_id = update["channel_id"]
            cache_patterns.add(f"analytics:{channel_id}:*")
            cache_patterns.add(f"channel_stats:{channel_id}:*")
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
        if hasattr(performance_manager, "cache"):
            cache_key = "performance:analytics:last_run"
            await performance_manager.cache.set(cache_key, stats, 3600)

    @cache_result("channel_analytics", ttl=getattr(PerformanceConfig, "CACHE_ANALYTICS_TTL", 300))
    async def get_channel_analytics_cached(self, channel_id: int, days: int = 7) -> dict[str, Any]:
        """📊 Cached channel analytics with performance optimization"""
        try:
            return await self.analytics_repository.get_channel_analytics(channel_id, days)
        except Exception:
            return await self.analytics_repository.get_channel_analytics(channel_id, days)

    @cache_result("top_posts", ttl=getattr(PerformanceConfig, "CACHE_ANALYTICS_TTL", 300))
    async def get_top_posts_cached(self, channel_id: int, limit: int = 10) -> list[dict]:
        """🏆 Cached top posts retrieval"""
        try:
            return await self.analytics_repository.get_top_posts(channel_id, limit)
        except Exception:
            return await self.analytics_repository.get_top_posts(channel_id, limit)

    async def get_posts_ordered_by_views(self, channel_id: int) -> list[dict] | None:
        """
        Get posts ordered by views with error handling.
        """
        try:
            return await self.analytics_repository.get_posts_ordered_by_views(channel_id)
        except Exception as e:
            context = (
                ErrorContext()
                .add("operation", "get_posts_ordered_by_views")
                .add("channel_id", channel_id)
            )
            ErrorHandler.handle_database_error(e, context)
            return None

    async def create_views_chart(self, channel_id: int, limit: int = 10) -> bytes:
        """Generate a simple bar chart of top N posts by views with error handling."""
        try:
            posts = await self.get_posts_ordered_by_views(channel_id)
            if not posts:
                logger.info(f"No posts found for channel {channel_id} to create chart")
                return b""
            top_posts = posts[:limit]
            post_ids = [str(p["id"]) for p in top_posts]
            views = [int(p.get("views") or 0) for p in top_posts]
            from io import BytesIO

            import matplotlib.pyplot as plt

            fig, ax = plt.subplots(figsize=(min(12, 1.2 * len(post_ids)), 4))
            ax.bar(post_ids, views, color="#4C72B0")
            ax.set_title(f"Top {limit} Posts by Views")
            ax.set_xlabel("Post ID")
            ax.set_ylabel("Views")
            for i, v in enumerate(views):
                ax.text(i, v, str(v), ha="center", va="bottom", fontsize=8)
            fig.tight_layout()
            buf = BytesIO()
            fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
            plt.close(fig)
            buf.seek(0)
            logger.info(f"Chart created for channel {channel_id} with {len(top_posts)} posts")
            return buf.read()
        except ImportError:
            logger.warning("matplotlib not available for chart generation")
            return b""
        except Exception as e:
            context = (
                ErrorContext()
                .add("operation", "create_views_chart")
                .add("channel_id", channel_id)
                .add("limit", limit)
            )
            ErrorHandler.log_error(e, context)
            return b""

    async def get_post_views(
        self, scheduled_post_id: int, user_id: int | None = None
    ) -> int | None:
        """
        Return stored view count for a scheduled post with error handling.

        Args:
            scheduled_post_id: The ID of the scheduled post
            user_id: Optional user ID for future authorization checks
        """
        try:
            return await self.analytics_repository.get_post_views(scheduled_post_id)
        except Exception as e:
            context = (
                ErrorContext()
                .add("operation", "get_post_views")
                .add("scheduled_post_id", scheduled_post_id)
                .add("user_id", user_id)
            )
            ErrorHandler.handle_database_error(e, context)
            return None

    async def get_total_users_count(self) -> int:
        """Get total users count with error handling."""
        try:
            return await self.analytics_repository.get_total_users_count()
        except Exception as e:
            context = ErrorContext().add("operation", "get_total_users_count")
            ErrorHandler.handle_database_error(e, context)
            return 0

    async def get_total_channels_count(self) -> int:
        """Get total channels count with error handling."""
        try:
            return await self.analytics_repository.get_total_channels_count()
        except Exception as e:
            context = ErrorContext().add("operation", "get_total_channels_count")
            ErrorHandler.handle_database_error(e, context)
            return 0

    async def get_total_posts_count(self) -> int:
        """Get total posts count with error handling."""
        try:
            return await self.analytics_repository.get_total_posts_count()
        except Exception as e:
            context = ErrorContext().add("operation", "get_total_posts_count")
            ErrorHandler.handle_database_error(e, context)
            return 0

    async def get_analytics_data(
        self,
        channel_id: int | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Get analytics data with filtering"""
        try:
            return await self.analytics_repository.get_analytics_data(
                channel_id=channel_id, start_date=start_date, end_date=end_date, limit=limit
            )
        except Exception as e:
            context = (
                ErrorContext().add("operation", "get_analytics_data").add("channel_id", channel_id)
            )
            ErrorHandler.handle_database_error(e, context)
            return []

    async def get_analytics_summary(
        self, channel_id: int, start_date: datetime, end_date: datetime
    ) -> dict[str, Any]:
        """Get analytics summary for a channel"""
        try:
            return await self.analytics_repository.get_analytics_summary(
                channel_id=channel_id, start_date=start_date, end_date=end_date
            )
        except Exception as e:
            context = (
                ErrorContext()
                .add("operation", "get_analytics_summary")
                .add("channel_id", channel_id)
            )
            ErrorHandler.handle_database_error(e, context)
            return {}

    async def get_dashboard_data(self, channel_id: int) -> dict[str, Any]:
        """Get comprehensive dashboard data for a channel"""
        try:
            return await self.analytics_repository.get_dashboard_data(channel_id)
        except Exception as e:
            context = (
                ErrorContext().add("operation", "get_dashboard_data").add("channel_id", channel_id)
            )
            ErrorHandler.handle_database_error(e, context)
            return {}

    async def refresh_channel_analytics(self, channel_id: int):
        """Manually trigger analytics refresh for a channel"""
        try:
            if hasattr(self, "_invalidate_analytics_cache"):
                await self._invalidate_analytics_cache([{"channel_id": channel_id}])
            posts = await self.analytics_repository.get_channel_posts_for_tracking(channel_id)
            if posts:
                await self._process_channel_posts(channel_id, posts)
        except Exception as e:
            context = (
                ErrorContext()
                .add("operation", "refresh_channel_analytics")
                .add("channel_id", channel_id)
            )
            ErrorHandler.handle_database_error(e, context)

    @performance_timer("bulk_analytics_processing")
    async def process_bulk_analytics(self, data: list[dict]) -> dict[str, int]:
        """⚡ Bulk analytics processing with optimization"""
        stats = {"processed": 0, "inserted": 0, "errors": 0}
        try:
            if hasattr(performance_manager, "query_optimizer"):
                batches = performance_manager.query_optimizer.batch_queries(data, 100)
                for batch in batches:
                    batch_stats = await self._process_analytics_batch(batch)
                    for key in stats:
                        stats[key] += batch_stats.get(key, 0)
                if hasattr(performance_manager, "cache"):
                    await performance_manager.cache.flush_pattern("analytics:*")
            else:
                for item in data:
                    try:
                        await self.analytics_repository.insert_analytics_data(item)
                        stats["inserted"] += 1
                    except Exception:
                        stats["errors"] += 1
                    stats["processed"] += 1
        except Exception as e:
            logger.error(f"❌ Bulk analytics processing failed: {e}")
            stats["errors"] += len(data)
        return stats

    async def _process_analytics_batch(self, batch: list[dict]) -> dict[str, int]:
        """Process a batch of analytics data"""
        stats = {"processed": len(batch), "inserted": 0, "errors": 0}
        try:
            if hasattr(performance_manager, "pool"):
                async with performance_manager.pool.acquire_connection() as conn:
                    query = "\n                        INSERT INTO analytics (channel_id, message_id, view_count, created_at)\n                        VALUES ($1, $2, $3, $4)\n                        ON CONFLICT (channel_id, message_id) \n                        DO UPDATE SET view_count = EXCLUDED.view_count, updated_at = NOW()\n                    "
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
            else:
                for item in batch:
                    await self.analytics_repository.insert_analytics_data(item)
                    stats["inserted"] += 1
        except Exception as e:
            logger.error(f"❌ Analytics batch processing failed: {e}")
            stats["errors"] = len(batch)
        return stats
        "Process a batch of posts from the same channel"
        stats = {"processed": 0, "updated": 0, "errors": 0, "skipped": 0}
        message_ids = [post["message_id"] for post in batch]
        try:
            messages = await self.bot.get_messages(chat_id=channel_id, message_ids=message_ids)
            msg_map = {m.message_id: m for m in messages if m}
            for post in batch:
                stats["processed"] += 1
                message = msg_map.get(post["message_id"])
                if not message:
                    stats["skipped"] += 1
                    continue
                if message.views is None:
                    stats["skipped"] += 1
                    continue
                try:
                    await self.analytics_repository.update_post_views(
                        scheduled_post_id=post["id"], views=message.views
                    )
                    stats["updated"] += 1
                except Exception as e:
                    context = (
                        ErrorContext()
                        .add("operation", "update_post_views")
                        .add("post_id", post["id"])
                        .add("channel_id", channel_id)
                    )
                    ErrorHandler.handle_database_error(e, context)
                    stats["errors"] += 1
        except TelegramBadRequest as e:
            context = (
                ErrorContext()
                .add("operation", "get_messages_batch")
                .add("channel_id", channel_id)
                .add("batch_size", len(batch))
            )
            ErrorHandler.handle_telegram_api_error(e, context)
            stats["errors"] += len(batch)
        except TelegramAPIError as e:
            context = (
                ErrorContext().add("operation", "get_messages_batch").add("channel_id", channel_id)
            )
            ErrorHandler.handle_telegram_api_error(e, context)
            stats["errors"] += len(batch)
        except Exception as e:
            context = (
                ErrorContext().add("operation", "process_post_batch").add("channel_id", channel_id)
            )
            ErrorHandler.log_error(e, context)
            stats["errors"] += len(batch)
        return stats

    async def get_posts_ordered_by_views(self, channel_id: int) -> list[dict] | None:
        """
        Get posts ordered by views with error handling.
        """
        try:
            return await self.analytics_repository.get_posts_ordered_by_views(channel_id)
        except Exception as e:
            context = (
                ErrorContext()
                .add("operation", "get_posts_ordered_by_views")
                .add("channel_id", channel_id)
            )
            ErrorHandler.handle_database_error(e, context)
            return None

    async def create_views_chart(self, channel_id: int, limit: int = 10) -> bytes:
        """Generate a simple bar chart of top N posts by views with error handling."""
        try:
            posts = await self.get_posts_ordered_by_views(channel_id)
            if not posts:
                logger.info(f"No posts found for channel {channel_id} to create chart")
                return b""
            top_posts = posts[:limit]
            post_ids = [str(p["id"]) for p in top_posts]
            views = [int(p.get("views") or 0) for p in top_posts]
            from io import BytesIO

            import matplotlib.pyplot as plt

            fig, ax = plt.subplots(figsize=(min(12, 1.2 * len(post_ids)), 4))
            ax.bar(post_ids, views, color="#4C72B0")
            ax.set_title(f"Top {limit} Posts by Views")
            ax.set_xlabel("Post ID")
            ax.set_ylabel("Views")
            for i, v in enumerate(views):
                ax.text(i, v, str(v), ha="center", va="bottom", fontsize=8)
            fig.tight_layout()
            buf = BytesIO()
            fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
            plt.close(fig)
            buf.seek(0)
            logger.info(f"Chart created for channel {channel_id} with {len(top_posts)} posts")
            return buf.read()
        except ImportError:
            logger.warning("matplotlib not available for chart generation")
            return b""
        except Exception as e:
            context = (
                ErrorContext()
                .add("operation", "create_views_chart")
                .add("channel_id", channel_id)
                .add("limit", limit)
            )
            ErrorHandler.log_error(e, context)
            return b""

    async def get_post_views(
        self, scheduled_post_id: int, user_id: int | None = None
    ) -> int | None:
        """
        Return stored view count for a scheduled post with error handling.

        Args:
            scheduled_post_id: The ID of the scheduled post
            user_id: Optional user ID for future authorization checks
        """
        try:
            return await self.analytics_repository.get_post_views(scheduled_post_id)
        except Exception as e:
            context = (
                ErrorContext()
                .add("operation", "get_post_views")
                .add("scheduled_post_id", scheduled_post_id)
                .add("user_id", user_id)
            )
            ErrorHandler.handle_database_error(e, context)
            return None

    async def get_total_users_count(self) -> int:
        """Get total users count with error handling."""
        try:
            return await self.analytics_repository.get_total_users_count()
        except Exception as e:
            context = ErrorContext().add("operation", "get_total_users_count")
            ErrorHandler.handle_database_error(e, context)
            return 0

    async def get_total_channels_count(self) -> int:
        """Get total channels count with error handling."""
        try:
            return await self.analytics_repository.get_total_channels_count()
        except Exception as e:
            context = ErrorContext().add("operation", "get_total_channels_count")
            ErrorHandler.handle_database_error(e, context)
            return 0

    async def get_total_posts_count(self) -> int:
        """Get total posts count with error handling."""
        try:
            return await self.analytics_repository.get_total_posts_count()
        except Exception as e:
            context = ErrorContext().add("operation", "get_total_posts_count")
            ErrorHandler.handle_database_error(e, context)
            return 0

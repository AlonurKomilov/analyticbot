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

    async def update_posts_views_batch(
        self, posts_data: list[dict], batch_size: int = 50
    ) -> dict[str, int]:
        """
        🚀 OPTIMIZED BATCH PROCESSING - Enhanced version with concurrent processing
        Process view updates in optimized batches with semaphore-based concurrency control
        """
        stats = {
            "total_posts": len(posts_data),
            "processed": 0,
            "updated": 0,
            "errors": 0,
            "skipped": 0,
            "batch_count": 0,
            "concurrent_batches": 0,
        }

        if not posts_data:
            logger.info("📊 No posts provided for batch view update")
            return stats

        # Group posts by channel for efficient API calls
        channel_groups = defaultdict(list)
        for post in posts_data:
            channel_groups[post["channel_id"]].append(post)

        # Process channels concurrently with semaphore control
        semaphore = asyncio.Semaphore(self._concurrent_limit)
        tasks = []

        for channel_id, channel_posts in channel_groups.items():
            task = asyncio.create_task(
                self._process_channel_batch_optimized(
                    channel_id, channel_posts, batch_size, semaphore
                )
            )
            tasks.append(task)

        # Execute all channel processing tasks
        channel_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Aggregate statistics
        for result in channel_results:
            if isinstance(result, dict):
                for key in ["processed", "updated", "errors", "skipped", "batch_count"]:
                    stats[key] += result.get(key, 0)
            elif isinstance(result, Exception):
                logger.error(f"Channel batch processing failed: {result}")
                stats["errors"] += 1

        stats["concurrent_batches"] = len(channel_groups)
        logger.info(f"⚡ Batch processing completed: {stats}")
        return stats

    async def _process_channel_batch_optimized(
        self, channel_id: int, posts: list[dict], batch_size: int, semaphore: asyncio.Semaphore
    ) -> dict[str, int]:
        """
        Process posts for a single channel in optimized batches
        """
        async with semaphore:
            stats = {"processed": 0, "updated": 0, "errors": 0, "skipped": 0, "batch_count": 0}

            # Process posts in smaller batches to avoid API limits
            for i in range(0, len(posts), batch_size):
                batch = posts[i : i + batch_size]
                batch_stats = await self._process_post_batch_optimized(channel_id, batch)

                # Aggregate batch statistics
                for key in ["processed", "updated", "errors", "skipped"]:
                    stats[key] += batch_stats.get(key, 0)
                stats["batch_count"] += 1

                # Rate limiting between batches
                if i + batch_size < len(posts):
                    await asyncio.sleep(self._rate_limit_delay)

            return stats

    async def _process_post_batch_optimized(
        self, channel_id: int, batch: list[dict]
    ) -> dict[str, int]:
        """
        Optimized batch processing with concurrent view fetching and bulk database updates
        """
        stats = {"processed": 0, "updated": 0, "errors": 0, "skipped": 0}

        try:
            # Step 1: Fetch all view counts concurrently
            view_tasks = []
            for post in batch:
                task = asyncio.create_task(
                    self._fetch_single_post_views(channel_id, post["message_id"])
                )
                view_tasks.append(task)

            # Wait for all view fetches to complete
            view_results = await asyncio.gather(*view_tasks, return_exceptions=True)

            # Step 2: Prepare batch updates
            updates_needed = []
            for post, view_result in zip(batch, view_results, strict=False):
                stats["processed"] += 1

                if isinstance(view_result, Exception):
                    logger.debug(f"Failed to fetch views for post {post['id']}: {view_result}")
                    stats["errors"] += 1
                    continue

                if view_result is None:
                    stats["skipped"] += 1
                    continue

                # Check if update is needed (avoid unnecessary writes)
                current_views = post.get("views", 0) or 0
                if view_result != current_views:
                    updates_needed.append(
                        {
                            "post_id": post["id"],
                            "new_views": view_result,
                            "old_views": current_views,
                        }
                    )

            # Step 3: Execute batch database updates
            if updates_needed:
                updated_count = await self._batch_update_views(updates_needed)
                stats["updated"] = updated_count

        except Exception as e:
            logger.error(f"Optimized batch processing failed for channel {channel_id}: {e}")
            stats["errors"] += len(batch)

        return stats

    async def _fetch_single_post_views(self, channel_id: int, message_id: int) -> int | None:
        """
        Fetch view count for a single post with error handling
        """
        try:
            message = await self.bot.get_message(chat_id=channel_id, message_id=message_id)
            return getattr(message, "views", None)
        except TelegramBadRequest as e:
            if "message not found" in str(e).lower():
                return 0  # Message deleted, return 0 views
            raise
        except Exception as e:
            logger.debug(f"Failed to fetch views for message {message_id}: {e}")
            return None

    async def _batch_update_views(self, updates: list[dict]) -> int:
        """
        🚀 ENHANCED BATCH DATABASE UPDATES with transaction support and conflict handling
        Execute database updates in a single optimized transaction
        """
        if not updates:
            return 0

        try:
            # Prepare batch update query
            query = """
                UPDATE scheduled_posts
                SET views = $2, updated_at = NOW()
                WHERE id = $1 AND (views IS NULL OR views != $2)
            """

            update_params = [(update["post_id"], update["new_views"]) for update in updates]

            # Execute batch update using connection pool
            updated_count = 0
            async with self.analytics_repository._pool.acquire() as conn:
                async with conn.transaction():
                    for post_id, new_views in update_params:
                        result = await conn.execute(query, post_id, new_views)
                        # Extract number of affected rows from result
                        if hasattr(result, "split") and len(result.split()) > 1:
                            try:
                                affected_rows = int(result.split()[1])
                                updated_count += affected_rows
                            except (ValueError, IndexError):
                                updated_count += 1  # Assume 1 row affected as fallback
                        else:
                            updated_count += 1

            if updated_count > 0:
                logger.info(f"📊 Batch updated {updated_count} posts with new view counts")

            return updated_count

        except Exception as e:
            logger.error(f"❌ Batch update failed: {e}")
            # Fallback to sequential updates
            return await self._sequential_update_views(updates)

    # 🚀 NEW MEMORY-OPTIMIZED PROCESSING METHODS

    async def process_all_posts_memory_optimized(
        self, max_concurrent_batches: int = 5
    ) -> dict[str, int]:
        """
        🧠 ADVANCED MEMORY OPTIMIZATION: Process all posts using generators
        Uses async generators to minimize memory footprint for very large datasets
        """
        stats = {
            "total_processed": 0,
            "total_updated": 0,
            "total_errors": 0,
            "total_batches": 0,
            "peak_memory_batch_size": 0,
        }

        logger.info("🚀 Starting memory-optimized post processing using generators")

        try:
            # Use semaphore to limit concurrent processing
            semaphore = asyncio.Semaphore(max_concurrent_batches)

            # Process posts in memory-efficient batches using generator
            batch_tasks = []
            async for post_batch in self.analytics_repository.iter_posts_to_track_views(
                batch_size=200
            ):
                if len(post_batch) > stats["peak_memory_batch_size"]:
                    stats["peak_memory_batch_size"] = len(post_batch)

                # Create concurrent batch processing task
                task = asyncio.create_task(
                    self._process_memory_optimized_batch(post_batch, semaphore)
                )
                batch_tasks.append(task)
                stats["total_batches"] += 1

                # Process in groups to avoid excessive memory usage from too many tasks
                if len(batch_tasks) >= max_concurrent_batches:
                    completed_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

                    # Aggregate results and clear tasks
                    for result in completed_results:
                        if isinstance(result, dict):
                            stats["total_processed"] += result.get("processed", 0)
                            stats["total_updated"] += result.get("updated", 0)
                            stats["total_errors"] += result.get("errors", 0)
                        else:
                            logger.error(f"Batch processing error: {result}")
                            stats["total_errors"] += 1

                    batch_tasks = []  # Clear for next iteration

                    # Small delay to prevent overwhelming the system
                    await asyncio.sleep(0.1)

            # Process any remaining tasks
            if batch_tasks:
                completed_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                for result in completed_results:
                    if isinstance(result, dict):
                        stats["total_processed"] += result.get("processed", 0)
                        stats["total_updated"] += result.get("updated", 0)
                        stats["total_errors"] += result.get("errors", 0)

            success_rate = (
                (stats["total_updated"] / stats["total_processed"]) * 100
                if stats["total_processed"] > 0
                else 0
            )

            logger.info(
                f"⚡ Memory-optimized processing completed. "
                f"Batches: {stats['total_batches']}, "
                f"Processed: {stats['total_processed']}, "
                f"Updated: {stats['total_updated']}, "
                f"Success rate: {success_rate:.1f}%, "
                f"Peak batch size: {stats['peak_memory_batch_size']}"
            )

        except Exception as e:
            logger.error(f"❌ Memory-optimized processing failed: {e}")
            stats["total_errors"] += 1

        return stats

    async def _process_memory_optimized_batch(
        self, post_batch: list[dict], semaphore: asyncio.Semaphore
    ) -> dict[str, int]:
        """
        Process a single batch of posts with memory optimization
        """
        async with semaphore:
            return await self._process_post_batch_optimized(
                channel_id=post_batch[0]["channel_id"], batch=post_batch
            )

    async def stream_process_large_channel(self, channel_id: int) -> dict[str, int]:
        """
        🧠 MEMORY-OPTIMIZED: Process a single large channel using streaming
        Perfect for channels with thousands of posts
        """
        stats = {"processed": 0, "updated": 0, "errors": 0, "streamed_posts": 0}

        logger.info(f"🌊 Starting streaming processing for channel {channel_id}")

        batch = []
        batch_size = 100

        try:
            # Stream individual posts to minimize memory usage
            async for post in self.analytics_repository.stream_all_posts_to_track_views():
                if post["channel_id"] != channel_id:
                    continue

                batch.append(post)
                stats["streamed_posts"] += 1

                # Process when batch is full
                if len(batch) >= batch_size:
                    batch_stats = await self._process_post_batch_optimized(channel_id, batch)

                    stats["processed"] += batch_stats.get("processed", 0)
                    stats["updated"] += batch_stats.get("updated", 0)
                    stats["errors"] += batch_stats.get("errors", 0)

                    batch = []  # Clear batch
                    await asyncio.sleep(0.05)  # Small delay to prevent overwhelming

            # Process final batch
            if batch:
                batch_stats = await self._process_post_batch_optimized(channel_id, batch)
                stats["processed"] += batch_stats.get("processed", 0)
                stats["updated"] += batch_stats.get("updated", 0)
                stats["errors"] += batch_stats.get("errors", 0)

            logger.info(f"🌊 Streaming processing completed for channel {channel_id}: {stats}")

        except Exception as e:
            logger.error(f"❌ Streaming processing failed for channel {channel_id}: {e}")
            stats["errors"] += 1

        return stats

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

    @performance_timer("update_all_post_views_optimized")
    @prometheus_timer("telegram_api_concurrent")
    async def update_all_post_views(self) -> dict[str, int]:
        """
        🔥 AFTER - Optimized with concurrent processing and batching with semaphore
        Combines modern concurrency patterns with intelligent error handling
        """
        stats = {
            "processed": 0,
            "updated": 0,
            "errors": 0,
            "skipped": 0,
            "cached": 0,
            "duration": 0,
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

            # Use new optimized batch processing method
            batch_stats = await self.update_posts_views_batch(
                posts_data=posts,
                batch_size=min(self._batch_size, 25),  # Smaller batches for better concurrency
            )

            # Merge statistics
            for key in ["processed", "updated", "errors", "skipped"]:
                stats[key] = batch_stats.get(key, 0)

            stats["duration"] = asyncio.get_event_loop().time() - start_time

            # Log comprehensive performance metrics
            success_rate = (
                (stats["updated"] / stats["processed"]) * 100 if stats["processed"] > 0 else 0
            )
            throughput = stats["processed"] / stats["duration"] if stats["duration"] > 0 else 0

            logger.info(
                f"⚡ Optimized view update completed in {stats['duration']:.2f}s. "
                f"Processed: {stats['processed']}, Updated: {stats['updated']}, "
                f"Success rate: {success_rate:.1f}%, Throughput: {throughput:.1f} posts/sec, "
                f"Concurrent batches: {batch_stats.get('concurrent_batches', 0)}"
            )

            # Record metrics
            prometheus_service.record_post_views_update(stats["updated"])

            if hasattr(self, "_cache_performance_stats"):
                await self._cache_performance_stats(stats)

        except Exception as e:
            context = ErrorContext().add("operation", "update_all_post_views_optimized")
            ErrorHandler.log_error(e, context)
            stats["errors"] += 1
            stats["duration"] = asyncio.get_event_loop().time() - start_time

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
            sum(post["_priority"] for post in channel_posts)
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
        """📊 High-performance batch database updates"""

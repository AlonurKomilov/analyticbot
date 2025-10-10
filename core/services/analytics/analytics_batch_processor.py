"""
Analytics Batch Processor - Pure Business Logic
Framework-agnostic batch processing for analytics operations
"""

import asyncio
import logging
from collections import defaultdict
from typing import Any

logger = logging.getLogger(__name__)


class AnalyticsBatchProcessor:
    """
    Pure business logic for batch processing analytics operations
    No framework dependencies - follows Clean Architecture
    """

    def __init__(
        self,
        analytics_repository: Any,
        telegram_port: Any = None,
        batch_size: int = 50,
        concurrent_limit: int = 10,
        rate_limit_delay: float = 0.1,
    ):
        """
        Initialize batch processor

        Args:
            analytics_repository: Repository for analytics data persistence
            telegram_port: Optional telegram abstraction for view fetching
            batch_size: Number of posts per batch
            concurrent_limit: Maximum concurrent operations
            rate_limit_delay: Delay between batches (seconds)
        """
        self.analytics_repository = analytics_repository
        self.telegram_port = telegram_port
        self._batch_size = batch_size
        self._concurrent_limit = concurrent_limit
        self._rate_limit_delay = rate_limit_delay
        self._semaphore = asyncio.Semaphore(concurrent_limit)

    async def update_posts_views_batch(
        self, posts_data: list[dict], batch_size: int | None = None
    ) -> dict[str, int]:
        """
        Process view updates in optimized batches with concurrent processing

        Args:
            posts_data: List of post dictionaries with channel_id, message_id, views
            batch_size: Optional batch size override

        Returns:
            Statistics dict with processed, updated, errors counts
        """
        batch_size = batch_size or self._batch_size

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

        # Group posts by channel for efficient processing
        channel_groups = self._group_posts_by_channel(posts_data)

        # Process channels concurrently with semaphore control
        semaphore = asyncio.Semaphore(self._concurrent_limit)
        tasks = []

        for channel_id, channel_posts in channel_groups.items():
            task = asyncio.create_task(
                self._process_channel_batch(
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

    def _group_posts_by_channel(self, posts: list[dict]) -> dict[int, list[dict]]:
        """Group posts by channel ID for efficient batch processing"""
        channel_groups = defaultdict(list)
        for post in posts:
            channel_groups[post["channel_id"]].append(post)
        return dict(channel_groups)

    async def _process_channel_batch(
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
                batch_stats = await self._process_post_batch(channel_id, batch)

                # Aggregate batch statistics
                for key in ["processed", "updated", "errors", "skipped"]:
                    stats[key] += batch_stats.get(key, 0)
                stats["batch_count"] += 1

                # Rate limiting between batches
                if i + batch_size < len(posts):
                    await asyncio.sleep(self._rate_limit_delay)

            return stats

    async def _process_post_batch(
        self, channel_id: int, batch: list[dict]
    ) -> dict[str, int]:
        """
        Optimized batch processing with concurrent view fetching and bulk database updates
        """
        stats = {"processed": 0, "updated": 0, "errors": 0, "skipped": 0}

        try:
            # Step 1: Fetch all view counts concurrently (if telegram_port available)
            if self.telegram_port:
                view_results = await self._fetch_views_concurrent(channel_id, batch)
            else:
                # No telegram port - skip view fetching
                view_results = [None] * len(batch)

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
            logger.error(f"Batch processing failed for channel {channel_id}: {e}")
            stats["errors"] += len(batch)

        return stats

    async def _fetch_views_concurrent(
        self, channel_id: int, batch: list[dict]
    ) -> list[int | None | Exception]:
        """Fetch view counts concurrently for a batch of posts"""
        view_tasks = []
        for post in batch:
            task = asyncio.create_task(
                self._fetch_single_post_views(channel_id, post["message_id"])
            )
            view_tasks.append(task)

        return await asyncio.gather(*view_tasks, return_exceptions=True)

    async def _fetch_single_post_views(self, channel_id: int, message_id: int) -> int | None:
        """
        Fetch view count for a single post using telegram port
        """
        if not self.telegram_port:
            return None

        try:
            return await self.telegram_port.get_post_views(channel_id, message_id)
        except Exception as e:
            logger.debug(f"Failed to fetch views for message {message_id}: {e}")
            return None

    async def _batch_update_views(self, updates: list[dict]) -> int:
        """
        Execute database updates in a single optimized transaction

        Args:
            updates: List of dicts with post_id, new_views, old_views

        Returns:
            Number of records updated
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

    async def _sequential_update_views(self, updates: list[dict]) -> int:
        """
        Fallback: Update views sequentially if batch update fails
        """
        updated_count = 0
        for update in updates:
            try:
                query = """
                    UPDATE scheduled_posts
                    SET views = $2, updated_at = NOW()
                    WHERE id = $1
                """
                await self.analytics_repository._pool.execute(
                    query, update["post_id"], update["new_views"]
                )
                updated_count += 1
            except Exception as e:
                logger.error(f"Failed to update post {update['post_id']}: {e}")

        return updated_count

    async def process_all_posts_memory_optimized(
        self, max_concurrent_batches: int = 5
    ) -> dict[str, int]:
        """
        Advanced memory optimization: Process all posts using generators
        Minimizes memory footprint for very large datasets

        Args:
            max_concurrent_batches: Maximum concurrent batch operations

        Returns:
            Statistics dict
        """
        stats = {
            "total_processed": 0,
            "total_updated": 0,
            "total_errors": 0,
            "total_batches": 0,
            "peak_memory_batch_size": 0,
        }

        logger.info("🚀 Starting memory-optimized post processing")

        try:
            # Use semaphore to limit concurrent processing
            semaphore = asyncio.Semaphore(max_concurrent_batches)

            # Fetch posts in batches using repository
            async for post_batch in self._fetch_posts_in_batches():
                batch_stats = await self._process_memory_optimized_batch(
                    post_batch, semaphore
                )

                # Update statistics
                stats["total_processed"] += batch_stats.get("processed", 0)
                stats["total_updated"] += batch_stats.get("updated", 0)
                stats["total_errors"] += batch_stats.get("errors", 0)
                stats["total_batches"] += 1
                stats["peak_memory_batch_size"] = max(
                    stats["peak_memory_batch_size"], len(post_batch)
                )

        except Exception as e:
            logger.error(f"Memory-optimized processing failed: {e}")
            stats["total_errors"] += 1

        logger.info(f"✅ Memory-optimized processing completed: {stats}")
        return stats

    async def _fetch_posts_in_batches(self):
        """
        Generator that yields post batches from repository
        This prevents loading entire dataset into memory
        """
        offset = 0
        batch_size = 1000

        while True:
            # Fetch batch from repository
            query = """
                SELECT id, channel_id, message_id, views
                FROM scheduled_posts
                WHERE status = 'published'
                ORDER BY created_at DESC
                LIMIT $1 OFFSET $2
            """

            async with self.analytics_repository._pool.acquire() as conn:
                rows = await conn.fetch(query, batch_size, offset)

            if not rows:
                break

            # Convert rows to dicts
            posts = [dict(row) for row in rows]
            yield posts

            offset += batch_size

            # Stop if we got less than batch_size (end of data)
            if len(rows) < batch_size:
                break

    async def _process_memory_optimized_batch(
        self, posts: list[dict], semaphore: asyncio.Semaphore
    ) -> dict[str, int]:
        """Process a batch with memory constraints"""
        async with semaphore:
            return await self.update_posts_views_batch(posts)

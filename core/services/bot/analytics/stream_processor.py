"""
Analytics Stream Processor - Memory-Optimized Processing
Handles streaming and memory-efficient processing for large datasets
"""

import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)


class AnalyticsStreamProcessor:
    """
    Memory-optimized stream processor for large channel analytics
    Uses async generators to minimize memory footprint
    """

    def __init__(
        self,
        analytics_repository: Any,
        batch_processor: Any,
        max_concurrent_batches: int = 5,
        stream_batch_size: int = 100,
    ):
        """
        Initialize stream processor

        Args:
            analytics_repository: Repository with stream_all_posts_to_track_views()
            batch_processor: Batch processor for processing post batches
            max_concurrent_batches: Maximum concurrent batch operations
            stream_batch_size: Size of batches for streaming
        """
        self.analytics_repository = analytics_repository
        self.batch_processor = batch_processor
        self._max_concurrent_batches = max_concurrent_batches
        self._stream_batch_size = stream_batch_size

    async def process_all_posts_memory_optimized(
        self, max_concurrent_batches: int | None = None
    ) -> dict[str, int]:
        """
        🧠 ADVANCED MEMORY OPTIMIZATION: Process all posts using generators
        Uses async generators to minimize memory footprint for very large datasets

        Args:
            max_concurrent_batches: Optional override for concurrent batch limit

        Returns:
            Statistics dict with processing results
        """
        max_concurrent = max_concurrent_batches or self._max_concurrent_batches

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
            semaphore = asyncio.Semaphore(max_concurrent)

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
                if len(batch_tasks) >= max_concurrent:
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
        Uses the batch processor for actual processing logic
        """
        async with semaphore:
            if not post_batch:
                return {"processed": 0, "updated": 0, "errors": 0}

            # Delegate to batch processor
            channel_id = post_batch[0]["channel_id"]
            return await self.batch_processor._process_post_batch(channel_id, post_batch)

    async def stream_process_large_channel(self, channel_id: int) -> dict[str, int]:
        """
        🧠 MEMORY-OPTIMIZED: Process a single large channel using streaming
        Perfect for channels with thousands of posts

        Args:
            channel_id: ID of the channel to process

        Returns:
            Statistics dict with processing results
        """
        stats = {"processed": 0, "updated": 0, "errors": 0, "streamed_posts": 0}

        logger.info(f"🌊 Starting streaming processing for channel {channel_id}")

        batch = []
        batch_size = self._stream_batch_size

        try:
            # Stream individual posts to minimize memory usage
            async for post in self.analytics_repository.stream_all_posts_to_track_views():
                if post["channel_id"] != channel_id:
                    continue

                batch.append(post)
                stats["streamed_posts"] += 1

                # Process when batch is full
                if len(batch) >= batch_size:
                    batch_stats = await self.batch_processor._process_post_batch(channel_id, batch)

                    stats["processed"] += batch_stats.get("processed", 0)
                    stats["updated"] += batch_stats.get("updated", 0)
                    stats["errors"] += batch_stats.get("errors", 0)

                    batch = []  # Clear batch
                    await asyncio.sleep(0.05)  # Small delay to prevent overwhelming

            # Process final batch
            if batch:
                batch_stats = await self.batch_processor._process_post_batch(channel_id, batch)
                stats["processed"] += batch_stats.get("processed", 0)
                stats["updated"] += batch_stats.get("updated", 0)
                stats["errors"] += batch_stats.get("errors", 0)

            logger.info(f"🌊 Streaming processing completed for channel {channel_id}: {stats}")

        except Exception as e:
            logger.error(f"❌ Streaming processing failed for channel {channel_id}: {e}")
            stats["errors"] += 1

        return stats


def create_stream_processor(
    analytics_repository: Any,
    batch_processor: Any,
    max_concurrent_batches: int = 5,
    stream_batch_size: int = 100,
) -> AnalyticsStreamProcessor:
    """
    Factory function to create stream processor instance

    Args:
        analytics_repository: Repository with stream capabilities
        batch_processor: Batch processor for processing logic
        max_concurrent_batches: Maximum concurrent operations
        stream_batch_size: Size of streaming batches

    Returns:
        Configured AnalyticsStreamProcessor instance
    """
    return AnalyticsStreamProcessor(
        analytics_repository=analytics_repository,
        batch_processor=batch_processor,
        max_concurrent_batches=max_concurrent_batches,
        stream_batch_size=stream_batch_size,
    )

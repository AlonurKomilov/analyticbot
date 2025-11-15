#!/usr/bin/env python3
"""
Background collection script for ABC LEGACY NEWS
Collects in batches with proper rate limiting
"""

import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/tmp/mtproto_collection.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


async def collect_in_batches():
    """Collect posts in multiple batches"""

    from apps.di import get_container
    from apps.mtproto.services.data_collection_service import (
        MTProtoDataCollectionService,
    )

    container = get_container()
    pool = await container.database.asyncpg_pool()

    channel_id = 1002678877654

    async with pool.acquire() as conn:
        user_row = await conn.fetchrow("SELECT user_id FROM channels WHERE id = $1", channel_id)
        if not user_row:
            logger.error("Channel not found!")
            return False
        user_id = user_row["user_id"]

    # Initialize service
    service = MTProtoDataCollectionService()
    await service.initialize()

    # Collect in multiple runs (Telegram has rate limits)
    total_collected = 0
    max_runs = 10  # Run up to 10 times
    batch_size = 1000  # Collect up to 1000 per batch

    logger.info(f"Starting batch collection: {max_runs} runs of {batch_size} messages each")

    for run in range(1, max_runs + 1):
        logger.info(f"\n{'=' * 60}")
        logger.info(f"Batch {run}/{max_runs}")
        logger.info(f"{'=' * 60}")

        try:
            result = await service.collect_user_channel_history(
                user_id=user_id, limit_per_channel=batch_size
            )

            messages_this_run = result.get("total_messages", 0)
            total_collected += messages_this_run

            logger.info(f"Batch {run} result: {messages_this_run} messages")
            logger.info(f"Total collected so far: {total_collected}")

            # Check final count
            async with pool.acquire() as conn:
                count = await conn.fetchval(
                    "SELECT COUNT(*) FROM posts WHERE channel_id = $1", channel_id
                )
                logger.info(f"Total posts in database: {count}")

            # If we got less than expected, we might be done
            if messages_this_run < batch_size:
                logger.info("Got less than batch size, collection might be complete")
                break

            # Wait between batches to respect rate limits
            if run < max_runs:
                wait_time = 30
                logger.info(f"Waiting {wait_time}s before next batch...")
                await asyncio.sleep(wait_time)

        except Exception as e:
            logger.error(f"Error in batch {run}: {e}")
            await asyncio.sleep(60)  # Wait longer on error
            continue

    logger.info(f"\n{'=' * 60}")
    logger.info(f"Collection complete! Total collected: {total_collected}")
    logger.info(f"{'=' * 60}")

    return True


if __name__ == "__main__":
    try:
        asyncio.run(collect_in_batches())
    except KeyboardInterrupt:
        logger.info("Collection interrupted by user")
    except Exception as e:
        logger.error(f"Collection failed: {e}", exc_info=True)

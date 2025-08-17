import asyncio
import logging

import asyncpg

from bot.config import settings

logger = logging.getLogger(__name__)


async def create_pool(max_retries: int = 5, backoff_factor: float = 0.5):
    """
    Creates a connection pool with retry logic.

    Attempts to connect to the database with exponential backoff.
    """
    dsn_string = str(settings.DATABASE_URL.unicode_string())
    last_exception = None

    for attempt in range(max_retries):
        try:
            pool = await asyncpg.create_pool(dsn=dsn_string)
            logger.info("Successfully connected to the database.")
            return pool
        except (OSError, asyncpg.exceptions.CannotConnectNowError) as e:
            last_exception = e
            wait_time = backoff_factor * (2 ** attempt)
            logger.warning(
                "DB connection attempt %d/%d failed. Retrying in %.2f seconds...",
                attempt + 1,
                max_retries,
                wait_time,
            )
            await asyncio.sleep(wait_time)

    logger.error("Could not connect to the database after %d attempts.", max_retries)
    raise last_exception

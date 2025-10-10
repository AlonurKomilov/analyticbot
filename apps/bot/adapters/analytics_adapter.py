"""
Bot Analytics Adapter - Thin layer adapting core analytics to bot interface
Follows Clean Architecture: Apps layer adapter wrapping Core business logic
"""

import logging
from typing import Any

from aiogram import Bot

from core.ports.telegram_port import TelegramBotPort
from core.services.analytics.analytics_batch_processor import AnalyticsBatchProcessor
from infra.adapters.analytics.aiogram_bot_adapter import AiogramBotAdapter

logger = logging.getLogger(__name__)


class BotAnalyticsAdapter:
    """
    Thin adapter for bot layer - translates bot requests to core analytics service
    This is how apps layer should work: thin translation, no business logic
    """

    def __init__(
        self,
        batch_processor: AnalyticsBatchProcessor,
        bot: Bot | None = None,
        telegram_port: TelegramBotPort | None = None,
    ):
        """
        Initialize bot analytics adapter

        Args:
            batch_processor: Core analytics batch processor
            bot: Optional Aiogram bot (for creating telegram_port)
            telegram_port: Optional telegram port (overrides bot)
        """
        self.batch_processor = batch_processor

        # Setup telegram port
        if telegram_port:
            self.telegram_port = telegram_port
        elif bot:
            self.telegram_port = AiogramBotAdapter(bot)
        else:
            # No bot or port provided - batch processor will handle it
            self.telegram_port = None

        # Update batch processor's telegram port if provided
        if self.telegram_port and self.batch_processor.telegram_port is None:
            self.batch_processor.telegram_port = self.telegram_port

    async def update_posts_views_batch(
        self, posts_data: list[dict], batch_size: int = 50
    ) -> dict[str, int]:
        """
        Update view counts for multiple posts in batches

        Args:
            posts_data: List of post dictionaries
            batch_size: Batch size for processing

        Returns:
            Statistics dictionary
        """
        try:
            return await self.batch_processor.update_posts_views_batch(posts_data, batch_size)
        except Exception as e:
            logger.error(f"Failed to update posts views batch: {e}")
            return {
                "total_posts": len(posts_data),
                "processed": 0,
                "updated": 0,
                "errors": len(posts_data),
                "skipped": 0,
            }

    async def update_all_post_views(self) -> dict[str, int]:
        """
        Update view counts for all posts

        Returns:
            Statistics dictionary
        """
        try:
            return await self.batch_processor.process_all_posts_memory_optimized()
        except Exception as e:
            logger.error(f"Failed to update all post views: {e}")
            return {
                "total_processed": 0,
                "total_updated": 0,
                "total_errors": 1,
                "total_batches": 0,
            }

    # Additional adapter methods can be added here as needed
    # For now, we support the main batch processing operations

    def get_batch_processor(self) -> AnalyticsBatchProcessor:
        """
        Get the underlying batch processor for advanced operations

        Returns:
            Core analytics batch processor
        """
        return self.batch_processor

import asyncio
import logging
from collections import defaultdict

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest

from bot.database.repositories.analytics_repository import AnalyticsRepository
from bot.services.prometheus_service import prometheus_service, prometheus_timer
from bot.utils.error_handler import ErrorContext, ErrorHandler

# Logger sozlamalari
logger = logging.getLogger(__name__)


class AnalyticsService:
    """Enhanced analytics service with better error handling and rate limiting"""

    def __init__(self, bot: Bot, analytics_repository: AnalyticsRepository):
        self.analytics_repository = analytics_repository
        self.bot = bot
        self._rate_limit_delay = 0.5  # seconds between API calls
        self._batch_size = 50  # reduced for better rate limiting

    @prometheus_timer("telegram_api")
    async def update_all_post_views(self) -> dict[str, int]:
        """
        Update view counts for all posts with improved error handling.
        Returns statistics about the operation.
        """
        stats = {"processed": 0, "updated": 0, "errors": 0, "skipped": 0}

        try:
            posts = await self.analytics_repository.get_all_posts_to_track_views()

            if not posts:
                logger.info("No posts found for view tracking.")
                return stats

            logger.info(f"Starting view update for {len(posts)} posts.")

            # Group posts by channel for efficient processing
            grouped: dict[int, list[dict]] = defaultdict(list)
            for post in posts:
                grouped[post["channel_id"]].append(post)

            # Process each channel
            for channel_id, channel_posts in grouped.items():
                channel_stats = await self._process_channel_posts(
                    channel_id, channel_posts
                )

                # Update overall stats
                for key in stats:
                    stats[key] += channel_stats.get(key, 0)

                # Rate limiting between channels
                await asyncio.sleep(self._rate_limit_delay)

            logger.info(
                f"View update completed. Processed: {stats['processed']}, "
                f"Updated: {stats['updated']}, Errors: {stats['errors']}, "
                f"Skipped: {stats['skipped']}"
            )

            # Record Prometheus metrics
            prometheus_service.record_post_views_update(stats["updated"])

        except Exception as e:
            context = ErrorContext().add("operation", "update_all_post_views")
            ErrorHandler.log_error(e, context)
            stats["errors"] += 1

        return stats

    async def _process_channel_posts(
        self, channel_id: int, posts: list[dict]
    ) -> dict[str, int]:
        """Process posts for a specific channel"""
        stats = {"processed": 0, "updated": 0, "errors": 0, "skipped": 0}

        # Process in batches to avoid rate limits
        for i in range(0, len(posts), self._batch_size):
            batch = posts[i : i + self._batch_size]
            batch_stats = await self._process_post_batch(channel_id, batch)

            # Update stats
            for key in stats:
                stats[key] += batch_stats.get(key, 0)

            # Rate limiting between batches
            if i + self._batch_size < len(posts):
                await asyncio.sleep(self._rate_limit_delay)

        return stats

    async def _process_post_batch(
        self, channel_id: int, batch: list[dict]
    ) -> dict[str, int]:
        """Process a batch of posts from the same channel"""
        stats = {"processed": 0, "updated": 0, "errors": 0, "skipped": 0}

        message_ids = [post["message_id"] for post in batch]

        try:
            # Get messages from Telegram
            messages = await self.bot.get_messages(
                chat_id=channel_id, message_ids=message_ids
            )

            # Create mapping for quick lookup
            msg_map = {m.message_id: m for m in messages if m}

            # Update view counts
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
                ErrorContext()
                .add("operation", "get_messages_batch")
                .add("channel_id", channel_id)
            )
            ErrorHandler.handle_telegram_api_error(e, context)
            stats["errors"] += len(batch)

        except Exception as e:
            context = (
                ErrorContext()
                .add("operation", "process_post_batch")
                .add("channel_id", channel_id)
            )
            ErrorHandler.log_error(e, context)
            stats["errors"] += len(batch)

        return stats

    async def get_posts_ordered_by_views(self, channel_id: int) -> list[dict] | None:
        """
        Get posts ordered by views with error handling.
        """
        try:
            return await self.analytics_repository.get_posts_ordered_by_views(
                channel_id
            )
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

            # Lazy import matplotlib (heavy) only when needed
            from io import BytesIO

            import matplotlib.pyplot as plt

            fig, ax = plt.subplots(figsize=(min(12, 1.2 * len(post_ids)), 4))
            ax.bar(post_ids, views, color="#4C72B0")
            ax.set_title(f"Top {limit} Posts by Views")
            ax.set_xlabel("Post ID")
            ax.set_ylabel("Views")

            # Add value labels on bars
            for i, v in enumerate(views):
                ax.text(i, v, str(v), ha="center", va="bottom", fontsize=8)

            fig.tight_layout()

            # Save to bytes
            buf = BytesIO()
            fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
            plt.close(fig)
            buf.seek(0)

            logger.info(
                f"Chart created for channel {channel_id} with {len(top_posts)} posts"
            )
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

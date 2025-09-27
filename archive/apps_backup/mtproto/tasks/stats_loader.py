"""Statistics loading tasks for Telegram channels."""

import logging

from apps.mtproto.di import get_settings, get_tg_client
from core.ports.tg_client import BroadcastStats, TGClient


class StatsLoaderTask:
    """Task for loading broadcast statistics from Telegram channels.

    This is a stub implementation that will be extended in future phases
    with actual statistics collection and processing capabilities.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._tg_client: TGClient | None = None

    async def initialize(self) -> None:
        """Initialize the stats loader task."""
        settings = get_settings()

        if not settings.MTPROTO_ENABLED:
            self.logger.info("StatsLoaderTask disabled (MTPROTO_ENABLED=False)")
            return

        self._tg_client = get_tg_client()
        await self._tg_client.start()
        self.logger.info("StatsLoaderTask initialized")

    async def load_channel_stats(
        self, channel_username: str, include_detailed: bool = False
    ) -> BroadcastStats | None:
        """Load statistics for a single channel.

        Args:
            channel_username: Username or ID of the channel
            include_detailed: Whether to include detailed statistics

        Returns:
            Channel broadcast statistics or None if failed
        """
        if not self._tg_client:
            self.logger.warning("TGClient not initialized")
            return None

        self.logger.info(f"Loading stats for channel {channel_username}")

        try:
            stats = await self._tg_client.get_broadcast_stats(
                channel_username, include_detailed=include_detailed
            )

            if stats:
                self.logger.info(
                    f"Loaded stats for {channel_username}: "
                    f"{stats.subscriber_count} subscribers, "
                    f"{stats.view_count_avg} avg views"
                )
            else:
                self.logger.warning(f"No stats available for {channel_username}")

            return stats

        except Exception as e:
            self.logger.error(f"Failed to load stats for {channel_username}: {e}")
            return None

    async def load_batch_stats(
        self, channels: list[str], include_detailed: bool = False
    ) -> dict[str, BroadcastStats | None]:
        """Load statistics for multiple channels in batch.

        Args:
            channels: List of channel usernames/IDs
            include_detailed: Whether to include detailed statistics

        Returns:
            Dictionary mapping channel names to their statistics
        """
        results = {}

        self.logger.info(f"Loading batch stats for {len(channels)} channels")

        for channel in channels:
            try:
                stats = await self.load_channel_stats(channel, include_detailed=include_detailed)
                results[channel] = stats
            except Exception as e:
                self.logger.error(f"Failed to load stats for {channel}: {e}")
                results[channel] = None

        successful_loads = sum(1 for stats in results.values() if stats is not None)
        self.logger.info(
            f"Batch stats loading complete: {successful_loads}/{len(channels)} successful"
        )

        return results

    async def schedule_stats_refresh(self, channels: list[str], interval_minutes: int = 60) -> None:
        """Schedule periodic statistics refresh for channels.

        Args:
            channels: List of channel usernames/IDs to refresh
            interval_minutes: Refresh interval in minutes
        """
        self.logger.info(
            f"Scheduling stats refresh for {len(channels)} channels "
            f"every {interval_minutes} minutes"
        )

        # This is a stub implementation
        # In future phases, this would integrate with a task scheduler
        # like Celery or APScheduler

        self.logger.info("Stats refresh scheduling completed (stub implementation)")

    async def shutdown(self) -> None:
        """Shutdown the stats loader task."""
        if self._tg_client:
            await self._tg_client.stop()
            self.logger.info("StatsLoaderTask shutdown complete")

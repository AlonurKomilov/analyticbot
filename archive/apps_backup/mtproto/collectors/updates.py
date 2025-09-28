"""Real-time updates collector for Telegram with repository integration."""

import asyncio
import logging
from collections.abc import Callable
from datetime import datetime
from typing import Any

from apps.mtproto.config import MTProtoSettings
from core.ports.tg_client import TGClient

from infra.tg.parsers import normalize_update


class UpdatesCollector:
    """Collects real-time updates from Telegram and stores them in database.

    Handles new messages, edits, and other updates with graceful error handling
    and proper shutdown support.
    """

    def __init__(self, tg_client: TGClient, repos: Any, settings: MTProtoSettings):
        """Initialize the updates collector.

        Args:
            tg_client: Telegram client implementation
            repos: Repository container with channel_repo, post_repo, metrics_repo, parsers
            settings: MTProto configuration settings
        """
        self.logger = logging.getLogger(__name__)
        self.tg_client = tg_client
        self.repos = repos
        self.settings = settings
        self._running = False
        self._shutdown_event = asyncio.Event()
        self._stats = {
            "updates_processed": 0,
            "updates_skipped": 0,
            "updates_errors": 0,
            "start_time": None,
        }

    async def start_collecting(self) -> None:
        """Start collecting real-time updates."""
        if not self.settings.MTPROTO_ENABLED or not self.settings.MTPROTO_UPDATES_ENABLED:
            self.logger.info("Updates collection disabled by feature flags")
            return

        if self._running:
            self.logger.warning("UpdatesCollector already running")
            return

        self._running = True
        self._stats["start_time"] = datetime.utcnow()
        self._shutdown_event.clear()

        self.logger.info("Starting real-time updates collection...")

        try:
            await self.run_updates_stream()
        except Exception as e:
            self.logger.error(f"Fatal error in updates collection: {e}")
        finally:
            self._running = False
            self.logger.info(f"Updates collection stopped. Stats: {self._stats}")

    async def run_updates_stream(self) -> None:
        """Run the main updates processing loop."""
        try:
            async for update in self.tg_client.iter_updates():
                # Check for shutdown signal
                if not self._running or self._shutdown_event.is_set():
                    self.logger.info("Shutdown signal received, stopping updates stream")
                    break

                try:
                    # Normalize the update
                    normalized = normalize_update(update)

                    if not normalized:
                        self._stats["updates_skipped"] += 1
                        continue

                    # Process the normalized update
                    await self._process_normalized_update(normalized)
                    self._stats["updates_processed"] += 1

                    # Rate limiting
                    await asyncio.sleep(self.settings.MTPROTO_SLEEP_THRESHOLD / 10)

                except Exception as e:
                    self.logger.error(f"Error processing update: {e}")
                    self._stats["updates_errors"] += 1
                    continue

        except Exception as e:
            self.logger.error(f"Error in updates stream: {e}")
            raise

    async def _process_normalized_update(self, normalized: dict) -> None:
        """Process a normalized update by storing it in repositories.

        Args:
            normalized: Normalized update dictionary
        """
        try:
            # Ensure channel exists
            if normalized.get("channel"):
                await self.repos.channel_repo.ensure_channel(**normalized["channel"])

            # Upsert post data
            if normalized.get("post"):
                await self.repos.post_repo.upsert_post(**normalized["post"])

            # Add/update metrics snapshot
            if normalized.get("metrics"):
                await self.repos.metrics_repo.add_or_update_snapshot(**normalized["metrics"])

            self.logger.debug(
                f"Processed update for channel {normalized.get('channel', {}).get('channel_id', 'unknown')}"
            )

        except Exception as e:
            self.logger.error(f"Error storing normalized update: {e}")
            raise

    async def stop_collecting(self) -> None:
        """Stop collecting updates gracefully."""
        if self._running:
            self.logger.info("Initiating graceful shutdown of updates collector...")
            self._running = False
            self._shutdown_event.set()

            # Give some time for the collection loop to stop
            await asyncio.sleep(2)

    def is_collecting(self) -> bool:
        """Check if collector is currently running."""
        return self._running

    def get_stats(self) -> dict:
        """Get collection statistics.

        Returns:
            Dictionary with collection statistics
        """
        stats = self._stats.copy()
        if stats["start_time"]:
            stats["uptime_seconds"] = (datetime.utcnow() - stats["start_time"]).total_seconds()
        return stats

    # Legacy methods for backward compatibility
    def set_update_handler(self, handler: Callable[[Any], None]) -> None:
        """Set handler for processing updates (legacy method)."""
        self.logger.warning("set_update_handler is deprecated, updates are processed automatically")

    async def initialize(self) -> None:
        """Initialize the updates collector (legacy method)."""
        self.logger.info("UpdatesCollector using new initialization via constructor")

    async def shutdown(self) -> None:
        """Shutdown the updates collector."""
        await self.stop_collecting()
        self.logger.info("UpdatesCollector shutdown complete")


async def run_updates_stream(tg: TGClient, repos: Any) -> None:
    """Standalone function for updates stream (matches PR specification).

    Args:
        tg: TGClient instance
        repos: Repository container
    """
    from apps.mtproto.config import MTProtoSettings

    settings = MTProtoSettings()
    collector = UpdatesCollector(tg, repos, settings)

    try:
        await collector.start_collecting()
    except KeyboardInterrupt:
        await collector.stop_collecting()
    except Exception as e:
        logging.error(f"Updates stream error: {e}")
        await collector.stop_collecting()
        raise

"""Task script for syncing channel history with feature flag safety."""

import asyncio
import logging
import sys
from datetime import datetime

from apps.mtproto.collectors.history import HistoryCollector
from apps.mtproto.config import MTProtoSettings
from apps.mtproto.di import create_tg_client, get_repositories


async def sync_channel_history(
    channel_ids: list[int] | None = None,
    limit: int | None = None,
    max_concurrent: int = 3,
) -> dict:
    """Sync history for specified channels or all tracked channels.

    Args:
        channel_ids: Specific channel IDs to sync, or None for all
        limit: Max messages per channel, or None for default
        max_concurrent: Maximum concurrent channel syncs

    Returns:
        Dictionary with sync results
    """
    settings = MTProtoSettings()

    # Safety check - feature must be enabled
    if not settings.MTPROTO_ENABLED or not settings.MTPROTO_HISTORY_ENABLED:
        logging.warning("History sync disabled by feature flags")
        return {
            "success": False,
            "reason": "disabled_by_flags",
            "channels_synced": 0,
            "total_messages": 0,
        }

    logging.info(f"Starting history sync for channels: {channel_ids or 'all'}")

    repos = await get_repositories()
    tg_client = create_tg_client(settings)

    try:
        # Initialize TG client
        await tg_client.start()

        # Get channels to sync
        if channel_ids:
            channels = []
            for channel_id in channel_ids:
                try:
                    channel = await repos.channel_repo.get_channel(channel_id)
                    if channel:
                        channels.append(channel)
                except Exception as e:
                    logging.warning(f"Could not load channel {channel_id}: {e}")
        else:
            # Get all tracked channels
            channels = await repos.channel_repo.get_tracked_channels()

        if not channels:
            logging.warning("No channels found to sync")
            return {
                "success": True,
                "reason": "no_channels",
                "channels_synced": 0,
                "total_messages": 0,
            }

        # Create collector
        collector = HistoryCollector(tg_client, repos, settings)

        # Sync channels with concurrency control
        semaphore = asyncio.Semaphore(max_concurrent)
        tasks = []

        for channel in channels:
            task = _sync_single_channel(semaphore, collector, channel, limit)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Aggregate results
        total_synced = 0
        total_messages = 0
        errors = []

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                errors.append(f"Channel {channels[i]['channel_id']}: {result}")
            else:
                total_synced += 1
                total_messages += result.get("messages_collected", 0)

        if errors:
            logging.error(f"Sync errors: {errors}")

        logging.info(
            f"History sync complete. Channels: {total_synced}/{len(channels)}, "
            f"Messages: {total_messages}, Errors: {len(errors)}"
        )

        return {
            "success": len(errors) < len(channels),
            "channels_synced": total_synced,
            "total_channels": len(channels),
            "total_messages": total_messages,
            "errors": errors,
            "sync_time": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logging.error(f"Fatal error in history sync: {e}")
        return {
            "success": False,
            "reason": f"fatal_error: {e}",
            "channels_synced": 0,
            "total_messages": 0,
        }

    finally:
        try:
            await tg_client.stop()
        except Exception as e:
            logging.warning(f"Error stopping TG client: {e}")


async def _sync_single_channel(
    semaphore: asyncio.Semaphore,
    collector: HistoryCollector,
    channel: dict,
    limit: int | None,
) -> dict:
    """Sync a single channel with concurrency control.

    Args:
        semaphore: Concurrency control semaphore
        collector: History collector instance
        channel: Channel data dictionary
        limit: Message limit for this channel

    Returns:
        Dictionary with sync results for this channel
    """
    async with semaphore:
        channel_id = channel["channel_id"]
        username = channel.get("username", "unknown")

        logging.info(f"Syncing channel {channel_id} ({username})")

        try:
            result = await collector.collect_history(channel_id=channel_id, limit=limit)

            logging.info(
                f"Channel {channel_id} sync complete: "
                f"{result.get('messages_collected', 0)} messages"
            )

            return result

        except Exception as e:
            logging.error(f"Error syncing channel {channel_id}: {e}")
            raise


async def main():
    """Main entry point for the sync history task."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Parse command line arguments
    channel_ids = None
    limit = None
    max_concurrent = 3

    if len(sys.argv) > 1:
        # Parse channel IDs from command line
        try:
            channel_ids = [int(x.strip()) for x in sys.argv[1].split(",")]
        except ValueError:
            logging.error("Invalid channel IDs format. Use: channel_id1,channel_id2,...")
            sys.exit(1)

    if len(sys.argv) > 2:
        try:
            limit = int(sys.argv[2])
        except ValueError:
            logging.error("Invalid limit format. Must be an integer.")
            sys.exit(1)

    if len(sys.argv) > 3:
        try:
            max_concurrent = int(sys.argv[3])
        except ValueError:
            logging.error("Invalid max_concurrent format. Must be an integer.")
            sys.exit(1)

    # Run the sync
    try:
        result = await sync_channel_history(
            channel_ids=channel_ids, limit=limit, max_concurrent=max_concurrent
        )

        if result["success"]:
            logging.info(f"History sync completed successfully: {result}")
            sys.exit(0)
        else:
            logging.error(f"History sync failed: {result}")
            sys.exit(1)

    except KeyboardInterrupt:
        logging.info("History sync interrupted by user")
        sys.exit(130)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

"""Task script for loading MTProto official channel/supergroup stats (Phase 4.3)."""

import asyncio
import logging
import sys

from apps.mtproto.config import MTProtoSettings
from apps.mtproto.di import create_stats_loader, create_tg_client, get_repositories


async def main():
    """Main entry point for the load stats task."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger = logging.getLogger("mtproto.load_stats")

    try:
        # Load settings
        settings = MTProtoSettings()

        # Safety check - feature must be enabled
        if not settings.MTPROTO_ENABLED or not settings.MTPROTO_STATS_ENABLED:
            logger.info(
                "Stats task disabled by flags (MTPROTO_ENABLED=%s, MTPROTO_STATS_ENABLED=%s)",
                settings.MTPROTO_ENABLED,
                settings.MTPROTO_STATS_ENABLED,
            )
            return

        if not settings.MTPROTO_STATS_PEERS:
            logger.warning("No peers configured in MTPROTO_STATS_PEERS")
            return

        logger.info(
            "Starting stats loader for %d peers: %s",
            len(settings.MTPROTO_STATS_PEERS),
            settings.MTPROTO_STATS_PEERS,
        )

        # Initialize dependencies
        repos = await get_repositories()
        tg_client = create_tg_client(settings)

        try:
            # Start TG client
            await tg_client.start()
            logger.info("TG client started successfully")

            # Create stats loader
            stats_loader = create_stats_loader(tg_client, repos, settings)

            # Run stats collection
            results = await stats_loader.run(
                peers=settings.MTPROTO_STATS_PEERS,
                concurrency=settings.MTPROTO_STATS_CONCURRENCY,
            )

            # Log results summary
            total_graphs = sum(r.get("graphs", 0) for r in results)
            total_points = sum(r.get("daily_points", 0) for r in results)
            skipped_count = sum(1 for r in results if r.get("skipped", False))

            logger.info("Stats loading completed:")
            logger.info("  - Total peers processed: %d", len(results))
            logger.info("  - Graphs processed: %d", total_graphs)
            logger.info("  - Daily points materialized: %d", total_points)
            logger.info("  - Peers skipped: %d", skipped_count)

            # Log individual results
            for result in results:
                if result.get("skipped"):
                    logger.warning(
                        "Skipped peer %s: %s",
                        result["peer"],
                        result.get("reason", "unknown"),
                    )
                else:
                    logger.info(
                        "Processed peer %s: %d graphs, %d daily points",
                        result["peer"],
                        result.get("graphs", 0),
                        result.get("daily_points", 0),
                    )

        finally:
            # Always stop TG client
            await tg_client.stop()
            logger.info("TG client stopped")

    except Exception as e:
        logger.error("Fatal error in stats loading: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
MTProto Worker Entry Point

Runs the automatic data collection service that fetches channel messages
for all users with MTProto enabled.

Usage:
    python -m apps.mtproto.worker [options]
    
Options:
    --interval MINUTES    Collection interval in minutes (default: 10)
    --once               Run collection once and exit
    --user-id USER_ID    Collect only for specific user
    --status             Show service status and exit
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from apps.mtproto.services.data_collection_service import MTProtoDataCollectionService


def setup_logging(level: str = "INFO"):
    """Setup logging for the worker."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


async def main():
    """Main entry point for MTProto worker."""
    parser = argparse.ArgumentParser(description="MTProto Data Collection Worker")
    parser.add_argument(
        "--interval",
        type=int,
        default=10,
        help="Collection interval in minutes (default: 10)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run collection once and exit",
    )
    parser.add_argument(
        "--user-id",
        type=int,
        help="Collect only for specific user ID",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show service status and exit",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    # Create service
    service = MTProtoDataCollectionService()

    try:
        # Initialize service
        await service.initialize()

        if args.status:
            # Show status and exit
            status = await service.get_status()
            logger.info("📊 MTProto Service Status:")
            for key, value in status.items():
                logger.info(f"   {key}: {value}")
            sys.exit(0)

        elif args.once:
            # Run once and exit
            logger.info("🔄 Running single collection cycle...")

            if args.user_id:
                result = await service.collect_user_channel_history(args.user_id)
            else:
                result = await service.collect_all_users()

            if result.get("success"):
                logger.info(f"✅ Collection successful: {result}")
                sys.exit(0)
            else:
                logger.error(f"❌ Collection failed: {result}")
                sys.exit(1)

        elif args.user_id:
            # Run continuous collection for specific user
            logger.info(f"🚀 Starting continuous collection for user {args.user_id}...")

            while service.running or not service.running:  # Will be set to True in run loop
                service.running = True
                result = await service.collect_user_channel_history(args.user_id)

                if result.get("success"):
                    logger.info(f"✅ Collection cycle complete: {result}")
                else:
                    logger.error(f"❌ Collection cycle failed: {result}")

                logger.info(f"⏳ Waiting {args.interval} minutes until next cycle...")
                await asyncio.sleep(args.interval * 60)

        else:
            # Run continuous collection for all users
            await service.run_continuous_service(interval_minutes=args.interval)

    except KeyboardInterrupt:
        logger.info("🛑 Interrupted by user")
        sys.exit(130)

    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)

    finally:
        await service.shutdown()


if __name__ == "__main__":
    asyncio.run(main())

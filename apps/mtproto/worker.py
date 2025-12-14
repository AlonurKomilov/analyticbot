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

from apps.mtproto.connection_pool import (
    ConnectionPoolConfig,
    init_connection_pool,
    shutdown_connection_pool,
)
from apps.mtproto.services.data_collection_service import MTProtoDataCollectionService
from apps.shared.health_server import HealthCheckServer
from apps.shared.process_manager import ProcessManager


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
        help="Collection interval in minutes (default: 10). Ignored in tiered mode.",
    )
    parser.add_argument(
        "--tiered",
        action="store_true",
        help="Use tiered intervals based on user plans (free=60min, pro=20min, business=10min, enterprise=5min)",
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
    parser.add_argument(
        "--max-runtime",
        type=float,
        default=24.0,
        help="Maximum runtime in hours before auto-shutdown (default: 24, 0 = infinite)",
    )
    parser.add_argument(
        "--memory-limit",
        type=int,
        default=2048,
        help="Memory limit in MB before auto-shutdown (default: 2048, 0 = no limit)",
    )
    parser.add_argument(
        "--cpu-limit",
        type=float,
        default=80.0,
        help="CPU limit %% before auto-shutdown (default: 80, 0 = no limit)",
    )
    parser.add_argument(
        "--health-port",
        type=int,
        default=9091,
        help="Health check HTTP server port (default: 9091, 0 = disabled)",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    # Initialize process manager for lifecycle management
    process_manager = ProcessManager(
        name=(f"mtproto_worker_user_{args.user_id}" if args.user_id else "mtproto_worker_all"),
        max_runtime_hours=args.max_runtime if args.max_runtime > 0 else None,
        memory_limit_mb=args.memory_limit if args.memory_limit > 0 else None,
        cpu_limit_percent=args.cpu_limit if args.cpu_limit > 0 else None,
    )
    process_manager.start()

    # Start health check server if enabled
    health_server = None
    if args.health_port > 0:
        health_server = HealthCheckServer(port=args.health_port, process_manager=process_manager)
        health_server.start()

    # Create service first to get settings
    service = MTProtoDataCollectionService()

    # Initialize connection pool from settings
    pool_config = ConnectionPoolConfig.from_settings(service.settings)
    await init_connection_pool(pool_config)

    logger.info(
        f"✅ MTProto connection pool initialized: "
        f"max_users={pool_config.MAX_TOTAL_CONNECTIONS}, "
        f"max_per_user={pool_config.MAX_CONNECTIONS_PER_USER}, "
        f"session_timeout={pool_config.SESSION_TIMEOUT}s"
    )

    # Register cleanup callbacks
    async def cleanup_service():
        if health_server:
            health_server.stop()
        await service.shutdown()
        await shutdown_connection_pool()
        logger.info("✅ Service cleanup complete")

    process_manager.add_cleanup_callback(cleanup_service)

    try:
        # Initialize service
        await service.initialize()

        if args.status:
            # Show status and exit
            from apps.mtproto.connection_pool import get_connection_pool

            status = await service.get_status()
            pool_metrics = get_connection_pool().get_metrics_summary()

            logger.info("📊 MTProto Service Status:")
            for key, value in status.items():
                logger.info(f"   {key}: {value}")

            logger.info("📊 Connection Pool Metrics:")
            for key, value in pool_metrics.items():
                logger.info(f"   {key}: {value}")

            sys.exit(0)

        elif args.once:
            # Run once and exit
            logger.info("🔄 Running single collection cycle...")

            # Get configured limit
            limit = service.settings.MTPROTO_HISTORY_LIMIT_PER_RUN
            logger.info(f"📊 Using limit: {limit} messages per channel")

            if args.user_id:
                result = await service.collect_user_channel_history(
                    args.user_id, limit_per_channel=limit
                )
            else:
                result = await service.collect_all_users(limit_per_channel=limit)

            if result.get("success"):
                logger.info(f"✅ Collection successful: {result}")
                sys.exit(0)
            else:
                logger.error(f"❌ Collection failed: {result}")
                sys.exit(1)

        elif args.user_id:
            # Run continuous collection for specific user
            logger.info(f"🚀 Starting continuous collection for user {args.user_id}...")

            while process_manager.should_continue():
                service.running = True
                process_manager.heartbeat()  # Mark as alive

                result = await service.collect_user_channel_history(args.user_id)

                if result.get("success"):
                    logger.info(f"✅ Collection cycle complete: {result}")
                else:
                    logger.error(f"❌ Collection cycle failed: {result}")

                logger.info(f"⏳ Waiting {args.interval} minutes until next cycle...")

                # Sleep in small chunks to check should_continue() frequently
                for _ in range(args.interval * 60):
                    if not process_manager.should_continue():
                        break
                    await asyncio.sleep(1)

        else:
            # Run continuous collection for all users with process manager
            if args.tiered:
                logger.info(
                    "🚀 Starting continuous collection with TIERED intervals "
                    "(per-user plan-based intervals)..."
                )
                # Use tiered mode - intervals from user plans
                await service.run_continuous_service_tiered(process_manager=process_manager)
            else:
                logger.info(
                    f"🚀 Starting continuous collection with FIXED interval "
                    f"({args.interval} minutes for all users)..."
                )
                # Use fixed interval mode (legacy)
                await service.run_continuous_service(
                    interval_minutes=args.interval, process_manager=process_manager
                )

    except KeyboardInterrupt:
        logger.info("🛑 Interrupted by user")
        process_manager.request_shutdown("keyboard_interrupt")
        sys.exit(130)

    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        process_manager.request_shutdown(f"fatal_error: {e}")
        sys.exit(1)

    finally:
        process_manager.shutdown()
        logger.info("✅ Shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())

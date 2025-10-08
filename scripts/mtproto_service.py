#!/usr/bin/env python3
"""
MTProto Service Manager - Phase 2 Real Data Collection

Manages real Telegram data collection services using existing infrastructure.
Controls history sync, real-time updates, and stats collection.
"""

import argparse
import asyncio
import logging
import os
import signal
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set environment to only load MTProto-specific settings
os.environ.setdefault("MTPROTO_STANDALONE", "true")

from apps.mtproto.collectors.history import HistoryCollector
from apps.mtproto.collectors.updates import UpdatesCollector
from apps.mtproto.config import MTProtoSettings
from apps.mtproto.di import (
    RepositoryContainer,
    ScalingContainer,
    create_tg_client,
    get_repositories,
)
from core.ports.tg_client import TGClient


class MTProtoServiceManager:
    """Service manager for MTProto real data collection."""

    def __init__(self):
        self.settings = MTProtoSettings()
        self.repos: RepositoryContainer | None = None
        self.tg_client: TGClient | None = None
        self.scaling_container: ScalingContainer | None = None
        self.running = False
        self.tasks = []

    async def initialize(self):
        """Initialize all components."""
        print("🔧 Initializing MTProto services...")

        # Check configuration
        if not self.settings.MTPROTO_ENABLED:
            raise RuntimeError("MTProto is disabled. Set MTPROTO_ENABLED=true in .env")

        # Initialize repositories
        self.repos = await get_repositories()

        # Initialize Telegram client
        self.tg_client = create_tg_client(self.settings)

        # Initialize scaling container for advanced features
        self.scaling_container = ScalingContainer(self.settings)
        await self.scaling_container.initialize()

        print("✅ MTProto services initialized")

    async def start_history_collection(self) -> bool:
        """Start historical data collection."""
        if self.tg_client is None:
            raise RuntimeError("MTProtoServiceManager not initialized. Call initialize() first.")

        if not self.settings.MTPROTO_HISTORY_ENABLED:
            print("⚠️  History collection disabled")
            return False

        if not self.settings.MTPROTO_PEERS:
            print("⚠️  No peers configured for history collection")
            return False

        print("📥 Starting historical data collection...")

        try:
            await self.tg_client.start()

            collector = HistoryCollector(self.tg_client, self.repos, self.settings)

            # Collect from all configured peers
            result = await collector.backfill_history_for_peers(
                peers=self.settings.MTPROTO_PEERS,
                limit_per_peer=self.settings.MTPROTO_HISTORY_LIMIT_PER_RUN,
            )

            print(f"✅ History collection completed: {result}")
            return True

        except Exception as e:
            print(f"❌ History collection failed: {e}")
            return False

    async def start_updates_stream(self):
        """Start real-time updates collection."""
        if self.tg_client is None:
            raise RuntimeError("MTProtoServiceManager not initialized. Call initialize() first.")

        if not self.settings.MTPROTO_UPDATES_ENABLED:
            print("⚠️  Updates collection disabled")
            return

        print("🔄 Starting real-time updates collection...")

        try:
            await self.tg_client.start()

            collector = UpdatesCollector(self.tg_client, self.repos, self.settings)

            # Start collecting in background
            task = asyncio.create_task(collector.start_collecting())
            self.tasks.append(task)

            print("✅ Real-time updates collection started")

        except Exception as e:
            print(f"❌ Updates collection failed: {e}")

    async def run_continuous_service(self):
        """Run continuous data collection service."""
        print("🚀 Starting continuous MTProto data collection service...")

        self.running = True

        # Set up signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            print(f"\n🛑 Received signal {signum}, shutting down...")
            self.running = False

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        try:
            # Start updates stream
            await self.start_updates_stream()

            # Periodic history sync
            last_history_sync = 0
            history_interval = 3600  # 1 hour

            while self.running:
                current_time = asyncio.get_event_loop().time()

                # Run periodic history sync
                if current_time - last_history_sync > history_interval:
                    print("🔄 Running periodic history sync...")
                    await self.start_history_collection()
                    last_history_sync = current_time

                # Wait before next check
                await asyncio.sleep(60)  # Check every minute

        except Exception as e:
            print(f"❌ Service error: {e}")

        finally:
            await self.shutdown()

    async def get_status(self):
        """Get status of all MTProto services."""
        status = {
            "mtproto_enabled": self.settings.MTPROTO_ENABLED,
            "history_enabled": self.settings.MTPROTO_HISTORY_ENABLED,
            "updates_enabled": self.settings.MTPROTO_UPDATES_ENABLED,
            "stats_enabled": self.settings.MTPROTO_STATS_ENABLED,
            "configured_peers": len(self.settings.MTPROTO_PEERS),
            "running_tasks": len(self.tasks),
            "scaling_stats": self.scaling_container.get_stats() if self.scaling_container else None,
        }

        return status

    async def shutdown(self):
        """Gracefully shutdown all services."""
        print("🛑 Shutting down MTProto services...")

        self.running = False

        # Cancel all tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()

        # Wait for tasks to complete
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)

        # Stop Telegram client
        if self.tg_client:
            try:
                await self.tg_client.stop()
            except Exception as e:
                print(f"Warning: Error stopping TG client: {e}")

        # Stop scaling container
        if self.scaling_container:
            try:
                await self.scaling_container.shutdown()
            except Exception as e:
                print(f"Warning: Error stopping scaling container: {e}")

        print("✅ MTProto services shutdown complete")


async def main():
    """Main entry point for MTProto service management."""
    parser = argparse.ArgumentParser(description="MTProto Service Manager")
    parser.add_argument(
        "command",
        choices=["status", "history", "updates", "service", "test"],
        help="Command to execute",
    )
    parser.add_argument("--peers", help="Comma-separated list of peers for history collection")
    parser.add_argument(
        "--limit", type=int, default=50, help="Message limit per peer (default: 50 for safety)"
    )

    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    manager = MTProtoServiceManager()

    try:
        await manager.initialize()

        if args.command == "status":
            status = await manager.get_status()
            print("📊 MTProto Service Status:")
            for key, value in status.items():
                print(f"   {key}: {value}")

        elif args.command == "history":
            if args.peers:
                # Override configured peers
                manager.settings.MTPROTO_PEERS = args.peers.split(",")

            success = await manager.start_history_collection()
            sys.exit(0 if success else 1)

        elif args.command == "updates":
            await manager.start_updates_stream()

            # Keep running until interrupted
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Interrupted")

        elif args.command == "service":
            await manager.run_continuous_service()

        elif args.command == "test":
            print("🧪 Testing MTProto configuration...")

            if manager.repos is None or manager.tg_client is None:
                raise RuntimeError("MTProtoServiceManager not properly initialized")

            # Test database
            channels = await manager.repos.channel_repo.get_tracked_channels()
            print(f"✅ Database: {len(channels)} channels tracked")

            # Test Telegram connection
            await manager.tg_client.start()
            me = await manager.tg_client.get_me()
            print(f"✅ Telegram: Connected as {me.first_name}")
            await manager.tg_client.stop()

            print("✅ All tests passed!")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    finally:
        await manager.shutdown()


if __name__ == "__main__":
    asyncio.run(main())

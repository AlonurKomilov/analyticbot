"""
MTProto Data Collection Service

Multi-tenant service that automatically collects channel data for all users
by reading their configured channels from the database.
"""

import asyncio
import logging
import signal
from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any

from apps.di import get_container
from apps.mtproto.collectors.history import HistoryCollector
from apps.mtproto.config import MTProtoSettings
from apps.mtproto.multi_tenant.user_mtproto_service import UserMTProtoService

logger = logging.getLogger(__name__)


class TelegramClientAdapter:
    """Adapter to wrap Telethon TelegramClient to match TGClient protocol."""

    def __init__(self, telegram_client: Any):
        """Initialize adapter with existing TelegramClient.
        
        Args:
            telegram_client: Telethon TelegramClient instance
        """
        self._client = telegram_client

    async def start(self) -> None:
        """Start client (no-op as client is already started)."""
        pass

    async def stop(self) -> None:
        """Stop client (handled by UserMTProtoClient)."""
        pass

    async def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._client.is_connected() if self._client else False

    async def iter_history(
        self, peer: Any, *, offset_id: int = 0, limit: int = 200
    ) -> AsyncIterator[Any]:
        """Iterate through message history.
        
        Args:
            peer: The target peer (username or ID)
            offset_id: Start from this message ID
            limit: Maximum messages to fetch
            
        Yields:
            Message objects
        """
        # Resolve entity first to ensure it's in cache
        try:
            entity = await self._client.get_entity(peer)
            peer = entity  # Use resolved entity for iteration
        except Exception as e:
            logger.warning(f"Could not resolve entity for {peer}: {e}")
            # Continue with original peer, might still work
        
        async for message in self._client.iter_messages(peer, offset_id=offset_id, limit=limit):
            yield message

    async def get_broadcast_stats(self, channel: Any) -> Any:
        """Get broadcast statistics for a channel."""
        return await self._client.get_broadcast_stats(channel)

    async def get_megagroup_stats(self, channel: Any) -> Any:
        """Get megagroup statistics for a channel."""
        return await self._client.get_megagroup_stats(channel)

    async def load_async_graph(self, token: str, x: int = 0) -> Any:
        """Load async graph data."""
        return await self._client.load_async_graph(token, x)

    async def get_full_channel(self, channel: Any) -> Any:
        """Get full channel information."""
        return await self._client.get_full_channel(channel)

    async def get_me(self) -> Any:
        """Get information about the current user."""
        return await self._client.get_me()

    async def disconnect(self) -> None:
        """Disconnect the client."""
        if self._client:
            await self._client.disconnect()

    async def iter_updates(self) -> AsyncIterator[Any]:
        """Iterate through updates (not used in current implementation)."""
        if False:  # pragma: no cover
            yield None


class MTProtoDataCollectionService:
    """Service for automatic multi-tenant MTProto data collection."""

    def __init__(self):
        self.settings = MTProtoSettings()
        self.container: Any = None
        self.channel_repo: Any = None
        self.user_bot_repo: Any = None
        self.user_mtproto_service: UserMTProtoService | None = None
        self.running = False
        self.tasks: list = []

    async def initialize(self):
        """Initialize all components."""
        logger.info("🔧 Initializing MTProto Data Collection Service...")

        # Check configuration
        if not self.settings.MTPROTO_ENABLED:
            raise RuntimeError("MTProto is disabled. Set MTPROTO_ENABLED=true in .env")

        # Get main DI container
        self.container = get_container()

        # Initialize repositories
        self.channel_repo = await self.container.database.channel_repo()
        self.user_bot_repo = await self.container.database.user_bot_repo()

        # Initialize user MTProto service for multi-tenant support
        self.user_mtproto_service = UserMTProtoService(self.user_bot_repo)

        logger.info("✅ MTProto Data Collection Service initialized")

    async def collect_user_channel_history(self, user_id: int, limit_per_channel: int = 50) -> dict:
        """Collect history for all channels of a specific user.

        Args:
            user_id: The user ID
            limit_per_channel: Maximum messages to fetch per channel

        Returns:
            Dictionary with collection results
        """
        try:
            # Get user's MTProto client
            user_client = await self.user_mtproto_service.get_user_client(user_id)  # type: ignore
            if not user_client:
                logger.warning(f"User {user_id} has no MTProto credentials configured")
                return {
                    "success": False,
                    "user_id": user_id,
                    "reason": "no_mtproto_credentials",
                    "channels_synced": 0,
                    "total_messages": 0,
                }

            # Connect to Telegram
            await user_client.connect()

            # Get user's channels from database
            channels = await self.channel_repo.get_user_channels(user_id)

            if not channels:
                logger.info(f"User {user_id} has no channels configured")
                return {
                    "success": True,
                    "user_id": user_id,
                    "reason": "no_channels",
                    "channels_synced": 0,
                    "total_messages": 0,
                }

            logger.info(f"📥 Collecting history for user {user_id}: {len(channels)} channels")

            # Create a repos object for the collector
            class ReposWrapper:
                def __init__(self, channel_repo, post_repo, metrics_repo):
                    self.channel_repo = channel_repo
                    self.post_repo = post_repo
                    self.post_metrics_repo = metrics_repo
                    self.metrics_repo = metrics_repo  # Alias for compatibility

            # Get repositories from DI container
            channel_repo = await self.container.database.channel_repo()
            post_repo = await self.container.database.post_repo()
            metrics_repo = await self.container.database.metrics_repo()
            
            repos = ReposWrapper(channel_repo, post_repo, metrics_repo)

            # Wrap the TelegramClient with our adapter to match TGClient protocol
            tg_client_adapter = TelegramClientAdapter(user_client._client)

            # Create collector with adapted client and user_id for multi-tenant ownership
            collector = HistoryCollector(tg_client_adapter, repos, self.settings, user_id=user_id)  # type: ignore

            total_messages = 0
            synced_channels = 0
            errors = []

            # Collect from each channel
            for channel in channels:
                channel_name = "Unknown"
                try:
                    channel_id = channel.get("id") or channel.get("telegram_id")
                    channel_name = channel.get("title") or channel.get("name", "Unknown")

                    # Convert channel ID to Telethon format
                    # Telegram channel IDs in our DB already include the "100" prefix (e.g., 1002678877654)
                    # We just need to make them negative for the API (e.g., -1002678877654)
                    channel_id_str = str(channel_id)
                    if channel_id_str.startswith("-"):
                        # Already negative
                        peer_identifier = int(channel_id_str)
                    else:
                        # Make negative
                        peer_identifier = -int(channel_id_str)

                    logger.info(f"  📡 Syncing channel: {channel_name} (DB ID: {channel_id}, Telegram ID: {peer_identifier})")

                    # Use _process_peer_history for storage (internal method handles DB upserts)
                    stats = await collector._process_peer_history(
                        peer=peer_identifier,
                        limit=limit_per_channel
                    )

                    messages_collected = stats.get("ingested", 0) + stats.get("updated", 0)
                    total_messages += messages_collected
                    synced_channels += 1

                    logger.info(
                        f"  ✅ Channel {channel_name}: {messages_collected} messages stored (ingested: {stats.get('ingested', 0)}, updated: {stats.get('updated', 0)})"
                    )

                except Exception as e:
                    logger.error(f"  ❌ Error syncing channel {channel_name}: {e}")
                    errors.append(f"Channel {channel_name}: {str(e)}")

            # Disconnect user client
            await user_client.disconnect()

            logger.info(
                f"✅ User {user_id} collection complete: "
                f"{synced_channels}/{len(channels)} channels, {total_messages} messages"
            )

            return {
                "success": len(errors) < len(channels),
                "user_id": user_id,
                "channels_synced": synced_channels,
                "total_channels": len(channels),
                "total_messages": total_messages,
                "errors": errors,
                "sync_time": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Error collecting data for user {user_id}: {e}")
            return {
                "success": False,
                "user_id": user_id,
                "reason": f"error: {str(e)}",
                "channels_synced": 0,
                "total_messages": 0,
            }

    async def collect_all_users(self, limit_per_channel: int = 50) -> dict:
        """Collect channel history for all users with MTProto enabled.

        Args:
            limit_per_channel: Maximum messages to fetch per channel

        Returns:
            Dictionary with collection results for all users
        """
        try:
            # Get all users with MTProto enabled
            users = await self.user_bot_repo.get_all_mtproto_enabled_users()

            if not users:
                logger.info("No users with MTProto enabled")
                return {
                    "success": True,
                    "reason": "no_users",
                    "users_processed": 0,
                    "total_messages": 0,
                }

            logger.info(f"🚀 Collecting data for {len(users)} users with MTProto enabled")

            total_messages = 0
            users_processed = 0
            all_results = []

            # Process each user
            for user in users:
                user_id = user.get("user_id") or user.get("id")  # user_id is the actual user ID, not record ID
                logger.info(f"📊 Processing user {user_id}...")

                result = await self.collect_user_channel_history(user_id, limit_per_channel)

                if result.get("success"):
                    users_processed += 1
                    total_messages += result.get("total_messages", 0)

                all_results.append(result)

            logger.info(
                f"🎉 Collection complete: {users_processed}/{len(users)} users, "
                f"{total_messages} total messages"
            )

            return {
                "success": True,
                "users_processed": users_processed,
                "total_users": len(users),
                "total_messages": total_messages,
                "results": all_results,
                "sync_time": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Error collecting data for all users: {e}")
            return {
                "success": False,
                "reason": f"error: {str(e)}",
                "users_processed": 0,
                "total_messages": 0,
            }

    async def run_continuous_service(self, interval_minutes: int = 10):
        """Run continuous data collection service.

        Args:
            interval_minutes: Interval between collection runs in minutes
        """
        logger.info(
            f"🚀 Starting continuous MTProto data collection service "
            f"(interval: {interval_minutes} minutes)..."
        )

        self.running = True

        # Set up signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            logger.info(f"🛑 Received signal {signum}, shutting down...")
            self.running = False

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        interval_seconds = interval_minutes * 60

        try:
            while self.running:
                logger.info("🔄 Starting collection cycle...")

                # Run collection for all users
                result = await self.collect_all_users(limit_per_channel=50)

                if result.get("success"):
                    logger.info(
                        f"✅ Collection cycle complete: "
                        f"{result.get('users_processed', 0)} users, "
                        f"{result.get('total_messages', 0)} messages"
                    )
                else:
                    logger.error(f"❌ Collection cycle failed: {result.get('reason', 'unknown')}")

                # Wait for next cycle
                logger.info(f"⏳ Waiting {interval_minutes} minutes until next cycle...")
                await asyncio.sleep(interval_seconds)

        except Exception as e:
            logger.error(f"❌ Service error: {e}")

        finally:
            await self.shutdown()

    async def get_status(self):
        """Get status of the data collection service."""
        status = {
            "mtproto_enabled": self.settings.MTPROTO_ENABLED,
            "history_enabled": self.settings.MTPROTO_HISTORY_ENABLED,
            "updates_enabled": self.settings.MTPROTO_UPDATES_ENABLED,
            "running": self.running,
            "running_tasks": len(self.tasks),
        }

        # Get user count
        if self.user_bot_repo:
            try:
                users = await self.user_bot_repo.get_all_mtproto_enabled_users()
                status["mtproto_enabled_users"] = len(users)
            except Exception as e:
                logger.error(f"Error getting user count: {e}")
                status["mtproto_enabled_users"] = "error"

        return status

    async def shutdown(self):
        """Gracefully shutdown all services."""
        logger.info("🛑 Shutting down MTProto Data Collection Service...")

        self.running = False

        # Cancel all tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()

        # Wait for tasks to complete
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)

        # Stop user MTProto service
        if self.user_mtproto_service:
            try:
                await self.user_mtproto_service.cleanup_idle_clients()
            except Exception as e:
                logger.warning(f"Warning: Error cleaning up user clients: {e}")

        logger.info("✅ MTProto Data Collection Service shutdown complete")

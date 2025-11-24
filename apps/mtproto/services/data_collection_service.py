"""
MTProto Data Collection Service

Multi-tenant service that automatically collects channel data for all users
by reading their configured channels from the database.
"""

import asyncio
import logging
import signal
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any

from apps.di import get_container
from apps.mtproto.collectors.history import HistoryCollector
from apps.mtproto.config import MTProtoSettings
from apps.mtproto.connection_pool import get_connection_pool
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

    async def stop(self) -> None:
        """Stop client (handled by UserMTProtoClient)."""

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
        """Get full channel information including participant count."""
        from telethon.tl.functions.channels import GetFullChannelRequest

        # Resolve entity first
        entity = await self._client.get_entity(channel)

        # Get full channel info
        full_channel = await self._client(GetFullChannelRequest(entity))
        return full_channel

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

    async def _log_collection_start(self, user_id: int, total_channels: int):
        """Log collection start event to audit log.

        Args:
            user_id: User ID
            total_channels: Total number of channels to collect from
        """
        try:
            from apps.api.services.mtproto_audit_service import MTProtoAuditService

            session_factory = await self.container.database.async_session_maker()
            async with session_factory() as audit_session:
                audit_service = MTProtoAuditService(audit_session)
                await audit_service.log_event(
                    user_id=user_id,
                    action="collection_start",
                    metadata={
                        "total_channels": total_channels,
                        "start_time": datetime.now(UTC).isoformat(),
                    },
                )
        except Exception as e:
            logger.warning(f"Failed to log collection start for user {user_id}: {e}")

    async def _log_collection_progress(
        self,
        user_id: int,
        channel_id: int,
        channel_name: str,
        messages_collected: int,
        channels_processed: int,
        total_channels: int,
        errors: int = 0,
    ):
        """Log collection progress event to audit log.

        Args:
            user_id: User ID
            channel_id: Channel ID
            channel_name: Channel name
            messages_collected: Messages collected for this channel
            channels_processed: Number of channels processed so far
            total_channels: Total number of channels
            errors: Error count for this channel
        """
        try:
            from apps.api.services.mtproto_audit_service import MTProtoAuditService

            session_factory = await self.container.database.async_session_maker()
            async with session_factory() as audit_session:
                audit_service = MTProtoAuditService(audit_session)
                await audit_service.log_event(
                    user_id=user_id,
                    action="collection_progress",
                    channel_id=channel_id,
                    metadata={
                        "channel_name": channel_name,
                        "messages_collected": messages_collected,
                        "channels_processed": channels_processed,
                        "total_channels": total_channels,
                        "errors": errors,
                        "progress_time": datetime.now(UTC).isoformat(),
                    },
                )
        except Exception as e:
            logger.warning(
                f"Failed to log collection progress for user {user_id}, channel {channel_id}: {e}"
            )

    async def _log_collection_end(
        self,
        user_id: int,
        total_messages: int,
        channels_synced: int,
        total_channels: int,
        errors: int = 0,
    ):
        """Log collection end event to audit log.

        Args:
            user_id: User ID
            total_messages: Total messages collected across all channels
            channels_synced: Number of channels successfully synced
            total_channels: Total number of channels
            errors: Total error count
        """
        try:
            from apps.api.services.mtproto_audit_service import MTProtoAuditService

            session_factory = await self.container.database.async_session_maker()
            async with session_factory() as audit_session:
                audit_service = MTProtoAuditService(audit_session)
                await audit_service.log_event(
                    user_id=user_id,
                    action="collection_end",
                    metadata={
                        "total_messages": total_messages,
                        "channels_synced": channels_synced,
                        "total_channels": total_channels,
                        "errors": errors,
                        "end_time": datetime.now(UTC).isoformat(),
                    },
                )
        except Exception as e:
            logger.warning(f"Failed to log collection end for user {user_id}: {e}")

    async def collect_user_channel_history(self, user_id: int, limit_per_channel: int = 50) -> dict:
        """Collect history for all channels of a specific user.

        Args:
            user_id: The user ID
            limit_per_channel: Maximum messages to fetch per channel

        Returns:
            Dictionary with collection results
        """
        # Get connection pool
        pool = get_connection_pool()

        # Try to acquire session (will fail if user already has active session)
        if not await pool.acquire_session(user_id):
            logger.warning(f"⏭️  Skipping user {user_id} - already has active collection session")
            return {
                "success": False,
                "user_id": user_id,
                "reason": "session_already_active",
                "channels_synced": 0,
                "total_messages": 0,
            }

        session_start = datetime.now(UTC)
        total_messages = 0
        synced_channels = 0
        errors = 0

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
            logger.info(f"🔌 Connected MTProto for user {user_id}")

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

            # Log collection start
            await self._log_collection_start(user_id, len(channels))

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

            error_list = []

            # Collect from each channel
            for idx, channel in enumerate(channels):
                channel_name = "Unknown"
                channel_id = None
                channel_errors = 0
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

                    logger.info(
                        f"  📡 Syncing channel: {channel_name} (DB ID: {channel_id}, Telegram ID: {peer_identifier})"
                    )

                    # Use _process_peer_history for storage (internal method handles DB upserts)
                    stats = await collector._process_peer_history(
                        peer=peer_identifier, limit=limit_per_channel
                    )

                    messages_collected = stats.get("ingested", 0) + stats.get("updated", 0)
                    total_messages += messages_collected
                    synced_channels += 1

                    logger.info(
                        f"  ✅ Channel {channel_name}: {messages_collected} messages stored (ingested: {stats.get('ingested', 0)}, updated: {stats.get('updated', 0)})"
                    )

                    # Log progress for this channel
                    await self._log_collection_progress(
                        user_id=user_id,
                        channel_id=channel_id,
                        channel_name=channel_name,
                        messages_collected=messages_collected,
                        channels_processed=idx + 1,
                        total_channels=len(channels),
                        errors=channel_errors,
                    )

                except Exception as e:
                    logger.error(f"  ❌ Error syncing channel {channel_name}: {e}")
                    error_list.append(f"Channel {channel_name}: {str(e)}")
                    channel_errors = 1
                    errors += 1

                    # Still log progress even on error
                    if channel_id:
                        await self._log_collection_progress(
                            user_id=user_id,
                            channel_id=channel_id,
                            channel_name=channel_name,
                            messages_collected=0,
                            channels_processed=idx + 1,
                            total_channels=len(channels),
                            errors=channel_errors,
                        )

            # Disconnect user client - AUTO CLOSE after collection
            await user_client.disconnect()
            logger.info(f"🔌 Disconnected MTProto for user {user_id}")

            # Log collection end
            await self._log_collection_end(
                user_id=user_id,
                total_messages=total_messages,
                channels_synced=synced_channels,
                total_channels=len(channels),
                errors=len(error_list),
            )

            session_duration = (datetime.now(UTC) - session_start).total_seconds()
            logger.info(
                f"✅ User {user_id} collection complete: "
                f"{synced_channels}/{len(channels)} channels, "
                f"{total_messages} messages in {session_duration:.1f}s"
            )

            return {
                "success": len(error_list) < len(channels),
                "user_id": user_id,
                "channels_synced": synced_channels,
                "total_channels": len(channels),
                "total_messages": total_messages,
                "errors": error_list,
                "sync_time": datetime.now(UTC).isoformat(),
                "duration_seconds": session_duration,
            }

        except Exception as e:
            logger.error(f"❌ Error collecting data for user {user_id}: {e}")
            errors += 1
            # Try to log the error end state
            try:
                await self._log_collection_end(
                    user_id=user_id,
                    total_messages=0,
                    channels_synced=0,
                    total_channels=0,
                    errors=1,
                )
            except Exception:
                # Ignore any logging errors during error handling to avoid cascading failures
                pass

            return {
                "success": False,
                "user_id": user_id,
                "reason": f"error: {str(e)}",
                "channels_synced": 0,
                "total_messages": 0,
            }

        finally:
            # ALWAYS release session in connection pool
            await pool.release_session(
                user_id=user_id,
                channels_processed=synced_channels,
                messages_collected=total_messages,
                errors=errors,
            )

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
                user_id = user.get("user_id") or user.get(
                    "id"
                )  # user_id is the actual user ID, not record ID
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
                "sync_time": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Error collecting data for all users: {e}")
            return {
                "success": False,
                "reason": f"error: {str(e)}",
                "users_processed": 0,
                "total_messages": 0,
            }

    async def run_continuous_service(self, interval_minutes: int = 10, process_manager=None):
        """Run continuous data collection service.

        Args:
            interval_minutes: Interval between collection runs in minutes
            process_manager: Optional ProcessManager for lifecycle management
        """
        logger.info(
            f"🚀 Starting continuous MTProto data collection service "
            f"(interval: {interval_minutes} minutes)..."
        )

        self.running = True

        # Use process_manager if provided, otherwise set up own signal handlers
        if not process_manager:
            # Set up signal handlers for graceful shutdown
            def signal_handler(signum, frame):
                logger.info(f"🛑 Received signal {signum}, shutting down...")
                self.running = False

            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

        interval_seconds = interval_minutes * 60

        # Helper function to check if collection should continue
        def should_run() -> bool:
            """Check if collection loop should continue running"""
            if process_manager:
                return process_manager.should_continue()
            return self.running

        try:
            while should_run():
                collection_start = datetime.now(UTC)
                logger.info(
                    f"🔄 Starting collection cycle at {collection_start.strftime('%H:%M:%S')}..."
                )

                # Update heartbeat if using process_manager
                if process_manager:
                    process_manager.heartbeat()

                # Run collection for all users using configured limit
                limit = self.settings.MTPROTO_HISTORY_LIMIT_PER_RUN
                logger.info(f"📊 Using history limit: {limit} messages per channel")
                result = await self.collect_all_users(limit_per_channel=limit)

                collection_end = datetime.now(UTC)
                collection_duration = (collection_end - collection_start).total_seconds()

                if result.get("success"):
                    logger.info(
                        f"✅ Collection cycle complete: "
                        f"{result.get('users_processed', 0)} users, "
                        f"{result.get('total_messages', 0)} messages, "
                        f"took {collection_duration:.1f}s"
                    )
                else:
                    logger.error(f"❌ Collection cycle failed: {result.get('reason', 'unknown')}")

                # Calculate wait time: ensure minimum gap between collections
                # If collection took 5 minutes and interval is 10 minutes, wait only 5 more minutes
                # This maintains 10-minute intervals between START times, not END times
                remaining_wait = max(
                    60, interval_seconds - collection_duration
                )  # Minimum 60 seconds cooldown

                logger.info(
                    f"⏳ Collection took {collection_duration:.1f}s, "
                    f"waiting {remaining_wait:.1f}s until next cycle... "
                    f"(target interval: {interval_minutes}min between starts)"
                )

                if collection_duration > interval_seconds:
                    logger.warning(
                        f"⚠️  Collection took {collection_duration / 60:.1f}min, "
                        f"longer than configured interval of {interval_minutes}min! "
                        f"Collections will run back-to-back with {remaining_wait}s cooldown."
                    )

                # Sleep in small chunks to respond quickly to shutdown signals
                for _ in range(int(remaining_wait)):
                    if not should_run():
                        break
                    await asyncio.sleep(1)

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

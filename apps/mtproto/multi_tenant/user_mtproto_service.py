"""
User-specific MTProto client management service.
Each user gets their own isolated Telegram client for reading channel history.
"""

import asyncio
import logging
from datetime import datetime, timedelta

from telethon import TelegramClient
from telethon.sessions import StringSession

from core.ports.user_bot_repository import IUserBotRepository

logger = logging.getLogger(__name__)


class UserMTProtoClient:
    """Wrapper for user-specific Telethon client"""

    def __init__(
        self,
        user_id: int,
        api_id: int,
        api_hash: str,
        session_string: str,
    ):
        self.user_id = user_id
        self.api_id = api_id
        self.api_hash = api_hash
        self._client: TelegramClient | None = None
        self._session_string = session_string
        self._last_used = datetime.utcnow()
        self._is_connected = False

    async def connect(self) -> bool:
        """Connect to Telegram"""
        try:
            if self._client and self._is_connected:
                return True

            # Create client with StringSession
            session = StringSession(self._session_string)
            self._client = TelegramClient(
                session,
                api_id=self.api_id,
                api_hash=self.api_hash,
            )

            await self._client.connect()

            # Verify authorization
            if not await self._client.is_user_authorized():
                logger.error(f"User {self.user_id} MTProto session expired")
                return False

            self._is_connected = True
            self._last_used = datetime.utcnow()

            logger.info(f"User {self.user_id} MTProto client connected")
            return True

        except Exception as e:
            logger.error(f"Failed to connect user {self.user_id} MTProto: {e}")
            return False

    async def disconnect(self):
        """Disconnect from Telegram"""
        if self._client:
            try:
                if self._client.is_connected():
                    # Telethon disconnect returns a coroutine or None
                    disconnect_result = self._client.disconnect()
                    if disconnect_result is not None:
                        await disconnect_result
            except Exception as e:
                logger.warning(f"Error disconnecting client for user {self.user_id}: {e}")
        self._is_connected = False
        logger.info(f"User {self.user_id} MTProto client disconnected")

    @property
    def client(self) -> TelegramClient:
        """Get underlying Telethon client"""
        if not self._client or not self._is_connected:
            raise RuntimeError("Client not connected. Call connect() first.")

        self._last_used = datetime.utcnow()
        return self._client

    @property
    def last_used(self) -> datetime:
        return self._last_used


class UserMTProtoService:
    """
    Manages pool of user-specific MTProto clients.
    Ensures proper isolation between users.
    """

    def __init__(self, user_bot_repo: IUserBotRepository | None = None, user_bot_repo_factory=None):
        """
        Initialize service with either a repository or a factory.
        Factory pattern is preferred for long-running services.
        """
        self.user_bot_repo = user_bot_repo
        self.user_bot_repo_factory = user_bot_repo_factory
        self._client_pool: dict[int, UserMTProtoClient] = {}
        self._cleanup_task: asyncio.Task | None = None
        self._max_idle_minutes = 30

    async def _get_user_credentials(self, user_id: int):
        """Get user credentials using either repo or factory"""
        if self.user_bot_repo_factory:
            # Factory IS the repository - it handles sessions internally
            return await self.user_bot_repo_factory.get_by_user_id(user_id)
        elif self.user_bot_repo:
            # Use existing repository
            return await self.user_bot_repo.get_by_user_id(user_id)
        else:
            raise RuntimeError("No repository or factory configured")

    async def get_user_client(
        self, user_id: int, channel_id: int | None = None
    ) -> UserMTProtoClient | None:
        """
        Get or create MTProto client for user.
        Returns None if user hasn't configured MTProto or if MTProto is disabled
        (either globally or for the specific channel).

        Args:
            user_id: User ID
            channel_id: Optional channel ID to check per-channel settings
        """
        # Check pool first
        if user_id in self._client_pool:
            client = self._client_pool[user_id]
            if client._is_connected:
                # Still need to check if MTProto is enabled for this channel
                if not await self._is_mtproto_enabled(user_id, channel_id):
                    logger.info(f"MTProto is disabled for user {user_id}, channel {channel_id}")
                    return None
                return client
            # Reconnect if disconnected
            if await client.connect():
                if not await self._is_mtproto_enabled(user_id, channel_id):
                    logger.info(f"MTProto is disabled for user {user_id}, channel {channel_id}")
                    return None
                return client
            # Connection failed, remove from pool
            del self._client_pool[user_id]

        # Load credentials from database
        credentials = await self._get_user_credentials(user_id)

        if not credentials:
            logger.warning(f"No credentials found for user {user_id}")
            return None

        # Check if MTProto is enabled (global + per-channel)
        if not await self._is_mtproto_enabled(user_id, channel_id):
            logger.info(f"MTProto is disabled for user {user_id}, channel {channel_id}")
            return None

        # Check if MTProto is configured
        if not all(
            [
                credentials.telegram_api_id,
                credentials.telegram_api_hash,
                credentials.session_string,
            ]
        ):
            logger.info(f"User {user_id} has not configured MTProto")
            return None

        # Decrypt sensitive data (handled by domain model)
        from core.services.encryption_service import get_encryption_service

        encryption = get_encryption_service()

        if not credentials.telegram_api_hash or not credentials.telegram_api_id:
            logger.error(f"User {user_id} missing MTProto credentials")
            return None

        api_hash = encryption.decrypt(credentials.telegram_api_hash)
        session_string = (
            encryption.decrypt(credentials.session_string) if credentials.session_string else ""
        )

        # Create new client
        try:
            client = UserMTProtoClient(
                user_id=user_id,
                api_id=credentials.telegram_api_id,
                api_hash=api_hash,
                session_string=session_string,
            )

            # Connect
            if not await client.connect():
                logger.error(f"Failed to connect MTProto client for user {user_id}")
                return None

            # Add to pool
            self._client_pool[user_id] = client

            logger.info(f"Created and cached MTProto client for user {user_id}")
            return client

        except Exception as e:
            logger.error(f"Error creating MTProto client for user {user_id}: {e}")
            return None

    async def disconnect_user(self, user_id: int):
        """Disconnect and remove user's MTProto client"""
        if user_id in self._client_pool:
            client = self._client_pool[user_id]
            await client.disconnect()
            del self._client_pool[user_id]
            logger.info(f"Disconnected and removed MTProto client for user {user_id}")

    async def cleanup_idle_clients(self):
        """Remove idle clients to free resources"""
        now = datetime.utcnow()
        max_idle = timedelta(minutes=self._max_idle_minutes)

        to_remove = []
        for user_id, client in self._client_pool.items():
            if now - client.last_used > max_idle:
                to_remove.append(user_id)

        for user_id in to_remove:
            await self.disconnect_user(user_id)
            logger.info(f"Cleaned up idle MTProto client for user {user_id}")

    async def start_cleanup_task(self):
        """Start background task to cleanup idle clients"""

        async def cleanup_loop():
            while True:
                await asyncio.sleep(300)  # Every 5 minutes
                try:
                    await self.cleanup_idle_clients()
                except Exception as e:
                    logger.error(f"Error in cleanup task: {e}")

        self._cleanup_task = asyncio.create_task(cleanup_loop())

    async def stop_cleanup_task(self):
        """Stop cleanup task"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

    async def _is_mtproto_enabled(self, user_id: int, channel_id: int | None = None) -> bool:
        """
        Check if MTProto is enabled for a user (and optionally a specific channel).

        Logic:
        - If global mtproto_enabled is False, return False
        - If channel_id is provided, check per-channel setting
        - If no per-channel setting exists, default to enabled (inherit global)

        Args:
            user_id: User ID
            channel_id: Optional channel ID for per-channel check

        Returns:
            True if MTProto is enabled, False otherwise
        """
        try:
            # Get credentials for global flag
            credentials = await self._get_user_credentials(user_id)
            if not credentials:
                return False

            global_enabled = getattr(credentials, "mtproto_enabled", True)
            if not global_enabled:
                # Global disabled overrides everything
                return False

            # If no channel specified, return global setting
            if channel_id is None:
                return True

            # Check per-channel setting
            from apps.di import get_container
            from infra.db.repositories.channel_mtproto_repository import ChannelMTProtoRepository

            container = get_container()
            session_factory = await container.database.async_session_maker()
            async with session_factory() as session:
                channel_repo = ChannelMTProtoRepository(session)
                return await channel_repo.is_channel_enabled(user_id, channel_id, global_enabled)

        except Exception as e:
            logger.error(
                f"Error checking MTProto enabled status for user {user_id}, channel {channel_id}: {e}"
            )
            # Default to disabled on error (fail-safe)
            return False

    async def shutdown(self):
        """Disconnect all clients and stop cleanup"""
        await self.stop_cleanup_task()

        for user_id in list(self._client_pool.keys()):
            await self.disconnect_user(user_id)

        logger.info("UserMTProtoService shutdown complete")


# Global instance (initialized in DI container)
_user_mtproto_service: UserMTProtoService | None = None


def init_user_mtproto_service(
    user_bot_repo: IUserBotRepository | None = None, user_bot_repo_factory=None
) -> UserMTProtoService:
    """
    Initialize global UserMTProtoService instance.
    Accepts either a repository or a factory (factory preferred for long-running services).
    """
    global _user_mtproto_service
    _user_mtproto_service = UserMTProtoService(
        user_bot_repo=user_bot_repo, user_bot_repo_factory=user_bot_repo_factory
    )
    return _user_mtproto_service


def get_user_mtproto_service() -> UserMTProtoService:
    """Get global UserMTProtoService instance"""
    if _user_mtproto_service is None:
        raise RuntimeError(
            "UserMTProtoService not initialized. Call init_user_mtproto_service() first."
        )
    return _user_mtproto_service

"""
User Bot Instance - Isolated bot for single user
Each user gets their own dedicated bot and MTProto client instance
"""

import asyncio
from datetime import datetime
from typing import Any, Protocol

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from core.models.user_bot_domain import UserBotCredentials
from core.services.encryption_service import get_encryption_service


class MTProtoClient(Protocol):
    """Protocol for Pyrogram Client (optional dependency)"""

    is_connected: bool

    async def start(self) -> None: ...
    async def stop(self) -> None: ...
    async def get_chat(self, chat_id: int | str) -> Any: ...


class UserBotInstance:
    """
    Isolated bot instance for a single user

    Features:
    - Dedicated Aiogram Bot instance
    - Dedicated Pyrogram MTProto client (optional)
    - Rate limiting per user
    - Activity tracking
    - Graceful shutdown
    """

    def __init__(self, credentials: UserBotCredentials):
        """
        Initialize user bot instance

        Args:
            credentials: User's bot credentials (encrypted in database)
        """
        self.credentials = credentials
        self.user_id = credentials.user_id

        # Decrypt sensitive data
        encryption = get_encryption_service()
        self.bot_token = encryption.decrypt(credentials.bot_token)
        self.api_hash = (
            encryption.decrypt(credentials.telegram_api_hash)
            if credentials.telegram_api_hash
            else None
        )

        # Bot instances (lazy initialized)
        self.bot: Bot | None = None
        self.dp: Dispatcher | None = None
        self.mtproto_client: MTProtoClient | None = None  # Pyrogram Client (optional dependency)

        # State tracking
        self.is_initialized = False
        self.last_activity = datetime.now()
        self._session_closed = False  # Track if session is properly closed

        # Rate limiting
        self.request_semaphore = asyncio.Semaphore(credentials.max_concurrent_requests)
        # Domain model uses rate_limit_rps field name
        self.rate_limit_delay = (
            1.0 / credentials.rate_limit_rps if credentials.rate_limit_rps > 0 else 0
        )
        self.last_request_time = 0.0

    async def initialize(self) -> None:
        """
        Initialize bot and MTProto client

        Raises:
            Exception: If initialization fails
        """
        if self.is_initialized:
            return

        try:
            # Initialize Aiogram Bot
            self.bot = Bot(
                token=self.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
            )
            self.dp = Dispatcher()

            # Verify bot token works
            me = await self.bot.get_me()
            print(f"✅ Bot initialized for user {self.user_id}: @{me.username}")

            # Initialize Pyrogram MTProto client (optional, lazy load)
            # Only initialize if user has MTProto credentials
            if self.credentials.telegram_phone or self.credentials.session_string:
                await self._initialize_mtproto()

            self.is_initialized = True
            self.last_activity = datetime.now()

        except Exception as e:
            print(f"❌ Failed to initialize bot for user {self.user_id}: {e}")
            raise

    async def _initialize_mtproto(self) -> None:
        """
        Initialize Pyrogram MTProto client

        Note: Pyrogram is an optional dependency for MTProto functionality
        """
        try:
            from pyrogram import Client  # pyright: ignore[reportMissingImports]

            self.mtproto_client = Client(
                name=f"user_{self.user_id}_mtproto",
                api_id=self.credentials.telegram_api_id,
                api_hash=self.api_hash,
                phone_number=self.credentials.telegram_phone,
                session_string=self.credentials.session_string,
                workdir=f"./sessions/user_{self.user_id}/",
            )

            # Start MTProto client
            if self.mtproto_client is not None:
                await self.mtproto_client.start()
            print(f"✅ MTProto client initialized for user {self.user_id}")

        except ImportError:
            print(
                f"⚠️  Pyrogram not installed, MTProto client not available for user {self.user_id}"
            )
        except Exception as e:
            print(f"⚠️  Failed to initialize MTProto for user {self.user_id}: {e}")

    async def shutdown(self) -> None:
        """
        Gracefully shutdown bot instances
        Closes all connections and cleans up resources
        """
        # Prevent double-shutdown
        if self._session_closed:
            return

        try:
            # Stop MTProto client first
            if self.mtproto_client:
                try:
                    if (
                        hasattr(self.mtproto_client, "is_connected")
                        and self.mtproto_client.is_connected
                    ):
                        await self.mtproto_client.stop()
                    print(f"✅ MTProto client stopped for user {self.user_id}")
                except Exception as e:
                    print(f"⚠️  Error stopping MTProto for user {self.user_id}: {e}")

            # Close bot session
            if self.bot:
                try:
                    await self.bot.session.close()
                    self._session_closed = True  # Mark as closed
                    print(f"✅ Bot session closed for user {self.user_id}")
                except Exception as e:
                    print(f"⚠️  Error closing bot session for user {self.user_id}: {e}")

            self.is_initialized = False

        except Exception as e:
            print(f"❌ Error during shutdown for user {self.user_id}: {e}")

    async def __aenter__(self):
        """Context manager entry - ensures initialization"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup"""
        await self.shutdown()
        return False  # Don't suppress exceptions

    def __del__(self):
        """
        Destructor - last resort cleanup warning

        Note: This should rarely be called if code is properly using shutdown().
        If you see this warning, it indicates a resource leak in the code.
        """
        if self.bot and not self._session_closed:
            import logging
            import warnings

            warnings.warn(
                f"UserBotInstance for user {self.user_id} being garbage collected "
                f"without proper shutdown! This indicates a resource leak. "
                f"Always call shutdown() or use async context manager.",
                ResourceWarning,
                stacklevel=2,
            )

            # Log for monitoring
            logging.warning(
                f"🔴 RESOURCE LEAK: Bot session for user {self.user_id} not properly closed. "
                f"This will cause memory growth over time."
            )

    async def rate_limited_request(self, coro):
        """
        Execute request with rate limiting

        Args:
            coro: Coroutine to execute

        Returns:
            Result of the coroutine
        """
        async with self.request_semaphore:
            # Apply rate limiting delay
            if self.rate_limit_delay > 0:
                now = asyncio.get_event_loop().time()
                time_since_last = now - self.last_request_time
                if time_since_last < self.rate_limit_delay:
                    await asyncio.sleep(self.rate_limit_delay - time_since_last)
                self.last_request_time = asyncio.get_event_loop().time()

            # Update activity timestamp
            self.last_activity = datetime.now()

            # Execute request
            return await coro

    async def get_bot_info(self) -> dict:
        """
        Get bot information

        Returns:
            Dict with bot info (id, username, first_name, etc.)
        """
        if not self.bot:
            await self.initialize()

        # Type assertion for type checker - we know bot is initialized after line above
        assert self.bot is not None, "Bot should be initialized"

        bot_info = await self.rate_limited_request(self.bot.get_me())

        return {
            "id": bot_info.id,
            "username": bot_info.username,
            "first_name": bot_info.first_name,
            "is_bot": bot_info.is_bot,
        }

    async def send_message(self, chat_id: int | str, text: str, **kwargs):
        """
        Send message (rate-limited)

        Args:
            chat_id: Chat ID to send message to
            text: Message text
            **kwargs: Additional parameters for send_message

        Returns:
            Message object
        """
        if not self.bot:
            await self.initialize()

        # Type assertion for type checker - we know bot is initialized after line above
        assert self.bot is not None, "Bot should be initialized"

        return await self.rate_limited_request(self.bot.send_message(chat_id, text, **kwargs))

    async def get_channel_info(self, channel_id: str):
        """
        Get channel information using MTProto

        Args:
            channel_id: Channel ID or username

        Returns:
            Channel info dict

        Raises:
            RuntimeError: If MTProto client not initialized
        """
        if not self.mtproto_client:
            raise RuntimeError("MTProto client not initialized for this user")

        if not self.mtproto_client.is_connected:
            await self.mtproto_client.start()

        return await self.rate_limited_request(self.mtproto_client.get_chat(channel_id))

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"UserBotInstance(user_id={self.user_id}, "
            f"bot_username={self.credentials.bot_username}, "
            f"status={self.credentials.status.value}, "
            f"initialized={self.is_initialized})"
        )

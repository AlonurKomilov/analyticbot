"""
User Bot Instance - Isolated bot for single user
Each user gets their own dedicated bot and MTProto client instance
"""

import asyncio
import warnings
from datetime import datetime
from typing import Any, Protocol

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

from apps.bot.multi_tenant.bot_health import get_health_monitor
from apps.bot.multi_tenant.circuit_breaker import (
    CircuitBreakerOpenError,
    get_circuit_breaker_registry,
)
from apps.bot.multi_tenant.global_rate_limiter import GlobalRateLimiter
from apps.bot.multi_tenant.retry_logic import get_retry_statistics, retry_with_backoff
from apps.bot.multi_tenant.session_pool import SharedAiogramSession
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

        # Circuit breaker (per-user protection)
        breaker_registry = get_circuit_breaker_registry()
        self.circuit_breaker = breaker_registry.get_breaker(self.user_id)

    async def initialize(self) -> None:
        """
        Initialize bot and MTProto client

        Raises:
            Exception: If initialization fails
        """
        if self.is_initialized:
            return

        try:
            # Initialize Aiogram Bot with shared session pool
            shared_session = SharedAiogramSession()
            self.bot = Bot(
                token=self.bot_token,
                session=shared_session,  # Use shared session instead of creating new one
                default=DefaultBotProperties(parse_mode=ParseMode.HTML),
            )
            self.dp = Dispatcher()

            # ✅ Register default message handlers for webhook support
            self._register_handlers()

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

    def _register_handlers(self) -> None:
        """
        Register default message handlers for webhook support.

        These handlers process incoming messages when webhook is enabled:
        - /start: Welcome message
        - /help: Help information
        - /status: Bot status (for admin/debugging)
        - Echo handler: Responds to any other message
        """
        if self.dp is None:
            return

        @self.dp.message(Command("start"))
        async def handle_start(message: Message) -> None:
            """Handle /start command."""
            await message.answer(
                "👋 <b>Welcome!</b>\n\n"
                "I'm your personal bot. Here's what I can do:\n\n"
                "• Use /help to see available commands\n"
                "• Use /status to check my status\n"
                "• Send me any message and I'll echo it back\n\n"
                "Let's get started! 🚀"
            )

        @self.dp.message(Command("help"))
        async def handle_help(message: Message) -> None:
            """Handle /help command."""
            await message.answer(
                "📋 <b>Available Commands:</b>\n\n"
                "/start - Start the bot and see welcome message\n"
                "/help - Show this help message\n"
                "/status - Check bot status and info\n\n"
                "💡 <b>Tip:</b> Send me any message and I'll echo it back!"
            )

        @self.dp.message(Command("status"))
        async def handle_status(message: Message) -> None:
            """Handle /status command - shows bot info."""
            webhook_status = (
                "✅ Webhook enabled" if self.credentials.webhook_enabled else "⏸ Polling mode"
            )
            await message.answer(
                f"🤖 <b>Bot Status</b>\n\n"
                f"• User ID: <code>{self.user_id}</code>\n"
                f"• Bot Username: @{self.credentials.bot_username}\n"
                f"• Connection: {webhook_status}\n"
                f"• Rate Limit: {self.credentials.rate_limit_rps} RPS\n"
                f"• Status: {self.credentials.status.value}\n"
                f"• Last Activity: {self.last_activity.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                "✅ All systems operational!"
            )

        @self.dp.message()
        async def echo_handler(message: Message) -> None:
            """Echo any other message back to user."""
            if message.text:
                await message.answer(
                    f"📢 <b>Echo:</b>\n\n{message.text}\n\n"
                    "💡 Use /help to see available commands."
                )
            else:
                await message.answer(
                    "I can only echo text messages for now. " "Try /help to see what I can do!"
                )

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

        Note: Bot session is shared and managed by BotSessionPool,
        so we don't close it here - only stop bot-specific resources.
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

            # Note: Don't close bot.session here - it's shared across all bots
            # The shared session is managed by BotSessionPool and closed on app shutdown
            if self.bot:
                self._session_closed = True  # Mark as closed (even though session is shared)
                print(f"✅ Bot instance cleaned up for user {self.user_id}")

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

            warnings.warn(
                f"UserBotInstance for user {self.user_id} being garbage collected "
                f"without proper shutdown! This indicates a resource leak. "
                f"Always call shutdown() or use async context manager.",
                ResourceWarning,
                stacklevel=2,
            )

            # Log for monitoring
            logging.warning(
                f"🔴 RESOURCE LEAK: Bot instance for user {self.user_id} not properly closed. "
                f"MTProto connections may still be active. Call shutdown() explicitly."
            )

    async def rate_limited_request(self, coro, method: str = "default"):
        """
        Execute request with rate limiting, health monitoring, and circuit breaker

        Args:
            coro: Coroutine to execute
            method: Telegram API method name (for global rate limiting)

        Returns:
            Result of the coroutine

        Raises:
            CircuitBreakerOpenError: If circuit breaker is open (too many failures)
        """
        import time

        # Get health monitor
        health_monitor = get_health_monitor()
        start_time = time.time()

        # Check circuit breaker first (fail fast if open)
        async def _execute_request():
            async with self.request_semaphore:
                # 1. Apply per-user rate limiting delay
                if self.rate_limit_delay > 0:
                    now = asyncio.get_event_loop().time()
                    time_since_last = now - self.last_request_time
                    if time_since_last < self.rate_limit_delay:
                        await asyncio.sleep(self.rate_limit_delay - time_since_last)
                    self.last_request_time = asyncio.get_event_loop().time()

                # 2. Apply global rate limiting (across all users)
                global_limiter = await GlobalRateLimiter.get_instance()
                await global_limiter.acquire(method, user_id=self.user_id)

                # Update activity timestamp
                self.last_activity = datetime.now()

                # 3. Execute request
                return await coro

        # Wrap execution with retry logic and circuit breaker protection
        async def _execute_with_circuit_breaker():
            return await self.circuit_breaker.call(_execute_request)

        try:
            # Execute with retry logic (which includes circuit breaker)
            result = await retry_with_backoff(_execute_with_circuit_breaker)

            # Record success
            response_time_ms = (time.time() - start_time) * 1000
            health_monitor.record_success(
                user_id=self.user_id, response_time_ms=response_time_ms, method=method
            )

            # Record retry statistics
            retry_stats = get_retry_statistics()
            retry_stats.record_attempt(attempt=0, success=True, error_category=None)

            return result

        except CircuitBreakerOpenError:
            # Circuit breaker is open, don't record as failure
            # (already too many failures, that's why it's open)
            raise

        except Exception as e:
            # Record failure
            error_type = type(e).__name__
            health_monitor.record_failure(
                user_id=self.user_id, error_type=error_type, method=method
            )

            # Handle rate limit errors from Telegram
            if "429" in str(e) or "Too Many Requests" in str(e):
                # Extract retry_after if available
                retry_after = None
                if hasattr(e, "retry_after"):
                    retry_after = e.retry_after
                global_limiter = await GlobalRateLimiter.get_instance()
                await global_limiter.handle_rate_limit_error(retry_after)

            raise

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

        bot_info = await self.rate_limited_request(self.bot.get_me(), method="getMe")

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

        return await self.rate_limited_request(
            self.bot.send_message(chat_id, text, **kwargs), method="sendMessage"
        )

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

        return await self.rate_limited_request(
            self.mtproto_client.get_chat(channel_id), method="getChat"
        )

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"UserBotInstance(user_id={self.user_id}, "
            f"bot_username={self.credentials.bot_username}, "
            f"status={self.credentials.status.value}, "
            f"initialized={self.is_initialized})"
        )

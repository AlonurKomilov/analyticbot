"""
User Bot Service - Business logic for user bot management.

Handles bot creation, verification, status checks, and removal.
Integrates with repository, encryption service, and bot manager.
"""

import logging
from datetime import datetime

from core.models.user_bot_domain import BotStatus, UserBotCredentials
from core.ports.bot_manager_port import IBotManager
from core.ports.user_bot_repository import IUserBotRepository
from core.services.encryption_service import get_encryption_service

logger = logging.getLogger(__name__)


class UserBotService:
    """Service for managing user bots."""

    def __init__(self, repository: IUserBotRepository, bot_manager: IBotManager | None = None):
        """
        Initialize the user bot service.

        Args:
            repository: User bot repository for database operations
            bot_manager: Multi-tenant bot manager (optional, injected via DI)
        """
        self.repository = repository
        self.bot_manager = bot_manager
        self.encryption_service = get_encryption_service()

    async def validate_bot_token(self, bot_token: str) -> tuple[bool, str | None, dict | None]:
        """
        Validate a bot token by attempting to connect to Telegram.

        Args:
            bot_token: The bot token to validate

        Returns:
            Tuple of (is_valid, error_message, bot_info)
        """
        # Use bot_manager for validation if available
        if not self.bot_manager:
            logger.error("Bot manager not available for token validation")
            return False, "Bot validation service unavailable", None

        try:
            # Delegate to bot_manager port (implemented in infra layer)
            bot_info = await self.bot_manager.validate_bot_token(bot_token)

            # bot_info is already a dict from the port
            return True, None, bot_info

        except ValueError as e:
            # Token validation failed
            return False, str(e), None
        except Exception as e:
            logger.error(f"Error validating bot token: {e}")
            return False, f"Validation error: {str(e)}", None

    async def create_user_bot(
        self,
        user_id: int,
        bot_token: str,
        bot_username: str | None = None,
        api_id: int | None = None,
        api_hash: str | None = None,
        max_requests_per_second: int = 30,
        max_concurrent_requests: int = 10,
    ) -> UserBotCredentials:
        """
        Create a new user bot.

        Args:
            user_id: User ID who owns the bot
            bot_token: Telegram bot token
            bot_username: Bot username (optional, will be fetched if not provided)
            api_id: Telegram API ID for MTProto (optional)
            api_hash: Telegram API Hash for MTProto (optional)
            max_requests_per_second: Rate limit per second
            max_concurrent_requests: Max concurrent requests

        Returns:
            Created UserBotCredentials

        Raises:
            ValueError: If bot token is invalid or user already has a bot
        """
        # Check if user already has a bot
        existing = await self.repository.get_by_user_id(user_id)
        if existing:
            raise ValueError(f"User {user_id} already has a bot (ID: {existing.id})")

        # Validate bot token and get bot info
        is_valid, error_msg, bot_info = await self.validate_bot_token(bot_token)
        if not is_valid:
            raise ValueError(f"Invalid bot token: {error_msg}")

        # Extract bot info from validation
        bot_id = None
        if bot_info:
            if not bot_username:
                bot_username = bot_info.get("username")
            bot_id = bot_info.get("id")

        # Check if this bot is already assigned to another user
        if bot_id:
            existing_bot = await self.repository.get_by_bot_id(bot_id)
            if existing_bot and existing_bot.user_id != user_id:
                raise ValueError(
                    f"This bot (@{bot_username or bot_id}) is already connected to another user. "
                    f"Each bot can only be linked to one AnalyticBot account. "
                    f"Please use a different bot."
                )

        # Encrypt sensitive credentials
        encrypted_token = self.encryption_service.encrypt(bot_token)
        encrypted_api_hash = self.encryption_service.encrypt(api_hash) if api_hash else None

        # Create credentials object (map API-level names to domain model fields)
        credentials = UserBotCredentials(
            id=0,  # Will be set by database
            user_id=user_id,
            bot_token=encrypted_token,
            mtproto_api_id=api_id or 0,
            telegram_api_hash=encrypted_api_hash or "",
            bot_username=bot_username,
            bot_id=bot_id,
            status=BotStatus.PENDING,
            is_verified=False,
            rate_limit_rps=float(max_requests_per_second),
            max_concurrent_requests=max_concurrent_requests,
            total_requests=0,
            last_used_at=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Save to database
        created = await self.repository.create(credentials)
        logger.info(f"Created bot for user {user_id}: {created.id} (@{bot_username})")

        return created

    async def get_user_bot_status(self, user_id: int) -> UserBotCredentials | None:
        """
        Get the status of a user's bot.

        Args:
            user_id: User ID

        Returns:
            UserBotCredentials if found, None otherwise
        """
        return await self.repository.get_by_user_id(user_id)

    async def verify_bot_credentials(
        self,
        user_id: int,
        send_test_message: bool = False,
        test_chat_id: int | None = None,
        test_message: str | None = None,
    ) -> tuple[bool, str, dict | None]:
        """
        Verify bot credentials by initializing the bot.

        Args:
            user_id: User ID
            send_test_message: Whether to send a test message
            test_chat_id: Chat ID to send test message to
            test_message: Custom test message (optional)

        Returns:
            Tuple of (success, message, bot_info)
        """
        # Get user's bot credentials
        credentials = await self.repository.get_by_user_id(user_id)
        if not credentials:
            return False, "No bot found for this user", None

        try:
            # Get bot manager and bot instance from manager
            if not self.bot_manager:
                return False, "Bot manager not available", None
            bot_instance = await self.bot_manager.get_user_bot(user_id)

            if not bot_instance:
                return False, "Failed to initialize bot", None

            # Get bot info
            bot_info_dict = await bot_instance.get_bot_info()

            # Send test message if requested
            if send_test_message and test_chat_id:
                try:
                    message_text = (
                        test_message
                        or "✅ Bot verification successful! Your bot is working correctly."
                    )
                    logger.info(f"📤 Attempting to send test message to chat_id={test_chat_id}")
                    await bot_instance.send_message(test_chat_id, message_text)
                    logger.info(f"✅ Test message sent successfully to chat_id={test_chat_id}")
                    bot_info_dict["test_message_sent"] = True
                except Exception as e:
                    logger.error(
                        f"❌ Failed to send test message to chat_id={test_chat_id}: {e}",
                        exc_info=True,
                    )
                    # Return failure if test message was requested but failed
                    return (
                        False,
                        f"Bot verified but failed to send test message: {str(e)}",
                        None,
                    )

            # Update verification status
            credentials.is_verified = True
            credentials.status = BotStatus.ACTIVE
            credentials.updated_at = datetime.utcnow()
            await self.repository.update(credentials)

            logger.info(f"Bot verified for user {user_id}: @{credentials.bot_username}")
            return True, "Bot verified successfully", bot_info_dict

        except Exception as e:
            logger.error(f"Error verifying bot for user {user_id}: {e}")

            # Update status to error
            credentials.status = BotStatus.ERROR
            credentials.updated_at = datetime.utcnow()
            await self.repository.update(credentials)

            return False, f"Verification failed: {str(e)}", None

    async def remove_user_bot(self, user_id: int) -> bool:
        """
        Remove a user's bot.

        Args:
            user_id: User ID

        Returns:
            True if removed, False if not found
        """
        # Get user's bot
        credentials = await self.repository.get_by_user_id(user_id)
        if not credentials:
            return False

        # Shutdown bot instance if active
        try:
            if self.bot_manager:
                await self.bot_manager.shutdown_user_bot(user_id)
        except Exception as e:
            logger.warning(f"Error shutting down bot for user {user_id}: {e}")

        # Delete from database
        success = await self.repository.delete(user_id)

        if success:
            logger.info(f"Removed bot for user {user_id}: {credentials.id}")

        return success

    async def update_rate_limits(
        self,
        user_id: int,
        max_requests_per_second: int | None = None,
        max_concurrent_requests: int | None = None,
    ) -> UserBotCredentials | None:
        """
        Update rate limits for a user's bot.

        Args:
            user_id: User ID
            max_requests_per_second: New RPS limit (optional)
            max_concurrent_requests: New concurrent limit (optional)

        Returns:
            Updated UserBotCredentials if found, None otherwise
        """
        credentials = await self.repository.get_by_user_id(user_id)
        if not credentials:
            return None

        # Update rate limits (map to domain fields)
        if max_requests_per_second is not None:
            credentials.rate_limit_rps = float(max_requests_per_second)

        if max_concurrent_requests is not None:
            credentials.max_concurrent_requests = max_concurrent_requests

        credentials.updated_at = datetime.utcnow()

        # Save to database
        updated = await self.repository.update(credentials)

        # Reload bot instance to apply new limits
        try:
            if self.bot_manager:
                await self.bot_manager.reload_user_bot(user_id)
            logger.info(
                f"Updated rate limits for user {user_id}: "
                f"RPS={max_requests_per_second}, Concurrent={max_concurrent_requests}"
            )
        except Exception as e:
            logger.warning(f"Error reloading bot for user {user_id}: {e}")

        return updated


def get_user_bot_service(
    repository: IUserBotRepository, bot_manager: IBotManager | None = None
) -> UserBotService:
    """
    Get a user bot service instance.

    Args:
        repository: User bot repository
        bot_manager: Multi-tenant bot manager (optional)

    Returns:
        UserBotService instance
    """
    return UserBotService(repository, bot_manager)

"""
Admin Bot Service - Business logic for admin bot management.

Handles admin operations: listing all bots, accessing user bots,
suspending/activating bots, and updating rate limits.
"""

import logging
from datetime import datetime

from core.models.user_bot_domain import (
    AdminBotAction,
    BotRole,
    BotStatus,
    UserBotCredentials,
)
from core.ports.bot_manager_port import IBotManager
from core.ports.user_bot_repository import IUserBotRepository

logger = logging.getLogger(__name__)


class AdminBotService:
    """Service for admin bot management operations."""

    def __init__(self, repository: IUserBotRepository, bot_manager: IBotManager | None = None):
        """
        Initialize the admin bot service.

        Args:
            repository: User bot repository for database operations
            bot_manager: Multi-tenant bot manager (optional, injected via DI)
        """
        self.repository = repository
        self.bot_manager = bot_manager

    async def list_all_user_bots(
        self,
        page: int = 1,
        page_size: int = 50,
        status_filter: BotStatus | None = None,
        role_filter: BotRole | None = None,
    ) -> tuple[list[UserBotCredentials], int]:
        """
        List all user bots with pagination.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            status_filter: Filter by bot status (optional)
            role_filter: Filter by bot role (optional) - 'system' or 'user'

        Returns:
            Tuple of (list of credentials, total count)
        """
        # Calculate offset
        offset = (page - 1) * page_size

        # Build status param
        status_param = status_filter.value if status_filter else None
        role_param = role_filter.value if role_filter else None

        # Get bots and total count
        bots = await self.repository.list_all(
            limit=page_size,
            offset=offset,
            status=status_param,
            role=role_param,
        )
        total = await self.repository.count(status=status_param, role=role_param)

        logger.info(f"Admin listed {len(bots)} bots (page {page}, total {total})")
        return bots, total

    async def create_user_bot(
        self,
        user_id: int,
        bot_token: str,
        bot_username: str,
        api_id: int | None = None,
        api_hash: str | None = None,
        max_requests_per_second: float = 1.0,
        max_concurrent_requests: int = 3,
    ) -> UserBotCredentials:
        """
        Create a new user bot.

        Args:
            user_id: User ID who owns the bot
            bot_token: Telegram bot token (from BotFather)
            bot_username: Bot username
            api_id: MTProto API ID (optional, for MTProto features)
            api_hash: MTProto API Hash (optional, for MTProto features)
            max_requests_per_second: Rate limit for requests per second
            max_concurrent_requests: Max concurrent requests

        Returns:
            Created UserBotCredentials

        Raises:
            ValueError: If bot creation fails
        """
        # Check if user already has a bot
        existing = await self.repository.get_by_user_id(user_id)
        if existing:
            raise ValueError(f"User {user_id} already has a bot configured")

        # Create credentials - bot_token is for Bot API, mtproto fields are separate
        credentials = UserBotCredentials(
            id=None,  # Will be assigned by database
            user_id=user_id,
            bot_token=bot_token,
            bot_username=bot_username,
            # MTProto credentials (optional)
            mtproto_api_id=api_id,
            telegram_api_hash=api_hash,
            # Status
            status=BotStatus.PENDING,
            role=BotRole.USER,
            # Rate limiting
            rate_limit_rps=max_requests_per_second,
            max_concurrent_requests=max_concurrent_requests,
            # Timestamps
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Save to database
        created = await self.repository.create(credentials)

        logger.info(f"Created bot @{bot_username} for user {user_id}")
        return created

    async def access_user_bot(
        self,
        admin_user_id: int,
        target_user_id: int,
        action: str = "admin_access",
        details: dict | None = None,
    ) -> dict | None:
        """
        Admin access to a user's bot.

        Args:
            admin_user_id: Admin user ID
            target_user_id: Target user ID whose bot to access
            action: Action description
            details: Additional action details

        Returns:
            Bot info dict if successful, None otherwise
        """
        # Get user's bot credentials
        credentials = await self.repository.get_by_user_id(target_user_id)
        if not credentials:
            return None

        try:
            # Access bot through manager (logs admin action)
            if not self.bot_manager:
                logger.error("Bot manager not available")
                return None
            bot_instance = await self.bot_manager.admin_access_bot(admin_user_id, target_user_id)

            if not bot_instance:
                return None

            # Get bot info
            bot_info = await bot_instance.get_bot_info()

            logger.info(
                f"Admin {admin_user_id} accessed bot for user {target_user_id}: "
                f"@{credentials.bot_username}"
            )

            return bot_info

        except Exception as e:
            logger.error(
                f"Error in admin access for user {target_user_id} by admin {admin_user_id}: {e}"
            )
            return None

    async def suspend_user_bot(
        self,
        admin_user_id: int,
        target_user_id: int,
        reason: str,
    ) -> UserBotCredentials | None:
        """
        Suspend a user's bot.

        Args:
            admin_user_id: Admin user ID performing the action
            target_user_id: Target user ID whose bot to suspend
            reason: Reason for suspension

        Returns:
            Updated UserBotCredentials if successful, None otherwise
        """
        credentials = await self.repository.get_by_user_id(target_user_id)
        if not credentials:
            return None

        # Suspend the bot
        credentials.suspend(reason)
        credentials.updated_at = datetime.utcnow()

        # Update in database
        updated = await self.repository.update(credentials)

        # Log admin action
        await self.repository.log_admin_action(
            AdminBotAction(
                id=0,  # Will be set by database
                admin_user_id=admin_user_id,
                target_user_id=target_user_id,
                action="suspend_bot",
                details={"reason": reason},
                timestamp=datetime.utcnow(),
            )
        )

        # Shutdown bot instance if active
        try:
            if self.bot_manager:
                await self.bot_manager.shutdown_user_bot(target_user_id)
        except Exception as e:
            logger.warning(f"Error shutting down bot for user {target_user_id}: {e}")

        logger.info(f"Admin {admin_user_id} suspended bot for user {target_user_id}: {reason}")

        return updated

    async def activate_user_bot(
        self,
        admin_user_id: int,
        target_user_id: int,
    ) -> UserBotCredentials | None:
        """
        Activate a suspended user bot.

        Args:
            admin_user_id: Admin user ID performing the action
            target_user_id: Target user ID whose bot to activate

        Returns:
            Updated UserBotCredentials if successful, None otherwise

        Raises:
            ValueError: If bot is incomplete (no bot_token or bot_id)
        """
        credentials = await self.repository.get_by_user_id(target_user_id)
        if not credentials:
            return None

        # Validate bot is complete before activating
        if not credentials.bot_token or not credentials.bot_id:
            raise ValueError("Cannot activate incomplete bot (missing bot_token or bot_id)")

        # Activate the bot
        credentials.activate()
        credentials.updated_at = datetime.utcnow()

        # Update in database
        updated = await self.repository.update(credentials)

        # Log admin action
        await self.repository.log_admin_action(
            AdminBotAction(
                id=0,  # Will be set by database
                admin_user_id=admin_user_id,
                target_user_id=target_user_id,
                action="activate_bot",
                details={},
                timestamp=datetime.utcnow(),
            )
        )

        logger.info(f"Admin {admin_user_id} activated bot for user {target_user_id}")

        return updated

    async def update_user_bot_rate_limits(
        self,
        admin_user_id: int,
        target_user_id: int,
        max_requests_per_second: int | None = None,
        max_concurrent_requests: int | None = None,
    ) -> UserBotCredentials | None:
        """
        Update rate limits for a user's bot (admin action).

        Args:
            admin_user_id: Admin user ID performing the action
            target_user_id: Target user ID whose bot to update
            max_requests_per_second: New RPS limit (optional)
            max_concurrent_requests: New concurrent limit (optional)

        Returns:
            Updated UserBotCredentials if successful, None otherwise
        """
        credentials = await self.repository.get_by_user_id(target_user_id)
        if not credentials:
            return None

        # Store old values for logging
        old_rps = credentials.rate_limit_rps
        old_concurrent = credentials.max_concurrent_requests

        # Update rate limits (map to domain fields)
        if max_requests_per_second is not None:
            credentials.rate_limit_rps = float(max_requests_per_second)

        if max_concurrent_requests is not None:
            credentials.max_concurrent_requests = max_concurrent_requests

        credentials.updated_at = datetime.utcnow()

        # Update in database
        updated = await self.repository.update(credentials)

        # Log admin action
        await self.repository.log_admin_action(
            AdminBotAction(
                id=0,  # Will be set by database
                admin_user_id=admin_user_id,
                target_user_id=target_user_id,
                action="update_rate_limits",
                details={
                    "old_rate_limit_rps": old_rps,
                    "new_rate_limit_rps": credentials.rate_limit_rps,
                    "old_max_concurrent_requests": old_concurrent,
                    "new_max_concurrent_requests": credentials.max_concurrent_requests,
                },
                timestamp=datetime.utcnow(),
            )
        )

        # Reload bot instance to apply new limits
        try:
            if self.bot_manager:
                await self.bot_manager.reload_user_bot(target_user_id)
            logger.info(
                f"Admin {admin_user_id} updated rate limits for user {target_user_id}: "
                f"RPS={max_requests_per_second}, Concurrent={max_concurrent_requests}"
            )
        except Exception as e:
            logger.warning(f"Error reloading bot for user {target_user_id}: {e}")

        return updated

    async def get_bot_by_id(self, bot_id: int) -> UserBotCredentials | None:
        """
        Get a bot by its ID.

        Args:
            bot_id: Bot ID

        Returns:
            UserBotCredentials if found, None otherwise
        """
        return await self.repository.get_by_id(bot_id)

    async def get_admin_action_logs(
        self,
        target_user_id: int | None = None,
        limit: int = 50,
    ) -> list[AdminBotAction]:
        """
        Get admin action logs.

        Args:
            target_user_id: Filter by target user ID (optional)
            limit: Maximum number of logs to return

        Returns:
            List of AdminBotAction logs
        """
        # TODO: Implement in repository if needed
        # For now, this would require adding a method to IUserBotRepository
        logger.info(f"Admin action logs requested (target_user_id={target_user_id}, limit={limit})")
        return []

    async def verify_bot_credentials(
        self,
        user_id: int,
        send_test_message: bool = False,
        test_chat_id: int | None = None,
        test_message: str | None = None,
    ) -> tuple[bool, str, dict | None]:
        """
        Verify bot credentials by testing the bot token.

        Args:
            user_id: User ID whose bot to verify
            send_test_message: Whether to send a test message
            test_chat_id: Chat ID to send test message to
            test_message: Test message content

        Returns:
            Tuple of (success, message, bot_info)
        """
        # Get user's bot
        credentials = await self.repository.get_by_user_id(user_id)
        if not credentials:
            return False, "No bot found for this user", None

        # Verify with Telegram
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                # Get bot info from Telegram
                url = f"https://api.telegram.org/bot{credentials.bot_token}/getMe"
                async with session.get(url) as response:
                    if response.status != 200:
                        return (
                            False,
                            "Invalid bot token - could not connect to Telegram",
                            None,
                        )

                    data = await response.json()
                    if not data.get("ok"):
                        return (
                            False,
                            f"Bot verification failed: {data.get('description', 'Unknown error')}",
                            None,
                        )

                    bot_info = data.get("result", {})
                    bot_username = bot_info.get("username")
                    bot_id = bot_info.get("id")

            # Update bot credentials with verified info
            credentials.bot_username = bot_username
            credentials.bot_id = bot_id
            credentials.status = BotStatus.ACTIVE
            credentials.is_verified = True
            credentials.updated_at = datetime.utcnow()

            await self.repository.update(credentials)

            # Send test message if requested
            if send_test_message and test_chat_id:
                try:
                    async with aiohttp.ClientSession() as session:
                        msg = test_message or "Hello! Your bot is now configured."
                        url = f"https://api.telegram.org/bot{credentials.bot_token}/sendMessage"
                        async with session.post(
                            url, json={"chat_id": test_chat_id, "text": msg}
                        ) as response:
                            if response.status != 200:
                                logger.warning(
                                    f"Failed to send test message: {await response.text()}"
                                )
                except Exception as e:
                    logger.warning(f"Failed to send test message: {e}")

            logger.info(f"Bot verified for user {user_id}: @{bot_username}")
            return (
                True,
                "Bot verified successfully",
                {
                    "bot_id": bot_id,
                    "bot_username": bot_username,
                    "is_verified": True,
                },
            )

        except Exception as e:
            logger.error(f"Error verifying bot for user {user_id}: {e}")
            return False, f"Verification failed: {str(e)}", None

    async def remove_user_bot(self, user_id: int) -> bool:
        """
        Remove a user's bot.

        Args:
            user_id: User ID whose bot to remove

        Returns:
            True if removed, False if not found
        """
        credentials = await self.repository.get_by_user_id(user_id)
        if not credentials:
            return False

        # Shutdown bot instance if active
        if self.bot_manager:
            try:
                await self.bot_manager.shutdown_user_bot(user_id)
            except Exception as e:
                logger.warning(f"Error shutting down bot for user {user_id}: {e}")

        # Delete from database - pass user_id, not credentials.id
        deleted = await self.repository.delete(user_id)
        if not deleted:
            logger.warning(f"Failed to delete bot credentials for user {user_id}")
            return False

        logger.info(f"Removed bot for user {user_id}")
        return True

    async def update_rate_limits(
        self,
        user_id: int,
        max_requests_per_second: float | None = None,
        max_concurrent_requests: int | None = None,
    ) -> UserBotCredentials | None:
        """
        Update rate limits for a user's bot.

        Args:
            user_id: User ID whose bot to update
            max_requests_per_second: New RPS limit (optional)
            max_concurrent_requests: New concurrent request limit (optional)

        Returns:
            Updated UserBotCredentials or None if not found
        """
        credentials = await self.repository.get_by_user_id(user_id)
        if not credentials:
            return None

        if max_requests_per_second is not None:
            credentials.rate_limit_rps = max_requests_per_second
        if max_concurrent_requests is not None:
            credentials.max_concurrent_requests = max_concurrent_requests

        credentials.updated_at = datetime.utcnow()

        await self.repository.update(credentials)

        logger.info(
            f"Updated rate limits for user {user_id}: rps={credentials.rate_limit_rps}, concurrent={credentials.max_concurrent_requests}"
        )
        return credentials


def get_admin_bot_service(
    repository: IUserBotRepository, bot_manager: IBotManager | None = None
) -> AdminBotService:
    """
    Get an admin bot service instance.

    Args:
        repository: User bot repository
        bot_manager: Multi-tenant bot manager (optional)

    Returns:
        AdminBotService instance
    """
    return AdminBotService(repository, bot_manager)

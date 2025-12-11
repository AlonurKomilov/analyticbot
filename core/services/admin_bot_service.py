"""
Admin Bot Service - Business logic for admin bot management.

Handles admin operations: listing all bots, accessing user bots,
suspending/activating bots, and updating rate limits.
"""

import logging
from datetime import datetime

from core.models.user_bot_domain import AdminBotAction, BotStatus, UserBotCredentials
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
    ) -> tuple[list[UserBotCredentials], int]:
        """
        List all user bots with pagination.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            status_filter: Filter by bot status (optional)

        Returns:
            Tuple of (list of credentials, total count)
        """
        # Calculate offset
        offset = (page - 1) * page_size

        # Build status param
        status_param = status_filter.value if status_filter else None

        # Get bots and total count
        bots = await self.repository.list_all(
            limit=page_size,
            offset=offset,
            status=status_param,
        )
        total = await self.repository.count(status=status_param)

        logger.info(f"Admin listed {len(bots)} bots (page {page}, total {total})")
        return bots, total

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

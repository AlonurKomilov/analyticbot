"""
Bot Manager Port - Interface for multi-tenant bot management.

This port defines the contract for managing multiple user bot instances
following the Ports & Adapters (Hexagonal Architecture) pattern.
"""

from abc import ABC, abstractmethod
from typing import Any


class IBotManager(ABC):
    """
    Interface for multi-tenant bot manager.

    This port allows core services to interact with bot management
    without depending on the concrete implementation.
    """

    @abstractmethod
    async def start(self) -> None:
        """Start bot manager background tasks."""

    @abstractmethod
    async def stop(self) -> None:
        """Stop bot manager and shutdown all bots."""

    @abstractmethod
    async def get_user_bot(self, user_id: int) -> Any:
        """
        Get or create bot instance for user.

        Args:
            user_id: User ID

        Returns:
            Bot instance for the user

        Raises:
            ValueError: If no credentials found or bot is suspended
        """

    @abstractmethod
    async def admin_access_bot(self, admin_id: int, target_user_id: int) -> Any:
        """
        Admin access to any user's bot.

        Args:
            admin_id: Admin user ID
            target_user_id: Target user's ID

        Returns:
            Bot instance for the target user
        """

    @abstractmethod
    async def shutdown_user_bot(self, user_id: int) -> None:
        """
        Force shutdown specific user's bot.

        Args:
            user_id: User ID
        """

    @abstractmethod
    async def reload_user_bot(self, user_id: int) -> Any:
        """
        Reload user's bot (shutdown and recreate).

        Args:
            user_id: User ID

        Returns:
            New bot instance with updated credentials
        """

    @abstractmethod
    async def get_active_bots_count(self) -> int:
        """
        Get count of currently active bots.

        Returns:
            Number of active bots in cache
        """

    @abstractmethod
    async def get_stats(self) -> dict:
        """
        Get bot manager statistics.

        Returns:
            Dict with statistics
        """

    @abstractmethod
    async def validate_bot_token(self, bot_token: str) -> dict:
        """
        Validate a Telegram bot token.

        Args:
            bot_token: Bot token to validate

        Returns:
            Dict with bot information (id, username, first_name, etc.)

        Raises:
            ValueError: If token is invalid
        """

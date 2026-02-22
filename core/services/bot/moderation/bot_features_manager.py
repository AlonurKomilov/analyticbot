"""
Bot Features Manager - Coordinates marketplace services with bot handlers

This manager:
1. Initializes bot service instances
2. Checks feature access before execution
3. Routes requests to appropriate services
4. Logs usage for billing/quotas
"""

import logging
from typing import Any

from aiogram import Bot
from aiogram.types import Message

from core.services.bot.moderation.anti_spam_service import AntiSpamService
from core.services.bot.moderation.auto_delete_joins_service import (
    AutoDeleteJoinsService,
)
from core.services.system.feature_gate_service import FeatureGateService
from core.services.system.user_bot_service import UserBotService
from infra.db.repositories.marketplace_service_repository import (
    MarketplaceServiceRepository,
)

logger = logging.getLogger(__name__)


class BotFeaturesManager:
    """
    Manager for marketplace bot services.

    Coordinates between bot handlers and marketplace services:
    - Initializes service instances
    - Provides easy access to services
    - Handles feature gate integration
    """

    def __init__(
        self,
        user_id: int,
        bot: Bot,
        service: UserBotService,
        feature_gate_service: FeatureGateService,
        marketplace_repo: MarketplaceServiceRepository,
    ):
        """
        Initialize bot features manager.

        Args:
            user_id: Bot owner's user ID
            bot: Bot instance
            service: Existing moderation service
            feature_gate_service: Feature gate service
            marketplace_repo: Marketplace repository
        """
        self.user_id = user_id
        self.bot = bot
        self.moderation_service = moderation_service
        self.feature_gate = feature_gate_service
        self.marketplace_repo = marketplace_repo

        # Initialize service instances
        self.anti_spam = AntiSpamService(
            user_id=user_id,
            feature_gate_service=feature_gate_service,
            marketplace_repo=marketplace_repo,
            moderation_service=moderation_service,
        )

        self.auto_delete_joins = AutoDeleteJoinsService(
            user_id=user_id,
            feature_gate_service=feature_gate_service,
            marketplace_repo=marketplace_repo,
            moderation_service=moderation_service,
            bot=bot,
        )

    async def check_message_spam(
        self,
        chat_id: int,
        sender_tg_id: int,
        message_text: str,
        message_id: int,
        has_links: bool = False,
        is_forward: bool = False,
    ) -> dict[str, Any]:
        """
        Check if a message is spam using the anti-spam service.

        This automatically checks feature access and logs usage.

        Args:
            chat_id: Chat ID where message was sent
            sender_tg_id: Telegram ID of sender
            message_text: Message text
            message_id: Message ID
            has_links: Whether message contains links
            is_forward: Whether message is forwarded

        Returns:
            dict with spam detection results
        """
        return await self.anti_spam.run(
            chat_id=chat_id,
            sender_tg_id=sender_tg_id,
            message_text=message_text,
            message_id=message_id,
            has_links=has_links,
            is_forward=is_forward,
        )

    async def handle_join_message(self, message: Message) -> dict[str, Any]:
        """
        Handle a join message using auto-delete joins service.

        Args:
            message: Aiogram Message object

        Returns:
            dict with deletion results
        """
        if not message.new_chat_members:
            return {"success": False, "error": "Not a join message"}

        return await self.auto_delete_joins.handle_service_message(message)

    async def handle_leave_message(self, message: Message) -> dict[str, Any]:
        """
        Handle a leave message using auto-delete joins service.

        Args:
            message: Aiogram Message object

        Returns:
            dict with deletion results
        """
        if not message.left_chat_member:
            return {"success": False, "error": "Not a leave message"}

        return await self.auto_delete_joins.handle_service_message(message)

    async def is_anti_spam_available(self, chat_id: int) -> bool:
        """
        Check if anti-spam service is available for user and enabled for chat.

        Returns:
            True if service is accessible and enabled
        """
        # Check marketplace access
        has_access, _ = await self.feature_gate.check_access(
            user_id=self.user_id,
            service_key="bot_anti_spam",
        )

        if not has_access:
            return False

        # Check if enabled in chat settings
        return await self.anti_spam.is_enabled_for_chat(chat_id)

    async def is_auto_delete_joins_available(self, chat_id: int) -> tuple[bool, bool]:
        """
        Check if auto-delete joins service is available.

        Returns:
            Tuple of (joins_enabled, leaves_enabled)
        """
        # Check marketplace access
        has_access, _ = await self.feature_gate.check_access(
            user_id=self.user_id,
            service_key="bot_auto_delete_joins",
        )

        if not has_access:
            return (False, False)

        # Check if enabled in chat settings
        return await self.auto_delete_joins.is_enabled_for_chat(chat_id)

    async def get_active_services(self) -> list[str]:
        """
        Get list of active service keys for this user.

        Returns:
            List of service keys (e.g., ['bot_anti_spam', 'bot_auto_delete_joins'])
        """
        active_services = []

        # Check each service
        services_to_check = [
            "bot_anti_spam",
            "bot_auto_delete_joins",
            "bot_banned_words",
            "bot_welcome_messages",
            "bot_invite_tracking",
        ]

        for service_key in services_to_check:
            has_access, _ = await self.feature_gate.check_access(
                user_id=self.user_id,
                service_key=service_key,
            )
            if has_access:
                active_services.append(service_key)

        return active_services

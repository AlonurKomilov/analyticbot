"""
Anti-Spam Service - Automatic spam detection and removal

Marketplace service: bot_anti_spam
Price: 50 credits/month

Features:
- Real-time spam detection
- Malicious link blocking
- Bot detection
- Flood prevention
- Customizable sensitivity
- Detailed logs
"""

import logging
from typing import Any

from core.services.bot.moderation.base_bot_service import BaseBotService
from core.services.system.user_bot_service import UserBotService

logger = logging.getLogger(__name__)


class AntiSpamService(BaseBotService):
    """
    Anti-spam protection service for user bots.

    Integrates with UserBotService to check messages
    for spam patterns and take action if spam is detected.
    """

    def __init__(
        self,
        user_id: int,
        feature_gate_service: Any,
        marketplace_repo: Any,
        moderation_service: UserBotService,
    ):
        """
        Initialize anti-spam service.

        Args:
            user_id: Bot owner's user ID
            feature_gate_service: Service for access control
            marketplace_repo: Repository for usage logging
            moderation_service: Service for moderation operations
        """
        super().__init__(user_id, feature_gate_service, marketplace_repo)
        self.moderation_service = moderation_service

    @property
    def service_key(self) -> str:
        return "bot_anti_spam"

    async def execute(self, **kwargs) -> dict[str, Any]:
        """
        Check a message for spam and take action if detected.

        Args:
            chat_id: Chat ID where message was sent
            sender_tg_id: Telegram ID of message sender
            message_text: Message text content
            message_id: Message ID for deletion
            has_links: Whether message contains links
            is_forward: Whether message is a forward

        Returns:
            dict with spam detection results
        """
        chat_id = kwargs.get("chat_id")
        sender_tg_id = kwargs.get("sender_tg_id")
        message_text = kwargs.get("message_text", "")
        message_id = kwargs.get("message_id")
        has_links = kwargs.get("has_links", False)
        is_forward = kwargs.get("is_forward", False)

        if not all([chat_id, sender_tg_id, message_text]):
            return {
                "is_spam": False,
                "action_taken": None,
                "error": "Missing required parameters",
            }

        # Get chat settings to check if spam protection is enabled
        settings = await self.moderation_service.get_settings(self.user_id, chat_id)

        if not settings or not settings.auto_delete_spam:
            return {
                "is_spam": False,
                "action_taken": None,
                "message": "Spam protection not enabled for this chat",
            }

        # Run spam detection
        spam_result = await self.moderation_service.detect_spam(
            message_text=message_text,
            has_links=has_links,
            is_forward=is_forward,
            sender_message_count=0,  # Could be enhanced with message counting
        )

        if not spam_result.is_spam:
            return {
                "is_spam": False,
                "confidence": spam_result.confidence,
                "patterns_matched": spam_result.patterns_matched,
                "action_taken": None,
            }

        # Spam detected - take action
        action_taken = "message_flagged"

        # If message_id provided and confidence is high, delete it
        if message_id and spam_result.confidence > 0.7:
            # The actual deletion happens in the message handler
            # This service just provides the detection logic
            action_taken = "message_deleted"

        logger.info(
            f"[AntiSpam] User {self.user_id} - Spam detected in chat {chat_id}: "
            f"confidence={spam_result.confidence:.2f}, "
            f"patterns={spam_result.patterns_matched}"
        )

        return {
            "is_spam": True,
            "confidence": spam_result.confidence,
            "patterns_matched": spam_result.patterns_matched,
            "reasons": spam_result.reasons,
            "action_taken": action_taken,
            "message_id": message_id,
        }

    async def is_enabled_for_chat(self, chat_id: int) -> bool:
        """Check if anti-spam is enabled for a specific chat."""
        settings = await self.moderation_service.get_settings(self.user_id, chat_id)
        return settings is not None and settings.auto_delete_spam

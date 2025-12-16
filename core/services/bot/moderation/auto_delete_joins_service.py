"""
Auto-Delete Joins Service - Automatic join/leave message cleanup

Marketplace service: bot_auto_delete_joins
Price: 30 credits/month

Features:
- Auto-delete joins
- Auto-delete leaves  
- Configurable delay
- Chat-specific settings
- Service message cleanup
"""

import asyncio
import logging
from typing import Any

from aiogram import Bot
from aiogram.types import Message

from core.services.bot.moderation.base_bot_service import BaseBotService
from core.services.system.user_bot_service import UserBotService


logger = logging.getLogger(__name__)


class AutoDeleteJoinsService(BaseBotService):
    """
    Auto-delete join/leave messages service for user bots.
    
    Integrates with UserBotService to clean up
    system messages about members joining or leaving chats.
    """

    def __init__(
        self,
        user_id: int,
        feature_gate_service: Any,
        marketplace_repo: Any,
        service: UserBotService,
        bot: Bot | None = None,
    ):
        """
        Initialize auto-delete joins service.
        
        Args:
            user_id: Bot owner's user ID
            feature_gate_service: Service for access control
            marketplace_repo: Repository for usage logging
            service: Service for moderation operations
            bot: Bot instance for message deletion
        """
        super().__init__(user_id, feature_gate_service, marketplace_repo)
        self.moderation_service = moderation_service
        self.bot = bot

    @property
    def service_key(self) -> str:
        return "bot_auto_delete_joins"

    async def execute(self, **kwargs) -> dict[str, Any]:
        """
        Delete a join/leave service message.
        
        Args:
            chat_id: Chat ID where message was sent
            message_id: Message ID to delete
            message_type: Type of service message ('join' or 'leave')
            delay_seconds: Optional delay before deletion (default: 0)
            
        Returns:
            dict with deletion results
        """
        chat_id = kwargs.get("chat_id")
        message_id = kwargs.get("message_id")
        message_type = kwargs.get("message_type", "join")
        delay_seconds = kwargs.get("delay_seconds", 0)
        
        if not all([chat_id, message_id]):
            return {
                "deleted": False,
                "error": "Missing required parameters (chat_id, message_id)",
            }
        
        if not self.bot:
            return {
                "deleted": False,
                "error": "Bot instance not available",
            }
        
        # Get chat settings to check if auto-delete is enabled
        settings = await self.moderation_service.get_settings(self.user_id, chat_id)
        
        if not settings:
            return {
                "deleted": False,
                "message": "No settings found for this chat",
            }
        
        # Check if feature is enabled
        if message_type == "join" and not settings.auto_delete_joins:
            return {
                "deleted": False,
                "message": "Auto-delete joins not enabled for this chat",
            }
        
        if message_type == "leave" and not settings.auto_delete_leaves:
            return {
                "deleted": False,
                "message": "Auto-delete leaves not enabled for this chat",
            }
        
        # Apply delay if specified
        if delay_seconds > 0:
            await asyncio.sleep(delay_seconds)
        
        # Delete the message
        try:
            await self.bot.delete_message(chat_id=chat_id, message_id=message_id)
            
            logger.info(
                f"[AutoDeleteJoins] User {self.user_id} - Deleted {message_type} message "
                f"in chat {chat_id} (message_id={message_id})"
            )
            
            return {
                "deleted": True,
                "message_type": message_type,
                "chat_id": chat_id,
                "message_id": message_id,
                "delay_applied": delay_seconds,
            }
            
        except Exception as e:
            logger.error(
                f"[AutoDeleteJoins] Failed to delete message {message_id} in chat {chat_id}: {e}"
            )
            return {
                "deleted": False,
                "error": str(e),
                "message_type": message_type,
            }

    async def is_enabled_for_chat(self, chat_id: int) -> tuple[bool, bool]:
        """
        Check if auto-delete is enabled for a specific chat.
        
        Returns:
            Tuple of (joins_enabled, leaves_enabled)
        """
        settings = await self.moderation_service.get_settings(self.user_id, chat_id)
        
        if not settings:
            return (False, False)
        
        return (settings.auto_delete_joins, settings.auto_delete_leaves)

    async def handle_service_message(self, message: Message) -> dict[str, Any]:
        """
        Handle a service message (join/leave) - convenience method.
        
        Args:
            message: Aiogram Message object
            
        Returns:
            dict with execution results
        """
        if not message.chat:
            return {"success": False, "error": "No chat in message"}
        
        # Determine message type
        message_type = "unknown"
        if message.new_chat_members:
            message_type = "join"
        elif message.left_chat_member:
            message_type = "leave"
        else:
            return {"success": False, "error": "Not a join/leave message"}
        
        # Get delete delay from settings
        settings = await self.moderation_service.get_settings(
            self.user_id, message.chat.id
        )
        delay = settings.auto_delete_delay_seconds if settings else 0
        
        # Execute deletion through feature-gated run()
        return await self.run(
            chat_id=message.chat.id,
            message_id=message.message_id,
            message_type=message_type,
            delay_seconds=delay,
        )

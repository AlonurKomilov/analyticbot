# infra/telegram/telegram_service_impl.py
"""
Telegram service implementation using aiogram.
"""

import logging
from typing import Dict, Any

from core.ports import TelegramService

logger = logging.getLogger(__name__)


class AiogramTelegramService(TelegramService):
    """Telegram service implementation using aiogram."""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self._bot = None
    
    async def _ensure_bot(self):
        """Ensure bot instance is created."""
        if self._bot is None:
            try:
                from aiogram import Bot
                self._bot = Bot(token=self.bot_token)
                logger.info("Telegram bot initialized")
            except ImportError:
                logger.error("aiogram not installed - Telegram service unavailable")
                raise RuntimeError("aiogram dependency required")
    
    async def send_message(self, chat_id: str, text: str, **kwargs) -> Dict[str, Any]:
        """Send text message to chat."""
        await self._ensure_bot()
        try:
            result = await self._bot.send_message(
                chat_id=int(chat_id),
                text=text,
                **kwargs
            )
            return {
                "message_id": result.message_id,
                "success": True,
                "chat_id": str(result.chat.id),
                "date": result.date.isoformat() if result.date else None
            }
        except Exception as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "chat_id": chat_id
            }
    
    async def send_media(self, chat_id: str, media_url: str, caption: str = "", **kwargs) -> Dict[str, Any]:
        """Send media message to chat."""
        await self._ensure_bot()
        try:
            # Determine media type from URL or kwargs
            media_type = kwargs.get("media_type", "photo")
            
            if media_type == "photo":
                result = await self._bot.send_photo(
                    chat_id=int(chat_id),
                    photo=media_url,
                    caption=caption,
                    **{k: v for k, v in kwargs.items() if k != "media_type"}
                )
            elif media_type == "video":
                result = await self._bot.send_video(
                    chat_id=int(chat_id),
                    video=media_url,
                    caption=caption,
                    **{k: v for k, v in kwargs.items() if k != "media_type"}
                )
            else:
                result = await self._bot.send_document(
                    chat_id=int(chat_id),
                    document=media_url,
                    caption=caption,
                    **{k: v for k, v in kwargs.items() if k != "media_type"}
                )
            
            return {
                "message_id": result.message_id,
                "success": True,
                "chat_id": str(result.chat.id),
                "media_url": media_url,
                "media_type": media_type
            }
        except Exception as e:
            logger.error(f"Failed to send media to {chat_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "chat_id": chat_id,
                "media_url": media_url
            }
    
    async def get_chat_info(self, chat_id: str) -> Dict[str, Any]:
        """Get chat information."""
        await self._ensure_bot()
        try:
            chat = await self._bot.get_chat(chat_id=int(chat_id))
            return {
                "id": str(chat.id),
                "title": chat.title,
                "username": chat.username,
                "type": chat.type,
                "description": getattr(chat, 'description', None),
                "member_count": getattr(chat, 'member_count', None),
                "success": True
            }
        except Exception as e:
            logger.error(f"Failed to get chat info for {chat_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "chat_id": chat_id
            }
    
    async def get_chat_members_count(self, chat_id: str) -> int:
        """Get chat members count."""
        await self._ensure_bot()
        try:
            count = await self._bot.get_chat_member_count(chat_id=int(chat_id))
            return count
        except Exception as e:
            logger.error(f"Failed to get member count for {chat_id}: {e}")
            return 0
    
    async def close(self):
        """Close bot session."""
        if self._bot:
            await self._bot.session.close()
            logger.info("Telegram bot session closed")
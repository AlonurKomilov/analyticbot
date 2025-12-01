"""
Bot Infrastructure Providers

Factory functions for bot client and dispatcher creation.
These are the foundational components for Telegram bot operation.
"""

import logging
import os
from typing import Any

from apps.bot.config import Settings as BotSettings

logger = logging.getLogger(__name__)


def create_bot_client(settings: BotSettings) -> Any | None:
    """Create bot client or return None for API-only deployments"""
    try:
        token = settings.BOT_TOKEN.get_secret_value() if hasattr(settings, "BOT_TOKEN") else None
    except Exception:
        token = os.getenv("BOT_TOKEN")

    if not token or token == "replace_me":
        logger.info("Bot token not configured - running in API-only mode")
        return None

    try:
        from aiogram import Bot as _AioBot
        from aiogram.client.default import DefaultBotProperties
        from aiogram.enums import ParseMode

        return _AioBot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    except ImportError:
        logger.warning("aiogram not installed - bot client unavailable")
        return None
    except Exception as e:
        # Handle invalid token format or other errors gracefully
        logger.warning(f"Failed to create bot client: {e} - running in API-only mode")
        return None


def create_dispatcher():
    """Create aiogram dispatcher"""
    try:
        from aiogram import Dispatcher as _AioDispatcher
        from aiogram.fsm.storage.memory import MemoryStorage

        return _AioDispatcher(storage=MemoryStorage())
    except ImportError:
        return None

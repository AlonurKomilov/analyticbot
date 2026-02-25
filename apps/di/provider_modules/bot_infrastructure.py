"""
Bot Infrastructure Providers

Factory functions for bot client and dispatcher creation.
These are the foundational components for Telegram bot operation.
"""

import logging
import os
from datetime import timedelta
from typing import Any

from apps.bot.system.config import Settings as BotSettings

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
    """
    Create aiogram dispatcher with scalable storage.

    Uses Redis storage for production (multi-instance support),
    falls back to MemoryStorage for development/testing.
    """
    try:
        from aiogram import Dispatcher as _AioDispatcher
        from aiogram.fsm.storage.base import BaseStorage, DefaultKeyBuilder
        from aiogram.fsm.storage.memory import MemoryStorage

        storage: BaseStorage = MemoryStorage()

        # Try Redis first for production scalability
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            try:
                from aiogram.fsm.storage.redis import RedisStorage

                storage = RedisStorage.from_url(
                    redis_url,
                    key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
                    state_ttl=timedelta(hours=24),
                    data_ttl=timedelta(hours=24),
                )
                logger.info("✅ DI Dispatcher using Redis storage (production-ready)")
            except ImportError:
                logger.warning("⚠️ aiogram Redis storage not available, using memory")
            except Exception as e:
                logger.warning(f"⚠️ Redis connection failed ({e}), using memory storage")
        else:
            logger.warning(
                "⚠️ REDIS_URL not set - using MemoryStorage (not suitable for production)"
            )

        return _AioDispatcher(storage=storage)
    except ImportError:
        return None

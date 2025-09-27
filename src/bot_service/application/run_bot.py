#!/usr/bin/env python3
"""
AnalyticBot - Telegram Bot Runner with Layered Architecture
Uses core services via dependency injection
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from src.bot_service.deps import bot_container
from src.bot_service.handlers.admin_handlers import router as admin_router
from src.bot_service.handlers.content_protection import router as content_router
from src.bot_service.handlers.user_handlers import router as user_router
from src.bot_service.middlewares.dependency_middleware import DependencyMiddleware
from src.bot_service.middlewares.i18n import i18n_middleware
from src.bot_service.schedule_handlers import schedule_router

from config import settings


def create_bot():
    """Create bot instance with development mode support"""
    token = settings.bot.BOT_TOKEN.get_secret_value()

    # Development mode: Create mock bot if token is invalid
    if token in ("your_bot_token_here", "test_token"):
        from unittest.mock import Mock

        class MockBot:
            def __init__(self):
                self.session = Mock()
                self.id = 7900046521
                self.username = "test_bot"
                self.first_name = "Test Bot"

            async def get_me(self):
                return self

            async def close(self):
                pass

        logging.getLogger(__name__).warning("Using mock bot for development (invalid token)")
        return MockBot()

    # Create bot with HTML parse mode as default
    return Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


def create_dispatcher(bot):
    """Create dispatcher with all handlers"""
    dp = Dispatcher()

    # Set up middleware for dependency injection
    dp.update.outer_middleware(DependencyMiddleware(bot_container))
    dp.update.outer_middleware(i18n_middleware)

    # Include all routers in the correct order
    dp.include_router(user_router)  # Basic user commands like /start
    dp.include_router(admin_router)  # Admin commands like /add_channel
    dp.include_router(content_router)  # Content protection handlers
    dp.include_router(schedule_router)  # Scheduling handlers

    return dp


async def main():
    """Main bot runner with layered architecture"""
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.monitoring.LOG_LEVEL.value),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger = logging.getLogger(__name__)

    try:
        # Initialize bot
        bot = create_bot()
        dp = create_dispatcher(bot)

        # Initialize DI container
        await bot_container.init_db_pool()

        logger.info("Starting AnalyticBot with layered architecture...")
        logger.info(f"Admin IDs: {settings.bot.ADMIN_IDS}")

        # Start polling (skip for mock bot)
        if hasattr(bot, "session"):
            await dp.start_polling(bot)
        else:
            logger.info("Mock bot running in development mode - no polling")
            # Keep running for testing
            await asyncio.sleep(3600)

    except Exception as e:
        logger.error(f"Bot error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # Cleanup
        await bot_container.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

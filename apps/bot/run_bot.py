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
from config import settings
from apps.bot.handlers import schedule_router
from apps.bot.deps import bot_container


async def main():
    """Main bot runner with layered architecture"""
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.monitoring.LOG_LEVEL.value),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize bot
        bot = Bot(token=settings.bot.BOT_TOKEN.get_secret_value())
        dp = Dispatcher()
        
        # Register routers
        dp.include_router(schedule_router)
        
        # Initialize DI container
        await bot_container.init_db_pool()
        
        logger.info("Starting AnalyticBot with layered architecture...")
        logger.info(f"Admin IDs: {settings.bot.ADMIN_IDS}")
        
        # Start polling
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Bot error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # Cleanup
        await bot_container.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

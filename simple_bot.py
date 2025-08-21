#!/usr/bin/env python3
"""
Simple bot test without complex dependencies
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from bot.config import settings

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

async def main():
    """Simple bot startup for testing"""
    try:
        bot = Bot(token=settings.BOT_TOKEN.get_secret_value())
        dp = Dispatcher(storage=MemoryStorage())
        
        logger.info("🚀 Starting AnalyticBot (simple mode)...")
        
        # Simple handler
        @dp.message()
        async def echo_handler(message):
            await message.reply(f"Salom! Bot ishlayapti! 🤖\n\nSizning xabaringiz: {message.text}")
        
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Bot startup error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())

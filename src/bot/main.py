"""Bot entry point"""

from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.bot.handlers import router
from src.config import settings
from src.db.session import init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


async def main() -> None:
    logger.info("Starting Analyticbot v2...")

    # Init database tables
    await init_db()

    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)

    logger.info("Bot is running. Polling for updates...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

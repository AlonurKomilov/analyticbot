"""Bot entry point"""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.analyzer.fetcher import disconnect_telethon_client
from src.bot.handlers import router
from src.cache import close_redis
from src.config import settings
from src.db.session import init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


async def _notify_admin(bot: Bot, text: str) -> None:
    """Send a notification to the admin if ADMIN_TELEGRAM_ID is configured."""
    if not settings.ADMIN_ID:
        return
    try:
        await bot.send_message(settings.ADMIN_ID, text, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.warning(f"Could not notify admin: {e}")


async def main() -> None:
    logger.info("Starting Analyticbot v2...")

    # Init database tables
    await init_db()

    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)

    # Auto-detect bot username if not set in env
    if not settings.BOT_USERNAME:
        me = await bot.get_me()
        if me.username:
            settings.BOT_USERNAME = me.username
            logger.info(f"Bot username: @{settings.BOT_USERNAME}")

    start_time = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    await _notify_admin(bot, f"🟢 <b>Analyticbot started</b>\n{start_time}")

    logger.info("Bot is running. Polling for updates...")
    try:
        await dp.start_polling(bot)
    finally:
        logger.info("Shutting down...")
        await _notify_admin(bot, "🔴 <b>Analyticbot shutting down</b>")
        await disconnect_telethon_client()
        await close_redis()


if __name__ == "__main__":
    asyncio.run(main())

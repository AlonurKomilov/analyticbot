import asyncio
import json
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage

from src.bot_service.config import settings
from src.bot_service.config import settings as app_settings
from src.bot_service.container import container
from src.bot_service.handlers import admin_handlers, user_handlers
from src.bot_service.middlewares.dependency_middleware import DependencyMiddleware
from src.bot_service.middlewares.i18n import i18n_middleware

if app_settings.LOG_FORMAT == "json":

    class _JsonFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            base = {"level": record.levelname, "name": record.name, "message": record.getMessage()}
            if record.exc_info:
                base["exc_info"] = self.formatException(record.exc_info)
            return json.dumps(base, ensure_ascii=False)

    handler = logging.StreamHandler()
    handler.setFormatter(_JsonFormatter())
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers[:] = [handler]
else:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


async def main():
    """
    Botni ishga tushiruvchi asosiy funksiya.
    """
    pool = await container.db_session()
    try:
        storage = RedisStorage.from_url(
            str(settings.REDIS_URL),
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )
    except Exception:
        logger.warning("Redis not available – falling back to in-memory FSM storage")
        storage = MemoryStorage()
    bot = Bot(
        token=settings.BOT_TOKEN.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=storage)
    dp.update.outer_middleware(DependencyMiddleware(container))
    dp.update.outer_middleware(i18n_middleware)
    dp.include_router(admin_handlers.router)
    dp.include_router(user_handlers.router)
    logger.info("Bot ishga tushirildi.")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await dp.storage.close()
        await bot.session.close()
        try:
            await pool.close()
        except Exception:
            pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")

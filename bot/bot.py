import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import settings
from bot.container import container
from bot.handlers import admin_handlers, user_handlers
from bot.middlewares.dependency_middleware import DependencyMiddleware
from bot.middlewares.i18n import i18n_middleware

# Logger sozlamalari
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """
    Botni ishga tushiruvchi asosiy funksiya.
    """
    # DB pool konteyner orqali lazy yaratiladi (bir marta yaratiladi)
    pool = await container.db_session()  # type: ignore[func-returns-value]

    # Redis (FSM holatlari) – to'g'ri konfiguratsiya nomi REDIS_URL; fallback Memory
    try:
        storage = RedisStorage.from_url(
            str(settings.REDIS_URL),
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )
    except Exception:
        logger.warning("Redis not available – falling back to in-memory FSM storage")
        storage = MemoryStorage()

    # Bot va Dispatcher obyektlarini yaratish
    bot = Bot(token=settings.BOT_TOKEN.get_secret_value(), parse_mode="HTML")
    dp = Dispatcher(storage=storage)

    # YAKUNIY TUZATISH: Middleware'larni to'g'ri tartibda ulaymiz

    # 1. BIRINCHI bo'lib, har bir xabarga kerakli bog'liqliklar (masalan, DB ulanishi) qo'shiladi.
    # DI middleware konteynerni oladi (oldingi noto'g'ri 'pool=' param o'chirildi)
    dp.update.outer_middleware(DependencyMiddleware(container))

    # 2. IKKINCHI bo'lib, bog'liqliklar mavjud bo'lgandan so'ng, lokalizatsiya (i18n) ishlaydi.
    dp.update.outer_middleware(i18n_middleware)

    # Handlers (buyruqlarga javob beruvchilar) ro'yxatdan o'tkaziladi
    dp.include_router(admin_handlers.router)
    dp.include_router(user_handlers.router)

    logger.info("Bot ishga tushirildi.")

    try:
        # Botni ishga tushirish
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        # To'xtatilganda ulanishlarni yopish
        await dp.storage.close()
        await bot.session.close()
        try:
            await pool.close()  # type: ignore[attr-defined]
        except Exception:
            pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")

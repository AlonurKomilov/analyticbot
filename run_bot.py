import asyncio
import logging
import os
from typing import cast

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores import FluentRuntimeCore
from aiogram_i18n.managers.base import BaseManager
import redis.asyncio as redis
import sentry_sdk
from sqlalchemy.ext.asyncio import async_sessionmaker

from bot.config import settings
from bot.container import container
from bot.database.repositories import UserRepository
from bot.handlers import admin_handlers, user_handlers
from bot.middlewares.dependency_middleware import DependencyMiddleware
from bot.utils.language_manager import LanguageManager


# --- CI-safe BOT_TOKEN check ---
token = None
try:
    token = settings.BOT_TOKEN.get_secret_value()
except Exception:
    token = os.getenv("BOT_TOKEN")

PLACEHOLDER = "replace_me"  # nosec B105
if not token or token == PLACEHOLDER:
    print("[bot] BOT_TOKEN is not set; skipping bot startup (CI-safe).")
    raise SystemExit(0)


async def _build_storage(config) -> BaseStorage:
    """Redis ishlasa RedisStorage; bo'lmasa MemoryStorage."""
    redis_url = None
    try:
        redis_url = config.REDIS_URL.unicode_string()
    except Exception:
        pass

    if not redis_url:
        return MemoryStorage()

    if hasattr(RedisStorage, "from_url"):
        try:
            return RedisStorage.from_url(redis_url)  # type: ignore[attr-defined]
        except Exception as e:
            logging.getLogger(__name__).warning(
                "RedisStorage.from_url failed (%s). Falling back to Redis instance.", e
            )

    try:
        r = redis.from_url(redis_url)
        return RedisStorage(redis=r)
    except Exception as e:
        logging.getLogger(__name__).warning(
            "RedisStorage(redis=...) init failed (%s). Falling back to MemoryStorage.", e
        )
        return MemoryStorage()


async def _warmup_db_session() -> None:
    """
    punctuated.Singleton(create_pool) birinchi chaqiriqda coroutine qaytarishi mumkin.
    Uni bir marta await qilamiz; xato bo‘lsa log qilib davom etamiz (CI/dev friendly).
    """
    ds = container.db_session  # punctuated.Singleton
    try:
        val = ds() if callable(ds) else ds  # coroutine | async_sessionmaker | asyncpg.Pool
    except Exception:
        return

    if asyncio.iscoroutine(val):
        try:
            real = await val  # asyncpg.Pool qaytishi ehtimoliy
        except Exception as e:
            logging.getLogger(__name__).warning(
                "[warmup] DB pool connect failed: %s (continue without DB)", e
            )
            return
        # Singleton ichidagi keshni real qiymatga almashtiramiz
        try:
            ds._instance = real  # type: ignore[attr-defined]
        except Exception:
            pass
        # punq alias ham real qiymatni olishi uchun qayta ro'yxatdan o'tkazamiz
        try:
            container.register(async_sessionmaker, factory=lambda: real)  # harmless
        except Exception:
            pass


async def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    config = settings

    # Sentry
    if getattr(config, "SENTRY_DSN", None):
        sentry_sdk.init(dsn=str(config.SENTRY_DSN), traces_sample_rate=1.0)

    # DB warm-up (repo/servicelar resolve’idan oldin)
    await _warmup_db_session()

    # DI: real Bot instansiyasi
    bot = cast(Bot, container.resolve(Bot))

    # FSM Storage
    storage = await _build_storage(config)

    # Dispatcher
    dp = Dispatcher(storage=storage)

    # DI → repo va LanguageManager
    user_repo = cast(UserRepository, container.resolve(UserRepository))
    language_manager = LanguageManager(user_repo=user_repo, config=config)

    # --- i18n middleware (AVVAL qo'yiladi) ---
    _i18n_middleware = I18nMiddleware(
        core=FluentRuntimeCore(path="bot/locales/{locale}"),
        default_locale=getattr(config, "DEFAULT_LOCALE", "en"),
        manager=cast(BaseManager, language_manager),  # <-- shu
    )

    # --- DI middleware (i18n’dan KEYIN) ---
    dp.update.middleware(DependencyMiddleware(container=container))

    # Routers
    dp.include_router(admin_handlers.router)
    dp.include_router(user_handlers.router)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Bot is starting polling...")

        allowed = dp.resolve_used_update_types()
        await dp.start_polling(bot, allowed_updates=allowed)
    finally:
        logger.info("Bot is shutting down.")
        try:
            await dp.storage.close()
        except Exception:
            pass
        try:
            await bot.session.close()
        except Exception:
            pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot was stopped by user.")

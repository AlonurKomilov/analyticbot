import os
from bot.config import settings

token = None
try:
    token = settings.BOT_TOKEN.get_secret_value()
except Exception:
    token = os.getenv("BOT_TOKEN")

if not token or token == "replace_me":
    print("[bot] BOT_TOKEN is not set; skipping bot startup (CI-safe).")
    raise SystemExit(0)


import asyncio
import logging

import sentry_sdk
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores import FluentRuntimeCore

from bot.config import settings

# Imports are now direct, without 'src'
from bot.container import container
from bot.database.repositories import UserRepository
from bot.handlers import admin_handlers, user_handlers
from bot.middlewares.dependency_middleware import DependencyMiddleware
from bot.utils.language_manager import LanguageManager


async def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    config = settings

    if config.SENTRY_DSN:
        sentry_sdk.init(dsn=str(config.SENTRY_DSN), traces_sample_rate=1.0)

    bot: Bot = container.resolve(Bot)
    storage = RedisStorage.from_url(config.REDIS_URL.unicode_string())
    dp = Dispatcher(storage=storage)

    user_repo = container.resolve(UserRepository)
    language_manager = LanguageManager(user_repo=user_repo, config=config)
    dp.update.middleware(DependencyMiddleware(container=container))

    i18n_middleware = I18nMiddleware(
        core=FluentRuntimeCore(path="bot/locales/{locale}/LC_MESSAGES"),
        default_locale=config.DEFAULT_LOCALE,
        manager=language_manager,
    )
    i18n_middleware.setup(dp)

    dp.include_router(admin_handlers.router)
    dp.include_router(user_handlers.router)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Bot is starting polling...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        logger.info("Bot is shutting down.")
        await dp.storage.close()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot was stopped by user.")

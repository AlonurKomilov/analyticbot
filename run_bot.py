import asyncio
import logging
import os
from typing import cast

import redis.asyncio as redis
import sentry_sdk
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores import FluentRuntimeCore
from aiogram_i18n.managers.base import BaseManager
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
            "RedisStorage(redis=...) init failed (%s). Falling back to MemoryStorage.",
            e,
        )
        return MemoryStorage()


async def _warmup_db_session() -> None:
    """
    punctuated.Singleton(create_pool) birinchi chaqiriqda coroutine qaytarishi mumkin.
    Uni bir marta await qilamiz; xato bo‘lsa log qilib davom etamiz (CI/dev friendly).
    """
    ds = container.db_session  # punctuated.Singleton
    try:
        val = (
            ds() if callable(ds) else ds
        )  # coroutine | async_sessionmaker | asyncpg.Pool
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
        import asyncio

import logging
import os
import signal
import sys
from typing import cast

import redis.asyncio as redis
import sentry_sdk
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores import FluentRuntimeCore
from aiogram_i18n.managers.base import BaseManager
from sqlalchemy.ext.asyncio import async_sessionmaker

from bot.config import settings
from bot.container import container
from bot.database.repositories import UserRepository
from bot.handlers import admin_handlers, user_handlers
from bot.middlewares.dependency_middleware import DependencyMiddleware
from bot.utils.error_handler import ErrorContext, ErrorHandler
from bot.utils.language_manager import LanguageManager
from bot.utils.monitoring import health_monitor, metrics


# Setup logging with improved configuration
def setup_logging(config):
    """Setup enhanced logging configuration"""
    logging_config = config.get_logging_config()
    if logging_config.get("version"):
        import logging.config
        logging.config.dictConfig(logging_config)
    else:
        level = getattr(logging, config.LOG_LEVEL.value, logging.INFO)
        logging.basicConfig(
            level=level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

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
    """Enhanced storage builder with better error handling"""
    redis_url = None
    try:
        redis_url = config.REDIS_URL.unicode_string()
    except Exception:

    if not redis_url:
        logging.getLogger(__name__).info("Using MemoryStorage (no Redis URL configured)")
        return MemoryStorage()

    # Try Redis storage with improved error handling
    try:
        if hasattr(RedisStorage, "from_url"):
            storage = RedisStorage.from_url(redis_url)  # type: ignore[attr-defined]
            logging.getLogger(__name__).info("Using RedisStorage with from_url method")
            return storage
    except Exception as e:
        context = ErrorContext().add("storage_method", "from_url").add("redis_url", redis_url)
        ErrorHandler.log_error(e, context, level=logging.WARNING)

    # Fallback to Redis instance method
    try:
        r = redis.from_url(redis_url)
        await r.ping()  # Test connection
        storage = RedisStorage(redis=r)
        logging.getLogger(__name__).info("Using RedisStorage with Redis instance")
        return storage
    except Exception as e:
        context = ErrorContext().add("storage_method", "redis_instance").add("redis_url", redis_url)
        ErrorHandler.log_error(e, context, level=logging.WARNING)
        logging.getLogger(__name__).warning("Falling back to MemoryStorage due to Redis connection issues")
        return MemoryStorage()


async def _warmup_db_session() -> bool:
    """
    Enhanced database warmup with better monitoring and error handling.
    Returns True if successful, False otherwise.
    """
    logger = logging.getLogger(__name__)
    ds = container.db_session  # punctuated.Singleton
    
    try:
        val = ds() if callable(ds) else ds
    except Exception as e:
        context = ErrorContext().add("operation", "db_warmup_get_session")
        ErrorHandler.handle_database_error(e, context)
        return False

    if asyncio.iscoroutine(val):
        try:
            logger.info("Initializing database connection pool...")
            real = await val  # asyncpg.Pool expected
            
            # Test the connection
            if hasattr(real, 'execute'):
                await real.execute('SELECT 1')
            
            # Update singleton cache
            try:
                ds._instance = real  # type: ignore[attr-defined]
            except Exception:
                
            # Update punq container
            try:
                container.register(async_sessionmaker, factory=lambda: real)
            except Exception:
            
            logger.info("Database connection pool initialized successfully")
            metrics.record_metric("database_warmup", 1.0, {"status": "success"})
            return True
            
        except Exception as e:
            context = ErrorContext().add("operation", "db_warmup_connection")
            ErrorHandler.handle_database_error(e, context)
            metrics.record_metric("database_warmup", 0.0, {"status": "failed"})
            return False
    else:
        logger.info("Database session already warmed up")
        return True


async def setup_signal_handlers(bot: Bot, dp: Dispatcher):
    """Setup graceful shutdown signal handlers"""
    logger = logging.getLogger(__name__)
    
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        asyncio.create_task(shutdown(bot, dp))
    
    if sys.platform != 'win32':  # Unix-like systems
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)


async def shutdown(bot: Bot, dp: Dispatcher):
    """Graceful shutdown procedure"""
    logger = logging.getLogger(__name__)
    logger.info("Shutting down bot gracefully...")
    
    try:
        # Stop polling
        await dp.stop_polling()
        logger.info("Stopped polling")
        
        # Close storage
        if dp.storage:
            await dp.storage.close()
            logger.info("Closed storage")
        
        # Close bot session
        if bot.session:
            await bot.session.close()
            logger.info("Closed bot session")
        
        # Close database connections
        try:
            from bot.database.db import db_manager
            await db_manager.close_pool()
            logger.info("Closed database pool")
        except Exception as e:
            logger.warning(f"Error closing database pool: {e}")
        
        logger.info("Graceful shutdown completed")
        
    except Exception as e:
        context = ErrorContext().add("operation", "graceful_shutdown")
        ErrorHandler.log_error(e, context)


async def main():
    config = settings
    setup_logging(config)
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting AnalyticBot v1.0.0")
    logger.info(f"Environment: {'Development' if config.DEBUG_MODE else 'Production'}")
    logger.info(f"Log level: {config.LOG_LEVEL.value}")

    # Initialize Sentry for error tracking
    if config.SENTRY_DSN:
        sentry_sdk.init(
            dsn=str(config.SENTRY_DSN), 
            traces_sample_rate=1.0,
            environment="development" if config.DEBUG_MODE else "production"
        )
        logger.info("Sentry error tracking initialized")

    # Database warmup (critical for proper operation)
    logger.info("Starting database warmup...")
    db_success = await _warmup_db_session()
    if not db_success:
        logger.error("Database warmup failed, continuing with limited functionality")
    
    # Initialize DI container
    try:
        bot = cast(Bot, container.resolve(Bot))
        logger.info("Bot instance initialized from container")
    except Exception as e:
        context = ErrorContext().add("operation", "bot_initialization")
        ErrorHandler.log_error(e, context)
        raise

    # Setup storage with retry logic
    try:
        storage = await _build_storage(config)
        logger.info(f"Storage initialized: {type(storage).__name__}")
    except Exception as e:
        context = ErrorContext().add("operation", "storage_initialization")
        ErrorHandler.log_error(e, context)
        logger.warning("Using fallback MemoryStorage")
        storage = MemoryStorage()

    # Initialize dispatcher
    dp = Dispatcher(storage=storage)
    logger.info("Dispatcher initialized")

    # Setup signal handlers for graceful shutdown
    await setup_signal_handlers(bot, dp)

    # Initialize repositories and services
    try:
        user_repo = cast(UserRepository, container.resolve(UserRepository))
        language_manager = LanguageManager(user_repo=user_repo, config=config)
        logger.info("Repositories and services initialized")
    except Exception as e:
        context = ErrorContext().add("operation", "services_initialization")
        ErrorHandler.log_error(e, context)
        raise

        # Setup middlewares (order is important!)
    try:
        # i18n middleware (should be first)
        i18n_middleware = I18nMiddleware(
            core=FluentRuntimeCore(path="bot/locales/{locale}"),
            default_locale=config.DEFAULT_LOCALE,
            manager=cast(BaseManager, language_manager),
        )
        dp.update.middleware(i18n_middleware)
        logger.info("i18n middleware registered")

        # Dependency injection middleware
        dp.update.middleware(DependencyMiddleware(container=container))
        logger.info("Dependency injection middleware registered")

    except Exception as e:
        context = ErrorContext().add("operation", "middleware_setup")
        ErrorHandler.log_error(e, context)
        raise

    # Register routers
    try:
        dp.include_router(admin_handlers.router)
        dp.include_router(user_handlers.router)
        logger.info("Handlers registered")
    except Exception as e:
        context = ErrorContext().add("operation", "handlers_registration")
        ErrorHandler.log_error(e, context)
        raise

    # Start health monitoring
    if config.ENABLE_HEALTH_MONITORING:
        logger.info("Health monitoring enabled")

    try:
        # Clear webhook and start polling
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook cleared, starting polling...")

        # Record startup metric
        metrics.record_metric("bot_startup", 1.0, {"version": "1.0.0"})

        allowed = dp.resolve_used_update_types()
        logger.info(f"Allowed update types: {allowed}")
        
        await dp.start_polling(bot, allowed_updates=allowed)
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (KeyboardInterrupt)")
    except Exception as e:
        context = ErrorContext().add("operation", "bot_polling")
        ErrorHandler.log_error(e, context)
        raise
    finally:
        await shutdown(bot, dp)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot was stopped by user.")
    except Exception as e:
        logging.error(f"Fatal error during bot startup: {e}", exc_info=True)
        sys.exit(1)
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

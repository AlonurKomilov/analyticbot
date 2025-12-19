"""
Bot Application Module - System and User Bot Management

Structure:
- system/: System bot (ENV-configured BOT_TOKEN)
- user/: User bots (database credentials, multi-tenant)
- shared/: Shared resources (keyboards, locales)
"""

import logging
from datetime import timedelta

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.base import BaseStorage, DefaultKeyBuilder
from aiogram.fsm.storage.memory import MemoryStorage

from config.settings import Settings

logger = logging.getLogger(__name__)


def _create_fsm_storage(settings: Settings) -> BaseStorage:
    """
    Create FSM storage - Redis for production scalability, Memory for development.
    
    Redis storage is required for:
    - Multi-instance deployments (100K+ users)
    - State persistence across restarts
    - Horizontal scaling
    """
    redis_url = getattr(settings, 'REDIS_URL', None)
    
    if redis_url:
        try:
            from aiogram.fsm.storage.redis import RedisStorage
            
            storage = RedisStorage.from_url(
                str(redis_url),
                key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
                state_ttl=timedelta(hours=24),  # Auto-expire old state
                data_ttl=timedelta(hours=24),
            )
            logger.info("✅ FSM using Redis storage (production-ready)")
            return storage
        except ImportError:
            logger.warning("⚠️ aiogram Redis storage not available, falling back to memory")
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed ({e}), falling back to memory")
    
    logger.warning("⚠️ FSM using MemoryStorage - NOT suitable for production scaling!")
    return MemoryStorage()


class AnalyticBot:
    """Main bot application class"""

    def __init__(self, token: str):
        # Lazy imports to avoid circular dependencies
        from apps.bot.system.handlers import alerts, exports
        from apps.bot.system.handlers.bot_microhandlers import bot_microhandlers_router
        from apps.bot.system.middlewares.suspension_middleware import SuspensionCheckMiddleware
        from apps.bot.system.middlewares.throttle import ThrottleMiddleware
        
        self.settings = Settings()
        self.bot = Bot(token=token)
        
        # Use Redis storage for production scalability
        storage = _create_fsm_storage(self.settings)
        self.dp = Dispatcher(storage=storage)

        # Setup middleware
        # Suspension check runs first to block suspended users
        self.dp.message.middleware(SuspensionCheckMiddleware())
        self.dp.callback_query.middleware(SuspensionCheckMiddleware())

        # Throttling to prevent spam
        self.dp.message.middleware(ThrottleMiddleware())
        self.dp.callback_query.middleware(ThrottleMiddleware())
        
        # Store references for handler registration
        self._alerts = alerts
        self._exports = exports
        self._bot_microhandlers_router = bot_microhandlers_router

        # Register handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register bot handlers"""
        # Bot Microhandlers (always enabled - replaces monolithic analytics_v2)
        self.dp.include_router(self._bot_microhandlers_router)
        logger.info("Bot Microhandlers registered (analytics, export, alerts)")

        # Legacy alert handlers (if enabled and needed)
        if self.settings.ALERTS_ENABLED:
            self.dp.include_router(self._alerts.router)
            logger.info("Legacy alert handlers registered")

        # Legacy export handlers (if enabled and needed)
        if self.settings.EXPORT_ENABLED:
            self.dp.include_router(self._exports.router)
            logger.info("Legacy export handlers registered")

    async def start_polling(self):
        """Start bot polling"""
        logger.info("Starting bot polling...")
        await self.dp.start_polling(self.bot)

    async def start_webhook(self, webhook_url: str, webhook_path: str = "/webhook"):
        """Start bot with webhook"""
        logger.info(f"Setting webhook: {webhook_url}")
        await self.bot.set_webhook(webhook_url)

        # Return webhook handler for web server
        from aiogram.webhook.aiohttp_server import SimpleRequestHandler

        return SimpleRequestHandler(dispatcher=self.dp, bot=self.bot)

    async def stop(self):
        """Stop bot gracefully"""
        logger.info("Stopping bot...")
        await self.bot.session.close()


def create_bot() -> AnalyticBot:
    """Factory function to create bot instance"""
    settings = Settings()

    if not settings.BOT_TOKEN:
        raise ValueError("BOT_TOKEN is required")

    return AnalyticBot(settings.BOT_TOKEN.get_secret_value())


async def run_bot():
    """Main entry point for running the bot"""
    try:
        bot = create_bot()
        await bot.start_polling()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot failed: {e}")
        raise

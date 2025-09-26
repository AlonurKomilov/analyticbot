"""
Bot Application Module
Telegram bot with Analytics V2 integration and alert system
"""

import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from apps.bot.handlers import alerts, exports
from apps.bot.handlers.bot_microhandlers import bot_microhandlers_router
from apps.bot.middleware.throttle import ThrottleMiddleware
from config.settings import Settings

logger = logging.getLogger(__name__)


class AnalyticBot:
    """Main bot application class"""

    def __init__(self, token: str):
        self.bot = Bot(token=token)
        self.dp = Dispatcher(storage=MemoryStorage())
        self.settings = Settings()

        # Setup middleware
        self.dp.message.middleware(ThrottleMiddleware())
        self.dp.callback_query.middleware(ThrottleMiddleware())

        # Register handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register bot handlers"""
        # Bot Microhandlers (always enabled - replaces monolithic analytics_v2)
        self.dp.include_router(bot_microhandlers_router)
        logger.info("Bot Microhandlers registered (analytics, export, alerts)")

        # Legacy alert handlers (if enabled and needed)
        if self.settings.ALERTS_ENABLED:
            self.dp.include_router(alerts.router)
            logger.info("Legacy alert handlers registered")

        # Legacy export handlers (if enabled and needed)
        if self.settings.EXPORT_ENABLED:
            self.dp.include_router(exports.router)
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

    return AnalyticBot(settings.BOT_TOKEN)


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

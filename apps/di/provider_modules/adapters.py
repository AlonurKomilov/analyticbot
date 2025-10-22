"""
Bot Adapter Providers

Factory functions for bot adapters.
These are thin layers that adapt core services for bot usage.
"""

import logging

logger = logging.getLogger(__name__)


async def create_bot_analytics_adapter(core_analytics_service=None, bot=None, **kwargs):
    """Create bot analytics adapter (thin layer over core service)"""
    try:
        from apps.bot.adapters.analytics_adapter import BotAnalyticsAdapter
        from infra.adapters.analytics.aiogram_bot_adapter import AiogramBotAdapter

        # Only create if core service is available
        if core_analytics_service is None:
            return None

        # Create telegram port from bot (factory pattern in DI container)
        telegram_port = AiogramBotAdapter(bot) if bot else None

        return BotAnalyticsAdapter(
            batch_processor=core_analytics_service, telegram_port=telegram_port
        )
    except ImportError as e:
        logger.warning(f"Bot analytics adapter not available: {e}")
        return None


async def create_bot_reporting_adapter(core_reporting_service=None, **kwargs):
    """Create bot reporting adapter (thin layer over core service)"""
    try:
        from apps.bot.adapters.reporting_adapter import BotReportingAdapter

        # Only create if core service is available
        if core_reporting_service is None:
            return None

        return BotReportingAdapter(reporting_system=core_reporting_service)
    except ImportError as e:
        logger.warning(f"Bot reporting adapter not available: {e}")
        return None


async def create_bot_dashboard_adapter(core_dashboard_service=None, **kwargs):
    """Create bot dashboard adapter (thin layer over core service)"""
    try:
        from apps.bot.adapters.dashboard_adapter import BotDashboardAdapter

        return BotDashboardAdapter(dashboard=core_dashboard_service)
    except ImportError as e:
        logger.warning(f"Bot dashboard adapter not available: {e}")
        return None


def create_aiogram_message_sender(bot=None, **kwargs):
    """Create Aiogram message sender adapter"""
    try:
        from apps.bot.adapters.scheduling_adapters import AiogramMessageSender

        if bot is None:
            logger.warning("Cannot create message sender: bot is None")
            return None

        return AiogramMessageSender(bot=bot)
    except ImportError as e:
        logger.warning(f"Message sender adapter not available: {e}")
        return None


def create_aiogram_markup_builder(**kwargs):
    """Create Aiogram markup builder adapter"""
    try:
        from apps.bot.adapters.scheduling_adapters import AiogramMarkupBuilder

        return AiogramMarkupBuilder()
    except ImportError as e:
        logger.warning(f"Markup builder adapter not available: {e}")
        return None

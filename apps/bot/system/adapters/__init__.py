"""
Bot Adapters Package
"""

from apps.bot.system.adapters.analytics_adapter import BotAnalyticsAdapter
from apps.bot.system.adapters.dashboard_adapter import BotDashboardAdapter
from apps.bot.system.adapters.reporting_adapter import BotReportingAdapter
from apps.bot.system.adapters.scheduling_adapters import (
    AiogramMarkupBuilder,
    AiogramMessageSender,
)

__all__ = [
    "BotAnalyticsAdapter",
    "BotReportingAdapter",
    "BotDashboardAdapter",
    "AiogramMessageSender",
    "AiogramMarkupBuilder",
]

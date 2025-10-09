"""
Analytics Adapters - Infrastructure Layer
==========================================

Concrete implementations of analytics service adapters.

Available Adapters:
- MockAnalyticsAdapter: Mock implementation for testing
- TelegramAnalyticsAdapter: Telegram API integration (with MTProto guard)
- AnalyticsAdapterFactory: Factory for creating adapters

Usage:
    from infra.adapters.analytics import AnalyticsAdapterFactory, AnalyticsProvider

    adapter = AnalyticsAdapterFactory.create_adapter(AnalyticsProvider.TELEGRAM)
"""

from typing import TYPE_CHECKING

from .factory import AnalyticsAdapterFactory, AnalyticsProvider
from .mock_analytics_adapter import MockAnalyticsAdapter

# MTProto guarded imports - only import at type checking time
if TYPE_CHECKING:
    from .tg_analytics_adapter import RateLimitConfig, TelegramAnalyticsAdapter
else:
    # Runtime: lazy import to avoid MTProto dependencies unless needed
    RateLimitConfig = None  # type: ignore
    TelegramAnalyticsAdapter = None  # type: ignore

    def __getattr__(name: str):
        """Lazy import for MTProto components"""
        if name == "TelegramAnalyticsAdapter":
            from .tg_analytics_adapter import TelegramAnalyticsAdapter
            return TelegramAnalyticsAdapter
        elif name == "RateLimitConfig":
            from .tg_analytics_adapter import RateLimitConfig
            return RateLimitConfig
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "AnalyticsAdapterFactory",
    "AnalyticsProvider",
    "MockAnalyticsAdapter",
    "TelegramAnalyticsAdapter",
    "RateLimitConfig",
]

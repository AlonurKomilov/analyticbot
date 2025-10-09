"""
Analytics Adapter Factory
Manages creation and configuration of analytics adapters
"""

import logging
from enum import Enum
from typing import TYPE_CHECKING, Any

from config.settings import settings
from core.adapters.analytics import AnalyticsAdapter

from .mock_analytics_adapter import MockAnalyticsAdapter

# MTProto guarded imports
if TYPE_CHECKING:
    from .tg_analytics_adapter import RateLimitConfig, TelegramAnalyticsAdapter

logger = logging.getLogger(__name__)


class AnalyticsProvider(Enum):
    """Supported analytics providers"""

    TELEGRAM = "telegram"
    MOCK = "mock"


class AnalyticsAdapterFactory:
    """
    Factory for creating analytics adapters with configuration-based switching
    """

    _adapters: dict[str, AnalyticsAdapter] = {}
    _current_adapter: AnalyticsAdapter | None = None

    @classmethod
    def create_adapter(cls, provider: AnalyticsProvider, **kwargs) -> AnalyticsAdapter:
        """
        Create or get existing adapter for specified provider

        Args:
            provider: The analytics provider to create adapter for
            **kwargs: Additional configuration options

        Returns:
            AnalyticsAdapter instance
        """
        provider_name = provider.value

        # Create cache key including configuration options
        config_key = f"{provider_name}:{hash(str(sorted(kwargs.items())))}"

        # Return existing adapter if already created with same config
        if config_key in cls._adapters:
            logger.debug(f"Returning existing {provider_name} adapter")
            return cls._adapters[config_key]

        # Create new adapter based on provider type
        if provider == AnalyticsProvider.TELEGRAM:
            # Lazy import MTProto components at runtime
            from .tg_analytics_adapter import RateLimitConfig, TelegramAnalyticsAdapter

            # Extract Telegram-specific configuration
            bot_token = kwargs.get("bot_token") or getattr(settings, "TELEGRAM_BOT_TOKEN", None)

            rate_limit_config = RateLimitConfig(
                calls_per_second=kwargs.get("calls_per_second", 1.0),
                calls_per_minute=kwargs.get("calls_per_minute", 20),
                calls_per_hour=kwargs.get("calls_per_hour", 500),
                burst_allowance=kwargs.get("burst_allowance", 5),
            )

            adapter = TelegramAnalyticsAdapter(
                bot_token=bot_token or "", rate_limit_config=rate_limit_config
            )

        elif provider == AnalyticsProvider.MOCK:
            adapter = MockAnalyticsAdapter()

        else:
            raise ValueError(f"Unsupported analytics provider: {provider_name}")

        # Cache the adapter
        cls._adapters[config_key] = adapter
        logger.info(f"Created new {provider_name} analytics adapter")

        return adapter

    @classmethod
    def get_current_adapter(cls, **kwargs) -> AnalyticsAdapter:
        """
        Get the currently configured analytics adapter based on settings

        Args:
            **kwargs: Override configuration options

        Returns:
            AnalyticsAdapter instance
        """
        if cls._current_adapter is not None and not kwargs:
            return cls._current_adapter

        # Determine provider from settings
        use_mock = kwargs.get("use_mock") or getattr(settings, "USE_MOCK_ANALYTICS", False)
        provider = AnalyticsProvider.MOCK if use_mock else AnalyticsProvider.TELEGRAM

        cls._current_adapter = cls.create_adapter(provider, **kwargs)
        logger.info(f"Set current analytics adapter to: {provider.value}")

        return cls._current_adapter

    @classmethod
    def set_current_adapter(cls, provider: AnalyticsProvider, **kwargs) -> AnalyticsAdapter:
        """
        Explicitly set the current analytics adapter

        Args:
            provider: The analytics provider to use
            **kwargs: Additional configuration options

        Returns:
            AnalyticsAdapter instance
        """
        cls._current_adapter = cls.create_adapter(provider, **kwargs)
        logger.info(f"Manually set current analytics adapter to: {provider.value}")

        return cls._current_adapter

    @classmethod
    def clear_cache(cls):
        """Clear all cached adapters"""
        # Close any adapters that need cleanup
        for adapter in cls._adapters.values():
            if hasattr(adapter, "close"):
                try:
                    import asyncio

                    if asyncio.get_event_loop().is_running():
                        asyncio.create_task(adapter.close())
                    else:
                        asyncio.run(adapter.close())
                except Exception as e:
                    logger.warning(f"Error closing adapter: {e}")

        cls._adapters.clear()
        cls._current_adapter = None
        logger.info("Cleared analytics adapter cache")

    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Get list of available analytics providers"""
        return [provider.value for provider in AnalyticsProvider]

    @classmethod
    async def health_check_all(cls) -> dict[str, Any]:
        """
        Run health check on all available analytics providers

        Returns:
            Dict with health status for each provider
        """
        results = {}

        for provider in AnalyticsProvider:
            try:
                adapter = cls.create_adapter(provider)
                health = await adapter.health_check()
                results[provider.value] = health
            except Exception as e:
                logger.error(f"Health check failed for {provider.value}: {e}")
                results[provider.value] = {
                    "status": "error",
                    "error": str(e),
                    "adapter": provider.value,
                }

        return results

    @classmethod
    def get_adapter_info(cls, provider: AnalyticsProvider) -> dict[str, Any]:
        """
        Get information about a specific adapter

        Args:
            provider: The analytics provider

        Returns:
            Dict with adapter information
        """
        try:
            adapter = cls.create_adapter(provider)
            return {
                "name": adapter.get_adapter_name(),
                "provider": provider.value,
                "class": adapter.__class__.__name__,
                "is_current": cls._current_adapter == adapter,
                "cached": any(provider.value in key for key in cls._adapters.keys()),
                "features": cls._get_adapter_features(adapter),
            }
        except Exception as e:
            return {"provider": provider.value, "error": str(e), "available": False}

    @classmethod
    def _get_adapter_features(cls, adapter: AnalyticsAdapter) -> list[str]:
        """Get list of features supported by an adapter"""
        features = []

        # Check which methods are implemented (not just abstract)
        method_names = [
            "get_channel_analytics",
            "get_post_analytics",
            "get_audience_demographics",
            "get_engagement_metrics",
            "get_growth_metrics",
            "health_check",
        ]

        for method_name in method_names:
            if hasattr(adapter, method_name):
                features.append(method_name)

        return features

    @classmethod
    async def benchmark_adapters(cls, channel_id: str = "test_channel") -> dict[str, Any]:
        """
        Benchmark all available adapters for performance comparison

        Args:
            channel_id: Test channel ID to use for benchmarking

        Returns:
            Dict with performance metrics for each adapter
        """
        import time
        from datetime import datetime, timedelta

        results = {}
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()

        for provider in AnalyticsProvider:
            try:
                adapter = cls.create_adapter(provider)

                # Benchmark health check
                start_time = time.time()
                health = await adapter.health_check()
                health_check_time = time.time() - start_time

                # Benchmark channel analytics
                start_time = time.time()
                analytics = await adapter.get_channel_analytics(channel_id, start_date, end_date)
                analytics_time = time.time() - start_time

                results[provider.value] = {
                    "health_check_time_ms": round(health_check_time * 1000, 2),
                    "analytics_time_ms": round(analytics_time * 1000, 2),
                    "health_status": health.get("status", "unknown"),
                    "analytics_success": not analytics.get("error", False),
                    "adapter_name": adapter.get_adapter_name(),
                }

            except Exception as e:
                logger.error(f"Benchmark failed for {provider.value}: {e}")
                results[provider.value] = {"error": str(e), "benchmark_failed": True}

        return results

    @classmethod
    def get_configuration_guide(cls) -> dict[str, Any]:
        """
        Get configuration guide for analytics adapters

        Returns:
            Dict with configuration information and examples
        """
        return {
            "providers": {
                "telegram": {
                    "description": "Real Telegram Bot API integration",
                    "required_settings": ["TELEGRAM_BOT_TOKEN"],
                    "optional_settings": ["USE_MOCK_ANALYTICS=false"],
                    "rate_limiting": {
                        "default_calls_per_second": 1.0,
                        "default_calls_per_minute": 20,
                        "default_calls_per_hour": 500,
                        "configurable": True,
                    },
                    "limitations": [
                        "Limited analytics via Bot API",
                        "No view counts for individual messages",
                        "No detailed engagement metrics",
                        "No demographic data",
                    ],
                    "recommendations": [
                        "Use for basic channel information",
                        "Consider MTProto for full analytics",
                        "Store periodic snapshots for growth tracking",
                    ],
                },
                "mock": {
                    "description": "Realistic mock data for development/testing",
                    "required_settings": ["USE_MOCK_ANALYTICS=true"],
                    "features": [
                        "Realistic time series data",
                        "Consistent data based on channel ID",
                        "Configurable trends and variations",
                        "Complete analytics suite",
                    ],
                    "use_cases": [
                        "Development and testing",
                        "Demo environments",
                        "UI development without API limits",
                        "Performance testing",
                    ],
                },
            },
            "environment_variables": {
                "USE_MOCK_ANALYTICS": {
                    "type": "boolean",
                    "default": False,
                    "description": "Switch to mock analytics adapter",
                },
                "TELEGRAM_BOT_TOKEN": {
                    "type": "string",
                    "required_for": "telegram provider",
                    "description": "Bot token from @BotFather",
                },
            },
            "factory_usage": {
                "get_current_adapter": "AnalyticsAdapterFactory.get_current_adapter()",
                "set_specific_adapter": "AnalyticsAdapterFactory.set_current_adapter(AnalyticsProvider.MOCK)",
                "custom_configuration": "AnalyticsAdapterFactory.create_adapter(provider, calls_per_second=2.0)",
                "health_check_all": "await AnalyticsAdapterFactory.health_check_all()",
            },
            "best_practices": [
                "Use mock adapter for development",
                "Configure rate limiting for production",
                "Monitor adapter health regularly",
                "Cache results when appropriate",
                "Handle API limitations gracefully",
            ],
        }

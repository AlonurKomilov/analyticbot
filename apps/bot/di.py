# apps/bot/di.py - Clean Architecture Bot Container
from typing import Any

import asyncpg
from dependency_injector import containers, providers

from apps.bot.config import Settings as BotSettings
from config.settings import settings
from infra.db.repositories import (
    AsyncpgAnalyticsRepository,
    AsyncpgChannelRepository,
    AsyncpgPaymentRepository,
    AsyncpgPlanRepository,
    AsyncpgScheduleRepository,
    AsyncpgUserRepository,
)


class BotContainer(containers.DeclarativeContainer):
    """Clean Architecture Bot Container - replaces god container."""

    wiring_config = containers.WiringConfiguration(
        modules=[
            "apps.bot.bot",
            "apps.bot.tasks",
            "apps.api.routers.admin_channels_router",
            "apps.api.routers.admin_system_router",
            "apps.api.routers.channels_router",
            "apps.api.routers.admin_users_router",
            "apps.api.di_analytics",
            "tests.test_comprehensive_integration",
        ]
    )

    # Configuration
    config = providers.Configuration()
    bot_settings = providers.Singleton(BotSettings)

    # AsyncPG pool for repositories
    asyncpg_pool = providers.Resource(
        asyncpg.create_pool,
        dsn=str(settings.DATABASE_URL or "").replace("postgresql+asyncpg://", "postgresql://"),
        min_size=1,
        max_size=getattr(settings, "DB_POOL_SIZE", 10),
    )

    # Bot Client
    bot_client = providers.Factory(_create_bot_client, settings=bot_settings)

    # Dispatcher
    dispatcher = providers.Factory(_create_dispatcher)

    # Repository providers
    user_repo = providers.Factory(AsyncpgUserRepository, pool=asyncpg_pool)
    channel_repo = providers.Factory(AsyncpgChannelRepository, pool=asyncpg_pool)
    analytics_repo = providers.Factory(AsyncpgAnalyticsRepository, pool=asyncpg_pool)
    payment_repo = providers.Factory(AsyncpgPaymentRepository, pool=asyncpg_pool)
    plan_repo = providers.Factory(AsyncpgPlanRepository, pool=asyncpg_pool)
    schedule_repo = providers.Factory(AsyncpgScheduleRepository, pool=asyncpg_pool)

    # Bot Services
    guard_service = providers.Factory(_create_guard_service, user_repository=user_repo)

    subscription_service = providers.Factory(
        _create_subscription_service,
        user_repository=user_repo,
        plan_repository=plan_repo,
    )

    scheduler_service = providers.Factory(
        _create_scheduler_service, schedule_repository=schedule_repo, bot=bot_client
    )

    analytics_service = providers.Factory(
        _create_analytics_service,
        analytics_repository=analytics_repo,
        channel_repository=channel_repo,
    )

    alerting_service = providers.Factory(
        _create_alerting_service, bot=bot_client, user_repository=user_repo
    )

    channel_management_service = providers.Factory(
        _create_channel_management_service,
        channel_repository=channel_repo,
        bot=bot_client,
    )

    # ML Services (optional)
    prediction_service = providers.Factory(_create_ml_service, "PredictiveAnalyticsEngine")
    content_optimizer = providers.Factory(_create_ml_service, "ContentOptimizer")
    churn_predictor = providers.Factory(_create_ml_service, "ChurnPredictor")
    engagement_analyzer = providers.Factory(_create_ml_service, "EngagementAnalyzer")


# Factory functions
def _create_bot_client(settings: BotSettings) -> Any | None:
    """Create bot client or return None for API-only deployments"""
    try:
        from aiogram import Bot as _AioBot
        from aiogram.client.default import DefaultBotProperties
        from aiogram.enums import ParseMode

        token = settings.BOT_TOKEN.get_secret_value() if hasattr(settings, "BOT_TOKEN") else None
    except Exception:
        import os

        token = os.getenv("BOT_TOKEN")

    if not token or token == "replace_me":
        return None

    try:
        from aiogram import Bot as _AioBot
        from aiogram.client.default import DefaultBotProperties
        from aiogram.enums import ParseMode

        return _AioBot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    except ImportError:
        return None


def _create_dispatcher():
    """Create aiogram dispatcher"""
    try:
        from aiogram import Dispatcher as _AioDispatcher
        from aiogram.fsm.storage.memory import MemoryStorage

        return _AioDispatcher(storage=MemoryStorage())
    except ImportError:
        return None


def _create_guard_service(user_repository=None, **kwargs):
    """Create guard service with flexible dependency resolution"""
    try:
        from apps.bot.services.guard_service import GuardService

        return _create_service_with_deps(GuardService, user_repository=user_repository, **kwargs)
    except ImportError:
        return None


def _create_subscription_service(user_repository=None, plan_repository=None, **kwargs):
    """Create subscription service with flexible dependency resolution"""
    try:
        from apps.bot.services.subscription_service import SubscriptionService

        return _create_service_with_deps(
            SubscriptionService,
            user_repository=user_repository,
            plan_repository=plan_repository,
            **kwargs,
        )
    except ImportError:
        return None


def _create_scheduler_service(schedule_repository=None, bot=None, **kwargs):
    """Create scheduler service with flexible dependency resolution"""
    try:
        from apps.bot.services.scheduler_service import SchedulerService

        return _create_service_with_deps(
            SchedulerService,
            schedule_repository=schedule_repository,
            scheduler_repo=schedule_repository,
            bot=bot,
            **kwargs,
        )
    except ImportError:
        return None


def _create_analytics_service(analytics_repository=None, channel_repository=None, **kwargs):
    """Create analytics service with flexible dependency resolution"""
    try:
        from apps.bot.services.analytics_service import AnalyticsService

        return _create_service_with_deps(
            AnalyticsService,
            analytics_repository=analytics_repository,
            channel_repository=channel_repository,
            **kwargs,
        )
    except ImportError:
        return None


def _create_alerting_service(bot=None, user_repository=None, **kwargs):
    """Create alerting service with flexible dependency resolution"""
    try:
        from apps.bot.services.alerting_service import AlertingService

        return _create_service_with_deps(
            AlertingService, bot=bot, user_repository=user_repository, **kwargs
        )
    except ImportError:
        return None


def _create_channel_management_service(channel_repository=None, bot=None, **kwargs):
    """Create channel management service with flexible dependency resolution"""
    try:
        from apps.bot.services.channel_management_service import (
            ChannelManagementService,
        )

        return _create_service_with_deps(
            ChannelManagementService,
            channel_repository=channel_repository,
            channel_repo=channel_repository,
            repository=channel_repository,
            bot=bot,
            **kwargs,
        )
    except ImportError:
        return None


def _create_ml_service(service_name: str) -> Any | None:
    """Create ML service (optional - returns None if not available)"""
    try:
        if service_name == "PredictiveAnalyticsEngine":
            from apps.bot.services.ml.predictive_engine import PredictiveAnalyticsEngine

            return PredictiveAnalyticsEngine()
        elif service_name == "ContentOptimizer":
            from apps.bot.services.ml.content_optimizer import ContentOptimizer

            return ContentOptimizer()
        elif service_name == "ChurnPredictor":
            from apps.bot.services.ml.churn_predictor import ChurnPredictor

            return ChurnPredictor()
        elif service_name == "EngagementAnalyzer":
            from apps.bot.services.ml.engagement_analyzer import EngagementAnalyzer

            return EngagementAnalyzer()
    except (ImportError, Exception):
        return None


def _create_service_with_deps(ServiceCls: type, **provided_kwargs) -> Any:
    """Create service with flexible dependency injection based on constructor signature"""
    import inspect

    sig = inspect.signature(ServiceCls.__init__)
    accepted_params = set(sig.parameters.keys()) - {"self"}

    # Filter to only include parameters the service accepts and that are not None
    filtered_kwargs = {
        k: v for k, v in provided_kwargs.items() if k in accepted_params and v is not None
    }

    try:
        return ServiceCls(**filtered_kwargs)
    except Exception:
        # Fallback: try without any parameters
        try:
            return ServiceCls()
        except Exception:
            return None


# Container instance
container = BotContainer()


def configure_bot_container() -> BotContainer:
    """Configure and return the Bot container"""
    return container


def configure_bot_container() -> BotContainer:
    """Configure and return the Bot container"""
    return container

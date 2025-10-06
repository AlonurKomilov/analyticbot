# apps/bot/di.py - Clean Architecture Bot Container
import logging
from typing import Any

from dependency_injector import containers, providers

from apps.bot.config import Settings as BotSettings

# ✅ CLEAN ARCHITECTURE: Use repository factory instead of direct infra imports
from apps.shared.factory import get_repository_factory

logger = logging.getLogger(__name__)


# Factory functions - defined before class to avoid forward references
async def _create_repository(factory, repo_type: str) -> Any:
    """Create repository using factory pattern - no direct infra imports"""
    try:
        if repo_type == "user":
            return await factory.get_user_repository()
        elif repo_type == "channel":
            return await factory.get_channel_repository()
        elif repo_type == "analytics":
            return await factory.get_analytics_repository()
        elif repo_type == "admin":
            return await factory.get_admin_repository()
        elif repo_type in ["plan", "schedule", "payment"]:
            # These need to be created with dynamic imports for now
            return await _create_extended_repository(repo_type)
        else:
            logger.warning(f"Unknown repository type: {repo_type}")
            return None
    except Exception as e:
        logger.warning(f"Failed to create {repo_type} repository: {e}")
        return None


async def _create_extended_repository(repo_type: str) -> Any:
    """Create extended repositories with dynamic imports"""
    try:
        # Get connection from shared container
        from apps.shared.di import get_container

        container = get_container()
        connection = await container.asyncpg_pool()

        if repo_type == "plan":
            from infra.db.repositories.plan_repository import AsyncpgPlanRepository

            return AsyncpgPlanRepository(connection)
        elif repo_type == "schedule":
            from infra.db.repositories.schedule_repository import AsyncpgScheduleRepository

            return AsyncpgScheduleRepository(connection)
        elif repo_type == "payment":
            from infra.db.repositories.payment_repository import AsyncpgPaymentRepository

            return AsyncpgPaymentRepository(connection)
        else:
            return None
    except Exception as e:
        logger.warning(f"Failed to create {repo_type} repository with dynamic import: {e}")
        return None


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
    """Create channel management service (using analytics service as fallback)"""
    try:
        # Try to use analytics service as channel manager
        from apps.bot.services.analytics_service import AnalyticsService

        return _create_service_with_deps(
            AnalyticsService,
            channel_repository=channel_repository,
            analytics_repository=channel_repository,  # Use channel repo as analytics for basic ops
            bot=bot,
            **kwargs,
        )
    except ImportError:
        logger.warning("Channel management service not available, returning None")
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
            try:
                # Create dependent services first
                prediction_service = _create_ml_service("PredictiveAnalyticsEngine")
                content_optimizer = _create_ml_service("ContentOptimizer")
                churn_predictor = _create_ml_service("ChurnPredictor")

                # Only create if all dependencies are available
                if prediction_service and content_optimizer and churn_predictor:
                    from apps.bot.services.ml.engagement_analyzer import EngagementAnalyzer

                    return EngagementAnalyzer(
                        prediction_service=prediction_service,
                        content_optimizer=content_optimizer,
                        churn_predictor=churn_predictor,
                    )
                else:
                    return None
            except (TypeError, ImportError, Exception):
                # ML services not available
                return None
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


class BotContainer(containers.DeclarativeContainer):
    """Clean Architecture Bot Container - replaces god container."""

    # Removed automatic wiring to prevent circular imports
    # Wiring is now done manually in configure_bot_container()

    # Configuration
    config = providers.Configuration()
    bot_settings = providers.Singleton(BotSettings)

    # ✅ CLEAN ARCHITECTURE: Repository factory (no direct DB dependencies)
    repository_factory = providers.Singleton(get_repository_factory)

    # Bot Client
    bot_client = providers.Factory(_create_bot_client, settings=bot_settings)

    # Dispatcher
    dispatcher = providers.Factory(_create_dispatcher)

    # ✅ CLEAN ARCHITECTURE: Repository providers using factory pattern
    user_repo = providers.Factory(_create_repository, factory=repository_factory, repo_type="user")
    channel_repo = providers.Factory(
        _create_repository, factory=repository_factory, repo_type="channel"
    )
    analytics_repo = providers.Factory(
        _create_repository, factory=repository_factory, repo_type="analytics"
    )
    admin_repo = providers.Factory(
        _create_repository, factory=repository_factory, repo_type="admin"
    )

    # Additional repositories for backward compatibility
    plan_repo = providers.Factory(_create_repository, factory=repository_factory, repo_type="plan")
    schedule_repo = providers.Factory(
        _create_repository, factory=repository_factory, repo_type="schedule"
    )
    payment_repo = providers.Factory(
        _create_repository, factory=repository_factory, repo_type="payment"
    )

    # Bot Services
    guard_service = providers.Factory(_create_guard_service, user_repository=user_repo)

    subscription_service = providers.Factory(
        _create_subscription_service, user_repository=user_repo, plan_repository=plan_repo
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
        _create_channel_management_service, channel_repository=channel_repo, bot=bot_client
    )

    # ML Services (optional)
    prediction_service = providers.Factory(_create_ml_service, "PredictiveAnalyticsEngine")
    content_optimizer = providers.Factory(_create_ml_service, "ContentOptimizer")
    churn_predictor = providers.Factory(_create_ml_service, "ChurnPredictor")
    engagement_analyzer = providers.Factory(_create_ml_service, "EngagementAnalyzer")


# Container instance - deferred initialization to prevent circular imports
_container: BotContainer | None = None


def configure_bot_container() -> BotContainer:
    """Configure and return the Bot container"""
    global _container
    if _container is None:
        _container = BotContainer()
        # Wire modules after all imports are complete
        _container.wire(
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
    return _container


# For backward compatibility
def get_container() -> BotContainer:
    """Get the configured container instance"""
    return configure_bot_container()

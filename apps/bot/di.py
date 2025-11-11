# apps/bot/di.py - Clean Architecture Bot Container
"""
⚠️ ⚠️ ⚠️ DEPRECATED - DO NOT USE ⚠️ ⚠️ ⚠️

This file is DEPRECATED and will be removed in a future release.
Please migrate to the new modular DI architecture: apps/di/

MIGRATION GUIDE:
---------------

OLD (deprecated):
    from apps.bot.di import configure_bot_container
    container = configure_bot_container()
    bot = container.bot_client()

NEW (modular DI):
    from apps.di import get_container
    container = get_unified_container()
    bot = await container.bot.bot_client()

DEPRECATION SCHEDULE:
- 2025-10-14: Deprecated (this warning added)
- 2025-10-21: Will be removed (1 week grace period)

See: LEGACY_VS_NEW_DI_COMPARISON.md for complete migration guide
"""

import logging
import warnings
from typing import Any

from dependency_injector import containers, providers

from apps.bot.config import Settings as BotSettings
from apps.di import get_container as get_unified_container  # noqa: E402

# Emit deprecation warning when module is imported
warnings.warn(
    "apps.bot.di is DEPRECATED. "
    "Please migrate to apps.di.get_container() for bot services. "
    "See LEGACY_VS_NEW_DI_COMPARISON.md for migration guide. "
    "This module will be removed on 2025-10-21.",
    DeprecationWarning,
    stacklevel=2,
)

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
        # Get connection from unified DI container
        container = get_unified_container()
        connection = await container.database.asyncpg_pool()

        if repo_type == "plan":
            from infra.db.repositories.plan_repository import AsyncpgPlanRepository

            return AsyncpgPlanRepository(connection)
        elif repo_type == "schedule":
            from infra.db.repositories.schedule_repository import (
                AsyncpgScheduleRepository,
            )

            return AsyncpgScheduleRepository(connection)
        elif repo_type == "payment":
            from infra.db.repositories.payment_repository import (
                AsyncpgPaymentRepository,
            )

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
    """Create guard service with cache adapter for content moderation.

    Uses Redis cache if available, falls back to in-memory cache.
    """
    try:
        from apps.bot.services.guard_service import GuardService
        from infra.cache.redis_cache_adapter import create_redis_cache_adapter

        # Try to get Redis connection from unified DI container
        redis_client = None
        try:
            # Try to get redis client if available
            # Most installations won't have Redis, so we'll use in-memory fallback
            redis_client = None  # For now, default to in-memory
        except Exception as e:
            logger.debug(f"Redis not available for guard service: {e}")
            redis_client = None

        # Create cache adapter (will use in-memory if redis_client is None)
        cache = create_redis_cache_adapter(redis_client)

        # Create service with cache
        return GuardService(cache=cache)
    except ImportError as e:
        logger.warning(f"Failed to create guard service: {e}")
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


def _create_payment_microservices(payment_repository=None, **kwargs):
    """Create payment microservices architecture"""
    try:
        from infra.services.payment import (
            PaymentAnalyticsService,
            PaymentGatewayManagerService,
            PaymentMethodService,
            PaymentOrchestratorService,
            PaymentProcessingService,
            WebhookService,
        )
        from infra.services.payment import (
            SubscriptionService as PaymentSubscriptionService,
        )

        if payment_repository is None:
            logger.warning("Payment repository not available for microservices")
            return None

        # Create individual microservices
        payment_method_service = PaymentMethodService(payment_repository)
        payment_processing_service = PaymentProcessingService(payment_repository)
        payment_subscription_service = PaymentSubscriptionService(payment_repository)
        webhook_service = WebhookService(payment_repository)
        analytics_service = PaymentAnalyticsService(payment_repository)
        gateway_manager_service = PaymentGatewayManagerService()

        # Create orchestrator with all services
        orchestrator = PaymentOrchestratorService(
            payment_method_service=payment_method_service,
            payment_processing_service=payment_processing_service,
            subscription_service=payment_subscription_service,
            webhook_service=webhook_service,
            analytics_service=analytics_service,
            gateway_manager_service=gateway_manager_service,
        )

        logger.info("Payment microservices architecture initialized successfully")
        return orchestrator

    except ImportError as e:
        logger.warning(f"Payment microservices not available: {e}")
        return None


def _create_scheduler_service(schedule_repository=None, bot=None, **kwargs):
    """
    Create scheduler service with flexible dependency resolution.
    LEGACY - use ScheduleManager
    """
    try:
        # UPDATED: Use new clean architecture service
        from core.services.bot.scheduling import ScheduleManager

        return _create_service_with_deps(
            ScheduleManager,
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
        # ✅ Phase 3.5.2: Migrated to core analytics (2025-10-15)
        from core.services.bot.analytics import AnalyticsService

        return _create_service_with_deps(
            AnalyticsService,
            analytics_repository=analytics_repository,
            channel_repository=channel_repository,
            **kwargs,
        )
    except ImportError:
        return None


def _create_alerting_service(bot=None, user_repository=None, **kwargs):
    """
    Create alerting service with flexible dependency resolution.
    LEGACY - use AlertEventManager
    """
    try:
        # UPDATED: Use new clean architecture service
        from core.services.bot.alerts import AlertEventManager

        return _create_service_with_deps(
            AlertEventManager, bot=bot, user_repository=user_repository, **kwargs
        )
    except ImportError:
        return None


def _create_channel_management_service(channel_repository=None, bot=None, **kwargs):
    """Create channel management service (using analytics service as fallback)"""
    try:
        # Try to use analytics service as channel manager
        # ✅ Phase 3.5.2: Migrated to core analytics (2025-10-15)
        from core.services.bot.analytics import AnalyticsService

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
        if service_name == "PredictiveEngine":
            from apps.shared.adapters.ml_coordinator import create_ml_coordinator

            return create_ml_coordinator()
        elif service_name == "EngagementAnalyzer":
            # REMOVED: bot_ml_facade module doesn't exist (Oct 19, 2025)
            # from apps.bot.services.adapters.bot_ml_facade import create_bot_ml_facade
            # return create_bot_ml_facade()
            logger.warning("EngagementAnalyzer not available - bot_ml_facade module missing")
            return None
        elif service_name == "ChurnPredictor":
            # Create ChurnPredictor using the new churn intelligence service
            from core.services.churn_intelligence import (
                ChurnIntelligenceOrchestratorService,
            )

            try:
                orchestrator = ChurnIntelligenceOrchestratorService()
                logger.info("ChurnPredictor (Churn Intelligence Orchestrator) created successfully")
                return orchestrator
            except Exception as e:
                logger.warning(f"Failed to create ChurnPredictor: {e}")
                return None
        elif service_name == "ContentOptimizer":
            try:
                # REMOVED: bot_ml_facade module doesn't exist (Oct 19, 2025)
                # ContentOptimizer depends on ML services that are not yet implemented
                logger.warning("ContentOptimizer not available - ML dependencies missing")
                return None
            except (TypeError, ImportError, Exception):
                # ML services not available
                return None
    except (ImportError, Exception):
        return None

    # Fallback for unknown service names
    return None


def _create_service_with_deps(ServiceCls: type, **provided_kwargs) -> Any:
    """Create service with flexible dependency injection based on constructor signature"""
    import inspect

    # Get signature from the class, not the instance
    sig = inspect.signature(ServiceCls)
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


# ✅ PHASE 3 FIX: Repository delegation helpers
# These async callables delegate to main container for repository access
async def _get_user_repo():
    """Get user repository from main container"""
    container = get_unified_container()
    return await container.database.user_repo()  # type: ignore[attr-defined]


async def _get_channel_repo():
    """Get channel repository from main container"""
    container = get_unified_container()
    return await container.database.channel_repo()  # type: ignore[attr-defined]


async def _get_analytics_repo():
    """Get analytics repository from main container"""
    container = get_unified_container()
    return await container.database.analytics_repo()  # type: ignore[attr-defined]


async def _get_admin_repo():
    """Get admin repository from main container"""
    container = get_unified_container()
    return await container.database.admin_repo()  # type: ignore[attr-defined]


async def _get_plan_repo():
    """Get plan repository from main container"""
    container = get_unified_container()
    return await container.database.plan_repo()  # type: ignore[attr-defined]


async def _get_schedule_repo():
    """Get schedule repository from main container"""
    container = get_unified_container()
    return await container.database.schedule_repo()  # type: ignore[attr-defined]


async def _get_payment_repo():
    """Get payment repository from main container"""
    container = get_unified_container()
    return await container.database.payment_repo()  # type: ignore[attr-defined]


class BotContainer(containers.DeclarativeContainer):
    """Clean Architecture Bot Container - replaces god container."""

    # Removed automatic wiring to prevent circular imports
    # Wiring is now done manually in configure_bot_container()

    # Configuration
    config = providers.Configuration()
    bot_settings = providers.Singleton(BotSettings)

    # ✅ PHASE 3 FIX (Oct 19, 2025): Use main container's repositories
    # Repository access now delegates to main DI container
    _main_container = providers.Singleton(get_unified_container)

    # Bot Client
    bot_client = providers.Factory(_create_bot_client, settings=bot_settings)

    # Dispatcher
    dispatcher = providers.Factory(_create_dispatcher)

    # ✅ PHASE 3 FIX: Repository providers delegate to main container
    # Note: These are kept for backward compatibility during migration
    # Bot handlers should eventually use get_container().database directly

    # Repository providers using Callable pattern
    user_repo = providers.Callable(_get_user_repo)
    channel_repo = providers.Callable(_get_channel_repo)
    analytics_repo = providers.Callable(_get_analytics_repo)
    admin_repo = providers.Callable(_get_admin_repo)
    plan_repo = providers.Callable(_get_plan_repo)
    schedule_repo = providers.Callable(_get_schedule_repo)
    payment_repo = providers.Callable(_get_payment_repo)

    # Bot Services
    guard_service = providers.Factory(_create_guard_service, user_repository=user_repo)

    subscription_service = providers.Factory(
        _create_subscription_service,
        user_repository=user_repo,
        plan_repository=plan_repo,
    )

    # ✅ NEW: Payment Microservices Architecture
    payment_orchestrator = providers.Factory(
        _create_payment_microservices, payment_repository=payment_repo
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
    prediction_service = providers.Factory(_create_ml_service, "PredictiveEngine")
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
            ]
        )
    return _container


# For backward compatibility - renamed to avoid conflict with apps.di.get_container
def get_bot_container() -> BotContainer:
    """Get the configured container instance"""
    return configure_bot_container()

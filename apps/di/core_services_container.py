"""
Core Services DI Container

Single Responsibility: Pure business logic services (framework-agnostic)
These services implement core business rules and are independent of delivery mechanisms
"""

import logging

from dependency_injector import containers, providers

logger = logging.getLogger(__name__)


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================


async def _create_analytics_batch_processor(analytics_repository=None, **kwargs):
    """Create core analytics batch processor (pure business logic)"""
    try:
        from core.services.bot.analytics.analytics_batch_processor import AnalyticsBatchProcessor

        # Check if repository is required
        if analytics_repository is None:
            logger.warning("Analytics repository not available for batch processor")
            return None

        return AnalyticsBatchProcessor(analytics_repository=analytics_repository)
    except (ImportError, TypeError) as e:
        logger.warning(f"Analytics batch processor not available: {e}")
        return None


async def _create_reporting_service(**kwargs):
    """Create core reporting service (pure business logic)"""
    try:
        from core.services.bot.reporting import create_reporting_system

        return create_reporting_system()
    except ImportError as e:
        logger.warning(f"Reporting service not available: {e}")
        return None


async def _create_dashboard_service(port: int = 8050, **kwargs):
    """Create core dashboard service (pure business logic)"""
    try:
        from core.services.bot.dashboard import create_dashboard

        return create_dashboard(port=port)
    except ImportError as e:
        logger.warning(f"Dashboard service not available: {e}")
        return None


async def _create_analytics_fusion_service(**kwargs):
    """Create analytics fusion orchestrator (API service)
    
    Delegates to analytics_container which has proper db_pool access.
    """
    logger.info("🏭 Creating analytics fusion service via analytics_container...")
    try:
        # Delegate to the properly-configured analytics container
        from apps.di.analytics_container import get_analytics_fusion_service as get_fusion_svc
        
        service = await get_fusion_svc()
        if service:
            logger.info("✅ Analytics fusion service obtained from analytics_container")
        return service
    except Exception as e:
        logger.error(f"❌ Failed to get analytics fusion service: {e}", exc_info=True)
        return None


async def _create_schedule_service(schedule_repo=None, **kwargs):
    """Create schedule service"""
    try:
        from core.services import ScheduleService

        return ScheduleService(schedule_repo) if schedule_repo else None
    except ImportError:
        return None


async def _create_delivery_service(delivery_repo=None, schedule_repo=None, **kwargs):
    """Create delivery service"""
    try:
        from core.services import DeliveryService

        return (
            DeliveryService(delivery_repo, schedule_repo)
            if delivery_repo and schedule_repo
            else None
        )
    except ImportError:
        return None


# ============================================================================
# CORE SERVICES CONTAINER
# ============================================================================


class CoreServicesContainer(containers.DeclarativeContainer):
    """
    Core Services Container

    Single Responsibility: Pure business logic services
    Framework-agnostic - can be used by any delivery mechanism (API, Bot, CLI, etc.)
    Follows Clean Architecture - depends only on abstractions
    """

    config = providers.Configuration()

    # Dependencies from other containers
    database = providers.DependenciesContainer()

    # ============================================================================
    # CORE BUSINESS LOGIC SERVICES (Framework-Agnostic)
    # ============================================================================

    # Analytics services
    analytics_batch_processor = providers.Singleton(
        _create_analytics_batch_processor,
        analytics_repository=database.analytics_repo,
    )

    analytics_fusion_service = providers.Singleton(
        _create_analytics_fusion_service
    )  # Reporting services
    reporting_service = providers.Singleton(_create_reporting_service)

    # Dashboard services
    dashboard_service = providers.Singleton(_create_dashboard_service, port=8050)

    # Scheduling services
    schedule_service = providers.Factory(
        _create_schedule_service,
        schedule_repo=database.schedule_repo,
    )

    # Delivery services
    delivery_service = providers.Factory(
        _create_delivery_service,
        delivery_repo=None,  # TODO: Add delivery repo when available
        schedule_repo=database.schedule_repo,
    )

    # ✅ PHASE 2: Business Intelligence Services (October 21, 2025)
    # Trend analysis and forecasting
    trend_analysis_service = providers.Factory(
        lambda channel_daily_repo, post_repo: __import__(
            "core.services.trend_analysis_service", fromlist=["TrendAnalysisService"]
        ).TrendAnalysisService(
            channel_daily_repo=channel_daily_repo,
            post_repo=post_repo,
            metrics_repo=None,  # Optional metrics repository
        ),
        channel_daily_repo=database.channel_daily_repo,
        post_repo=database.post_repo,
    )

    # ✅ PHASE 2.5: Predictive Intelligence Services (October 21, 2025)
    # Predictive orchestrator with contextual, temporal, modeling, and cross-channel intelligence
    predictive_orchestrator_service = providers.Factory(
        lambda: __import__(
            "core.services.predictive_intelligence", fromlist=["create_predictive_orchestrator"]
        ).create_predictive_orchestrator(
            analytics_service=None,  # Optional analytics service
            data_access_service=None,  # Optional data access service
            predictive_analytics_service=None,  # Optional predictive analytics service
            nlg_service=None,  # Optional NLG service
            config_manager=None,  # Optional config manager
        ),
    )

    # ============================================================================
    # USER BOT MANAGEMENT SERVICES (Clean Architecture)
    # ============================================================================

    # Note: bot_manager is injected at runtime from bot container
    # These factories accept bot_manager as a parameter when called
    user_bot_service = providers.Factory(
        lambda user_bot_repo, bot_manager=None: __import__(
            "core.services.user_bot_service", fromlist=["UserBotService"]
        ).UserBotService(repository=user_bot_repo, bot_manager=bot_manager),
        user_bot_repo=database.user_bot_repo,
    )

    admin_bot_service = providers.Factory(
        lambda user_bot_repo, bot_manager=None: __import__(
            "core.services.admin_bot_service", fromlist=["AdminBotService"]
        ).AdminBotService(repository=user_bot_repo, bot_manager=bot_manager),
        user_bot_repo=database.user_bot_repo,
    )

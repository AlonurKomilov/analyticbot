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


async def _create_analytics_batch_processor(**kwargs):
    """Create core analytics batch processor (pure business logic)"""
    try:
        from core.services.analytics.analytics_batch_processor import AnalyticsBatchProcessor

        return AnalyticsBatchProcessor()
    except ImportError as e:
        logger.warning(f"Analytics batch processor not available: {e}")
        return None


async def _create_reporting_service(**kwargs):
    """Create core reporting service (pure business logic)"""
    try:
        from core.services.reporting import create_reporting_system

        return create_reporting_system()
    except ImportError as e:
        logger.warning(f"Reporting service not available: {e}")
        return None


async def _create_dashboard_service(port: int = 8050, **kwargs):
    """Create core dashboard service (pure business logic)"""
    try:
        from core.services.dashboard import create_dashboard

        return create_dashboard(port=port)
    except ImportError as e:
        logger.warning(f"Dashboard service not available: {e}")
        return None


async def _create_analytics_fusion_service(**kwargs):
    """Create analytics fusion orchestrator (API service)"""
    try:
        from core.services.analytics_fusion import AnalyticsOrchestratorService
        from core.services.analytics_fusion.infrastructure import DataAccessService

        data_access_service = DataAccessService(repository_manager=None)
        return AnalyticsOrchestratorService(data_access_service=data_access_service)
    except ImportError as e:
        logger.warning(f"Analytics fusion service not available: {e}")
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
    analytics_batch_processor = providers.Singleton(_create_analytics_batch_processor)

    analytics_fusion_service = providers.Singleton(_create_analytics_fusion_service)

    # Reporting services
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

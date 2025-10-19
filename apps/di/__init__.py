"""
Modular DI Architecture - Main Container Aggregator

This is the Composition Root pattern from Dependency Injection principles.
It composes multiple focused containers into a cohesive application container.

Architecture:
- Each domain has its own focused container (~100 lines, single responsibility)
- This aggregator composes them together
- No God Object - just composition!

Containers:
1. DatabaseContainer - Database & repositories
2. CacheContainer - Redis & cache adapters
3. CoreServicesContainer - Pure business logic
4. MLContainer - ML services (optional)
5. BotContainer - Bot services & adapters
6. APIContainer - API services & dependencies
"""

import logging

from dependency_injector import containers, providers

from apps.di.api_container import APIContainer
from apps.di.bot_container import BotContainer
from apps.di.cache_container import CacheContainer
from apps.di.core_services_container import CoreServicesContainer
from apps.di.database_container import DatabaseContainer
from apps.di.ml_container import MLContainer

logger = logging.getLogger(__name__)


# ============================================================================
# APPLICATION CONTAINER (Composition Root)
# ============================================================================


class ApplicationContainer(containers.DeclarativeContainer):
    """
    Main Application Container - Composition Root

    This is NOT a God Object! It's a Composition Root that:
    - Composes focused domain containers
    - Wires dependencies between them
    - Provides unified access point

    Each domain container has single responsibility and ~100 lines.
    Total complexity is distributed across 7 files instead of 1 God Object.
    """

    config = providers.Configuration()

    # ============================================================================
    # DOMAIN CONTAINERS (Each with single responsibility)
    # ============================================================================

    # Infrastructure containers
    database = providers.Container(
        DatabaseContainer,
        config=config,
    )

    cache = providers.Container(
        CacheContainer,
        config=config,
    )

    # Core business logic (framework-agnostic)
    core_services = providers.Container(
        CoreServicesContainer,
        config=config,
        database=database,
    )

    # Optional ML services
    ml = providers.Container(
        MLContainer,
        config=config,
    )

    # Bot services and adapters
    bot = providers.Container(
        BotContainer,
        config=config,
        database=database,
        core_services=core_services,
    )

    # API services and dependencies
    api = providers.Container(
        APIContainer,
        config=config,
        database=database,
        core_services=core_services,
    )


# ============================================================================
# CONTAINER INSTANCE & ACCESSOR FUNCTIONS
# ============================================================================

_container: ApplicationContainer | None = None


def configure_container() -> ApplicationContainer:
    """
    Configure and return the application container

    This should be called once at application startup.
    Subsequent calls return the same instance (singleton pattern).
    """
    global _container
    if _container is None:
        _container = ApplicationContainer()

        # Wire modules after all imports are complete
        # This enables dependency injection in these modules
        _container.wire(
            modules=[
                "apps.bot.bot",
                "apps.bot.tasks",
                "apps.api.main",
            ]
        )

        logger.info("✅ Modular DI Container configured successfully")
        logger.info("   - Database Container: Ready")
        logger.info("   - Cache Container: Ready")
        logger.info("   - Core Services Container: Ready")
        logger.info("   - ML Container: Ready (optional)")
        logger.info("   - Bot Container: Ready")
        logger.info("   - API Container: Ready")

    return _container


def get_container() -> ApplicationContainer:
    """
    Get the configured application container

    Usage:
        container = get_container()
        service = await container.core_services.analytics_fusion_service()
        repo = await container.database.user_repo()
    """
    return configure_container()


# ============================================================================
# Public API
# ============================================================================
def get_unified_container() -> ApplicationContainer:
    """Alias for transition from unified_di.py"""
    return get_container()


# ============================================================================
# CLEANUP
# ============================================================================


async def cleanup_container():
    """
    Cleanup function for graceful shutdown

    Call this on application shutdown to properly close:
    - Database connections
    - Redis connections
    - Other resources
    """
    global _container
    if _container:
        logger.info("Cleaning up application containers...")

        # Cleanup is handled automatically by dependency-injector
        # Resources with providers.Resource() are automatically cleaned up

        _container = None
        logger.info("✅ Container cleanup complete")


# ============================================================================
# CONVENIENCE ACCESSORS
# ============================================================================


async def get_database_pool():
    """Get database pool from container"""
    container = get_container()
    return await container.database.asyncpg_pool()


async def get_cache_adapter():
    """Get cache adapter from container"""
    container = get_container()
    return await container.cache.cache_adapter()


async def get_analytics_fusion_service():
    """Get analytics fusion service from container"""
    container = get_container()
    return await container.core_services.analytics_fusion_service()


async def get_channel_management_service():
    """Get channel management service from container"""
    container = get_container()
    return await container.api.channel_management_service()


async def get_schedule_service():
    """Get schedule service from container"""
    container = get_container()
    return await container.core_services.schedule_service()


async def get_delivery_service():
    """Get delivery service from container"""
    container = get_container()
    return await container.core_services.delivery_service()


async def get_db_connection():
    """Get database connection (session) from container"""
    container = get_container()
    # Return the database pool which can be used for sessions
    return await container.database.asyncpg_pool()


# Alert Services (Phase 3.2)
def get_alert_condition_evaluator():
    """Get alert condition evaluator service from container"""
    container = get_container()
    return container.bot.alert_condition_evaluator()


def get_alert_rule_manager():
    """Get alert rule manager service from container"""
    container = get_container()
    return container.bot.alert_rule_manager()


def get_alert_event_manager():
    """Get alert event manager service from container"""
    container = get_container()
    return container.bot.alert_event_manager()


def get_telegram_alert_notifier():
    """Get telegram alert notifier adapter from container"""
    container = get_container()
    return container.bot.telegram_alert_notifier()


# Content Protection Services (Phase 3.3)
def get_content_protection_service():
    """Get content protection orchestrator service from container"""
    container = get_container()
    return container.bot.content_protection_service()


def get_watermark_service():
    """Get watermark service from container"""
    container = get_container()
    return container.bot.watermark_service()


def get_video_watermark_service():
    """Get video watermark service from container"""
    container = get_container()
    return container.bot.video_watermark_service()


def get_theft_detector():
    """Get content theft detector service from container"""
    container = get_container()
    return container.bot.theft_detector()


# Metrics Services (Phase 3.4)
def get_metrics_collector_service():
    """Get metrics collector service from container"""
    container = get_container()
    return container.bot.metrics_collector_service()


def get_business_metrics_service():
    """Get business metrics service from container"""
    container = get_container()
    return container.bot.business_metrics_service()


def get_health_check_service():
    """Get health check service from container"""
    container = get_container()
    return container.bot.health_check_service()


def get_system_metrics_service():
    """Get system metrics service from container"""
    container = get_container()
    return container.bot.system_metrics_service()


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "ApplicationContainer",
    "configure_container",
    "get_container",
    # "get_bot_container",  # REMOVED Oct 19, 2025: Function doesn't exist
    # "get_api_container",  # REMOVED Oct 19, 2025: Function doesn't exist
    "get_unified_container",
    "cleanup_container",
    "get_database_pool",
    "get_cache_adapter",
    "get_analytics_fusion_service",
    "get_channel_management_service",
    "get_schedule_service",
    "get_delivery_service",
    "get_db_connection",
    # Alert services (Phase 3.2)
    "get_alert_condition_evaluator",
    "get_alert_rule_manager",
    "get_alert_event_manager",
    "get_telegram_alert_notifier",
    # Content protection services (Phase 3.3)
    "get_content_protection_service",
    "get_watermark_service",
    "get_video_watermark_service",
    "get_theft_detector",
    # Metrics services (Phase 3.4)
    "get_metrics_collector_service",
    "get_business_metrics_service",
    "get_health_check_service",
    "get_system_metrics_service",
]

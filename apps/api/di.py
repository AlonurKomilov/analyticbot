# apps/api/di.py
"""
⚠️ ⚠️ ⚠️ DEPRECATED - DO NOT USE ⚠️ ⚠️ ⚠️

This file is DEPRECATED and will be removed in a future release.
Please use the unified DI system: apps/di/

MIGRATION GUIDE:
---------------

OLD (deprecated):
    from apps.api.di import ApiContainer, configure_api_container
    container = configure_api_container()

NEW (unified DI):
    from apps.di import get_container
    container = get_container()
    # Access API services via: container.api.X()

DEPRECATION SCHEDULE:
- 2025-10-19: Deprecated (all files migrated to apps/di)
- 2025-10-26: Will be removed (1 week grace period)

STATUS: All 12 dependent files have been successfully migrated to apps/di/
See: DI_MIGRATION_COMPLETE.md for full migration report
"""

import warnings
from dependency_injector import containers, providers

# Emit deprecation warning
warnings.warn(
    "apps/api/di is deprecated. Use apps/di/ instead. "
    "This module will be removed on 2025-10-26.",
    DeprecationWarning,
    stacklevel=2
)


class ApiContainer(containers.DeclarativeContainer):
    """
    API Application Composition Root

    This container wires together all dependencies needed by the API layer,
    implementing clean architecture by depending only on core and infra layers.
    """

    # Configuration
    config = providers.Configuration()

    # Mock services for immediate functionality
    mock_analytics_service = providers.Factory(lambda: None)

    mock_payment_service = providers.Factory(lambda: None)

    mock_ai_service = providers.Factory(lambda: None)

    cache_service = providers.Factory(lambda: None)

    analytics_fusion_service = providers.Factory(lambda: None)


# Container instance - composition root
container = ApiContainer()


def configure_api_container() -> ApiContainer:
    """Configure and return the API container"""
    return container


def get_container() -> ApiContainer:
    """Get configured API container (for backwards compatibility)"""
    return container


def get_analytics_fusion_service():
    """Get analytics fusion service"""
    return container.analytics_fusion_service()


def configure_services():
    """Configure all services (for backwards compatibility)"""
    # This is now handled by the container automatically
    pass

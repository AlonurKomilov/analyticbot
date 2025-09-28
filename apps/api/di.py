# apps/api/di.py
"""
API Application Composition Root
Implements clean architecture by providing all dependencies needed by the API layer.
"""
from dependency_injector import containers, providers
from typing import Optional, Dict, Any

from config.settings import settings


class ApiContainer(containers.DeclarativeContainer):
    """
    API Application Composition Root
    
    This container wires together all dependencies needed by the API layer,
    implementing clean architecture by depending only on core and infra layers.
    """
    
    # Configuration
    config = providers.Configuration()
    
    # Mock services for immediate functionality
    mock_analytics_service = providers.Factory(
        lambda: None
    )
    
    mock_payment_service = providers.Factory(
        lambda: None
    )
    
    mock_ai_service = providers.Factory(
        lambda: None
    )
    
    cache_service = providers.Factory(
        lambda: None
    )
    
    analytics_fusion_service = providers.Factory(
        lambda: None
    )


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
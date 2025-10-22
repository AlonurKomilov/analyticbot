"""
Shared dependencies for predictive insights endpoints.

This module provides dependency injection functions for services
used across predictive analytics and intelligence endpoints.
"""

import logging
from fastapi import HTTPException

from apps.api.di_analytics import get_analytics_fusion_service, get_cache
from apps.di import get_container
from apps.shared.clients.analytics_client import AnalyticsClient
from config.settings import settings

logger = logging.getLogger(__name__)


# Analytics Client Dependency
def get_analytics_client() -> AnalyticsClient:
    """Get Analytics V2 client instance"""
    return AnalyticsClient(settings.ANALYTICS_V2_BASE_URL)


# Predictive Orchestrator Dependency
async def get_predictive_orchestrator():
    """
    Get PredictiveOrchestratorService from DI container.

    Provides access to:
    - Contextual intelligence analysis
    - Temporal intelligence patterns
    - Predictive modeling with ML
    - Cross-channel intelligence
    """
    try:
        container = get_container()
        orchestrator = await container.core_services.predictive_orchestrator_service()
        return orchestrator
    except Exception as e:
        logger.error(f"Failed to get PredictiveOrchestratorService: {e}")
        raise HTTPException(status_code=503, detail="Predictive Orchestrator Service unavailable")


__all__ = [
    "get_analytics_client",
    "get_predictive_orchestrator",
    "get_analytics_fusion_service",
    "get_cache",
]

"""
ML Services DI Container

Single Responsibility: Machine Learning services (optional)
Gracefully degrades - returns None if ML dependencies not available
"""

import logging
from typing import Any

from dependency_injector import containers, providers

logger = logging.getLogger(__name__)


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================


def _create_ml_service(service_name: str) -> Any | None:
    """Create ML service (optional - returns None if not available)"""
    try:
        if service_name == "PredictiveEngine":
            from apps.bot.services.adapters.ml_coordinator import create_ml_coordinator

            return create_ml_coordinator()
        elif service_name == "EngagementAnalyzer":
            from apps.bot.services.adapters.bot_ml_facade import create_bot_ml_facade

            return create_bot_ml_facade()
        elif service_name == "ChurnPredictor":
            from core.services.churn_intelligence import ChurnIntelligenceOrchestratorService

            try:
                return ChurnIntelligenceOrchestratorService()
            except Exception as e:
                logger.warning(f"Failed to create ChurnPredictor: {e}")
                return None
    except (ImportError, Exception) as e:
        logger.warning(f"ML service {service_name} not available: {e}")
        return None


# ============================================================================
# ML CONTAINER
# ============================================================================


class MLContainer(containers.DeclarativeContainer):
    """
    ML Services Container

    Single Responsibility: Machine Learning services
    Optional services - application continues to work without ML features
    """

    config = providers.Configuration()

    # ============================================================================
    # ML SERVICES (All optional)
    # ============================================================================

    prediction_service = providers.Factory(
        _create_ml_service,
        service_name="PredictiveEngine"
    )

    engagement_analyzer = providers.Factory(
        _create_ml_service,
        service_name="EngagementAnalyzer"
    )

    churn_predictor = providers.Factory(
        _create_ml_service,
        service_name="ChurnPredictor"
    )

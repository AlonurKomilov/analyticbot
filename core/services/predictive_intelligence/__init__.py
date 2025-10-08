"""
Predictive Intelligence Package
===============================

Comprehensive predictive intelligence system with base ML engine and advanced microservices.

Architecture:
- Base ML Engine (PredictiveAnalyticsService): Low-level ML predictions and feature extraction
- 5 Intelligence Microservices: Enhanced predictions with contextual intelligence

Replaces: PredictiveIntelligenceService (906 lines god object)

Microservices:
- ContextualAnalysisService: Environmental, competitive, and behavioral intelligence
- TemporalIntelligenceService: Time-based patterns and cyclical analysis
- PredictiveModelingService: Enhanced predictions with intelligence context
- CrossChannelAnalysisService: Channel correlations and influence mapping
- PredictiveOrchestratorService: Workflow coordination and intelligence aggregation

Architecture: Protocol-based dependency injection with orchestrator pattern
Performance: Single responsibility principle with parallel execution support
"""

import logging

# Import base ML engine
from .base.predictive_analytics_service import PredictiveAnalyticsService

# Import concrete implementations
from .contextual.contextual_analysis_service import ContextualAnalysisService
from .cross_channel import (
    ChannelInfluenceService,
    CorrelationAnalysisService,
    CrossChannelOrchestrator,
    IntegrationOpportunityService,
)
from .modeling.predictive_modeling_service import PredictiveModelingService
from .orchestrator import (
    ComprehensiveAnalysisService,
    IntelligenceAggregationService,
    PredictiveOrchestratorService,
    PredictiveServiceExecutorService,
    PredictiveWorkflowOrchestratorService,
)

# Import protocols for type hints
from .protocols.predictive_protocols import (  # Data classes; Enums
    ConfidenceLevel,
    ContextualAnalysisProtocol,
    ContextualIntelligence,
    CrossChannelAnalysisProtocol,
    CrossChannelIntelligence,
    IntelligenceContext,
    PredictionHorizon,
    PredictionNarrative,
    PredictiveModelingProtocol,
    PredictiveOrchestratorProtocol,
    TemporalIntelligence,
    TemporalIntelligenceProtocol,
)
from .temporal.temporal_intelligence_service import TemporalIntelligenceService

logger = logging.getLogger(__name__)


def create_predictive_orchestrator(
    analytics_service=None,
    data_access_service=None,
    predictive_analytics_service=None,
    nlg_service=None,
    config_manager=None,
    **kwargs,
) -> PredictiveOrchestratorProtocol:
    """
    Factory function to create a complete predictive intelligence orchestrator.

    Creates and wires all predictive fusion microservices:
    - ContextualAnalysisService (environmental & competitive intelligence)
    - TemporalIntelligenceService (time-based patterns & cycles)
    - PredictiveModelingService (enhanced predictions with context)
    - CrossChannelAnalysisService (channel correlations & influence)
    - PredictiveOrchestratorService (workflow coordination)

    Args:
        analytics_service: Analytics service for data analysis
        data_access_service: Data access service for channel data
        predictive_analytics_service: Existing predictive analytics service
        nlg_service: Natural language generation service
        config_manager: Configuration manager service
        **kwargs: Additional configuration parameters

    Returns:
        PredictiveOrchestratorProtocol: Fully configured orchestrator with all services

    Example:
        # Create predictive orchestrator
        predictive_orchestrator = create_predictive_orchestrator(
            analytics_service=analytics_service,
            data_access_service=data_access_service
        )

        # Use for comprehensive predictive intelligence
        intelligence_result = await predictive_orchestrator.orchestrate_predictive_intelligence(
            request={"channel_ids": [1, 2, 3]},
            context=IntelligenceContext.COMPREHENSIVE
        )
    """
    try:
        logger.info("🎯 Creating predictive intelligence orchestrator with microservices")

        # Create contextual analysis service
        # ContextualAnalysisService expects: analytics_service, market_data_service, config_manager
        contextual_service = ContextualAnalysisService(
            analytics_service=analytics_service,
            market_data_service=None,  # No market data service available yet
            config_manager=config_manager,
        )
        logger.info("✅ ContextualAnalysisService created")

        # Create temporal intelligence service
        # TemporalIntelligenceService takes NO parameters
        temporal_service = TemporalIntelligenceService()
        logger.info("✅ TemporalIntelligenceService created")

        # Create predictive modeling service
        # PredictiveModelingService expects: predictive_analytics_service, nlg_service, config_manager
        modeling_service = PredictiveModelingService(
            predictive_analytics_service=predictive_analytics_service,
            nlg_service=nlg_service,
            config_manager=config_manager,
        )
        logger.info("✅ PredictiveModelingService created")

        # Create cross-channel orchestrator with microservices
        # CrossChannelOrchestrator expects: analytics_service, data_access_service, config_manager
        # Internally creates: CorrelationAnalysisService, ChannelInfluenceService, IntegrationOpportunityService
        cross_channel_service = CrossChannelOrchestrator(
            analytics_service=analytics_service,
            data_access_service=data_access_service,
            config_manager=config_manager,
        )
        logger.info(
            "✅ CrossChannelOrchestrator created (with 3 microservices: Correlation, Influence, Integration)"
        )

        # Create main orchestrator service with all intelligence services
        # PredictiveOrchestratorService internally creates 4 microservices:
        # - PredictiveServiceExecutorService
        # - IntelligenceAggregationService
        # - ComprehensiveAnalysisService
        # - PredictiveWorkflowOrchestratorService
        orchestrator = PredictiveOrchestratorService(
            contextual_analysis_service=contextual_service,
            temporal_intelligence_service=temporal_service,
            predictive_modeling_service=modeling_service,
            cross_channel_analysis_service=cross_channel_service,
            config_manager=config_manager,
        )
        logger.info(
            "✅ PredictiveOrchestratorService created (lightweight coordinator with 4 internal microservices)"
        )

        logger.info(
            "🚀 Predictive intelligence orchestrator ready - 9 microservices operational (5 intelligence + 4 orchestrator)"
        )
        return orchestrator

    except Exception as e:
        logger.error(f"❌ Failed to create predictive orchestrator: {e}")
        raise


# Convenience functions for individual services
def create_contextual_analysis_service(
    analytics_service=None, market_data_service=None, config_manager=None
) -> ContextualAnalysisProtocol:
    """Create standalone contextual analysis service"""
    # ContextualAnalysisService expects: analytics_service, market_data_service, config_manager
    return ContextualAnalysisService(
        analytics_service=analytics_service,
        market_data_service=market_data_service,
        config_manager=config_manager,
    )


def create_temporal_intelligence_service() -> TemporalIntelligenceProtocol:
    """Create standalone temporal intelligence service"""
    # TemporalIntelligenceService takes NO parameters
    return TemporalIntelligenceService()


def create_predictive_modeling_service(
    predictive_analytics_service=None, nlg_service=None, config_manager=None
) -> PredictiveModelingProtocol:
    """Create standalone predictive modeling service"""
    return PredictiveModelingService(
        predictive_analytics_service=predictive_analytics_service,
        nlg_service=nlg_service,
        config_manager=config_manager,
    )


def create_cross_channel_analysis_service(
    analytics_service=None, data_access_service=None, config_manager=None
) -> CrossChannelAnalysisProtocol:
    """Create standalone cross-channel orchestrator with microservices"""
    return CrossChannelOrchestrator(
        analytics_service=analytics_service,
        data_access_service=data_access_service,
        config_manager=config_manager,
    )


# Export all public interfaces
__all__ = [
    # Base ML Engine
    "PredictiveAnalyticsService",
    # Main factory function
    "create_predictive_orchestrator",
    # Individual service factories
    "create_contextual_analysis_service",
    "create_temporal_intelligence_service",
    "create_predictive_modeling_service",
    "create_cross_channel_analysis_service",
    # Protocol interfaces
    "ContextualAnalysisProtocol",
    "TemporalIntelligenceProtocol",
    "PredictiveModelingProtocol",
    "CrossChannelAnalysisProtocol",
    "PredictiveOrchestratorProtocol",
    # Data classes
    "ContextualIntelligence",
    "TemporalIntelligence",
    "PredictionNarrative",
    "CrossChannelIntelligence",
    # Enums
    "IntelligenceContext",
    "ConfidenceLevel",
    "PredictionHorizon",
    # Service implementations (for advanced usage)
    "ContextualAnalysisService",
    "TemporalIntelligenceService",
    "PredictiveModelingService",
    "CrossChannelOrchestrator",
    "PredictiveOrchestratorService",
    # Cross-channel microservices
    "CorrelationAnalysisService",
    "ChannelInfluenceService",
    "IntegrationOpportunityService",
    # Orchestrator microservices
    "PredictiveServiceExecutorService",
    "IntelligenceAggregationService",
    "ComprehensiveAnalysisService",
    "PredictiveWorkflowOrchestratorService",
]


# Package metadata
__version__ = "2.0.0"
__description__ = "Predictive intelligence package with base ML engine and microservices"
__architecture__ = "protocol_based_microservices"
__god_object_replaced__ = "PredictiveIntelligenceService (906 lines)"
__base_service__ = "PredictiveAnalyticsService (579 lines)"
__microservices_count__ = 5
__transformation_pattern__ = "analytics_fusion"
__migration_date__ = "2025-10-05"

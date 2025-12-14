"""
Optimization Fusion Package
============================

Microservices package for autonomous optimization functionality.

Transformed from: AutonomousOptimizationService (772 lines) god object
Into: 5 focused microservices with single responsibilities

Package Structure:
- protocols/: Protocol interfaces for dependency injection
- performance/: Performance analysis service
- recommendations/: Recommendation engine service
- application/: Optimization application service
- validation/: Validation and A/B testing service
- orchestrator/: Main orchestrator service

Factory Function: create_optimization_orchestrator() - Easy instantiation
"""

import logging

from .application.optimization_application_service import OptimizationApplicationService
from .orchestrator.optimization_orchestrator_service import (
    OptimizationOrchestratorService,
)
from .performance.performance_analysis_service import PerformanceAnalysisService
from .protocols.optimization_protocols import (
    OptimizationApplicationProtocol,
    OptimizationOrchestratorProtocol,
    OptimizationPriority,
    OptimizationRecommendation,
    OptimizationType,
    PerformanceAnalysisProtocol,
    PerformanceBaseline,
    RecommendationEngineProtocol,
    ValidationProtocol,
)
from .recommendations.recommendation_engine_service import RecommendationEngineService
from .validation.validation_service import ValidationService

logger = logging.getLogger(__name__)

__all__ = [
    # Protocols
    "PerformanceAnalysisProtocol",
    "RecommendationEngineProtocol",
    "OptimizationApplicationProtocol",
    "ValidationProtocol",
    "OptimizationOrchestratorProtocol",
    # Data classes
    "OptimizationRecommendation",
    "PerformanceBaseline",
    "OptimizationType",
    "OptimizationPriority",
    # Services
    "PerformanceAnalysisService",
    "RecommendationEngineService",
    "OptimizationApplicationService",
    "ValidationService",
    "OptimizationOrchestratorService",
    # Factory
    "create_optimization_orchestrator",
]


def create_optimization_orchestrator(
    analytics_service=None,
    cache_service=None,
    config_manager=None,
    logger_instance=None,
) -> OptimizationOrchestratorService:
    """
    Factory function to create fully configured optimization orchestrator.

    Creates all microservices with proper dependency injection.

    Args:
        analytics_service: Analytics service for performance data
        cache_service: Cache service for cache optimizations
        config_manager: Configuration management service
        logger_instance: Optional logger instance

    Returns:
        OptimizationOrchestratorService: Fully configured orchestrator

    Example:
        ```python
        # Create orchestrator with dependencies
        orchestrator = create_optimization_orchestrator(
            analytics_service=analytics,
            cache_service=cache,
            config_manager=config
        )

        # Run full optimization cycle
        result = await orchestrator.orchestrate_full_optimization_cycle(
            auto_apply_safe=True
        )

        # Run specific optimization workflow
        performance_data = await orchestrator.orchestrate_performance_analysis()
        ```
    """
    try:
        if logger_instance:
            logger.setLevel(logger_instance.level)

        logger.info("🏭 Creating Optimization Orchestrator with microservices")

        # Create performance analysis service
        performance_analysis_service = PerformanceAnalysisService(
            analytics_service=analytics_service,
            cache_service=cache_service,
            config_manager=config_manager,
        )
        logger.info("✅ Performance analysis service created")

        # Create recommendation engine service
        recommendation_engine_service = RecommendationEngineService()
        logger.info("✅ Recommendation engine service created")

        # Create optimization application service
        optimization_application_service = OptimizationApplicationService(
            analytics_service=analytics_service,
            cache_service=cache_service,
            config_manager=config_manager,
        )
        logger.info("✅ Optimization application service created")

        # Create validation service
        validation_service = ValidationService(
            analytics_service=analytics_service,
            performance_analysis_service=performance_analysis_service,
            config_manager=config_manager,
        )
        logger.info("✅ Validation service created")

        # Create main orchestrator
        orchestrator = OptimizationOrchestratorService(
            performance_analysis_service=performance_analysis_service,
            recommendation_engine_service=recommendation_engine_service,
            optimization_application_service=optimization_application_service,
            validation_service=validation_service,
        )
        logger.info("✅ Optimization orchestrator created")

        logger.info("🎉 Optimization Fusion package initialized successfully")
        logger.info(
            "📊 Microservices created: 5 (Performance, Recommendations, Application, Validation, Orchestrator)"
        )

        return orchestrator

    except Exception as e:
        logger.error(f"❌ Failed to create optimization orchestrator: {e}")
        raise


# Package metadata
__version__ = "1.0.0"
__description__ = "Optimization Fusion - Microservices package for autonomous optimization"
__transformation_source__ = "AutonomousOptimizationService (772 lines)"
__microservices_count__ = 5
__architecture__ = "protocol_based_dependency_injection"

# Transformation summary
TRANSFORMATION_SUMMARY = {
    "source_god_object": "AutonomousOptimizationService",
    "source_lines": 772,
    "microservices_created": 5,
    "architecture_pattern": "protocol_based_dependency_injection",
    "single_responsibility_principle": True,
    "dependency_injection": "protocol_based",
    "factory_pattern": True,
    "microservices": {
        "PerformanceAnalysisService": {
            "responsibility": "performance_analysis_and_metrics",
            "protocol": "PerformanceAnalysisProtocol",
            "estimated_lines": 400,
        },
        "RecommendationEngineService": {
            "responsibility": "optimization_recommendations",
            "protocol": "RecommendationEngineProtocol",
            "estimated_lines": 500,
        },
        "OptimizationApplicationService": {
            "responsibility": "optimization_application",
            "protocol": "OptimizationApplicationProtocol",
            "estimated_lines": 350,
        },
        "ValidationService": {
            "responsibility": "optimization_validation",
            "protocol": "ValidationProtocol",
            "estimated_lines": 400,
        },
        "OptimizationOrchestratorService": {
            "responsibility": "workflow_orchestration",
            "protocol": "OptimizationOrchestratorProtocol",
            "estimated_lines": 450,
        },
    },
    "total_microservices_lines": 2100,
    "code_expansion_factor": 2.72,
    "benefits": [
        "single_responsibility_principle",
        "protocol_based_dependency_injection",
        "autonomous_optimization_workflow",
        "ab_testing_validation",
        "safe_optimization_application",
        "comprehensive_performance_analysis",
        "intelligent_recommendation_engine",
        "factory_pattern_for_easy_instantiation",
    ],
}

# Usage examples
USAGE_EXAMPLES = {
    "full_optimization_cycle": """
# Run complete autonomous optimization cycle
orchestrator = create_optimization_orchestrator(analytics, cache, config)
result = await orchestrator.orchestrate_full_optimization_cycle(auto_apply_safe=True)
    """,
    "performance_analysis_only": """
# Analyze performance without applying optimizations
orchestrator = create_optimization_orchestrator(analytics, cache, config)
performance_data = await orchestrator.orchestrate_performance_analysis()
    """,
    "manual_optimization_review": """
# Generate recommendations for manual review
orchestrator = create_optimization_orchestrator(analytics, cache, config)
recommendations = await orchestrator.orchestrate_recommendation_generation(performance_data)
    """,
}

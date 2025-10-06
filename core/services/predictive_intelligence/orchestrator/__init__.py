"""
Predictive Orchestrator Module
==============================

Refactored microservices architecture for predictive intelligence orchestration.

Architecture:
- PredictiveOrchestratorService (refactored): Lightweight coordinator
- PredictiveServiceExecutorService: Service execution
- IntelligenceAggregationService: Intelligence synthesis
- ComprehensiveAnalysisService: Report generation
- PredictiveWorkflowOrchestratorService: Workflow coordination

Legacy:
- archive/legacy_god_objects_20251005/legacy_predictive_orchestrator_service_1473_lines.py: Original god object - ARCHIVED
"""

# New microservices architecture
from .comprehensive_analysis_service import ComprehensiveAnalysisService
from .intelligence_aggregation_service import IntelligenceAggregationService
from .predictive_orchestrator_service import PredictiveOrchestratorService
from .predictive_service_executor import PredictiveServiceExecutorService
from .workflow_orchestrator_service import PredictiveWorkflowOrchestratorService

__all__ = [
    # Main coordinator (refactored)
    "PredictiveOrchestratorService",
    # Microservices
    "PredictiveServiceExecutorService",
    "IntelligenceAggregationService",
    "ComprehensiveAnalysisService",
    "PredictiveWorkflowOrchestratorService",
]

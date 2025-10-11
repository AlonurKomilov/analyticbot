"""
Churn Intelligence Services Package
===================================

Comprehensive churn prediction and retention intelligence microservices.

This package provides:
- Churn risk prediction and assessment
- Behavioral pattern analysis
- Retention strategy generation and optimization
- Real-time churn monitoring and alerting
- Comprehensive churn intelligence orchestration

Main Services:
- ChurnPredictionService: Core churn risk prediction
- RetentionStrategyService: Retention strategy generation
- BehavioralAnalysisService: Behavioral pattern analysis
- ChurnIntelligenceOrchestratorService: Main orchestrator

Protocol Interfaces:
- ChurnPredictionProtocol
- RetentionStrategyProtocol
- BehavioralAnalysisProtocol
- ChurnOrchestratorProtocol
"""

from .behavioral_analysis_service import BehavioralAnalysisService
from .churn_prediction_service import ChurnPredictionService
from .orchestrator.churn_orchestrator_service import (
    ChurnIntelligenceOrchestratorService,
)
from .protocols import (
    BehavioralAnalysisProtocol,
    ChurnAnalytics,
    ChurnOrchestratorProtocol,
    ChurnPredictionProtocol,
    ChurnRiskLevel,
    ChurnRiskProfile,
    ChurnStage,
    ConfidenceLevel,
    RetentionRecommendation,
    RetentionStrategy,
    RetentionStrategyProtocol,
)
from .retention_strategy_service import RetentionStrategyService

__all__ = [
    # Main Services
    "ChurnPredictionService",
    "RetentionStrategyService",
    "BehavioralAnalysisService",
    "ChurnIntelligenceOrchestratorService",
    # Protocol Interfaces
    "ChurnPredictionProtocol",
    "RetentionStrategyProtocol",
    "BehavioralAnalysisProtocol",
    "ChurnOrchestratorProtocol",
    # Data Models & Enums
    "ChurnRiskProfile",
    "RetentionRecommendation",
    "ChurnAnalytics",
    "ChurnRiskLevel",
    "ChurnStage",
    "RetentionStrategy",
    "ConfidenceLevel",
]

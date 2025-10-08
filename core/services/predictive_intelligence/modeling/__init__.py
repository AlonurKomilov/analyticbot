"""
Predictive Modeling Package
============================

Refactored predictive modeling service split into 5 microservices:

1. PredictionGenerator - Core prediction generation and enhancement
2. ConfidenceCalculator - Confidence scoring and calibration
3. NarrativeBuilder - Natural language narrative generation
4. AccuracyValidator - Prediction accuracy validation
5. ModelingOrchestrator - Coordination and backwards compatibility

Usage:
    # Use orchestrator for complete functionality (backwards compatible)
    from core.services.predictive_intelligence.modeling import PredictiveModelingService

    # Or use individual microservices
    from core.services.predictive_intelligence.modeling import (
        PredictionGenerator,
        ConfidenceCalculator,
        NarrativeBuilder,
        AccuracyValidator,
    )
"""

# Export data models
from .confidence import ConfidenceCalculator
from .models import EnhancedPrediction, ModelingConfig, ValidationResult
from .narrative import NarrativeBuilder
from .orchestrator import ModelingOrchestrator, PredictiveModelingService

# Export microservices
from .prediction import PredictionGenerator
from .validation import AccuracyValidator

__all__ = [
    # Data models
    "ModelingConfig",
    "EnhancedPrediction",
    "ValidationResult",
    # Microservices
    "PredictionGenerator",
    "ConfidenceCalculator",
    "NarrativeBuilder",
    "AccuracyValidator",
    "ModelingOrchestrator",
    # Backwards compatibility alias
    "PredictiveModelingService",
]

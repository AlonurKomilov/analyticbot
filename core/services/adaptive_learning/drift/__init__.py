"""
Drift Detection Microservice
============================

Complete drift detection capabilities with clean architecture.
All drift-related services and components are contained within this microservice.
"""

from .drift_coordinator import (
    ComprehensiveDriftAnalysis,
    DriftCoordinator,
    DriftCoordinatorConfig,
)
from .drift_detection_service import DriftDetectionService
from .multivariate_analyzer import (
    DimensionalityReductionResult,
    MultivariateDriftAnalyzer,
    MultivariateDriftResult,
)
from .statistical_analyzer import (
    FeatureAnalysisResult,
    StatisticalDriftAnalyzer,
    StatisticalTestResult,
)

__all__ = [
    # Main service
    "DriftDetectionService",
    # Core coordinator
    "DriftCoordinator",
    "DriftCoordinatorConfig",
    "ComprehensiveDriftAnalysis",
    # Statistical analysis
    "StatisticalDriftAnalyzer",
    "StatisticalTestResult",
    "FeatureAnalysisResult",
    # Multivariate analysis
    "MultivariateDriftAnalyzer",
    "MultivariateDriftResult",
    "DimensionalityReductionResult",
]

# Microservice metadata
__microservice__ = {
    "name": "drift_detection",
    "version": "1.0.0",
    "description": "Comprehensive drift detection with statistical and multivariate analysis",
    "components": [
        "DriftDetectionService",
        "DriftCoordinator",
        "StatisticalDriftAnalyzer",
        "MultivariateDriftAnalyzer",
    ],
}

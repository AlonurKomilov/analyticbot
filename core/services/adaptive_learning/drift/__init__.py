"""
Drift Detection Microservice
============================

Complete drift detection capabilities with clean architecture.
All drift-related services and components are contained within this microservice.
"""

from .drift_detection_service import DriftDetectionService
from .drift_coordinator import DriftCoordinator, DriftCoordinatorConfig, ComprehensiveDriftAnalysis
from .statistical_analyzer import StatisticalDriftAnalyzer, StatisticalTestResult, FeatureAnalysisResult
from .multivariate_analyzer import MultivariateDriftAnalyzer, MultivariateDriftResult, DimensionalityReductionResult

__all__ = [
    # Main service
    'DriftDetectionService',
    
    # Core coordinator
    'DriftCoordinator',
    'DriftCoordinatorConfig',
    'ComprehensiveDriftAnalysis',
    
    # Statistical analysis
    'StatisticalDriftAnalyzer',
    'StatisticalTestResult',
    'FeatureAnalysisResult',
    
    # Multivariate analysis
    'MultivariateDriftAnalyzer',
    'MultivariateDriftResult',
    'DimensionalityReductionResult'
]

# Microservice metadata
__microservice__ = {
    'name': 'drift_detection',
    'version': '1.0.0',
    'description': 'Comprehensive drift detection with statistical and multivariate analysis',
    'components': [
        'DriftDetectionService',
        'DriftCoordinator', 
        'StatisticalDriftAnalyzer',
        'MultivariateDriftAnalyzer'
    ]
}
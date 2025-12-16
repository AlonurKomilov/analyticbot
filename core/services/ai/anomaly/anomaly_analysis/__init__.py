"""
Anomaly Analysis Microservices Package

Refactored from 748-line monolithic service into 5 focused microservices.

Architecture:
- AnomalyDetectionService: Statistical anomaly detection
- RootCauseAnalyzer: Root cause analysis
- SeverityAssessor: Severity and impact assessment
- AnomalyRecommender: Recommendation generation
- AnomalyOrchestrator: Lightweight coordinator

Benefits:
- Each service < 250 lines (avg 150 lines)
- Single responsibility per service
- Easy to test in isolation
- Better code organization
- Independent caching per service
"""

from .analysis.root_cause_analyzer import RootCauseAnalyzer
from .assessment.severity_assessor import SeverityAssessor
from .detection.anomaly_detection_service import AnomalyDetectionService
from .orchestrator.anomaly_orchestrator import AnomalyOrchestrator
from .recommendations.anomaly_recommender import AnomalyRecommender

# Export main orchestrator (primary interface)
# Also export individual services for advanced usage
__all__ = [
    # Main coordinator (recommended for most use cases)
    "AnomalyOrchestrator",
    # Individual microservices (for advanced usage)
    "AnomalyDetectionService",
    "RootCauseAnalyzer",
    "SeverityAssessor",
    "AnomalyRecommender",
]

# Legacy compatibility note:
# For backwards compatibility, the old AnomalyAnalysisService interface
# is replaced by AnomalyOrchestrator which provides the same public API

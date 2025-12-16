"""
Adaptive Learning Protocols Package
===================================

This package contains all protocol interfaces for adaptive learning microservices.
These protocols define clean contracts for dependency injection and service interaction.

Protocols:
- MonitoringProtocol: Model performance monitoring
- FeedbackProtocol: User feedback collection and processing
- LearningProtocol: Online and incremental learning
- DriftDetectionProtocol: Model and data drift detection

Key Benefits:
- Clean separation of concerns
- Dependency injection support
- Easy testing with mock implementations
- Clear service contracts
- Type safety and documentation
"""

# Monitoring protocols
# Drift detection protocols
from .drift_protocols import (
    DataDistribution,
    DriftAlert,
    DriftAnalysis,
    DriftAnalyzerProtocol,
    DriftDetectionMethod,
    DriftDetectionProtocol,
    DriftSeverity,
    DriftType,
    PerformanceDriftDetectorProtocol,
    StatisticalDriftDetectorProtocol,
)

# Feedback protocols
from .feedback_protocols import (
    ContentType,
    FeedbackAnalysis,
    FeedbackBatch,
    FeedbackProcessorProtocol,
    FeedbackProtocol,
    FeedbackQuality,
    FeedbackSource,
    FeedbackStorageProtocol,
    FeedbackType,
    UserFeedback,
)

# Learning protocols
from .learning_protocols import (
    IncrementalUpdaterProtocol,
    LearningProgress,
    LearningProtocol,
    LearningStrategy,
    LearningTask,
    ModelUpdate,
    ModelVersioningProtocol,
    ModelVersionType,
    OnlineLearnerProtocol,
    UpdateStatus,
)
from .monitoring_protocols import (
    AlertSeverity,
    MonitoringInfrastructureProtocol,
    MonitoringProtocol,
    MonitoringServiceProtocol,
    PerformanceAlert,
    PerformanceMetric,
    PerformanceMetricType,
    PerformanceTrackerProtocol,
)

__all__ = [
    # Monitoring
    "MonitoringProtocol",
    "MonitoringServiceProtocol",
    "PerformanceTrackerProtocol",
    "MonitoringInfrastructureProtocol",
    "PerformanceMetric",
    "PerformanceAlert",
    "PerformanceMetricType",
    "AlertSeverity",
    # Feedback
    "FeedbackProtocol",
    "FeedbackProcessorProtocol",
    "FeedbackStorageProtocol",
    "UserFeedback",
    "FeedbackBatch",
    "FeedbackAnalysis",
    "FeedbackType",
    "ContentType",
    "FeedbackQuality",
    "FeedbackSource",
    # Learning
    "LearningProtocol",
    "OnlineLearnerProtocol",
    "ModelVersioningProtocol",
    "IncrementalUpdaterProtocol",
    "LearningTask",
    "ModelUpdate",
    "LearningProgress",
    "LearningStrategy",
    "UpdateStatus",
    "ModelVersionType",
    # Drift Detection
    "DriftDetectionProtocol",
    "DriftAnalyzerProtocol",
    "PerformanceDriftDetectorProtocol",
    "StatisticalDriftDetectorProtocol",
    "DriftAlert",
    "DriftAnalysis",
    "DataDistribution",
    "DriftType",
    "DriftSeverity",
    "DriftDetectionMethod",
]

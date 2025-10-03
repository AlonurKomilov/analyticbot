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
from .monitoring_protocols import (
    MonitoringProtocol,
    MonitoringServiceProtocol,
    PerformanceTrackerProtocol,
    MonitoringInfrastructureProtocol,
    PerformanceMetric,
    PerformanceAlert,
    PerformanceMetricType,
    AlertSeverity
)

# Feedback protocols
from .feedback_protocols import (
    FeedbackProtocol,
    FeedbackProcessorProtocol,
    FeedbackStorageProtocol,
    UserFeedback,
    FeedbackBatch,
    FeedbackAnalysis,
    FeedbackType,
    ContentType,
    FeedbackQuality,
    FeedbackSource
)

# Learning protocols
from .learning_protocols import (
    LearningProtocol,
    OnlineLearnerProtocol,
    ModelVersioningProtocol,
    IncrementalUpdaterProtocol,
    LearningTask,
    ModelUpdate,
    LearningProgress,
    LearningStrategy,
    UpdateStatus,
    ModelVersion
)

# Drift detection protocols
from .drift_protocols import (
    DriftDetectionProtocol,
    DriftAnalyzerProtocol,
    PerformanceDriftDetectorProtocol,
    StatisticalDriftDetectorProtocol,
    DriftAlert,
    DriftAnalysis,
    DataDistribution,
    DriftType,
    DriftSeverity,
    DriftDetectionMethod
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
    "ModelVersion",
    
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
    "DriftDetectionMethod"
]
"""
Infrastructure Services Package for Adaptive Learning
====================================================

Provides infrastructure components supporting adaptive learning microservices:
- MonitoringInfrastructureService: Performance monitoring and alerting
- FeedbackStorageService: User feedback storage and management
- ModelVersioningService: Model version control and deployment
"""

from ..feedback.feedback_storage import FeedbackStorageConfig, FeedbackStorageService
from ..monitoring.monitoring_infrastructure import MonitoringConfig, MonitoringInfrastructureService

# Import models and service from new versioning package (refactored microservices)
from ..versioning import ModelVersioningService
from ..versioning.models import DeploymentStage, ModelStatus, ModelVersion, ModelVersioningConfig
from .monitoring_infrastructure import MonitoringInfrastructure, get_monitoring_infrastructure

__all__ = [
    # Core Monitoring Infrastructure
    "MonitoringInfrastructure",
    "get_monitoring_infrastructure",
    # Legacy Monitoring Infrastructure
    "MonitoringInfrastructureService",
    "MonitoringConfig",
    # Feedback Storage
    "FeedbackStorageService",
    "FeedbackStorageConfig",
    # Model Versioning
    "ModelVersioningService",
    "ModelVersioningConfig",
    "ModelVersion",
    "ModelStatus",
    "DeploymentStage",
]

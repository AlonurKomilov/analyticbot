"""
Adaptive Learning Microservices Package
=======================================

This package contains all adaptive learning microservices following clean architecture:

Microservices:
- drift: Model drift detection and analysis
- deployment: Model deployment and updates
- learning: Incremental learning and training
- feedback: User feedback collection and processing
- monitoring: Performance monitoring and alerting
- orchestrator: Central coordination and orchestration
- infrastructure: Shared infrastructure components
- protocols: Service interface definitions

Each microservice is self-contained with its own components and clear responsibilities.
"""

from .drift import DriftDetectionService
from .deployment import ModelUpdateService
from .learning import LearningTaskService
from .feedback import FeedbackCollectionService
from .monitoring import PerformanceMonitoringService
from .orchestrator import AdaptiveLearningOrchestrator

__version__ = "2.0.0"
__author__ = "Analytics Bot Team"

# Microservices registry
MICROSERVICES = {
    'drift': {
        'main_service': DriftDetectionService,
        'description': 'Model drift detection and analysis'
    },
    'deployment': {
        'main_service': ModelUpdateService,
        'description': 'Model deployment and updates'
    },
    'learning': {
        'main_service': LearningTaskService,
        'description': 'Incremental learning and training'
    },
    'feedback': {
        'main_service': FeedbackCollectionService,
        'description': 'User feedback collection and processing'
    },
    'monitoring': {
        'main_service': PerformanceMonitoringService,
        'description': 'Performance monitoring and alerting'
    },
    'orchestrator': {
        'main_service': AdaptiveLearningOrchestrator,
        'description': 'Central coordination and orchestration'
    }
}

__all__ = [
    # Main services
    'DriftDetectionService',
    'ModelUpdateService', 
    'LearningTaskService',
    'FeedbackCollectionService',
    'PerformanceMonitoringService',
    'AdaptiveLearningOrchestrator',
    
    # Registry
    'MICROSERVICES'
]
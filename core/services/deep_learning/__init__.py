"""
Deep Learning Microservices Package
==================================

This package contains all deep learning microservices following clean architecture:

- orchestrator: Lightweight coordination service
- engagement: Engagement prediction microservice
- growth: Growth forecasting microservice
- content: Content analysis microservice
- infrastructure: Shared infrastructure components
- protocols: Service interface definitions

Public API:
- DLOrchestratorService: Main entry point for all deep learning operations
- Use through DeepLearningServiceProtocol for proper dependency injection
"""

__version__ = "1.0.0"
__author__ = "Analytics Bot Team"

# Import main orchestrator for easy access
try:
    from .orchestrator import DLOrchestratorService
except ImportError:
    from .orchestrator.dl_orchestrator_service import DLOrchestratorService

# Import individual services for direct access if needed
from .content.content_analyzer_service import ContentAnalyzerService
from .engagement.engagement_predictor_service import EngagementPredictorService
from .growth_forecaster.growth_forecaster_service import GrowthForecasterService

__all__ = [
    "DLOrchestratorService",
    "GrowthForecasterService",
    "EngagementPredictorService",
    "ContentAnalyzerService",
]

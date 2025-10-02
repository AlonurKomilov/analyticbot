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
"""

__version__ = "1.0.0"
__author__ = "Analytics Bot Team"

# Import main orchestrator for easy access
try:
    from .orchestrator import DLOrchestratorService
except ImportError:
    from .orchestrator.dl_orchestrator_service import DLOrchestratorService

__all__ = [
    "DLOrchestratorService"
]
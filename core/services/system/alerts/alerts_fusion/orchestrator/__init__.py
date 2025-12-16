"""
Alerts Orchestrator Package
===========================

Service coordination and orchestration for alerts fusion microservices.

Services:
- AlertsOrchestratorService: Lightweight coordinator for all alerts microservices

Single Responsibility: Pure service coordination without business logic.
"""

from .alerts_orchestrator_service import AlertsOrchestratorService

__all__ = ["AlertsOrchestratorService"]

# Metadata
__version__ = "1.0.0"
__purpose__ = "Alerts orchestration microservice"
__responsibility__ = "Service coordination only"

"""
Analytics Orchestrator Microservice Package
===========================================

Lightweight coordinator for analytics fusion microservices.
Single responsibility: Service coordination only (no heavy business logic).
"""

from .analytics_orchestrator_service import AnalyticsOrchestratorService

__all__ = ["AnalyticsOrchestratorService"]

# Microservice metadata
__microservice__ = {
    "name": "analytics_orchestrator",
    "version": "1.0.0",
    "description": "Lightweight coordination service",
    "responsibility": "Service coordination only - no business logic",
    "pattern": "coordinator_pattern",
    "components": ["AnalyticsOrchestratorService"],
}

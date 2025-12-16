"""
Alerts Fusion Microservices Package
===================================

Clean alerts microservices following single responsibility principle.
Replaces AlertsIntelligenceService god object (900 lines) with focused, testable, maintainable services.

Microservices:
- orchestrator: Lightweight coordination service
- monitoring: Real-time monitoring and live metrics
- alerts: Alert configuration, rules, and checking
- competitive: Competitive intelligence and market analysis
- protocols: Service interface definitions

Each microservice is self-contained with clear responsibilities and clean boundaries.

Architecture Benefits:
✅ No god objects - single responsibility services
✅ Protocol-based dependency injection
✅ Clean separation of concerns
✅ Easy testing and mocking
✅ Independent scalability
✅ Maintainable codebase

Transformation Results:
🔥 AlertsIntelligenceService (900 lines) → 4 focused microservices
📊 Code organized by responsibility instead of size
🎯 Each service has single, clear purpose
"""

__version__ = "1.0.0"
__author__ = "Analytics Bot Team"

# Core services - import orchestrator as main entry point
try:
    from .orchestrator import AlertsOrchestratorService
except ImportError:
    from .orchestrator.alerts_orchestrator_service import AlertsOrchestratorService

# Individual microservices
from .alerts import AlertsManagementService
from .competitive import CompetitiveIntelligenceService
from .monitoring import LiveMonitoringService

# Protocols for dependency injection
from .protocols import (
    AlertsManagementProtocol,
    AlertsOrchestratorProtocol,
    CompetitiveIntelligenceProtocol,
    LiveMonitoringProtocol,
)

# Microservices registry
MICROSERVICES = {
    "orchestrator": {
        "main_service": AlertsOrchestratorService,
        "description": "Lightweight coordination and orchestration",
        "responsibility": "Service coordination only",
    },
    "monitoring": {
        "main_service": LiveMonitoringService,
        "description": "Real-time monitoring and live metrics",
        "responsibility": "Live metrics collection and monitoring",
    },
    "alerts": {
        "main_service": AlertsManagementService,
        "description": "Alert configuration, rules, and checking",
        "responsibility": "Intelligent alerting and rules management",
    },
    "competitive": {
        "main_service": CompetitiveIntelligenceService,
        "description": "Competitive intelligence and market analysis",
        "responsibility": "Competitor analysis and market insights",
    },
}

__all__ = [
    # Main orchestrator
    "AlertsOrchestratorService",
    # Individual microservices
    "LiveMonitoringService",
    "AlertsManagementService",
    "CompetitiveIntelligenceService",
    # Protocols
    "LiveMonitoringProtocol",
    "AlertsManagementProtocol",
    "CompetitiveIntelligenceProtocol",
    "AlertsOrchestratorProtocol",
    # Registry
    "MICROSERVICES",
]

# Package metadata
__package_info__ = {
    "name": "alerts_fusion",
    "type": "microservices_package",
    "architecture": "clean_architecture",
    "pattern": "single_responsibility",
    "god_object_eliminated": "AlertsIntelligenceService (900 lines)",
    "code_reduction": "900 lines → 4 focused services",
    "transformation_completed": True,
    "benefits": [
        "Single responsibility per service",
        "Protocol-based dependency injection",
        "Clean separation of concerns",
        "Easy testing and mocking",
        "Independent scalability",
        "Maintainable codebase",
    ],
}


# Factory function for easy orchestrator creation
def create_alerts_orchestrator(posts_repo, daily_repo, channels_repo) -> AlertsOrchestratorService:
    """
    Factory function to create fully configured alerts orchestrator.

    Args:
        posts_repo: Posts repository protocol
        daily_repo: Daily repository protocol
        channels_repo: Channels repository protocol

    Returns:
        Configured AlertsOrchestratorService with all microservices
    """
    # Create individual microservices
    monitoring_service = LiveMonitoringService()
    alerts_service = AlertsManagementService(
        posts_repo, daily_repo, channels_repo, monitoring_service
    )
    competitive_service = CompetitiveIntelligenceService(posts_repo, daily_repo, channels_repo)

    # Create orchestrator with all services
    orchestrator = AlertsOrchestratorService(
        live_monitoring_service=monitoring_service,
        alerts_management_service=alerts_service,
        competitive_intelligence_service=competitive_service,
    )

    return orchestrator

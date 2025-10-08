"""
Analytics Fusion Microservices Package
======================================

Clean analytics microservices following single responsibility principle.
Replaces god objects with focused, testable, maintainable services.

Microservices:
- orchestrator: Lightweight coordination service
- core: Core analytics processing
- reporting: Report generation and dashboards
- intelligence: AI insights and trend analysis
- monitoring: Real-time monitoring and alerts
- optimization: Performance optimization
- infrastructure: Shared infrastructure components
- protocols: Service interface definitions

Each microservice is self-contained with clear responsibilities and clean boundaries.

Architecture Benefits:
✅ No god objects - single responsibility services
✅ Protocol-based dependency injection
✅ Clean separation of concerns
✅ Easy testing and mocking
✅ Independent scalability
✅ Maintainable codebase
"""

__version__ = "1.0.0"
__author__ = "Analytics Bot Team"

# Core services - import orchestrator as main entry point
try:
    from .orchestrator import AnalyticsOrchestratorService
except ImportError:
    from .orchestrator.analytics_orchestrator_service import (
        AnalyticsOrchestratorService,
    )

# Individual microservices
from .core import AnalyticsCoreService

# Infrastructure
from .infrastructure import CacheManager, ConfigManager, DataAccessService
from .intelligence import IntelligenceService
from .monitoring import LiveMonitoringService
from .optimization import OptimizationService

# Protocols for dependency injection
from .protocols import (
    AnalyticsCoreProtocol,
    IntelligenceProtocol,
    MonitoringProtocol,
    OptimizationProtocol,
    OrchestratorProtocol,
    ReportingProtocol,
)
from .reporting import ReportingService

# Microservices registry
MICROSERVICES = {
    "orchestrator": {
        "main_service": AnalyticsOrchestratorService,
        "description": "Lightweight coordination and orchestration",
        "responsibility": "Service coordination only",
    },
    "core": {
        "main_service": AnalyticsCoreService,
        "description": "Core analytics processing",
        "responsibility": "Analytics calculations and processing",
    },
    "reporting": {
        "main_service": ReportingService,
        "description": "Report generation and dashboards",
        "responsibility": "Report creation and formatting",
    },
    "intelligence": {
        "main_service": IntelligenceService,
        "description": "AI insights and trend analysis",
        "responsibility": "AI-powered insights generation",
    },
    "monitoring": {
        "main_service": LiveMonitoringService,
        "description": "Real-time monitoring and alerts",
        "responsibility": "Live monitoring and alerting",
    },
    "optimization": {
        "main_service": OptimizationService,
        "description": "Performance optimization",
        "responsibility": "Optimization recommendations",
    },
}

__all__ = [
    # Main orchestrator
    "AnalyticsOrchestratorService",
    # Individual microservices
    "AnalyticsCoreService",
    "ReportingService",
    "IntelligenceService",
    "LiveMonitoringService",
    "OptimizationService",
    # Infrastructure
    "DataAccessService",
    "CacheManager",
    "ConfigManager",
    # Protocols
    "AnalyticsCoreProtocol",
    "ReportingProtocol",
    "IntelligenceProtocol",
    "MonitoringProtocol",
    "OptimizationProtocol",
    "OrchestratorProtocol",
    # Registry
    "MICROSERVICES",
]

# Package metadata
__package_info__ = {
    "name": "analytics_fusion",
    "type": "microservices_package",
    "architecture": "clean_architecture",
    "pattern": "single_responsibility",
    "god_objects_eliminated": [
        "AnalyticsFusionService (1409 lines)",
        "AnalyticsOrchestrationService (1024 lines)",
        "AnalyticsOrchestratorService (433 lines)",
    ],
    "code_reduction": "2866 lines → 6 focused services",
    "benefits": [
        "Single responsibility per service",
        "Protocol-based dependency injection",
        "Clean separation of concerns",
        "Easy testing and mocking",
        "Independent scalability",
        "Maintainable codebase",
    ],
}

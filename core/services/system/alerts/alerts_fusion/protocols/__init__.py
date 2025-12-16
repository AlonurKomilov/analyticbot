"""
Alerts Fusion Protocol Interfaces
=================================

Service protocol interfaces for alerts fusion microservices.
These protocols define clean contracts for dependency injection and service interaction.

Usage:
- Import specific protocols for dependency injection
- Use in service constructors for loose coupling
- Easy testing with mock implementations
- Type-safe service contracts
"""

from .alerts_protocols import (
    AlertConfig,
    AlertsManagementProtocol,
    AlertsOrchestratorProtocol,
    CompetitiveAnalysis,
    CompetitiveIntelligenceProtocol,
    LiveMetrics,
    LiveMonitoringProtocol,
)

__all__ = [
    # Service protocols
    "LiveMonitoringProtocol",
    "AlertsManagementProtocol",
    "CompetitiveIntelligenceProtocol",
    "AlertsOrchestratorProtocol",
    # Data models
    "AlertConfig",
    "LiveMetrics",
    "CompetitiveAnalysis",
]

# Metadata
__version__ = "1.0.0"
__purpose__ = "Alerts fusion microservices protocols"
__pattern__ = "Protocol-based dependency injection"

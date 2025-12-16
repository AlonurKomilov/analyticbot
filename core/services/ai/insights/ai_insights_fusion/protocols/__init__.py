"""
AI Insights Fusion Protocol Interfaces
======================================

Service protocol interfaces for AI insights fusion microservices.
These protocols define clean contracts for dependency injection and service interaction.

Usage:
- Import specific protocols for dependency injection
- Use in service constructors for loose coupling
- Easy testing with mock implementations
- Type-safe service contracts
"""

from .ai_insights_protocols import (
    AIInsightsData,
    AIInsightsOrchestratorProtocol,
    CoreInsightsProtocol,
    PatternAnalysisProtocol,
    PatternAnalysisResult,
    PredictionResult,
    PredictiveAnalysisProtocol,
    ServiceIntegrationProtocol,
)

__all__ = [
    # Service protocols
    "CoreInsightsProtocol",
    "PatternAnalysisProtocol",
    "PredictiveAnalysisProtocol",
    "ServiceIntegrationProtocol",
    "AIInsightsOrchestratorProtocol",
    # Data models
    "AIInsightsData",
    "PatternAnalysisResult",
    "PredictionResult",
]

# Metadata
__version__ = "1.0.0"
__purpose__ = "AI insights fusion microservices protocols"
__pattern__ = "Protocol-based dependency injection"

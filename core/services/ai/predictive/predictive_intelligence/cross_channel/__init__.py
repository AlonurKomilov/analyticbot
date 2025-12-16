"""
Cross-Channel Analysis Module
==============================

Refactored microservices architecture for cross-channel analysis.

Original CrossChannelAnalysisService (1,608 lines) split into:
- CorrelationAnalysisService (435 lines): Correlation calculations
- ChannelInfluenceService (476 lines): Influence mapping
- IntegrationOpportunityService (588 lines): Integration patterns
- CrossChannelOrchestrator (406 lines): Lightweight coordinator

Total: 1,905 lines (distributed across 4 focused services)
Reduction: More modular, testable, and maintainable
"""

from .channel_influence_service import ChannelInfluenceService
from .correlation_analysis_service import CorrelationAnalysisService
from .cross_channel_orchestrator import CrossChannelOrchestrator
from .integration_opportunity_service import IntegrationOpportunityService

__all__ = [
    # Microservices architecture
    "CrossChannelOrchestrator",
    "CorrelationAnalysisService",
    "ChannelInfluenceService",
    "IntegrationOpportunityService",
]

# Legacy service archived to: archive/legacy_god_objects_20251005/legacy_cross_channel_analysis_service_1608_lines.py

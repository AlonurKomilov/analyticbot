"""
Competitive Intelligence Microservices Package
==============================================

Competitive analysis and market intelligence services.

Services:
- CompetitiveIntelligenceService: Competitor analysis, market intelligence, and opportunities

Single Responsibility: Pure competitive analysis without alerts or monitoring logic.
"""

from .competitive_intelligence_service import CompetitiveIntelligenceService

__all__ = ["CompetitiveIntelligenceService"]

# Metadata
__version__ = "1.0.0"
__purpose__ = "Competitive intelligence microservices"
__responsibility__ = "Competitive analysis and market intelligence only"

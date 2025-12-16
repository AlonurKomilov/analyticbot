"""
Pattern Analysis Microservices Package
======================================

Pattern analysis and recognition services.

Services:
- PatternAnalysisService: Content patterns, audience behavior patterns, performance patterns

Single Responsibility: Pure pattern analysis without core insights or predictions.
"""

from .pattern_analysis_service import PatternAnalysisService

__all__ = ["PatternAnalysisService"]

# Metadata
__version__ = "1.0.0"
__purpose__ = "Pattern analysis microservices"
__responsibility__ = "Pattern recognition and analysis only"

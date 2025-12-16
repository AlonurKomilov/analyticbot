"""
Insights Microservices Package
==============================

Core AI insights generation services.

Services:
- CoreInsightsService: Core AI insights generation and data preparation

Single Responsibility: Pure AI insights generation without pattern analysis or predictions.
"""

from .core_insights_service import CoreInsightsService

__all__ = ["CoreInsightsService"]

# Metadata
__version__ = "1.0.0"
__purpose__ = "Core AI insights microservices"
__responsibility__ = "AI insights generation only"

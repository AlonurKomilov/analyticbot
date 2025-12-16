"""
Intelligence Microservice Package
=================================

AI insights and trend analysis microservice.
Single responsibility: Intelligence generation only.
"""

from .intelligence_service import IntelligenceService

__all__ = ["IntelligenceService"]

# Microservice metadata
__microservice__ = {
    "name": "intelligence",
    "version": "1.0.0",
    "description": "AI insights and trend analysis",
    "responsibility": "AI-powered insights generation only",
    "components": ["IntelligenceService"],
}

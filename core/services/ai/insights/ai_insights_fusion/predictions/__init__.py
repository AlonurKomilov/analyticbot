"""
Predictive Analysis Microservices Package
=========================================

AI predictions and recommendations services.

Services:
- PredictiveAnalysisService: AI predictions, trend forecasting, recommendations

Single Responsibility: Pure predictive analysis without core insights or patterns.
"""

from .predictive_analysis_service import PredictiveAnalysisService

__all__ = ["PredictiveAnalysisService"]

# Metadata
__version__ = "1.0.0"
__purpose__ = "Predictive analysis microservices"
__responsibility__ = "AI predictions and recommendations only"

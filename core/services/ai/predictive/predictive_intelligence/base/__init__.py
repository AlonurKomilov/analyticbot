"""
Base ML Engine
==============

Foundation ML prediction service for the predictive intelligence system.

This module contains the base PredictiveAnalyticsService which provides
low-level machine learning prediction capabilities used by the intelligence
layer microservices.
"""

from .predictive_analytics_service import PredictiveAnalyticsService

__all__ = [
    "PredictiveAnalyticsService",
]

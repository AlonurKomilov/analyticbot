"""
Predictive insights package - modular predictive analytics endpoints.

This package provides predictive analytics, AI recommendations,
forecasting, and intelligence analysis split into domain modules.
"""

from .models import (
    ContextualIntelligenceRequest,
    CrossChannelIntelligenceRequest,
    PredictionRequest,
)
from .router import router

__all__ = [
    "router",
    "PredictionRequest",
    "ContextualIntelligenceRequest",
    "CrossChannelIntelligenceRequest",
]

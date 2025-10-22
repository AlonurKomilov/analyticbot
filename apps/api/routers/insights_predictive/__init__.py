"""
Predictive insights package - modular predictive analytics endpoints.

This package provides predictive analytics, AI recommendations,
forecasting, and intelligence analysis split into domain modules.
"""

from .router import router
from .models import (
    PredictionRequest,
    ContextualIntelligenceRequest,
    CrossChannelIntelligenceRequest,
)

__all__ = [
    "router",
    "PredictionRequest",
    "ContextualIntelligenceRequest",
    "CrossChannelIntelligenceRequest",
]

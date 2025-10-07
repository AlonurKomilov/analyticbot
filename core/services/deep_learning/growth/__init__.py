"""
Growth Forecasting Module
========================

Deep learning-based growth forecasting with GRU + Attention neural networks.
This module provides microservices for predicting business and user growth patterns.
"""

from .data_processors.growth_data_processor import GrowthDataProcessor
from .growth_forecaster_service import GrowthForecasterService
from .models.gru_growth_model import GRUGrowthModel, GRUGrowthModelConfig

__all__ = [
    "GrowthForecasterService",
    "GRUGrowthModel",
    "GRUGrowthModelConfig",
    "GrowthDataProcessor",
]

__version__ = "1.0.0"

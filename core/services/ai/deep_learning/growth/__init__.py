"""
Growth Forecasting Module
========================

Deep learning-based growth forecasting with GRU + Attention neural networks.
This module provides models and data processors for growth forecasting.
"""

from .data_processors.growth_data_processor import GrowthDataProcessor
from .models.gru_growth_model import GRUGrowthModel, GRUGrowthModelConfig

__all__ = ["GRUGrowthModel", "GRUGrowthModelConfig", "GrowthDataProcessor"]

__version__ = "1.0.0"

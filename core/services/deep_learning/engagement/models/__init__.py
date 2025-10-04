"""
Engagement Models Package
========================

Contains PyTorch models specifically for engagement prediction:

- lstm_engagement_model: LSTM-based engagement prediction
"""

from .lstm_engagement_model import LSTMEngagementModel, LSTMEngagementModelConfig

__all__ = ["LSTMEngagementModel", "LSTMEngagementModelConfig"]

"""
ML Mock Data Package
Centralized mock data for ML services
"""

from .mock_ml_data import (
    get_mock_optimal_posting_time,
    get_mock_ml_health_check,
    get_mock_content_analysis,
    get_mock_churn_prediction
)

__all__ = [
    "get_mock_optimal_posting_time",
    "get_mock_ml_health_check",
    "get_mock_content_analysis", 
    "get_mock_churn_prediction"
]
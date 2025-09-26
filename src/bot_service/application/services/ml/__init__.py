"""
🤖 ML Service Module - AI/ML capabilities for AnalyticBot
"""

from .churn_predictor import ChurnPredictor
from .content_optimizer import ContentOptimizer
from .engagement_analyzer import EngagementAnalyzer
from .predictive_engine import PredictiveAnalyticsEngine, PredictionResult, ContentMetrics

# For backward compatibility
PredictionService = PredictiveAnalyticsEngine

__all__ = ["PredictiveAnalyticsEngine", "PredictionService", "PredictionResult", "ContentMetrics", "ContentOptimizer", "ChurnPredictor", "EngagementAnalyzer"]

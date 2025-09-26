"""
Mock ML Data
Centralized mock data for ML services to keep production code clean
"""

from datetime import datetime, timedelta
from ..constants import (
    DEFAULT_DEMO_OPTIMAL_HOUR,
    DEFAULT_DEMO_POSTING_CONFIDENCE,
    DEFAULT_DEMO_ENGAGEMENT_RATE,
    DEFAULT_DEMO_CONTENT_LENGTH
)

from typing import Dict, Any, List
from datetime import datetime


def get_mock_optimal_posting_time():
    """Mock optimal posting time data"""
    return {
        "optimal_time": f"{DEFAULT_DEMO_OPTIMAL_HOUR}:00",
        "confidence": DEFAULT_DEMO_POSTING_CONFIDENCE,
        "timezone": "UTC",
        "engagement_prediction": DEFAULT_DEMO_ENGAGEMENT_RATE,
        "recommended_days": ["Monday", "Wednesday", "Friday"]
    }


def get_mock_ml_health_check() -> Dict[str, Any]:
    """
    Mock health check data for ML services
    """
    return {
        "status": "healthy",
        "models_loaded": 5,
        "last_training": "2025-09-20T10:30:00Z",
        "prediction_accuracy": 0.84,
        "memory_usage": "256MB",
        "cpu_usage": "12%",
        "active_predictions": 142,
        "cache_hit_rate": 0.78
    }


def get_mock_content_analysis():
    """Mock content analysis data"""
    return {
        "sentiment": "positive",
        "topics": ["technology", "productivity", "analysis"],
        "readability_score": 0.8,
        "engagement_prediction": DEFAULT_DEMO_ENGAGEMENT_RATE,
        "optimal_length": DEFAULT_DEMO_CONTENT_LENGTH,
        "hashtag_suggestions": ["#analytics", "#data", "#insights"]
    }


def get_mock_churn_prediction(user_id: int) -> Dict[str, Any]:
    """
    Mock churn prediction data
    """
    # Simple mock based on user_id for consistency
    churn_prob = (user_id % 100) / 100.0
    
    if churn_prob < 0.3:
        risk_level = "low"
        factors = ["High engagement rate", "Regular posting schedule", "Growing follower count"]
    elif churn_prob < 0.7:
        risk_level = "medium"
        factors = ["Moderate engagement", "Irregular posting", "Stable follower count"]
    else:
        risk_level = "high"
        factors = ["Low engagement rate", "Infrequent posting", "Declining followers"]
    
    return {
        "churn_probability": churn_prob,
        "risk_level": risk_level,
        "confidence": 0.82,
        "key_factors": factors,
        "recommendations": [
            "Increase posting frequency" if churn_prob > 0.5 else "Maintain current strategy",
            "Focus on engagement-driven content",
            "Monitor competitor activities"
        ],
        "user_id": user_id,
        "prediction_date": datetime.now().isoformat()
    }


# Export all mock functions
__all__ = [
    "get_mock_optimal_posting_time",
    "get_mock_ml_health_check", 
    "get_mock_content_analysis",
    "get_mock_churn_prediction"
]
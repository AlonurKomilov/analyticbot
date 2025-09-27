"""
Mock AI Service for centralized mocking
"""

from typing import Any


class MockAIService:
    """Centralized mock AI service"""

    def __init__(self):
        self._responses = {
            "sentiment_analysis": {"sentiment": "positive", "confidence": 0.85},
            "content_optimization": {
                "optimized": True,
                "suggestions": ["Use more engaging titles"],
            },
            "trend_prediction": {"trend": "upward", "confidence": 0.78},
        }

    def analyze_sentiment(self, text: str) -> dict[str, Any]:
        """Mock sentiment analysis"""
        return self._responses["sentiment_analysis"]

    def optimize_content(self, content: str) -> dict[str, Any]:
        """Mock content optimization"""
        return self._responses["content_optimization"]

    def predict_trends(self, data: list[dict]) -> dict[str, Any]:
        """Mock trend prediction"""
        return self._responses["trend_prediction"]

    def generate_insights(self, channel_id: int) -> list[dict[str, Any]]:
        """Generate mock AI insights"""
        return [
            {
                "insight_type": "engagement_pattern",
                "message": "Peak engagement occurs at 2-4 PM",
                "confidence": 0.82,
                "channel_id": channel_id,
            },
            {
                "insight_type": "content_recommendation",
                "message": "Video content performs 40% better",
                "confidence": 0.75,
                "channel_id": channel_id,
            },
        ]

    def get_service_name(self) -> str:
        return "MockAIService"

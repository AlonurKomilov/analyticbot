"""
Performance Analytics Service
Handles calculation of performance scores and metrics analysis
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class PerformanceAnalyticsService:
    """Service for calculating and analyzing performance metrics"""

    def __init__(self):
        # Configuration for performance scoring weights
        self._weights = {
            "growth_rate": 0.3,
            "engagement_rate": 0.4,
            "reach_score": 0.2,
            "consistency": 0.1,
        }

        # Thresholds for normalization
        self._thresholds = {
            "growth_rate_max": 20,  # Max expected growth rate for normalization
            "engagement_rate_max": 10,  # Max expected engagement rate for normalization
        }

    def calculate_performance_score(self, metrics: dict[str, Any]) -> int:
        """
        Calculate overall performance score based on multiple metrics

        Args:
            metrics: Dictionary containing performance metrics

        Returns:
            Performance score as integer (0-100)
        """
        try:
            # Normalize metrics to 0-100 scale
            growth_score = self._normalize_growth_rate(metrics.get("growth_rate", 0))
            engagement_score = self._normalize_engagement_rate(metrics.get("engagement_rate", 0))
            reach_score = metrics.get("reach_score", 0)
            consistency_score = self._calculate_consistency_score(metrics)

            # Calculate weighted total score
            total_score = (
                growth_score * self._weights["growth_rate"]
                + engagement_score * self._weights["engagement_rate"]
                + reach_score * self._weights["reach_score"]
                + consistency_score * self._weights["consistency"]
            )

            return int(min(100, max(0, total_score)))

        except Exception as e:
            logger.error(f"Error calculating performance score: {e}")
            return 50  # Default middle score on error

    def _normalize_growth_rate(self, growth_rate: float) -> float:
        """Normalize growth rate to 0-100 scale"""
        return min(100, max(0, (growth_rate / self._thresholds["growth_rate_max"]) * 100))

    def _normalize_engagement_rate(self, engagement_rate: float) -> float:
        """Normalize engagement rate to 0-100 scale"""
        return min(
            100,
            max(0, (engagement_rate / self._thresholds["engagement_rate_max"]) * 100),
        )

    def _calculate_consistency_score(self, metrics: dict[str, Any]) -> float:
        """
        Calculate consistency score based on variance and stability

        For now, returns a default good consistency score.
        In the future, this could analyze historical data variance.
        """
        # TODO: Implement actual consistency calculation based on historical variance
        return 75.0  # Default good consistency

    def analyze_performance_trends(
        self, historical_metrics: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Analyze performance trends over time

        Args:
            historical_metrics: List of historical metric dictionaries

        Returns:
            Dictionary containing trend analysis
        """
        if not historical_metrics:
            return {
                "trend_direction": "unknown",
                "stability": "unknown",
                "recommendation": "Insufficient data for analysis",
            }

        # Calculate trend direction
        scores = [self.calculate_performance_score(metrics) for metrics in historical_metrics]

        if len(scores) < 2:
            trend_direction = "stable"
        else:
            recent_avg = sum(scores[-3:]) / len(scores[-3:])  # Last 3 periods
            earlier_avg = sum(scores[:-3]) / len(scores[:-3]) if len(scores) > 3 else scores[0]

            if recent_avg > earlier_avg + 5:
                trend_direction = "improving"
            elif recent_avg < earlier_avg - 5:
                trend_direction = "declining"
            else:
                trend_direction = "stable"

        # Calculate stability (coefficient of variation)
        if len(scores) > 1:
            mean_score = sum(scores) / len(scores)
            variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
            std_dev = variance**0.5
            cv = std_dev / mean_score if mean_score > 0 else 0

            if cv < 0.1:
                stability = "very_stable"
            elif cv < 0.2:
                stability = "stable"
            elif cv < 0.3:
                stability = "moderate"
            else:
                stability = "volatile"
        else:
            stability = "unknown"

        return {
            "trend_direction": trend_direction,
            "stability": stability,
            "current_score": scores[-1] if scores else 0,
            "average_score": sum(scores) / len(scores) if scores else 0,
            "score_range": (
                {"min": min(scores), "max": max(scores)} if scores else {"min": 0, "max": 0}
            ),
        }

    def get_performance_recommendations(self, metrics: dict[str, Any], score: int) -> list[str]:
        """
        Generate performance improvement recommendations based on metrics and score

        Args:
            metrics: Current performance metrics
            score: Current performance score

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Score-based recommendations
        if score < 30:
            recommendations.append(
                "Performance is critically low. Consider comprehensive strategy review."
            )
        elif score < 50:
            recommendations.append("Performance needs improvement. Focus on key growth metrics.")
        elif score < 70:
            recommendations.append("Good performance with room for optimization.")
        else:
            recommendations.append("Excellent performance! Maintain current strategies.")

        # Metric-specific recommendations
        growth_rate = metrics.get("growth_rate", 0)
        if growth_rate < 0:
            recommendations.append(
                "Negative growth detected. Review content strategy and engagement tactics."
            )
        elif growth_rate < 2:
            recommendations.append(
                "Low growth rate. Consider increasing posting frequency or content variety."
            )

        engagement_rate = metrics.get("engagement_rate", 0)
        if engagement_rate < 2:
            recommendations.append(
                "Low engagement. Try interactive content like polls, questions, or contests."
            )
        elif engagement_rate < 5:
            recommendations.append(
                "Moderate engagement. Focus on community building and response time."
            )

        reach_score = metrics.get("reach_score", 0)
        if reach_score < 30:
            recommendations.append(
                "Limited reach. Optimize posting times and use relevant hashtags."
            )

        return recommendations

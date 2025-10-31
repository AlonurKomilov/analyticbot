"""
Anomaly Recommender

Specialized service for generating actionable recommendations based on anomaly analysis.
Single Responsibility: Recommendation generation and confidence calculation.

Part of refactored Anomaly Analysis microservices architecture.
"""

from __future__ import annotations

import logging
from datetime import datetime

import numpy as np

logger = logging.getLogger(__name__)


class AnomalyRecommender:
    """
    💡 Anomaly Recommender

    Focused responsibility: Generate actionable recommendations
    based on anomaly analysis and root cause findings.
    """

    def __init__(self, config_manager=None):
        """Initialize recommender with optional configuration"""
        self.config_manager = config_manager

    async def generate_recommendations(
        self, anomaly_data: dict, root_causes: list[dict], severity_assessment: dict
    ) -> list[dict]:
        """
        Generate specific recommendations based on anomaly analysis

        Args:
            anomaly_data: Detected anomaly information
            root_causes: List of potential root causes
            severity_assessment: Severity and impact assessment

        Returns:
            List of prioritized recommendations with timelines
        """
        recommendations = []

        try:
            severity = severity_assessment.get("overall_severity", "medium")
            severity_assessment.get("urgency", "moderate")

            # Severity-based immediate actions
            if severity in ["critical", "high"]:
                recommendations.append(
                    {
                        "priority": "immediate",
                        "category": "emergency_response",
                        "action": "Conduct immediate strategy review and implement corrective measures",
                        "timeline": "Within 24 hours",
                        "expected_outcome": "Stabilize performance metrics",
                    }
                )

            # Root cause specific recommendations
            for cause in root_causes[:3]:  # Top 3 causes
                category = cause.get("category", "unknown")

                if category == "content_length":
                    recommendations.append(
                        {
                            "priority": "high",
                            "category": "content_optimization",
                            "action": f"Adjust content length based on analysis: {cause.get('description', '')}",
                            "timeline": "Next 3-5 posts",
                            "expected_outcome": "Improved content performance",
                        }
                    )

                elif category == "posting_frequency":
                    recommendations.append(
                        {
                            "priority": "medium",
                            "category": "schedule_optimization",
                            "action": "Optimize posting frequency based on historical performance",
                            "timeline": "Next 2 weeks",
                            "expected_outcome": "Better audience engagement",
                        }
                    )

                elif category == "posting_schedule":
                    recommendations.append(
                        {
                            "priority": "medium",
                            "category": "timing_optimization",
                            "action": "Review and optimize posting schedule for audience activity",
                            "timeline": "Next week",
                            "expected_outcome": "Increased reach and engagement",
                        }
                    )

                elif category == "external_factors":
                    recommendations.append(
                        {
                            "priority": "low",
                            "category": "market_analysis",
                            "action": "Monitor competitor activity and market trends",
                            "timeline": "Ongoing",
                            "expected_outcome": "Better strategic positioning",
                        }
                    )

                elif category == "audience_growth":
                    recommendations.append(
                        {
                            "priority": "high",
                            "category": "audience_retention",
                            "action": f"Address audience growth trend: {cause.get('description', '')}",
                            "timeline": "Next 2 weeks",
                            "expected_outcome": "Improved audience retention and growth",
                        }
                    )

            # General monitoring recommendation
            recommendations.append(
                {
                    "priority": "ongoing",
                    "category": "monitoring",
                    "action": "Implement enhanced monitoring for early anomaly detection",
                    "timeline": "Immediate setup, ongoing monitoring",
                    "expected_outcome": "Faster response to future anomalies",
                }
            )

            # Sort by priority
            priority_order = {
                "immediate": 4,
                "high": 3,
                "medium": 2,
                "low": 1,
                "ongoing": 0,
            }
            recommendations.sort(
                key=lambda x: priority_order.get(x.get("priority", "low"), 0),
                reverse=True,
            )

            return recommendations

        except Exception as e:
            logger.error(f"Anomaly recommendation generation failed: {e}")
            return [
                {
                    "priority": "high",
                    "category": "manual_review",
                    "action": "Conduct manual analysis of recent performance changes",
                    "timeline": "As soon as possible",
                    "expected_outcome": "Identify and address performance issues",
                }
            ]

    def calculate_analysis_confidence(
        self, anomaly_data: dict, historical_context: dict, root_causes: list[dict]
    ) -> float:
        """
        Calculate confidence score for the anomaly analysis

        Args:
            anomaly_data: Detected anomaly information
            historical_context: Historical data used in analysis
            root_causes: Identified root causes

        Returns:
            Confidence score (0.0 to 1.0)
        """
        try:
            confidence_factors = []

            # Data availability
            if historical_context.get("posts"):
                confidence_factors.append(0.3)
            if historical_context.get("daily_metrics"):
                confidence_factors.append(0.2)

            # Root cause confidence
            if root_causes:
                avg_cause_confidence = np.mean([c.get("confidence", 0) for c in root_causes])
                confidence_factors.append(avg_cause_confidence * 0.3)

            # Anomaly strength
            z_score = anomaly_data.get("z_score", 0)
            if z_score > 3:
                confidence_factors.append(0.2)
            elif z_score > 2:
                confidence_factors.append(0.15)
            else:
                confidence_factors.append(0.1)

            return min(1.0, sum(confidence_factors))

        except Exception:
            return 0.5  # Default moderate confidence

    async def health_check(self) -> dict:
        """Health check for anomaly recommender"""
        return {
            "service": "AnomalyRecommender",
            "status": "healthy",
            "capabilities": [
                "recommendation_generation",
                "confidence_calculation",
                "priority_assignment",
            ],
            "recommendation_categories": [
                "emergency_response",
                "content_optimization",
                "schedule_optimization",
                "timing_optimization",
                "market_analysis",
                "audience_retention",
                "monitoring",
            ],
            "priority_levels": ["immediate", "high", "medium", "low", "ongoing"],
            "timestamp": datetime.now().isoformat(),
        }

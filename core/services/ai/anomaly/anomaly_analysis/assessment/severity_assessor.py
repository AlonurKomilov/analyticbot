"""
Severity Assessor

Specialized service for assessing the severity and impact of anomalies.
Single Responsibility: Severity assessment and impact analysis.

Part of refactored Anomaly Analysis microservices architecture.
"""

from __future__ import annotations

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class SeverityAssessor:
    """
    ⚖️ Severity Assessor

    Focused responsibility: Assess the severity and potential
    business impact of detected anomalies.
    """

    def __init__(self, config_manager=None):
        """Initialize assessor with optional configuration"""
        self.config_manager = config_manager

    async def assess_severity(self, anomaly_data: dict, historical_context: dict) -> dict:
        """
        Assess the severity and potential impact of an anomaly

        Args:
            anomaly_data: Detected anomaly information
            historical_context: Historical data for comparison

        Returns:
            Severity assessment with score and impact details
        """
        try:
            severity_factors = {
                "magnitude": 0,
                "duration": 0,
                "trend": 0,
                "impact_scope": 0,
            }

            # Magnitude assessment
            deviation = abs(anomaly_data.get("deviation_percentage", 0))
            if deviation > 50:
                severity_factors["magnitude"] = 3  # High
            elif deviation > 25:
                severity_factors["magnitude"] = 2  # Medium
            elif deviation > 10:
                severity_factors["magnitude"] = 1  # Low

            # Duration assessment (placeholder - would need time series data)
            severity_factors["duration"] = 1  # Default to low

            # Overall severity calculation
            total_score = sum(severity_factors.values())
            max_score = len(severity_factors) * 3

            severity_percentage = (total_score / max_score) * 100

            if severity_percentage > 66:
                overall_severity = "critical"
            elif severity_percentage > 33:
                overall_severity = "high"
            elif severity_percentage > 15:
                overall_severity = "medium"
            else:
                overall_severity = "low"

            return {
                "overall_severity": overall_severity,
                "severity_score": severity_percentage,
                "factors": severity_factors,
                "impact_assessment": self._assess_business_impact(anomaly_data, overall_severity),
                "urgency": (
                    "immediate" if overall_severity in ["critical", "high"] else "moderate"
                ),
            }

        except Exception as e:
            logger.error(f"Severity assessment failed: {e}")
            return {"overall_severity": "unknown", "error": str(e)}

    def _assess_business_impact(self, anomaly_data: dict, severity: str) -> str:
        """Assess potential business impact of the anomaly"""
        metric = anomaly_data.get("metric", "unknown")

        impact_map = {
            "critical": {
                "views": "Significant audience reach reduction - immediate attention required",
                "engagement": "Severe engagement drop - content strategy review needed",
                "growth": "Critical growth issue - retention strategies required",
            },
            "high": {
                "views": "Notable performance decline - strategy adjustment recommended",
                "engagement": "Engagement concerns - content optimization needed",
                "growth": "Growth slowdown - audience acquisition review suggested",
            },
            "medium": {
                "views": "Moderate performance variation - monitoring recommended",
                "engagement": "Engagement fluctuation - minor adjustments may help",
                "growth": "Growth variation - continue current strategies with monitoring",
            },
            "low": {
                "views": "Minor performance variation - normal fluctuation range",
                "engagement": "Slight engagement change - minimal concern",
                "growth": "Small growth variation - within normal parameters",
            },
        }

        return impact_map.get(severity, {}).get(metric, "Impact assessment unavailable")

    def severity_score(self, severity: str) -> int:
        """
        Convert severity string to numeric score for sorting

        Args:
            severity: Severity level as string

        Returns:
            Numeric severity score (0-4)
        """
        severity_map = {"critical": 4, "high": 3, "medium": 2, "low": 1, "unknown": 0}
        return severity_map.get(severity.lower(), 0)

    async def health_check(self) -> dict:
        """Health check for severity assessor"""
        return {
            "service": "SeverityAssessor",
            "status": "healthy",
            "capabilities": [
                "severity_assessment",
                "impact_analysis",
                "urgency_determination",
            ],
            "severity_levels": ["critical", "high", "medium", "low"],
            "assessment_factors": ["magnitude", "duration", "trend", "impact_scope"],
            "timestamp": datetime.now().isoformat(),
        }

"""
Root Cause Analyzer

Specialized service for analyzing potential root causes of detected anomalies.
Single Responsibility: Root cause analysis for anomalous patterns.

Part of refactored Anomaly Analysis microservices architecture.
"""

from __future__ import annotations

import logging
from datetime import datetime

import numpy as np

logger = logging.getLogger(__name__)


class RootCauseAnalyzer:
    """
    🔬 Root Cause Analyzer

    Focused responsibility: Analyze and identify potential root causes
    of detected anomalies in channel performance.
    """

    def __init__(self, config_manager=None):
        """Initialize analyzer with optional configuration"""
        self.config_manager = config_manager

    async def analyze_root_causes(
        self, channel_id: int, anomaly_data: dict, historical_context: dict
    ) -> list[dict]:
        """
        Analyze potential root causes of detected anomalies

        Args:
            channel_id: Target channel ID
            anomaly_data: Detected anomaly information
            historical_context: Historical data for comparison

        Returns:
            List of potential root causes with confidence scores
        """
        try:
            root_causes = []
            anomaly_metric = anomaly_data.get("metric", "unknown")
            anomaly_type = anomaly_data.get("type", "unknown")

            # Content strategy changes
            if anomaly_metric in ["engagement", "views"]:
                content_causes = await self._analyze_content_related_causes(
                    anomaly_data, historical_context
                )
                root_causes.extend(content_causes)

            # Timing and frequency changes
            if anomaly_type == "temporal" or anomaly_metric == "frequency":
                timing_causes = await self._analyze_timing_related_causes(
                    anomaly_data, historical_context
                )
                root_causes.extend(timing_causes)

            # Growth-related causes
            if anomaly_metric in ["growth", "followers", "subscribers"]:
                growth_causes = await self._analyze_growth_related_causes(
                    anomaly_data, historical_context
                )
                root_causes.extend(growth_causes)

            # External factor analysis
            external_causes = await self._analyze_external_factors(anomaly_data, historical_context)
            root_causes.extend(external_causes)

            # Sort by confidence and relevance
            root_causes.sort(key=lambda x: x.get("confidence", 0), reverse=True)

            return root_causes[:5]  # Top 5 most likely causes

        except Exception as e:
            logger.error(f"Root cause analysis failed: {e}")
            return [
                {
                    "category": "unknown",
                    "description": "Unable to determine root cause",
                    "confidence": 0.1,
                }
            ]

    async def _analyze_content_related_causes(
        self, anomaly_data: dict, historical_context: dict
    ) -> list[dict]:
        """Analyze content-related potential causes"""
        causes = []
        posts = historical_context.get("posts", [])

        if posts and len(posts) >= 10:
            recent_posts = posts[:5]  # Most recent 5 posts
            historical_posts = posts[5:15]  # Previous 10 posts

            # Analyze content length changes
            recent_lengths = [len(p.get("title", "")) for p in recent_posts]
            hist_lengths = [len(p.get("title", "")) for p in historical_posts]

            if recent_lengths and hist_lengths:
                recent_avg = np.mean(recent_lengths)
                hist_avg = np.mean(hist_lengths)

                if abs(recent_avg - hist_avg) > hist_avg * 0.3:  # 30% change
                    causes.append(
                        {
                            "category": "content_length",
                            "description": f"Significant change in content length: {recent_avg:.0f} vs {hist_avg:.0f} characters",
                            "confidence": 0.7,
                            "change_percentage": ((recent_avg - hist_avg) / hist_avg * 100),
                        }
                    )

            # Analyze posting frequency changes
            if len(posts) >= 20:
                recent_dates = []
                hist_dates = []

                for post in recent_posts:
                    if post.get("date"):
                        try:
                            date = datetime.fromisoformat(post["date"].replace("Z", "+00:00"))
                            recent_dates.append(date)
                        except:
                            continue

                for post in historical_posts:
                    if post.get("date"):
                        try:
                            date = datetime.fromisoformat(post["date"].replace("Z", "+00:00"))
                            hist_dates.append(date)
                        except:
                            continue

                if len(recent_dates) >= 3 and len(hist_dates) >= 3:
                    # Calculate posting frequency
                    recent_span = (max(recent_dates) - min(recent_dates)).days
                    hist_span = (max(hist_dates) - min(hist_dates)).days

                    if recent_span > 0 and hist_span > 0:
                        recent_freq = len(recent_dates) / recent_span
                        hist_freq = len(hist_dates) / hist_span

                        if abs(recent_freq - hist_freq) > hist_freq * 0.4:  # 40% change
                            causes.append(
                                {
                                    "category": "posting_frequency",
                                    "description": f"Posting frequency changed from {hist_freq:.1f} to {recent_freq:.1f} posts per day",
                                    "confidence": 0.8,
                                    "frequency_change": (
                                        (recent_freq - hist_freq) / hist_freq * 100
                                    ),
                                }
                            )

        return causes

    async def _analyze_timing_related_causes(
        self, anomaly_data: dict, historical_context: dict
    ) -> list[dict]:
        """Analyze timing and schedule related causes"""
        causes = []

        # Placeholder for timing analysis
        # In a real implementation, this would analyze posting time changes
        causes.append(
            {
                "category": "posting_schedule",
                "description": "Potential changes in posting timing or schedule",
                "confidence": 0.6,
                "details": "Schedule analysis requires more detailed timestamp data",
            }
        )

        return causes

    async def _analyze_growth_related_causes(
        self, anomaly_data: dict, historical_context: dict
    ) -> list[dict]:
        """Analyze growth and audience related causes"""
        causes = []
        daily_metrics = historical_context.get("daily_metrics", {})
        followers_data = daily_metrics.get("followers", [])

        if followers_data and len(followers_data) >= 7:
            # Analyze follower growth patterns
            recent_followers = [f.get("value", 0) for f in followers_data[-7:]]

            if len(recent_followers) >= 2:
                growth_rates = []
                for i in range(1, len(recent_followers)):
                    if recent_followers[i - 1] > 0:
                        rate = (recent_followers[i] - recent_followers[i - 1]) / recent_followers[
                            i - 1
                        ]
                        growth_rates.append(rate)

                if growth_rates:
                    avg_growth = np.mean(growth_rates)
                    if abs(avg_growth) > 0.05:  # 5% change threshold
                        causes.append(
                            {
                                "category": "audience_growth",
                                "description": f"Audience growth rate: {avg_growth * 100:.1f}% daily average",
                                "confidence": 0.7,
                                "growth_trend": ("positive" if avg_growth > 0 else "negative"),
                            }
                        )

        return causes

    async def _analyze_external_factors(
        self, anomaly_data: dict, historical_context: dict
    ) -> list[dict]:
        """Analyze potential external factors"""
        causes = []

        # General external factors (in a real implementation, this could integrate with external APIs)
        causes.append(
            {
                "category": "external_factors",
                "description": "Market conditions, platform changes, or competitive factors",
                "confidence": 0.4,
                "details": "External factor analysis requires additional data sources",
            }
        )

        # Seasonal factors
        now = datetime.now()
        if now.month == 12 or now.month == 1:  # Holiday season
            causes.append(
                {
                    "category": "seasonal",
                    "description": "Holiday season impact on engagement patterns",
                    "confidence": 0.6,
                    "season": "holiday",
                }
            )

        return causes

    async def health_check(self) -> dict:
        """Health check for root cause analyzer"""
        return {
            "service": "RootCauseAnalyzer",
            "status": "healthy",
            "capabilities": [
                "content_analysis",
                "timing_analysis",
                "growth_analysis",
                "external_factor_analysis",
            ],
            "analysis_categories": [
                "content_length",
                "posting_frequency",
                "posting_schedule",
                "audience_growth",
                "external_factors",
                "seasonal",
            ],
            "timestamp": datetime.now().isoformat(),
        }

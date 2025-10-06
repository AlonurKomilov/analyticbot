"""
Anomaly Detection Service

S    as    async def _detect_metric_anomalies(
        self,
        channel_id: int,
        metrics: Optional[List[str]] = None,
        sensitivity: float = 2.0,
        days: int = 30
    ) -> List[dict]: detect_performance_anomalies(
        self,
        channel_id: int,
        metrics: Optional[List[str]] = None,
        sensitivity: float = 2.0,
        lookback_days: int = 30
    ) -> List[Dict]:zed service for detecting performance anomalies in channel metrics.
Single Responsibility: Statistical anomaly detection using z-score analysis.

Part of refactored Anomaly Analysis microservices architecture.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

import numpy as np

logger = logging.getLogger(__name__)


class AnomalyDetectionService:
    """
    🔍 Anomaly Detection Service

    Focused responsibility: Detect statistical anomalies in channel metrics
    using z-score analysis and other statistical methods.
    """

    def __init__(self, channel_daily_repo, post_repo):
        """Initialize with required repositories"""
        self._daily = channel_daily_repo
        self._posts = post_repo

    async def detect_performance_anomalies(
        self,
        channel_id: int,
        metrics: list[str] | None = None,
        sensitivity: float = 2.0,
        days: int = 30,
    ) -> list[dict]:
        """
        🔍 Detect Performance Anomalies in Channel Metrics

        Analyzes channel performance data to automatically detect unusual patterns
        that deviate significantly from historical norms.

        Args:
            channel_id: Target channel ID
            metrics: List of metrics to analyze (views, engagement, growth)
            sensitivity: Standard deviations threshold (lower = more sensitive)
            days: Historical period to analyze

        Returns:
            List of detected anomalies with details
        """
        try:
            if metrics is None:
                metrics = ["views", "engagement", "growth"]

            detected_anomalies = []
            now = datetime.now()
            start_date = now - timedelta(days=days)

            # Analyze each metric for anomalies
            for metric in metrics:
                anomalies = await self._detect_metric_anomalies(
                    channel_id, metric, start_date, now, sensitivity
                )
                detected_anomalies.extend(anomalies)

            # Sort by severity and recency
            detected_anomalies.sort(
                key=lambda x: (
                    self._severity_score(x.get("severity", "low")),
                    x.get("detected_at", ""),
                ),
                reverse=True,
            )

            logger.info(f"Detected {len(detected_anomalies)} anomalies for channel {channel_id}")
            return detected_anomalies

        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return []

    async def _detect_metric_anomalies(
        self,
        channel_id: int,
        metric: str,
        start_date: datetime,
        end_date: datetime,
        sensitivity: float,
    ) -> list[dict]:
        """Detect anomalies in a specific metric"""
        anomalies = []

        try:
            if metric == "views":
                # Analyze view anomalies
                posts = await self._posts.top_by_views(channel_id, start_date, end_date, 50)
                if posts:
                    view_counts = [p.get("views", 0) for p in posts]
                    anomalies.extend(
                        self.statistical_anomaly_detection(view_counts, "views", sensitivity)
                    )

            elif metric == "engagement":
                # Analyze engagement anomalies
                posts = await self._posts.top_by_views(channel_id, start_date, end_date, 50)
                if posts:
                    engagement_scores = []
                    for post in posts:
                        views = post.get("views", 0)
                        forwards = post.get("forwards", 0)
                        replies = post.get("replies", 0)

                        if views > 0:
                            engagement = (forwards + replies) / views * 100
                            engagement_scores.append(engagement)

                    if engagement_scores:
                        anomalies.extend(
                            self.statistical_anomaly_detection(
                                engagement_scores, "engagement", sensitivity
                            )
                        )

            elif metric == "growth":
                # Analyze growth anomalies
                daily_data = await self._daily.series_data(
                    channel_id, "followers", start_date, end_date
                )
                if daily_data:
                    growth_rates = []
                    values = [d.get("value", 0) for d in daily_data]

                    for i in range(1, len(values)):
                        if values[i - 1] > 0:
                            rate = (values[i] - values[i - 1]) / values[i - 1]
                            growth_rates.append(rate)

                    if growth_rates:
                        anomalies.extend(
                            self.statistical_anomaly_detection(growth_rates, "growth", sensitivity)
                        )

        except Exception as e:
            logger.error(f"Metric anomaly detection failed for {metric}: {e}")

        return anomalies

    def statistical_anomaly_detection(
        self, data: list[float], metric_name: str, sensitivity: float
    ) -> list[dict]:
        """
        Perform statistical anomaly detection using z-score method

        Args:
            data: List of metric values
            metric_name: Name of the metric being analyzed
            sensitivity: Z-score threshold for anomaly detection

        Returns:
            List of detected anomalies with statistical details
        """
        anomalies = []

        if len(data) < 5:  # Need minimum data points
            return anomalies

        try:
            mean_val = np.mean(data)
            std_val = np.std(data)

            if std_val == 0:  # No variation
                return anomalies

            for i, value in enumerate(data):
                z_score = abs((value - mean_val) / std_val)

                if z_score > sensitivity:
                    severity = "high" if z_score > sensitivity * 1.5 else "medium"

                    anomalies.append(
                        {
                            "metric": metric_name,
                            "value": value,
                            "expected_value": mean_val,
                            "z_score": z_score,
                            "deviation_percentage": ((value - mean_val) / mean_val * 100),
                            "severity": severity,
                            "position": i,
                            "type": "statistical",
                            "detected_at": datetime.now().isoformat(),
                        }
                    )

        except Exception as e:
            logger.error(f"Statistical anomaly detection failed: {e}")

        return anomalies

    def _severity_score(self, severity: str) -> int:
        """Convert severity string to numeric score for sorting"""
        severity_map = {"critical": 4, "high": 3, "medium": 2, "low": 1, "unknown": 0}
        return severity_map.get(severity.lower(), 0)

    async def health_check(self) -> dict:
        """Health check for anomaly detection service"""
        return {
            "service": "AnomalyDetectionService",
            "status": "healthy",
            "capabilities": [
                "statistical_anomaly_detection",
                "z_score_analysis",
                "multi_metric_support",
            ],
            "supported_metrics": ["views", "engagement", "growth"],
            "dependencies": {"numpy": True},
            "timestamp": datetime.now().isoformat(),
        }

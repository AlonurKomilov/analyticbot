"""
Metrics Processor
================

Handles metrics calculations for analytics core service.
Single responsibility: Metrics calculations only.
"""

import logging
from datetime import datetime
from typing import Any

import numpy as np

from ...protocols.analytics_protocols import MetricsProcessorProtocol

logger = logging.getLogger(__name__)


class MetricsProcessor(MetricsProcessorProtocol):
    """
    Metrics processing component for analytics core service.

    Single responsibility: Metrics calculations only.
    """

    def __init__(self):
        self.calculation_count = 0
        self.last_calculation_time: datetime | None = None

        logger.info("📊 Metrics Processor initialized")

    async def calculate_engagement_metrics(self, channel_data: dict[str, Any]) -> dict[str, float]:
        """Calculate engagement metrics"""
        try:
            logger.info("📈 Calculating engagement metrics")

            engagement_metrics = {}
            daily_data = channel_data.get("daily_data", [])
            post_data = channel_data.get("post_data", [])

            if daily_data:
                # Calculate engagement rate
                total_engagement = sum(day.get("engagement_count", 0) for day in daily_data)
                total_views = sum(day.get("views_count", 0) for day in daily_data)
                engagement_metrics["engagement_rate"] = self._safe_divide(
                    total_engagement, total_views
                )

                # Calculate average daily engagement
                daily_engagements = [day.get("engagement_count", 0) for day in daily_data]
                engagement_metrics["avg_daily_engagement"] = np.mean(daily_engagements)

                # Calculate engagement consistency
                engagement_metrics["engagement_consistency"] = (
                    1.0 - np.std(daily_engagements) / np.mean(daily_engagements)
                    if np.mean(daily_engagements) > 0
                    else 0.0
                )

            if post_data:
                # Calculate post-level metrics
                post_engagements = [post.get("engagement_score", 0) for post in post_data]
                if post_engagements:
                    engagement_metrics["avg_post_engagement"] = np.mean(post_engagements)
                    engagement_metrics["max_post_engagement"] = max(post_engagements)
                    engagement_metrics["engagement_variance"] = np.var(post_engagements)

            self.calculation_count += 1
            self.last_calculation_time = datetime.utcnow()

            logger.info(f"✅ Calculated {len(engagement_metrics)} engagement metrics")
            return engagement_metrics

        except Exception as e:
            logger.error(f"❌ Error calculating engagement metrics: {e}")
            return {}

    async def calculate_performance_metrics(self, channel_data: dict[str, Any]) -> dict[str, float]:
        """Calculate performance metrics"""
        try:
            logger.info("🚀 Calculating performance metrics")

            performance_metrics = {}
            daily_data = channel_data.get("daily_data", [])

            if daily_data:
                # Growth metrics
                subscriber_counts = [day.get("subscribers_count", 0) for day in daily_data]
                if len(subscriber_counts) > 1:
                    growth_rate = (subscriber_counts[-1] - subscriber_counts[0]) / max(
                        subscriber_counts[0], 1
                    )
                    performance_metrics["subscriber_growth_rate"] = growth_rate
                    performance_metrics["total_subscriber_growth"] = (
                        subscriber_counts[-1] - subscriber_counts[0]
                    )

                # View metrics
                view_counts = [day.get("views_count", 0) for day in daily_data]
                performance_metrics["total_views"] = sum(view_counts)
                performance_metrics["avg_daily_views"] = np.mean(view_counts)
                performance_metrics["view_consistency"] = (
                    1.0 - np.std(view_counts) / np.mean(view_counts)
                    if np.mean(view_counts) > 0
                    else 0.0
                )

                # Reach metrics
                reach_counts = [day.get("reach_count", 0) for day in daily_data]
                performance_metrics["total_reach"] = sum(reach_counts)
                performance_metrics["avg_daily_reach"] = np.mean(reach_counts)
                performance_metrics["reach_rate"] = self._safe_divide(
                    sum(reach_counts), sum(view_counts)
                )

            self.calculation_count += 1
            self.last_calculation_time = datetime.utcnow()

            logger.info(f"✅ Calculated {len(performance_metrics)} performance metrics")
            return performance_metrics

        except Exception as e:
            logger.error(f"❌ Error calculating performance metrics: {e}")
            return {}

    async def aggregate_metrics(self, metrics_list: list[dict[str, float]]) -> dict[str, float]:
        """Aggregate multiple metric sets"""
        try:
            logger.info(f"🔄 Aggregating {len(metrics_list)} metric sets")

            if not metrics_list:
                return {}

            aggregated = {}

            # Get all unique metric keys
            all_keys = set()
            for metrics in metrics_list:
                all_keys.update(metrics.keys())

            # Aggregate each metric
            for key in all_keys:
                values = [metrics.get(key, 0) for metrics in metrics_list if key in metrics]
                if values:
                    aggregated[f"{key}_avg"] = np.mean(values)
                    aggregated[f"{key}_sum"] = sum(values)
                    aggregated[f"{key}_max"] = max(values)
                    aggregated[f"{key}_min"] = min(values)
                    if len(values) > 1:
                        aggregated[f"{key}_std"] = np.std(values)

            logger.info(f"✅ Aggregated into {len(aggregated)} metrics")
            return aggregated

        except Exception as e:
            logger.error(f"❌ Error aggregating metrics: {e}")
            return {}

    def _safe_divide(self, numerator: float, denominator: float) -> float:
        """Safe division that handles zero denominator"""
        try:
            return numerator / denominator if denominator != 0 else 0.0
        except (TypeError, ZeroDivisionError):
            return 0.0

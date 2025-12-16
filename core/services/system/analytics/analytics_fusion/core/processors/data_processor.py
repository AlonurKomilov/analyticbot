"""
Data Processor
==============

Handles data processing and normalization for analytics core service.
Single responsibility: Clean data processing only.
"""

import logging
from datetime import datetime
from typing import Any

import numpy as np

from ...protocols.analytics_protocols import DataProcessorProtocol, MetricsData

logger = logging.getLogger(__name__)


class DataProcessor(DataProcessorProtocol):
    """
    Data processing component for analytics core service.

    Single responsibility: Data cleaning and normalization.
    """

    def __init__(self):
        self.processing_count = 0
        self.last_processing_time: datetime | None = None

        logger.info("🔧 Data Processor initialized")

    async def process_raw_data(self, raw_data: dict[str, Any]) -> MetricsData:
        """Process raw data into structured metrics"""
        try:
            logger.info("🔄 Processing raw channel data")

            # Extract basic information
            channel_id = raw_data.get("channel_id", 0)
            timestamp = raw_data.get("fetched_at", datetime.utcnow())

            # Process engagement metrics
            engagement_metrics = await self._process_engagement_data(raw_data)

            # Process performance metrics
            performance_metrics = await self._process_performance_data(raw_data)

            # Process content metrics
            content_metrics = await self._process_content_data(raw_data)

            # Create metadata
            metadata = {
                "data_points": len(raw_data.get("daily_data", [])),
                "posts_analyzed": len(raw_data.get("post_data", [])),
                "processing_timestamp": datetime.utcnow(),
                "data_quality_score": await self._calculate_data_quality(raw_data),
            }

            metrics_data = MetricsData(
                channel_id=channel_id,
                timestamp=timestamp,
                engagement_metrics=engagement_metrics,
                performance_metrics=performance_metrics,
                content_metrics=content_metrics,
                metadata=metadata,
            )

            # Update tracking
            self.processing_count += 1
            self.last_processing_time = datetime.utcnow()

            logger.info(f"✅ Processed data for channel {channel_id}")
            return metrics_data

        except Exception as e:
            logger.error(f"❌ Error processing raw data: {e}")
            # Return empty metrics data with error
            return MetricsData(
                channel_id=raw_data.get("channel_id", 0),
                timestamp=datetime.utcnow(),
                engagement_metrics={},
                performance_metrics={},
                content_metrics={"error": str(e)},
                metadata={"processing_error": str(e)},
            )

    async def normalize_metrics(self, metrics: dict[str, float]) -> dict[str, float]:
        """Normalize metrics to standard scales"""
        try:
            normalized = {}

            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    # Normalize to 0-1 scale
                    normalized[key] = await self._normalize_value(value, key)
                else:
                    normalized[key] = 0.0

            logger.info(f"📏 Normalized {len(metrics)} metrics")
            return normalized

        except Exception as e:
            logger.error(f"❌ Error normalizing metrics: {e}")
            return metrics  # Return original if normalization fails

    async def validate_data_quality(self, data: Any) -> bool:
        """Validate data quality and completeness"""
        try:
            if not data:
                return False

            # Check if it's MetricsData
            if isinstance(data, MetricsData):
                return await self._validate_metrics_data(data)

            # Check if it's raw data dict
            if isinstance(data, dict):
                return await self._validate_raw_data(data)

            return False

        except Exception as e:
            logger.error(f"❌ Error validating data quality: {e}")
            return False

    # Private helper methods

    async def _process_engagement_data(self, raw_data: dict[str, Any]) -> dict[str, float]:
        """Process engagement-related data"""
        engagement_metrics = {}

        try:
            daily_data = raw_data.get("daily_data", [])
            post_data = raw_data.get("post_data", [])

            if daily_data:
                # Calculate average engagement rate
                engagement_rates = [
                    self._safe_divide(day.get("engagement_count", 0), day.get("views_count", 1))
                    for day in daily_data
                ]
                engagement_metrics["avg_engagement_rate"] = (
                    np.mean(engagement_rates) if engagement_rates else 0.0
                )

                # Calculate engagement consistency
                engagement_metrics["engagement_consistency"] = (
                    1.0 - np.std(engagement_rates)
                    if engagement_rates and len(engagement_rates) > 1
                    else 0.0
                )

            if post_data:
                # Calculate post engagement metrics
                post_engagements = [post.get("engagement_score", 0) for post in post_data]
                engagement_metrics["avg_post_engagement"] = (
                    np.mean(post_engagements) if post_engagements else 0.0
                )
                engagement_metrics["max_post_engagement"] = (
                    max(post_engagements) if post_engagements else 0.0
                )

            return engagement_metrics

        except Exception as e:
            logger.error(f"❌ Error processing engagement data: {e}")
            return {}

    async def _process_performance_data(self, raw_data: dict[str, Any]) -> dict[str, float]:
        """Process performance-related data"""
        performance_metrics = {}

        try:
            daily_data = raw_data.get("daily_data", [])

            if daily_data:
                # Calculate growth metrics
                subscriber_counts = [day.get("subscribers_count", 0) for day in daily_data]
                if len(subscriber_counts) > 1:
                    growth_rate = (
                        subscriber_counts[-1] - subscriber_counts[0]
                    ) / subscriber_counts[0]
                    performance_metrics["subscriber_growth_rate"] = growth_rate

                # Calculate view metrics
                view_counts = [day.get("views_count", 0) for day in daily_data]
                performance_metrics["avg_daily_views"] = (
                    np.mean(view_counts) if view_counts else 0.0
                )
                performance_metrics["total_views"] = sum(view_counts)

                # Calculate reach metrics
                reach_counts = [day.get("reach_count", 0) for day in daily_data]
                performance_metrics["avg_daily_reach"] = (
                    np.mean(reach_counts) if reach_counts else 0.0
                )

            return performance_metrics

        except Exception as e:
            logger.error(f"❌ Error processing performance data: {e}")
            return {}

    async def _process_content_data(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        """Process content-related data"""
        content_metrics = {}

        try:
            post_data = raw_data.get("post_data", [])

            if post_data:
                # Analyze content types
                content_types = [post.get("content_type", "unknown") for post in post_data]
                content_metrics["content_type_distribution"] = {
                    content_type: content_types.count(content_type) / len(content_types)
                    for content_type in set(content_types)
                }

                # Analyze content length
                content_lengths = [
                    len(post.get("content", "")) for post in post_data if post.get("content")
                ]
                if content_lengths:
                    content_metrics["avg_content_length"] = np.mean(content_lengths)
                    content_metrics["content_length_variance"] = np.var(content_lengths)

                # Content quality indicators
                content_metrics["total_posts"] = len(post_data)
                content_metrics["posts_with_media"] = sum(
                    1 for post in post_data if post.get("has_media", False)
                )

            return content_metrics

        except Exception as e:
            logger.error(f"❌ Error processing content data: {e}")
            return {}

    async def _normalize_value(self, value: float, metric_key: str) -> float:
        """Normalize a single value based on metric type"""
        try:
            # Define normalization ranges for different metric types
            normalization_ranges = {
                "engagement_rate": (0, 0.1),  # 0-10% engagement rate
                "growth_rate": (-0.5, 0.5),  # -50% to +50% growth
                "views": (0, 100000),  # 0 to 100k views
                "subscribers": (0, 1000000),  # 0 to 1M subscribers
            }

            # Find appropriate range
            min_val, max_val = normalization_ranges.get(
                metric_key,
                (0, max(abs(value) * 2, 1)),  # Dynamic range fallback
            )

            # Normalize to 0-1 scale
            normalized = (value - min_val) / (max_val - min_val)
            return max(0.0, min(1.0, normalized))  # Clamp to [0, 1]

        except Exception:
            return 0.5  # Default middle value

    async def _calculate_data_quality(self, raw_data: dict[str, Any]) -> float:
        """Calculate data quality score"""
        try:
            quality_factors = []

            # Check data completeness
            daily_data = raw_data.get("daily_data", [])
            post_data = raw_data.get("post_data", [])
            metrics_data = raw_data.get("metrics_data", [])

            quality_factors.append(1.0 if len(daily_data) > 0 else 0.0)
            quality_factors.append(1.0 if len(post_data) > 0 else 0.0)
            quality_factors.append(1.0 if len(metrics_data) > 0 else 0.0)

            # Check data freshness
            if daily_data:
                latest_date = max(
                    day.get("date", datetime.min)
                    for day in daily_data
                    if isinstance(day.get("date"), datetime)
                )
                days_old = (datetime.utcnow() - latest_date).days
                quality_factors.append(1.0 if days_old < 7 else 0.5)

            return sum(quality_factors) / len(quality_factors) if quality_factors else 0.0

        except Exception:
            return 0.5  # Default medium quality

    async def _validate_metrics_data(self, data: MetricsData) -> bool:
        """Validate MetricsData structure"""
        try:
            return (
                data.channel_id > 0
                and isinstance(data.engagement_metrics, dict)
                and isinstance(data.performance_metrics, dict)
                and isinstance(data.content_metrics, dict)
                and data.timestamp is not None
            )
        except Exception:
            return False

    async def _validate_raw_data(self, data: dict[str, Any]) -> bool:
        """Validate raw data structure"""
        try:
            required_fields = ["channel_id", "daily_data", "post_data"]
            return all(field in data for field in required_fields)
        except Exception:
            return False

    def _safe_divide(self, numerator: float, denominator: float) -> float:
        """Safe division that handles zero denominator"""
        try:
            return numerator / denominator if denominator != 0 else 0.0
        except (TypeError, ZeroDivisionError):
            return 0.0

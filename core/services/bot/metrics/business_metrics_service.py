"""
Business metrics collection service.

This service handles business-specific metrics like channel counts,
user statistics, post metrics, etc.
"""

import logging

from core.services.bot.metrics.models import (
    BusinessMetrics,
    MetricDefinition,
    MetricType,
)
from core.services.bot.metrics.protocols import MetricsBackendPort

logger = logging.getLogger(__name__)


class BusinessMetricsService:
    """
    Service for collecting business-specific metrics.

    This service tracks application-level metrics that are specific
    to the business domain (channels, users, posts, etc.).
    """

    def __init__(self, metrics_backend: MetricsBackendPort):
        """
        Initialize the business metrics service.

        Args:
            metrics_backend: Backend implementation for metrics storage
        """
        self.backend = metrics_backend
        self._initialized = False

    def initialize_metrics(self) -> None:
        """Initialize business metrics."""
        if self._initialized:
            return

        # Channel metrics
        self.backend.initialize_metric(
            MetricDefinition(
                name="channels_total",
                metric_type=MetricType.GAUGE,
                description="Total number of channels",
            )
        )

        # User metrics
        self.backend.initialize_metric(
            MetricDefinition(
                name="users_total",
                metric_type=MetricType.GAUGE,
                description="Total number of users",
            )
        )

        # Post metrics
        self.backend.initialize_metric(
            MetricDefinition(
                name="posts_scheduled",
                metric_type=MetricType.GAUGE,
                description="Number of scheduled posts",
            )
        )
        self.backend.initialize_metric(
            MetricDefinition(
                name="posts_sent_total",
                metric_type=MetricType.COUNTER,
                description="Total posts sent",
                labels=["status"],
            )
        )
        self.backend.initialize_metric(
            MetricDefinition(
                name="post_views_updated_total",
                metric_type=MetricType.COUNTER,
                description="Total post view updates",
            )
        )

        self._initialized = True
        logger.info("Business metrics initialized successfully")

    async def update_business_metrics(self, metrics: BusinessMetrics) -> None:
        """
        Update all business metrics at once.

        Args:
            metrics: Business metrics snapshot
        """
        try:
            self.backend.set_gauge("channels_total", float(metrics.channels_count))
            self.backend.set_gauge("users_total", float(metrics.users_count))
            self.backend.set_gauge("posts_scheduled", float(metrics.scheduled_posts_count))

            # Update any additional custom metrics
            for name, value in metrics.additional_metrics.items():
                self.backend.set_gauge(name, float(value))

        except Exception as e:
            logger.error(f"Failed to update business metrics: {e}")

    async def record_post_sent(self, status: str = "success") -> None:
        """
        Record a post being sent.

        Args:
            status: Post send status (success, failed, etc.)
        """
        try:
            self.backend.record_counter(
                "posts_sent_total",
                value=1.0,
                labels={"status": status},
            )
        except Exception as e:
            logger.error(f"Failed to record post sent: {e}")

    async def record_post_views_update(self) -> None:
        """Record a post views update."""
        try:
            self.backend.record_counter("post_views_updated_total", value=1.0)
        except Exception as e:
            logger.error(f"Failed to record post views update: {e}")

    async def update_channels_count(self, count: int) -> None:
        """
        Update total channels count.

        Args:
            count: Number of channels
        """
        try:
            self.backend.set_gauge("channels_total", float(count))
        except Exception as e:
            logger.error(f"Failed to update channels count: {e}")

    async def update_users_count(self, count: int) -> None:
        """
        Update total users count.

        Args:
            count: Number of users
        """
        try:
            self.backend.set_gauge("users_total", float(count))
        except Exception as e:
            logger.error(f"Failed to update users count: {e}")

    async def update_scheduled_posts_count(self, count: int) -> None:
        """
        Update scheduled posts count.

        Args:
            count: Number of scheduled posts
        """
        try:
            self.backend.set_gauge("posts_scheduled", float(count))
        except Exception as e:
            logger.error(f"Failed to update scheduled posts count: {e}")

"""
Health check metrics service.

This service manages health check status metrics for various
system components.
"""

import logging

from core.services.bot.metrics.models import (
    HealthCheckResult,
    MetricDefinition,
    MetricType,
)
from core.services.bot.metrics.protocols import MetricsBackendPort

logger = logging.getLogger(__name__)


class HealthCheckService:
    """
    Service for managing health check metrics.

    This service tracks the health status of various system components
    and exposes them as metrics.
    """

    def __init__(self, metrics_backend: MetricsBackendPort):
        """
        Initialize the health check service.

        Args:
            metrics_backend: Backend implementation for metrics storage
        """
        self.backend = metrics_backend
        self._initialized = False

    def initialize_metrics(self) -> None:
        """Initialize health check metrics."""
        if self._initialized:
            return

        self.backend.initialize_metric(
            MetricDefinition(
                name="health_check_status",
                metric_type=MetricType.GAUGE,
                description="Health check status (1=healthy, 0=unhealthy)",
                labels=["check_name"],
            )
        )

        self._initialized = True
        logger.info("Health check metrics initialized successfully")

    async def update_health_check(self, result: HealthCheckResult) -> None:
        """
        Update health check status.

        Args:
            result: Health check result
        """
        try:
            self.backend.set_gauge(
                "health_check_status",
                result.status_value,
                labels={"check_name": result.check_name},
            )
            if not result.is_healthy:
                logger.warning(f"Health check '{result.check_name}' failed: {result.message}")
        except Exception as e:
            logger.error(f"Failed to update health check: {e}")

    async def update_multiple_health_checks(self, results: list[HealthCheckResult]) -> None:
        """
        Update multiple health checks at once.

        Args:
            results: List of health check results
        """
        for result in results:
            await self.update_health_check(result)

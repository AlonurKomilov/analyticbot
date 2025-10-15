"""
System metrics collection service.

This service handles system resource metrics like CPU, memory, disk usage.
"""

import logging

from core.services.bot.metrics.models import MetricDefinition, MetricType, SystemMetrics
from core.services.bot.metrics.protocols import MetricsBackendPort, SystemMetricsPort

logger = logging.getLogger(__name__)


class SystemMetricsService:
    """
    Service for collecting system resource metrics.

    This service orchestrates the collection of system-level metrics
    (CPU, memory, disk) using a SystemMetricsPort implementation.
    """

    def __init__(
        self,
        metrics_backend: MetricsBackendPort,
        system_monitor: SystemMetricsPort,
    ):
        """
        Initialize the system metrics service.

        Args:
            metrics_backend: Backend implementation for metrics storage
            system_monitor: System monitor implementation (e.g., PSUtil)
        """
        self.backend = metrics_backend
        self.monitor = system_monitor
        self._initialized = False

    def initialize_metrics(self) -> None:
        """Initialize system metrics."""
        if self._initialized:
            return

        self.backend.initialize_metric(
            MetricDefinition(
                name="system_memory_usage",
                metric_type=MetricType.GAUGE,
                description="System memory usage percentage",
            )
        )

        self.backend.initialize_metric(
            MetricDefinition(
                name="system_cpu_usage",
                metric_type=MetricType.GAUGE,
                description="System CPU usage percentage",
            )
        )

        self.backend.initialize_metric(
            MetricDefinition(
                name="system_disk_usage",
                metric_type=MetricType.GAUGE,
                description="System disk usage percentage",
                labels=["path"],
            )
        )

        self._initialized = True
        logger.info("System metrics initialized successfully")

    async def collect_and_update_system_metrics(self) -> SystemMetrics | None:
        """
        Collect and update all system metrics.

        Returns:
            SystemMetrics if collection successful, None otherwise
        """
        try:
            if not await self.monitor.is_available():
                logger.debug("System metrics not available")
                return None

            metrics = await self.monitor.collect_all_metrics()

            self.backend.set_gauge("system_memory_usage", metrics.memory_percent)
            self.backend.set_gauge("system_cpu_usage", metrics.cpu_percent)
            self.backend.set_gauge(
                "system_disk_usage",
                metrics.disk_percent,
                labels={"path": "/"},
            )

            # Update any additional custom metrics
            for name, value in metrics.additional_metrics.items():
                self.backend.set_gauge(name, value)

            return metrics

        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return None

    async def update_memory_usage(self) -> float | None:
        """
        Update memory usage metric.

        Returns:
            Memory usage percentage if successful, None otherwise
        """
        try:
            memory_percent = await self.monitor.get_memory_usage()
            self.backend.set_gauge("system_memory_usage", memory_percent)
            return memory_percent
        except Exception as e:
            logger.error(f"Failed to update memory usage: {e}")
            return None

    async def update_cpu_usage(self) -> float | None:
        """
        Update CPU usage metric.

        Returns:
            CPU usage percentage if successful, None otherwise
        """
        try:
            cpu_percent = await self.monitor.get_cpu_usage()
            self.backend.set_gauge("system_cpu_usage", cpu_percent)
            return cpu_percent
        except Exception as e:
            logger.error(f"Failed to update CPU usage: {e}")
            return None

    async def update_disk_usage(self, path: str = "/") -> float | None:
        """
        Update disk usage metric.

        Args:
            path: Filesystem path to check

        Returns:
            Disk usage percentage if successful, None otherwise
        """
        try:
            disk_percent = await self.monitor.get_disk_usage(path)
            self.backend.set_gauge(
                "system_disk_usage",
                disk_percent,
                labels={"path": path},
            )
            return disk_percent
        except Exception as e:
            logger.error(f"Failed to update disk usage: {e}")
            return None

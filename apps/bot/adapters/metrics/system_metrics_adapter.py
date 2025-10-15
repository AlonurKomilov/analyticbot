"""
System metrics adapter using psutil.

This adapter implements the SystemMetricsPort using the psutil library
for cross-platform system resource monitoring.
"""

import logging

from core.services.bot.metrics.models import SystemMetrics

logger = logging.getLogger(__name__)


class PSUtilSystemMetricsAdapter:
    """
    PSUtil implementation of SystemMetricsPort.

    This adapter uses the psutil library to collect system resource metrics
    (CPU, memory, disk) in a cross-platform manner.

    Gracefully handles cases where psutil is not installed.
    """

    def __init__(self):
        """Initialize the PSUtil adapter."""
        self._psutil_available = self._check_psutil_availability()
        if self._psutil_available:
            logger.info("PSUtilSystemMetricsAdapter initialized successfully")
        else:
            logger.warning(
                "psutil not available - system metrics will return default values"
            )

    def _check_psutil_availability(self) -> bool:
        """
        Check if psutil is available.

        Returns:
            True if psutil can be imported, False otherwise
        """
        try:
            import psutil  # noqa: F401

            return True
        except ImportError:
            return False

    async def get_memory_usage(self) -> float:
        """
        Get current memory usage percentage.

        Returns:
            Memory usage as percentage (0.0-100.0)
        """
        if not self._psutil_available:
            return 0.0

        try:
            import psutil

            return psutil.virtual_memory().percent
        except Exception as e:
            logger.error(f"Failed to get memory usage: {e}")
            return 0.0

    async def get_cpu_usage(self) -> float:
        """
        Get current CPU usage percentage.

        Returns:
            CPU usage as percentage (0.0-100.0)
        """
        if not self._psutil_available:
            return 0.0

        try:
            import psutil

            return psutil.cpu_percent(interval=1.0)
        except Exception as e:
            logger.error(f"Failed to get CPU usage: {e}")
            return 0.0

    async def get_disk_usage(self, path: str = "/") -> float:
        """
        Get disk usage percentage for a given path.

        Args:
            path: Filesystem path to check (default: root)

        Returns:
            Disk usage as percentage (0.0-100.0)
        """
        if not self._psutil_available:
            return 0.0

        try:
            import psutil

            return psutil.disk_usage(path).percent
        except Exception as e:
            logger.error(f"Failed to get disk usage for '{path}': {e}")
            return 0.0

    async def collect_all_metrics(self) -> SystemMetrics:
        """
        Collect all system metrics at once.

        Returns:
            SystemMetrics with current resource usage
        """
        memory = await self.get_memory_usage()
        cpu = await self.get_cpu_usage()
        disk = await self.get_disk_usage()

        return SystemMetrics(
            memory_percent=memory,
            cpu_percent=cpu,
            disk_percent=disk,
        )

    async def is_available(self) -> bool:
        """
        Check if system metrics collection is available.

        Returns:
            True if psutil is available, False otherwise
        """
        return self._psutil_available

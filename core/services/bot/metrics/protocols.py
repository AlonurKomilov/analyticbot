"""
Protocol definitions for metrics system.

These protocols define the interfaces that adapters must implement,
allowing the core business logic to remain independent of specific
metrics backends (Prometheus, StatsD, CloudWatch, etc.).
"""

from typing import Protocol

from core.services.bot.metrics.models import (
    MetricDefinition,
    SystemMetrics,
)


class MetricsBackendPort(Protocol):
    """
    Port for metrics backend implementation.

    This abstraction allows switching between different metrics systems:
    - Prometheus (Counter, Gauge, Histogram)
    - StatsD
    - CloudWatch
    - DataDog
    - Custom implementations

    All implementations must be thread-safe and support concurrent access.
    """

    def initialize_metric(self, definition: MetricDefinition) -> None:
        """
        Initialize a metric with the given definition.

        Args:
            definition: Metric definition with name, type, labels, etc.
        """
        ...

    def record_counter(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """
        Record a counter metric (monotonically increasing).

        Args:
            name: Metric name
            value: Value to increment by (default: 1.0)
            labels: Optional labels for the metric
        """
        ...

    def set_gauge(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """
        Set a gauge metric (can increase or decrease).

        Args:
            name: Metric name
            value: Current value to set
            labels: Optional labels for the metric
        """
        ...

    def record_histogram(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """
        Record a histogram observation.

        Args:
            name: Metric name
            value: Observed value
            labels: Optional labels for the metric
        """
        ...

    def get_metrics_output(self) -> str:
        """
        Get formatted metrics output for exposition.

        Returns:
            Formatted metrics string (format depends on backend)
        """
        ...

    def get_content_type(self) -> str:
        """
        Get the content type for metrics output.

        Returns:
            MIME type for the metrics format
        """
        ...


class SystemMetricsPort(Protocol):
    """
    Port for system metrics collection.

    Abstracts system resource monitoring, allowing different implementations:
    - PSUtil (cross-platform)
    - /proc filesystem (Linux)
    - Windows Performance Counters
    - macOS Activity Monitor API
    """

    async def get_memory_usage(self) -> float:
        """
        Get current memory usage percentage.

        Returns:
            Memory usage as percentage (0.0-100.0)
        """
        ...

    async def get_cpu_usage(self) -> float:
        """
        Get current CPU usage percentage.

        Returns:
            CPU usage as percentage (0.0-100.0)
        """
        ...

    async def get_disk_usage(self, path: str = "/") -> float:
        """
        Get disk usage percentage for a given path.

        Args:
            path: Filesystem path to check (default: root)

        Returns:
            Disk usage as percentage (0.0-100.0)
        """
        ...

    async def collect_all_metrics(self) -> SystemMetrics:
        """
        Collect all system metrics at once.

        Returns:
            SystemMetrics with current resource usage
        """
        ...

    async def is_available(self) -> bool:
        """
        Check if system metrics collection is available.

        Returns:
            True if metrics can be collected, False otherwise
        """
        ...


class DatabaseMetricsPort(Protocol):
    """
    Port for database metrics collection.

    Abstracts database-specific metrics like connection pools,
    query performance, etc.
    """

    async def get_active_connections(self) -> int:
        """
        Get number of active database connections.

        Returns:
            Count of active connections
        """
        ...

    async def get_pool_size(self) -> int:
        """
        Get database connection pool size.

        Returns:
            Total pool size
        """
        ...

    async def get_idle_connections(self) -> int:
        """
        Get number of idle connections in the pool.

        Returns:
            Count of idle connections
        """
        ...


class CeleryMetricsPort(Protocol):
    """
    Port for Celery metrics collection.

    Abstracts Celery-specific metrics like worker status,
    task queues, etc.
    """

    async def get_active_workers(self) -> int:
        """
        Get number of active Celery workers.

        Returns:
            Count of active workers
        """
        ...

    async def get_queue_length(self, queue_name: str = "default") -> int:
        """
        Get length of a specific Celery queue.

        Args:
            queue_name: Name of the queue (default: "default")

        Returns:
            Number of tasks in the queue
        """
        ...

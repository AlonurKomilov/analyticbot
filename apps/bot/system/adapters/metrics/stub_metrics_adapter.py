"""
Stub metrics adapters for testing.

These adapters provide testing implementations that record metrics
without requiring actual Prometheus or system monitoring libraries.
"""

import logging
from typing import Any

from core.services.bot.metrics.models import MetricDefinition, SystemMetrics

logger = logging.getLogger(__name__)


class StubMetricsAdapter:
    """
    Stub implementation of MetricsBackendPort for testing.

    This adapter records all metric operations in memory for
    verification in tests without requiring Prometheus.
    """

    def __init__(self):
        """Initialize the stub adapter."""
        self.initialized_metrics: list[MetricDefinition] = []
        self.counters: dict[str, float] = {}
        self.gauges: dict[str, float] = {}
        self.histograms: dict[str, list[float]] = {}
        self.labels_history: list[dict[str, Any]] = []

    def initialize_metric(self, definition: MetricDefinition) -> None:
        """Record metric initialization."""
        self.initialized_metrics.append(definition)

    def record_counter(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record counter increment."""
        key = f"{name}:{labels}" if labels else name
        self.counters[key] = self.counters.get(key, 0.0) + value
        if labels:
            self.labels_history.append({"metric": name, "labels": labels, "value": value})

    def set_gauge(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record gauge value."""
        key = f"{name}:{labels}" if labels else name
        self.gauges[key] = value
        if labels:
            self.labels_history.append({"metric": name, "labels": labels, "value": value})

    def record_histogram(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record histogram observation."""
        key = f"{name}:{labels}" if labels else name
        if key not in self.histograms:
            self.histograms[key] = []
        self.histograms[key].append(value)
        if labels:
            self.labels_history.append({"metric": name, "labels": labels, "value": value})

    def get_metrics_output(self) -> str:
        """Get formatted metrics output."""
        lines = ["# Stub Metrics Output"]
        lines.extend([f"counter {k} = {v}" for k, v in self.counters.items()])
        lines.extend([f"gauge {k} = {v}" for k, v in self.gauges.items()])
        for k, values in self.histograms.items():
            lines.append(f"histogram {k} = {values}")
        return "\n".join(lines)

    def get_content_type(self) -> str:
        """Get content type."""
        return "text/plain"

    def reset(self) -> None:
        """Reset all recorded metrics."""
        self.initialized_metrics.clear()
        self.counters.clear()
        self.gauges.clear()
        self.histograms.clear()
        self.labels_history.clear()


class StubSystemMetricsAdapter:
    """
    Stub implementation of SystemMetricsPort for testing.

    Returns configurable test values for system metrics.
    """

    def __init__(
        self,
        memory_percent: float = 50.0,
        cpu_percent: float = 25.0,
        disk_percent: float = 60.0,
    ):
        """
        Initialize the stub adapter with test values.

        Args:
            memory_percent: Memory usage percentage to return
            cpu_percent: CPU usage percentage to return
            disk_percent: Disk usage percentage to return
        """
        self.memory_percent = memory_percent
        self.cpu_percent = cpu_percent
        self.disk_percent = disk_percent
        self._available = True

    async def get_memory_usage(self) -> float:
        """Get test memory usage."""
        return self.memory_percent

    async def get_cpu_usage(self) -> float:
        """Get test CPU usage."""
        return self.cpu_percent

    async def get_disk_usage(self, path: str = "/") -> float:
        """Get test disk usage."""
        return self.disk_percent

    async def collect_all_metrics(self) -> SystemMetrics:
        """Collect all test metrics."""
        return SystemMetrics(
            memory_percent=self.memory_percent,
            cpu_percent=self.cpu_percent,
            disk_percent=self.disk_percent,
        )

    async def is_available(self) -> bool:
        """Check if stub is available."""
        return self._available

    def set_available(self, available: bool) -> None:
        """Set availability status."""
        self._available = available

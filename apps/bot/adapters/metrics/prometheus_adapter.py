"""
Prometheus metrics adapter.

This adapter implements the MetricsBackendPort using the Prometheus
client library, providing concrete metrics collection functionality.
"""

import logging
from typing import Any

from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Counter, Gauge, Histogram, generate_latest

from core.services.bot.metrics.models import MetricDefinition, MetricType

logger = logging.getLogger(__name__)


class PrometheusMetricsAdapter:
    """
    Prometheus implementation of MetricsBackendPort.

    This adapter wraps the prometheus_client library to provide
    metrics collection using Prometheus conventions.

    Features:
    - Counter metrics (monotonically increasing)
    - Gauge metrics (can increase/decrease)
    - Histogram metrics (observations with buckets)
    - Thread-safe operations
    - Custom CollectorRegistry support
    """

    def __init__(self, registry: CollectorRegistry | None = None):
        """
        Initialize the Prometheus adapter.

        Args:
            registry: Custom Prometheus registry (optional, creates new if None)
        """
        self.registry = registry or CollectorRegistry()
        self._counters: dict[str, Counter] = {}
        self._gauges: dict[str, Gauge] = {}
        self._histograms: dict[str, Histogram] = {}
        logger.info("PrometheusMetricsAdapter initialized")

    def initialize_metric(self, definition: MetricDefinition) -> None:
        """
        Initialize a metric with the given definition.

        Args:
            definition: Metric definition with name, type, labels, etc.
        """
        try:
            name = definition.name
            if definition.metric_type == MetricType.COUNTER:
                if name not in self._counters:
                    self._counters[name] = Counter(
                        name,
                        definition.description,
                        definition.labels,
                        registry=self.registry,
                    )
            elif definition.metric_type == MetricType.GAUGE:
                if name not in self._gauges:
                    self._gauges[name] = Gauge(
                        name,
                        definition.description,
                        definition.labels,
                        registry=self.registry,
                    )
            elif definition.metric_type == MetricType.HISTOGRAM:
                if name not in self._histograms:
                    buckets = definition.buckets or (
                        0.005,
                        0.01,
                        0.025,
                        0.05,
                        0.075,
                        0.1,
                        0.25,
                        0.5,
                        0.75,
                        1.0,
                        2.5,
                        5.0,
                        7.5,
                        10.0,
                    )
                    self._histograms[name] = Histogram(
                        name,
                        definition.description,
                        definition.labels,
                        buckets=buckets,
                        registry=self.registry,
                    )
            else:
                logger.warning(f"Unsupported metric type: {definition.metric_type}")
        except Exception as e:
            logger.error(f"Failed to initialize metric '{definition.name}': {e}")

    def record_counter(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """
        Record a counter metric.

        Args:
            name: Metric name
            value: Value to increment by (default: 1.0)
            labels: Optional labels for the metric
        """
        try:
            counter = self._counters.get(name)
            if not counter:
                logger.warning(f"Counter '{name}' not initialized")
                return

            if labels:
                counter.labels(**labels).inc(value)
            else:
                counter.inc(value)
        except Exception as e:
            logger.error(f"Failed to record counter '{name}': {e}")

    def set_gauge(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """
        Set a gauge metric.

        Args:
            name: Metric name
            value: Current value to set
            labels: Optional labels for the metric
        """
        try:
            gauge = self._gauges.get(name)
            if not gauge:
                logger.warning(f"Gauge '{name}' not initialized")
                return

            if labels:
                gauge.labels(**labels).set(value)
            else:
                gauge.set(value)
        except Exception as e:
            logger.error(f"Failed to set gauge '{name}': {e}")

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
        try:
            histogram = self._histograms.get(name)
            if not histogram:
                logger.warning(f"Histogram '{name}' not initialized")
                return

            if labels:
                histogram.labels(**labels).observe(value)
            else:
                histogram.observe(value)
        except Exception as e:
            logger.error(f"Failed to record histogram '{name}': {e}")

    def get_metrics_output(self) -> str:
        """
        Get formatted metrics output in Prometheus exposition format.

        Returns:
            Prometheus-formatted metrics string
        """
        try:
            return generate_latest(self.registry).decode("utf-8")
        except Exception as e:
            logger.error(f"Failed to generate metrics output: {e}")
            return ""

    def get_content_type(self) -> str:
        """
        Get the content type for Prometheus metrics.

        Returns:
            Prometheus content type
        """
        return CONTENT_TYPE_LATEST

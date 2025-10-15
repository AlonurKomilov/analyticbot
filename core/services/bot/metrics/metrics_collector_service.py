"""
Core metrics collection service.

This service orchestrates metrics collection across the application,
using protocol-based ports to remain independent of specific backends.
"""

import logging
from typing import Any

from core.services.bot.metrics.models import (
    CeleryTaskMetric,
    DatabaseQueryMetric,
    HTTPRequestMetric,
    MetricDefinition,
    MetricType,
    TelegramAPIMetric,
    TelegramUpdateMetric,
)
from core.services.bot.metrics.protocols import MetricsBackendPort

logger = logging.getLogger(__name__)


class MetricsCollectorService:
    """
    Core service for collecting and recording metrics.

    This service provides a clean, protocol-based API for recording
    various types of metrics throughout the application. It delegates
    the actual storage/exposition to a MetricsBackendPort implementation.

    Benefits:
    - Backend-agnostic (works with Prometheus, StatsD, etc.)
    - Type-safe metric recording
    - Structured metric models
    - Easy to test with mock backends
    """

    def __init__(self, metrics_backend: MetricsBackendPort):
        """
        Initialize the metrics collector.

        Args:
            metrics_backend: Backend implementation for metrics storage
        """
        self.backend = metrics_backend
        self._initialized = False

    def initialize_metrics(self) -> None:
        """Initialize all application metrics."""
        if self._initialized:
            return

        # App info metric
        self.backend.initialize_metric(
            MetricDefinition(
                name="app_info",
                metric_type=MetricType.GAUGE,
                description="Application information",
                labels=["version", "environment"],
            )
        )

        # HTTP metrics
        self.backend.initialize_metric(
            MetricDefinition(
                name="http_requests_total",
                metric_type=MetricType.COUNTER,
                description="Total HTTP requests",
                labels=["method", "endpoint", "status"],
            )
        )
        self.backend.initialize_metric(
            MetricDefinition(
                name="http_request_duration_seconds",
                metric_type=MetricType.HISTOGRAM,
                description="HTTP request duration in seconds",
                labels=["method", "endpoint"],
                buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            )
        )

        # Telegram API metrics
        self.backend.initialize_metric(
            MetricDefinition(
                name="telegram_api_requests_total",
                metric_type=MetricType.COUNTER,
                description="Total Telegram API requests",
                labels=["method", "status"],
            )
        )
        self.backend.initialize_metric(
            MetricDefinition(
                name="telegram_api_request_duration_seconds",
                metric_type=MetricType.HISTOGRAM,
                description="Telegram API request duration",
                labels=["method"],
                buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0],
            )
        )
        self.backend.initialize_metric(
            MetricDefinition(
                name="telegram_updates_processed_total",
                metric_type=MetricType.COUNTER,
                description="Total Telegram updates processed",
                labels=["update_type", "status"],
            )
        )

        # Database metrics
        self.backend.initialize_metric(
            MetricDefinition(
                name="database_connections_active",
                metric_type=MetricType.GAUGE,
                description="Active database connections",
            )
        )
        self.backend.initialize_metric(
            MetricDefinition(
                name="database_query_duration_seconds",
                metric_type=MetricType.HISTOGRAM,
                description="Database query duration",
                labels=["operation"],
                buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
            )
        )
        self.backend.initialize_metric(
            MetricDefinition(
                name="database_queries_total",
                metric_type=MetricType.COUNTER,
                description="Total database queries",
                labels=["operation", "status"],
            )
        )

        # Celery task metrics
        self.backend.initialize_metric(
            MetricDefinition(
                name="celery_tasks_total",
                metric_type=MetricType.COUNTER,
                description="Total Celery tasks",
                labels=["task_name", "status"],
            )
        )
        self.backend.initialize_metric(
            MetricDefinition(
                name="celery_task_duration_seconds",
                metric_type=MetricType.HISTOGRAM,
                description="Celery task duration",
                labels=["task_name"],
                buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 300.0],
            )
        )
        self.backend.initialize_metric(
            MetricDefinition(
                name="celery_workers_active",
                metric_type=MetricType.GAUGE,
                description="Active Celery workers",
            )
        )

        self._initialized = True
        logger.info("Metrics initialized successfully")

    async def record_http_request(self, metric: HTTPRequestMetric) -> None:
        """
        Record an HTTP request metric.

        Args:
            metric: HTTP request metric data
        """
        try:
            self.backend.record_counter(
                "http_requests_total",
                value=1.0,
                labels=metric.to_labels(),
            )
            self.backend.record_histogram(
                "http_request_duration_seconds",
                value=metric.duration,
                labels={"method": metric.method, "endpoint": metric.endpoint},
            )
        except Exception as e:
            logger.error(f"Failed to record HTTP request metric: {e}")

    async def record_telegram_api_request(self, metric: TelegramAPIMetric) -> None:
        """
        Record a Telegram API request metric.

        Args:
            metric: Telegram API metric data
        """
        try:
            self.backend.record_counter(
                "telegram_api_requests_total",
                value=1.0,
                labels=metric.to_labels(),
            )
            self.backend.record_histogram(
                "telegram_api_request_duration_seconds",
                value=metric.duration,
                labels={"method": metric.method},
            )
        except Exception as e:
            logger.error(f"Failed to record Telegram API metric: {e}")

    async def record_telegram_update(self, metric: TelegramUpdateMetric) -> None:
        """
        Record a Telegram update processing metric.

        Args:
            metric: Telegram update metric data
        """
        try:
            self.backend.record_counter(
                "telegram_updates_processed_total",
                value=1.0,
                labels=metric.to_labels(),
            )
        except Exception as e:
            logger.error(f"Failed to record Telegram update metric: {e}")

    async def record_database_query(self, metric: DatabaseQueryMetric) -> None:
        """
        Record a database query metric.

        Args:
            metric: Database query metric data
        """
        try:
            self.backend.record_counter(
                "database_queries_total",
                value=1.0,
                labels=metric.to_labels(),
            )
            self.backend.record_histogram(
                "database_query_duration_seconds",
                value=metric.duration,
                labels={"operation": metric.operation},
            )
        except Exception as e:
            logger.error(f"Failed to record database query metric: {e}")

    async def update_database_connections(self, count: int) -> None:
        """
        Update active database connections gauge.

        Args:
            count: Number of active connections
        """
        try:
            self.backend.set_gauge("database_connections_active", float(count))
        except Exception as e:
            logger.error(f"Failed to update database connections: {e}")

    async def record_celery_task(self, metric: CeleryTaskMetric) -> None:
        """
        Record a Celery task execution metric.

        Args:
            metric: Celery task metric data
        """
        try:
            self.backend.record_counter(
                "celery_tasks_total",
                value=1.0,
                labels=metric.to_labels(),
            )
            self.backend.record_histogram(
                "celery_task_duration_seconds",
                value=metric.duration,
                labels={"task_name": metric.task_name},
            )
        except Exception as e:
            logger.error(f"Failed to record Celery task metric: {e}")

    async def update_celery_workers(self, count: int) -> None:
        """
        Update active Celery workers gauge.

        Args:
            count: Number of active workers
        """
        try:
            self.backend.set_gauge("celery_workers_active", float(count))
        except Exception as e:
            logger.error(f"Failed to update Celery workers: {e}")

    def set_app_info(self, version: str, environment: str) -> None:
        """
        Set application info metric.

        Args:
            version: Application version
            environment: Deployment environment
        """
        try:
            self.backend.set_gauge(
                "app_info",
                1.0,
                labels={"version": version, "environment": environment},
            )
        except Exception as e:
            logger.error(f"Failed to set app info: {e}")

    def get_metrics_output(self) -> str:
        """
        Get formatted metrics output for exposition.

        Returns:
            Formatted metrics string
        """
        return self.backend.get_metrics_output()

    def get_content_type(self) -> str:
        """
        Get content type for metrics output.

        Returns:
            MIME type string
        """
        return self.backend.get_content_type()

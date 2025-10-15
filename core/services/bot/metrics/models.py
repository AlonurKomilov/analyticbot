"""
Domain models for metrics system.

These models represent the core business concepts for metrics collection,
completely independent of any specific metrics backend (Prometheus, StatsD, etc.).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MetricType(str, Enum):
    """Type of metric."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class HTTPRequestMetric:
    """HTTP request metric data."""

    method: str
    endpoint: str
    status_code: int
    duration: float
    labels: dict[str, str] = field(default_factory=dict)

    def to_labels(self) -> dict[str, str]:
        """Convert to metric labels."""
        return {
            "method": self.method,
            "endpoint": self.endpoint,
            "status": str(self.status_code),
            **self.labels,
        }


@dataclass
class TelegramAPIMetric:
    """Telegram API call metric."""

    method: str
    status: str
    duration: float
    labels: dict[str, str] = field(default_factory=dict)

    def to_labels(self) -> dict[str, str]:
        """Convert to metric labels."""
        return {
            "method": self.method,
            "status": self.status,
            **self.labels,
        }


@dataclass
class TelegramUpdateMetric:
    """Telegram update processing metric."""

    update_type: str
    status: str
    labels: dict[str, str] = field(default_factory=dict)

    def to_labels(self) -> dict[str, str]:
        """Convert to metric labels."""
        return {
            "update_type": self.update_type,
            "status": self.status,
            **self.labels,
        }


@dataclass
class DatabaseQueryMetric:
    """Database query metric."""

    operation: str
    status: str
    duration: float
    labels: dict[str, str] = field(default_factory=dict)

    def to_labels(self) -> dict[str, str]:
        """Convert to metric labels."""
        return {
            "operation": self.operation,
            "status": self.status,
            **self.labels,
        }


@dataclass
class CeleryTaskMetric:
    """Celery task execution metric."""

    task_name: str
    status: str
    duration: float
    labels: dict[str, str] = field(default_factory=dict)

    def to_labels(self) -> dict[str, str]:
        """Convert to metric labels."""
        return {
            "task_name": self.task_name,
            "status": self.status,
            **self.labels,
        }


@dataclass
class BusinessMetrics:
    """Business metrics snapshot."""

    channels_count: int = 0
    users_count: int = 0
    scheduled_posts_count: int = 0
    additional_metrics: dict[str, int | float] = field(default_factory=dict)


@dataclass
class SystemMetrics:
    """System resource metrics."""

    memory_percent: float
    cpu_percent: float
    disk_percent: float = 0.0
    additional_metrics: dict[str, float] = field(default_factory=dict)


@dataclass
class HealthCheckResult:
    """Health check result."""

    check_name: str
    is_healthy: bool
    message: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def status_value(self) -> float:
        """Get numeric status value (1.0 = healthy, 0.0 = unhealthy)."""
        return 1.0 if self.is_healthy else 0.0


@dataclass
class MetricDefinition:
    """Definition of a metric."""

    name: str
    metric_type: MetricType
    description: str
    labels: list[str] = field(default_factory=list)
    buckets: list[float] | None = None  # For histograms


@dataclass
class MetricValue:
    """A recorded metric value."""

    name: str
    value: float
    labels: dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.COUNTER

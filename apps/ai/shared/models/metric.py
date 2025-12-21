"""Metric models for AI Worker system"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class MetricType(str, Enum):
    """Types of metrics"""

    PERFORMANCE = "performance"
    RESOURCE = "resource"
    HEALTH = "health"
    BUSINESS = "business"
    ERROR = "error"
    CUSTOM = "custom"


@dataclass
class Metric:
    """A single metric measurement"""

    # Identity
    metric_name: str
    metric_type: MetricType
    worker_name: str | None = None

    # Value
    value: float = 0.0
    unit: str = ""

    # Context
    dimensions: dict[str, str] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)

    # Timestamp
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Metadata
    source: str = "ai_worker"
    aggregation_period_seconds: int | None = None


@dataclass
class WorkerMetrics:
    """Collection of metrics for a worker"""

    worker_name: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Resource metrics
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    memory_percent: float = 0.0
    disk_usage_mb: float = 0.0

    # Performance metrics
    requests_per_second: float = 0.0
    avg_response_time_ms: float = 0.0
    throughput: float = 0.0

    # Error metrics
    error_rate: float = 0.0
    errors_count: int = 0
    warnings_count: int = 0

    # Health metrics
    uptime_seconds: float = 0.0
    health_score: float = 100.0  # 0-100
    availability_percent: float = 100.0

    # Custom metrics
    custom_metrics: dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricThreshold:
    """Threshold for metric alerting"""

    metric_name: str
    threshold_type: str  # 'above', 'below', 'equal'
    threshold_value: float
    severity: str  # 'info', 'warning', 'critical'
    action_required: str | None = None

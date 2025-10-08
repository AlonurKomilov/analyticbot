"""
Monitoring Protocols for Adaptive Learning
==========================================

Defines interfaces for model performance monitoring and tracking.
These protocols ensure clean separation of concerns and dependency injection.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class PerformanceMetricType(Enum):
    """Types of performance metrics to monitor"""

    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    MEMORY_USAGE = "memory_usage"
    GPU_UTILIZATION = "gpu_utilization"
    ERROR_RATE = "error_rate"


class AlertSeverity(Enum):
    """Alert severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PerformanceMetric:
    """Performance metric data structure"""

    metric_type: PerformanceMetricType
    value: float
    timestamp: datetime
    model_id: str
    service_name: str
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass
class PerformanceMetrics:
    """Aggregate performance metrics data structure"""

    model_id: str
    timestamp: datetime
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    avg_latency_ms: float = 0.0
    throughput_rps: float = 0.0
    error_rate: float = 0.0
    memory_usage_mb: float = 0.0
    gpu_utilization: float = 0.0
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass
class PerformanceAlert:
    """Performance alert data structure"""

    alert_id: str
    severity: AlertSeverity
    metric_type: PerformanceMetricType
    current_value: float
    threshold_value: float
    model_id: str
    service_name: str
    message: str
    timestamp: datetime
    resolved: bool = False


class MonitoringProtocol(ABC):
    """
    Protocol for model performance monitoring services.

    This interface defines the contract for monitoring model performance,
    tracking metrics, and generating alerts when thresholds are exceeded.
    """

    @abstractmethod
    async def track_metric(self, metric: PerformanceMetric) -> bool:
        """
        Track a performance metric

        Args:
            metric: Performance metric to track

        Returns:
            True if metric was successfully tracked
        """

    @abstractmethod
    async def get_metrics(
        self,
        model_id: str,
        metric_types: list[PerformanceMetricType] | None = None,
        time_range: tuple[datetime, datetime] | None = None,
    ) -> list[PerformanceMetric]:
        """
        Retrieve performance metrics for a model

        Args:
            model_id: ID of the model to get metrics for
            metric_types: Optional filter for specific metric types
            time_range: Optional time range filter (start, end)

        Returns:
            List of performance metrics
        """

    @abstractmethod
    async def set_alert_threshold(
        self,
        model_id: str,
        metric_type: PerformanceMetricType,
        threshold_value: float,
        severity: AlertSeverity,
    ) -> bool:
        """
        Set alert threshold for a metric

        Args:
            model_id: ID of the model
            metric_type: Type of metric to monitor
            threshold_value: Threshold value that triggers alert
            severity: Severity level of the alert

        Returns:
            True if threshold was successfully set
        """

    @abstractmethod
    async def get_active_alerts(
        self, model_id: str | None = None, severity: AlertSeverity | None = None
    ) -> list[PerformanceAlert]:
        """
        Get active performance alerts

        Args:
            model_id: Optional filter for specific model
            severity: Optional filter for alert severity

        Returns:
            List of active alerts
        """

    @abstractmethod
    async def resolve_alert(self, alert_id: str) -> bool:
        """
        Mark an alert as resolved

        Args:
            alert_id: ID of the alert to resolve

        Returns:
            True if alert was successfully resolved
        """

    @abstractmethod
    async def get_model_health_status(self, model_id: str) -> dict[str, Any]:
        """
        Get overall health status of a model

        Args:
            model_id: ID of the model

        Returns:
            Dictionary containing health status information
        """


class PerformanceTrackerProtocol(ABC):
    """
    Protocol for tracking and analyzing performance trends.

    This interface defines methods for analyzing performance over time
    and detecting performance degradation patterns.
    """

    @abstractmethod
    async def analyze_performance_trend(
        self,
        model_id: str,
        metric_type: PerformanceMetricType,
        time_window: int,  # hours
    ) -> dict[str, Any]:
        """
        Analyze performance trend for a metric

        Args:
            model_id: ID of the model
            metric_type: Type of metric to analyze
            time_window: Time window in hours to analyze

        Returns:
            Dictionary containing trend analysis results
        """

    @abstractmethod
    async def detect_performance_degradation(
        self, model_id: str, sensitivity: float = 0.1
    ) -> dict[str, Any]:
        """
        Detect performance degradation

        Args:
            model_id: ID of the model
            sensitivity: Sensitivity threshold for detection

        Returns:
            Dictionary containing degradation detection results
        """

    @abstractmethod
    async def get_performance_summary(
        self, model_id: str, time_range: tuple[datetime, datetime]
    ) -> dict[str, Any]:
        """
        Get performance summary for a time range

        Args:
            model_id: ID of the model
            time_range: Time range (start, end) for summary

        Returns:
            Dictionary containing performance summary
        """


class MonitoringInfrastructureProtocol(ABC):
    """
    Protocol for monitoring infrastructure services.

    This interface defines methods for setting up monitoring infrastructure,
    configuring storage, and managing monitoring resources.
    """

    @abstractmethod
    async def initialize_monitoring(self, config: dict[str, Any]) -> bool:
        """
        Initialize monitoring infrastructure

        Args:
            config: Configuration dictionary

        Returns:
            True if initialization was successful
        """

    @abstractmethod
    async def get_monitoring_status(self) -> dict[str, Any]:
        """
        Get status of monitoring infrastructure

        Returns:
            Dictionary containing monitoring status
        """

    @abstractmethod
    async def cleanup_old_metrics(self, retention_days: int) -> int:
        """
        Clean up old metrics beyond retention period

        Args:
            retention_days: Number of days to retain metrics

        Returns:
            Number of metrics cleaned up
        """


class MonitoringServiceProtocol(ABC):
    """
    Protocol for performance monitoring services.

    This interface defines the contract for high-level monitoring services
    that coordinate between monitoring protocols and infrastructure.
    """

    @abstractmethod
    async def start_monitoring(self, model_ids: list[str]) -> bool:
        """
        Start monitoring specified models

        Args:
            model_ids: List of model IDs to monitor

        Returns:
            True if monitoring started successfully
        """

    @abstractmethod
    async def stop_monitoring(self, model_ids: list[str] | None = None) -> bool:
        """
        Stop monitoring specified models or all models

        Args:
            model_ids: List of model IDs to stop monitoring, None for all

        Returns:
            True if monitoring stopped successfully
        """

    @abstractmethod
    async def record_performance_metric(self, metric: PerformanceMetric) -> bool:
        """
        Record a performance metric

        Args:
            metric: Performance metric to record

        Returns:
            True if metric was recorded successfully
        """

    @abstractmethod
    async def get_performance_summary(
        self, model_id: str, time_range: tuple[datetime, datetime] | None = None
    ) -> dict[str, Any]:
        """
        Get performance summary for a model

        Args:
            model_id: ID of the model
            time_range: Time range for summary

        Returns:
            Dictionary containing performance summary
        """

    @abstractmethod
    async def detect_performance_issues(self, model_id: str) -> list[dict[str, Any]]:
        """
        Detect performance issues for a model

        Args:
            model_id: ID of the model to check

        Returns:
            List of detected issues
        """

    @abstractmethod
    async def get_current_metrics(self, model_id: str) -> Optional["PerformanceMetrics"]:
        """
        Get current performance metrics for a model

        Args:
            model_id: ID of the model

        Returns:
            Current performance metrics or None if not available
        """

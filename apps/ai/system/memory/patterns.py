"""
Pattern Detection System
========================

Detects patterns in metrics and worker behavior for proactive management.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from apps.ai.system.memory.metrics import MetricsStore, get_metrics_store

logger = logging.getLogger(__name__)


class PatternType(str, Enum):
    """Types of patterns that can be detected"""

    SPIKE = "spike"  # Sudden increase
    DROP = "drop"  # Sudden decrease
    TREND_UP = "trend_up"  # Gradual increase
    TREND_DOWN = "trend_down"  # Gradual decrease
    CYCLIC = "cyclic"  # Repeating pattern
    ANOMALY = "anomaly"  # Unusual behavior
    THRESHOLD_BREACH = "threshold"  # Crossed threshold


class PatternSeverity(str, Enum):
    """Severity levels for patterns"""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class DetectedPattern:
    """A detected pattern"""

    pattern_id: str
    pattern_type: PatternType
    severity: PatternSeverity
    metric_name: str
    description: str
    detected_at: datetime = field(default_factory=datetime.utcnow)

    # Pattern details
    current_value: float = 0.0
    baseline_value: float = 0.0
    change_percent: float = 0.0

    # Context
    labels: dict[str, str] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "pattern_id": self.pattern_id,
            "pattern_type": self.pattern_type.value,
            "severity": self.severity.value,
            "metric_name": self.metric_name,
            "description": self.description,
            "detected_at": self.detected_at.isoformat(),
            "current_value": self.current_value,
            "baseline_value": self.baseline_value,
            "change_percent": self.change_percent,
            "labels": self.labels,
            "recommendations": self.recommendations,
        }


class PatternDetector:
    """
    Detects patterns in metrics and worker behavior.

    Patterns detected:
    - Spikes: Sudden increases in CPU, memory, errors
    - Drops: Sudden decreases in throughput, health
    - Trends: Gradual changes over time
    - Anomalies: Unusual deviations from baseline
    - Threshold breaches: Values crossing critical limits

    Usage:
        detector = PatternDetector()
        patterns = detector.analyze_worker("mtproto_worker")
    """

    def __init__(self, metrics_store: MetricsStore | None = None):
        self.metrics = metrics_store or get_metrics_store()

        # Configurable thresholds
        self.thresholds = {
            "cpu_percent": {"warning": 70, "critical": 85},
            "memory_percent": {"warning": 75, "critical": 90},
            "error_rate": {"warning": 0.05, "critical": 0.10},
            "response_time_ms": {"warning": 1000, "critical": 3000},
        }

        # Spike/drop detection settings
        self.spike_threshold_percent = 50  # 50% change = spike
        self.trend_threshold_percent = 20  # 20% change over period = trend

        logger.info("🔍 Pattern Detector initialized")

    def analyze_metric(
        self,
        metric_name: str,
        window_hours: int = 24,
    ) -> list[DetectedPattern]:
        """
        Analyze a metric for patterns.

        Args:
            metric_name: Metric to analyze
            window_hours: Time window for analysis

        Returns:
            List of detected patterns
        """
        patterns = []

        # Get metric data
        aggregate = self.metrics.get_aggregate(metric_name, hours=window_hours)

        if aggregate["count"] < 10:
            return patterns  # Not enough data

        # Check for threshold breaches
        threshold_patterns = self._check_thresholds(metric_name, aggregate)
        patterns.extend(threshold_patterns)

        # Check for anomalies
        anomaly_result = self.metrics.detect_anomaly(metric_name, window_hours=window_hours)
        if anomaly_result.get("has_anomaly"):
            patterns.append(
                DetectedPattern(
                    pattern_id=f"anomaly_{metric_name}_{datetime.utcnow().timestamp()}",
                    pattern_type=PatternType.ANOMALY,
                    severity=PatternSeverity.WARNING,
                    metric_name=metric_name,
                    description=f"Anomaly detected in {metric_name}",
                    current_value=anomaly_result.get("recent_avg", 0),
                    baseline_value=anomaly_result.get("baseline", {}).get("avg", 0),
                    recommendations=[
                        "Investigate recent changes",
                        "Check for unusual activity",
                    ],
                )
            )

        # Check for trends
        trend_patterns = self._detect_trends(metric_name, window_hours)
        patterns.extend(trend_patterns)

        return patterns

    def _check_thresholds(
        self,
        metric_name: str,
        aggregate: dict[str, Any],
    ) -> list[DetectedPattern]:
        """Check if metric breaches thresholds"""
        patterns = []

        # Extract metric type from name (e.g., "worker.cpu_percent" -> "cpu_percent")
        metric_type = metric_name.split(".")[-1]

        if metric_type not in self.thresholds:
            return patterns

        thresholds = self.thresholds[metric_type]
        latest = aggregate.get("latest", 0)

        if latest >= thresholds.get("critical", float("inf")):
            patterns.append(
                DetectedPattern(
                    pattern_id=f"threshold_{metric_name}_{datetime.utcnow().timestamp()}",
                    pattern_type=PatternType.THRESHOLD_BREACH,
                    severity=PatternSeverity.CRITICAL,
                    metric_name=metric_name,
                    description=f"{metric_name} critically high: {latest:.1f}",
                    current_value=latest,
                    baseline_value=thresholds["critical"],
                    recommendations=[
                        "Immediate attention required",
                        "Consider scaling or reducing load",
                        "Check for resource leaks",
                    ],
                )
            )
        elif latest >= thresholds.get("warning", float("inf")):
            patterns.append(
                DetectedPattern(
                    pattern_id=f"threshold_{metric_name}_{datetime.utcnow().timestamp()}",
                    pattern_type=PatternType.THRESHOLD_BREACH,
                    severity=PatternSeverity.WARNING,
                    metric_name=metric_name,
                    description=f"{metric_name} elevated: {latest:.1f}",
                    current_value=latest,
                    baseline_value=thresholds["warning"],
                    recommendations=[
                        "Monitor closely",
                        "Consider preemptive scaling",
                    ],
                )
            )

        return patterns

    def _detect_trends(
        self,
        metric_name: str,
        window_hours: int,
    ) -> list[DetectedPattern]:
        """Detect upward or downward trends"""
        patterns = []

        now = datetime.utcnow()

        # Compare first half vs second half of window
        first_half = self.metrics.query(
            metric_name,
            start_time=now - timedelta(hours=window_hours),
            end_time=now - timedelta(hours=window_hours // 2),
        )

        second_half = self.metrics.query(
            metric_name,
            start_time=now - timedelta(hours=window_hours // 2),
        )

        if len(first_half) < 5 or len(second_half) < 5:
            return patterns

        first_avg = sum(p.value for p in first_half) / len(first_half)
        second_avg = sum(p.value for p in second_half) / len(second_half)

        if first_avg == 0:
            return patterns

        change_percent = ((second_avg - first_avg) / first_avg) * 100

        if change_percent > self.trend_threshold_percent:
            patterns.append(
                DetectedPattern(
                    pattern_id=f"trend_up_{metric_name}_{datetime.utcnow().timestamp()}",
                    pattern_type=PatternType.TREND_UP,
                    severity=PatternSeverity.INFO,
                    metric_name=metric_name,
                    description=f"{metric_name} trending up: +{change_percent:.1f}%",
                    current_value=second_avg,
                    baseline_value=first_avg,
                    change_percent=change_percent,
                    recommendations=[
                        "Monitor for continued increase",
                        "Consider capacity planning",
                    ],
                )
            )
        elif change_percent < -self.trend_threshold_percent:
            patterns.append(
                DetectedPattern(
                    pattern_id=f"trend_down_{metric_name}_{datetime.utcnow().timestamp()}",
                    pattern_type=PatternType.TREND_DOWN,
                    severity=PatternSeverity.INFO,
                    metric_name=metric_name,
                    description=f"{metric_name} trending down: {change_percent:.1f}%",
                    current_value=second_avg,
                    baseline_value=first_avg,
                    change_percent=change_percent,
                    recommendations=[
                        "Verify this is expected behavior",
                        "Check for service issues if unexpected",
                    ],
                )
            )

        return patterns

    def analyze_worker(
        self,
        worker_name: str,
        window_hours: int = 24,
    ) -> list[DetectedPattern]:
        """
        Analyze all metrics for a specific worker.

        Args:
            worker_name: Worker to analyze
            window_hours: Time window

        Returns:
            List of detected patterns
        """
        patterns = []

        # Standard worker metrics to check
        metric_suffixes = [
            "cpu_percent",
            "memory_percent",
            "tasks_processed",
            "errors_count",
            "response_time_ms",
        ]

        for suffix in metric_suffixes:
            metric_name = f"worker.{worker_name}.{suffix}"
            worker_patterns = self.analyze_metric(metric_name, window_hours)

            # Add worker label to patterns
            for pattern in worker_patterns:
                pattern.labels["worker"] = worker_name

            patterns.extend(worker_patterns)

        return patterns

    def analyze_system(self, window_hours: int = 24) -> list[DetectedPattern]:
        """
        Analyze system-wide metrics.

        Returns:
            List of detected patterns
        """
        patterns = []

        # System metrics
        system_metrics = [
            "system.cpu_percent",
            "system.memory_percent",
            "system.disk_percent",
        ]

        for metric_name in system_metrics:
            patterns.extend(self.analyze_metric(metric_name, window_hours))

        return patterns

    def get_summary(self, window_hours: int = 24) -> dict[str, Any]:
        """
        Get summary of all detected patterns.

        Returns:
            Summary of patterns by type and severity
        """
        all_metrics = self.metrics.list_metrics()
        all_patterns = []

        for metric_name in all_metrics:
            all_patterns.extend(self.analyze_metric(metric_name, window_hours))

        # Summarize by type and severity
        by_type = {}
        by_severity = {}

        for pattern in all_patterns:
            type_key = pattern.pattern_type.value
            sev_key = pattern.severity.value

            by_type[type_key] = by_type.get(type_key, 0) + 1
            by_severity[sev_key] = by_severity.get(sev_key, 0) + 1

        return {
            "total_patterns": len(all_patterns),
            "by_type": by_type,
            "by_severity": by_severity,
            "critical_count": by_severity.get("critical", 0),
            "warning_count": by_severity.get("warning", 0),
            "patterns": [p.to_dict() for p in all_patterns],
            "analyzed_at": datetime.utcnow().isoformat(),
        }


def get_pattern_detector() -> PatternDetector:
    """Get pattern detector instance"""
    return PatternDetector()

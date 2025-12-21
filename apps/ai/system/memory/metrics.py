"""
Metrics Store
=============

Time-series storage for worker and system metrics.
Used for pattern detection and analysis.
"""

import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class MetricDataPoint:
    """Single metric data point"""
    metric_name: str
    value: float
    timestamp: datetime
    labels: dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "metric_name": self.metric_name,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "labels": self.labels,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MetricDataPoint":
        return cls(
            metric_name=data["metric_name"],
            value=data["value"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            labels=data.get("labels", {}),
        )


class MetricsStore:
    """
    Time-series store for metrics data.
    
    Features:
    - Store metric data points with labels
    - Query by metric name and time range
    - Calculate aggregations (avg, min, max)
    - Detect anomalies (values outside bounds)
    
    Uses file-based storage with rotation.
    """
    
    _instance: "MetricsStore | None" = None
    
    def __new__(cls, storage_path: str | None = None) -> "MetricsStore":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, storage_path: str | None = None):
        if self._initialized:
            return
        
        self._storage_path = Path(storage_path or "data/ai_metrics")
        self._storage_path.mkdir(parents=True, exist_ok=True)
        
        # In-memory buffer for recent metrics
        self._buffer: dict[str, list[MetricDataPoint]] = defaultdict(list)
        self._buffer_max_size = 1000  # Per metric
        
        # Aggregated data
        self._hourly_aggregates: dict[str, dict[str, dict[str, float]]] = defaultdict(
            lambda: defaultdict(dict)
        )
        
        self._load_recent()
        self._initialized = True
        
        logger.info("📊 Metrics Store initialized")
    
    def _get_file_path(self, date: datetime) -> Path:
        """Get file path for a specific date"""
        return self._storage_path / f"metrics_{date.strftime('%Y%m%d')}.json"
    
    def _load_recent(self, days: int = 1):
        """Load recent metrics from disk"""
        now = datetime.utcnow()
        
        for i in range(days):
            date = now - timedelta(days=i)
            file_path = self._get_file_path(date)
            
            if file_path.exists():
                try:
                    with open(file_path, "r") as f:
                        data = json.load(f)
                    
                    for point_data in data:
                        point = MetricDataPoint.from_dict(point_data)
                        self._buffer[point.metric_name].append(point)
                    
                except Exception as e:
                    logger.error(f"Failed to load metrics from {file_path}: {e}")
    
    def _save_to_disk(self):
        """Save today's metrics to disk"""
        today = datetime.utcnow()
        file_path = self._get_file_path(today)
        
        # Collect today's points
        cutoff = today.replace(hour=0, minute=0, second=0, microsecond=0)
        today_points = []
        
        for metric_name, points in self._buffer.items():
            for point in points:
                if point.timestamp >= cutoff:
                    today_points.append(point.to_dict())
        
        try:
            with open(file_path, "w") as f:
                json.dump(today_points, f)
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
    
    def record(
        self,
        metric_name: str,
        value: float,
        labels: dict[str, str] | None = None,
        timestamp: datetime | None = None,
    ) -> MetricDataPoint:
        """
        Record a metric data point.
        
        Args:
            metric_name: Name of the metric (e.g., "worker.cpu_percent")
            value: Metric value
            labels: Optional labels (e.g., {"worker": "mtproto"})
            timestamp: Optional timestamp (defaults to now)
            
        Returns:
            Created MetricDataPoint
        """
        point = MetricDataPoint(
            metric_name=metric_name,
            value=value,
            timestamp=timestamp or datetime.utcnow(),
            labels=labels or {},
        )
        
        # Add to buffer
        self._buffer[metric_name].append(point)
        
        # Trim buffer if needed
        if len(self._buffer[metric_name]) > self._buffer_max_size:
            self._buffer[metric_name] = self._buffer[metric_name][-self._buffer_max_size:]
        
        # Update hourly aggregate
        hour_key = point.timestamp.strftime("%Y%m%d%H")
        self._update_aggregate(metric_name, hour_key, value)
        
        return point
    
    def _update_aggregate(self, metric_name: str, hour_key: str, value: float):
        """Update hourly aggregate"""
        agg = self._hourly_aggregates[metric_name][hour_key]
        
        if "count" not in agg:
            agg["count"] = 0
            agg["sum"] = 0.0
            agg["min"] = value
            agg["max"] = value
        
        agg["count"] += 1
        agg["sum"] += value
        agg["min"] = min(agg["min"], value)
        agg["max"] = max(agg["max"], value)
        agg["avg"] = agg["sum"] / agg["count"]
    
    def query(
        self,
        metric_name: str,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        labels: dict[str, str] | None = None,
        limit: int = 1000,
    ) -> list[MetricDataPoint]:
        """
        Query metric data points.
        
        Args:
            metric_name: Metric to query
            start_time: Start of time range
            end_time: End of time range
            labels: Filter by labels
            limit: Maximum points to return
            
        Returns:
            List of MetricDataPoints
        """
        points = self._buffer.get(metric_name, [])
        results = []
        
        for point in reversed(points):
            # Time filter
            if start_time and point.timestamp < start_time:
                continue
            if end_time and point.timestamp > end_time:
                continue
            
            # Label filter
            if labels:
                match = all(
                    point.labels.get(k) == v
                    for k, v in labels.items()
                )
                if not match:
                    continue
            
            results.append(point)
            if len(results) >= limit:
                break
        
        return list(reversed(results))
    
    def get_aggregate(
        self,
        metric_name: str,
        hours: int = 24,
    ) -> dict[str, Any]:
        """
        Get aggregated stats for a metric.
        
        Args:
            metric_name: Metric name
            hours: Hours to aggregate
            
        Returns:
            Aggregate stats
        """
        now = datetime.utcnow()
        points = self.query(
            metric_name,
            start_time=now - timedelta(hours=hours),
        )
        
        if not points:
            return {
                "metric_name": metric_name,
                "period_hours": hours,
                "count": 0,
            }
        
        values = [p.value for p in points]
        
        return {
            "metric_name": metric_name,
            "period_hours": hours,
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1],
            "first_timestamp": points[0].timestamp.isoformat(),
            "last_timestamp": points[-1].timestamp.isoformat(),
        }
    
    def detect_anomaly(
        self,
        metric_name: str,
        threshold_std: float = 2.0,
        window_hours: int = 24,
    ) -> dict[str, Any]:
        """
        Detect anomalies in recent metrics.
        
        Uses simple standard deviation-based detection.
        
        Args:
            metric_name: Metric to check
            threshold_std: Number of standard deviations for anomaly
            window_hours: Historical window for baseline
            
        Returns:
            Anomaly detection result
        """
        now = datetime.utcnow()
        
        # Get historical data
        historical = self.query(
            metric_name,
            start_time=now - timedelta(hours=window_hours),
            end_time=now - timedelta(hours=1),  # Exclude last hour
        )
        
        # Get recent data
        recent = self.query(
            metric_name,
            start_time=now - timedelta(hours=1),
        )
        
        if len(historical) < 10:
            return {
                "metric_name": metric_name,
                "has_anomaly": False,
                "reason": "insufficient_historical_data",
            }
        
        if not recent:
            return {
                "metric_name": metric_name,
                "has_anomaly": False,
                "reason": "no_recent_data",
            }
        
        # Calculate baseline stats
        hist_values = [p.value for p in historical]
        avg = sum(hist_values) / len(hist_values)
        variance = sum((v - avg) ** 2 for v in hist_values) / len(hist_values)
        std = variance ** 0.5
        
        # Check recent values
        recent_values = [p.value for p in recent]
        recent_avg = sum(recent_values) / len(recent_values)
        
        # Detect anomaly
        lower_bound = avg - (threshold_std * std)
        upper_bound = avg + (threshold_std * std)
        
        anomalies = [
            {"value": v, "timestamp": p.timestamp.isoformat()}
            for p, v in zip(recent, recent_values)
            if v < lower_bound or v > upper_bound
        ]
        
        return {
            "metric_name": metric_name,
            "has_anomaly": len(anomalies) > 0,
            "baseline": {
                "avg": avg,
                "std": std,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
            },
            "recent_avg": recent_avg,
            "anomaly_count": len(anomalies),
            "anomalies": anomalies[:10],  # First 10
        }
    
    def list_metrics(self) -> list[str]:
        """List all known metric names"""
        return list(self._buffer.keys())
    
    def get_stats(self) -> dict[str, Any]:
        """Get metrics store statistics"""
        total_points = sum(len(points) for points in self._buffer.values())
        
        return {
            "metric_count": len(self._buffer),
            "total_points": total_points,
            "metrics": {
                name: len(points)
                for name, points in self._buffer.items()
            },
            "storage_path": str(self._storage_path),
        }
    
    def flush(self):
        """Flush metrics to disk"""
        self._save_to_disk()


def get_metrics_store() -> MetricsStore:
    """Get the global metrics store instance"""
    return MetricsStore()

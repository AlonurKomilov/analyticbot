"""
Performance Monitoring Service for Adaptive Learning
===================================================

Monitors model performance metrics, detects performance degradation,
and triggers adaptive learning responses.
"""

import asyncio
import logging
import statistics
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import numpy as np

from ..infrastructure.monitoring_infrastructure import MonitoringInfrastructureService
from ..protocols.monitoring_protocols import (
    AlertSeverity,
    PerformanceAlert,
    PerformanceMetric,
    PerformanceMetricType,
)

logger = logging.getLogger(__name__)


@dataclass
class PerformanceThresholds:
    """Performance thresholds for alerting"""

    accuracy_warning: float = 0.8
    accuracy_critical: float = 0.7
    error_rate_warning: float = 0.1
    error_rate_critical: float = 0.2
    latency_warning: float = 1000.0  # milliseconds
    latency_critical: float = 2000.0
    drift_warning: float = 0.3
    drift_critical: float = 0.5


@dataclass
class MonitoringServiceConfig:
    """Configuration for monitoring service"""

    collection_interval: int = 60  # seconds
    analysis_window: int = 300  # seconds (5 minutes)
    trend_analysis_enabled: bool = True
    anomaly_detection_enabled: bool = True
    real_time_alerts: bool = True
    batch_processing: bool = True
    min_samples_for_analysis: int = 10


class PerformanceMonitoringService:
    """
    Microservice for monitoring model performance.

    Tracks performance metrics, analyzes trends,
    and generates alerts for adaptive learning.
    """

    def __init__(
        self,
        infrastructure: MonitoringInfrastructureService,
        config: MonitoringServiceConfig | None = None,
        thresholds: PerformanceThresholds | None = None,
    ):
        self.infrastructure = infrastructure
        self.config = config or MonitoringServiceConfig()
        self.thresholds = thresholds or PerformanceThresholds()

        # Service state
        self.is_running = False
        self.monitored_models: set[str] = set()
        self.monitoring_tasks: list[asyncio.Task] = []

        # Performance tracking
        self.performance_history: dict[str, list[PerformanceMetric]] = {}
        self.trend_cache: dict[str, dict[PerformanceMetricType, float]] = {}
        self.anomaly_scores: dict[str, float] = {}

        logger.info("📊 Performance Monitoring Service initialized")

    async def start_monitoring(self, model_ids: list[str]) -> bool:
        """Start monitoring specified models"""
        try:
            if not self.infrastructure.is_initialized:
                logger.error("❌ Infrastructure not initialized")
                return False

            # Add models to monitoring
            self.monitored_models.update(model_ids)

            # Set up default thresholds for new models
            for model_id in model_ids:
                await self._setup_model_thresholds(model_id)

            # Start monitoring tasks
            if self.config.real_time_alerts:
                alert_task = asyncio.create_task(self._real_time_monitoring_loop())
                self.monitoring_tasks.append(alert_task)

            if self.config.trend_analysis_enabled:
                trend_task = asyncio.create_task(self._trend_analysis_loop())
                self.monitoring_tasks.append(trend_task)

            if self.config.anomaly_detection_enabled:
                anomaly_task = asyncio.create_task(self._anomaly_detection_loop())
                self.monitoring_tasks.append(anomaly_task)

            self.is_running = True
            logger.info(f"✅ Started monitoring {len(model_ids)} models")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start monitoring: {e}")
            return False

    async def stop_monitoring(self, model_ids: list[str] | None = None) -> bool:
        """Stop monitoring specified models or all models"""
        try:
            if model_ids:
                self.monitored_models -= set(model_ids)
                logger.info(f"⏹️ Stopped monitoring {len(model_ids)} models")
            else:
                # Stop all monitoring
                for task in self.monitoring_tasks:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

                self.monitoring_tasks.clear()
                self.monitored_models.clear()
                self.is_running = False
                logger.info("⏹️ Stopped all monitoring")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to stop monitoring: {e}")
            return False

    async def record_performance_metric(self, metric: PerformanceMetric) -> bool:
        """Record a performance metric"""
        try:
            # Validate metric
            if not await self._validate_metric(metric):
                return False

            # Store in infrastructure
            success = await self.infrastructure.store_metric(metric)
            if not success:
                return False

            # Add to local history
            if metric.model_id not in self.performance_history:
                self.performance_history[metric.model_id] = []

            self.performance_history[metric.model_id].append(metric)

            # Maintain history size
            await self._maintain_history_size(metric.model_id)

            # Real-time analysis if enabled
            if self.config.real_time_alerts:
                await self._analyze_metric_real_time(metric)

            logger.debug(
                f"📊 Recorded {metric.metric_type.value} for {metric.model_id}: {metric.value}"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Failed to record performance metric: {e}")
            return False

    async def get_performance_summary(
        self, model_id: str, time_range: tuple[datetime, datetime] | None = None
    ) -> dict[str, Any]:
        """Get performance summary for a model"""
        try:
            # Get metrics from infrastructure
            metrics = await self.infrastructure.get_metrics(
                model_id=model_id, time_range=time_range
            )

            if not metrics:
                return {"model_id": model_id, "status": "no_data", "metrics_count": 0}

            # Organize metrics by type
            metrics_by_type = {}
            for metric in metrics:
                metric_type = metric.metric_type
                if metric_type not in metrics_by_type:
                    metrics_by_type[metric_type] = []
                metrics_by_type[metric_type].append(metric.value)

            # Calculate statistics
            summary = {
                "model_id": model_id,
                "metrics_count": len(metrics),
                "time_range": {
                    "start": min(m.timestamp for m in metrics).isoformat(),
                    "end": max(m.timestamp for m in metrics).isoformat(),
                },
                "metric_statistics": {},
            }

            for metric_type, values in metrics_by_type.items():
                stats = {
                    "count": len(values),
                    "latest": values[-1] if values else None,
                    "average": statistics.mean(values) if values else 0,
                    "min": min(values) if values else 0,
                    "max": max(values) if values else 0,
                    "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                }

                # Add trend if available
                if model_id in self.trend_cache and metric_type in self.trend_cache[model_id]:
                    stats["trend"] = self.trend_cache[model_id][metric_type]

                summary["metric_statistics"][metric_type.value] = stats

            # Add health status
            summary["health_status"] = await self._assess_model_health(model_id, metrics)

            return summary

        except Exception as e:
            logger.error(f"❌ Failed to get performance summary: {e}")
            return {"model_id": model_id, "error": str(e)}

    async def detect_performance_issues(self, model_id: str) -> list[dict[str, Any]]:
        """Detect performance issues for a model"""
        try:
            issues = []

            # Get recent metrics
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(seconds=self.config.analysis_window)

            metrics = await self.infrastructure.get_metrics(
                model_id=model_id, time_range=(start_time, end_time)
            )

            if len(metrics) < self.config.min_samples_for_analysis:
                return [
                    {
                        "type": "insufficient_data",
                        "severity": "warning",
                        "message": f"Insufficient data for analysis: {len(metrics)} samples",
                    }
                ]

            # Group metrics by type
            metrics_by_type = {}
            for metric in metrics:
                if metric.metric_type not in metrics_by_type:
                    metrics_by_type[metric.metric_type] = []
                metrics_by_type[metric.metric_type].append(metric)

            # Check each metric type
            for metric_type, metric_list in metrics_by_type.items():
                values = [m.value for m in metric_list]
                latest_value = values[-1]

                # Threshold-based detection
                issue = await self._check_threshold_violation(metric_type, latest_value)
                if issue:
                    issues.append(issue)

                # Trend-based detection
                if len(values) >= 5:
                    trend_issue = await self._check_trend_degradation(metric_type, values)
                    if trend_issue:
                        issues.append(trend_issue)

                # Anomaly detection
                if self.config.anomaly_detection_enabled:
                    anomaly_issue = await self._check_anomaly(metric_type, values)
                    if anomaly_issue:
                        issues.append(anomaly_issue)

            return issues

        except Exception as e:
            logger.error(f"❌ Failed to detect performance issues: {e}")
            return [{"type": "detection_error", "error": str(e)}]

    async def get_monitoring_status(self) -> dict[str, Any]:
        """Get monitoring service status"""
        try:
            infrastructure_status = await self.infrastructure.get_monitoring_status()

            return {
                "service": "performance_monitoring",
                "is_running": self.is_running,
                "monitored_models": list(self.monitored_models),
                "active_tasks": len([t for t in self.monitoring_tasks if not t.done()]),
                "performance_history_size": {
                    model_id: len(metrics) for model_id, metrics in self.performance_history.items()
                },
                "infrastructure_status": infrastructure_status,
                "config": {
                    "collection_interval": self.config.collection_interval,
                    "analysis_window": self.config.analysis_window,
                    "real_time_alerts": self.config.real_time_alerts,
                    "trend_analysis_enabled": self.config.trend_analysis_enabled,
                    "anomaly_detection_enabled": self.config.anomaly_detection_enabled,
                },
            }

        except Exception as e:
            logger.error(f"❌ Failed to get monitoring status: {e}")
            return {"error": str(e)}

    async def _setup_model_thresholds(self, model_id: str) -> None:
        """Set up default thresholds for a model"""
        try:
            # Set accuracy thresholds
            await self.infrastructure.set_alert_threshold(
                model_id=model_id,
                metric_type=PerformanceMetricType.ACCURACY,
                threshold_value=self.thresholds.accuracy_warning,
                severity=AlertSeverity.WARNING,
            )

            await self.infrastructure.set_alert_threshold(
                model_id=model_id,
                metric_type=PerformanceMetricType.ACCURACY,
                threshold_value=self.thresholds.accuracy_critical,
                severity=AlertSeverity.CRITICAL,
            )

            # Set error rate thresholds
            await self.infrastructure.set_alert_threshold(
                model_id=model_id,
                metric_type=PerformanceMetricType.ERROR_RATE,
                threshold_value=self.thresholds.error_rate_warning,
                severity=AlertSeverity.WARNING,
            )

            await self.infrastructure.set_alert_threshold(
                model_id=model_id,
                metric_type=PerformanceMetricType.ERROR_RATE,
                threshold_value=self.thresholds.error_rate_critical,
                severity=AlertSeverity.CRITICAL,
            )

            # Set latency thresholds
            await self.infrastructure.set_alert_threshold(
                model_id=model_id,
                metric_type=PerformanceMetricType.LATENCY,
                threshold_value=self.thresholds.latency_warning,
                severity=AlertSeverity.WARNING,
            )

            logger.debug(f"🎯 Set up thresholds for model {model_id}")

        except Exception as e:
            logger.error(f"❌ Failed to setup thresholds for {model_id}: {e}")

    async def _validate_metric(self, metric: PerformanceMetric) -> bool:
        """Validate a performance metric"""
        try:
            # Check required fields
            if not metric.model_id or not metric.service_name:
                return False

            # Check metric value
            if metric.value is None or not isinstance(metric.value, (int, float)):
                return False

            # Check timestamp
            if not metric.timestamp:
                return False

            # Check if metric is too old
            age_threshold = timedelta(hours=1)
            if datetime.utcnow() - metric.timestamp > age_threshold:
                logger.warning(f"⚠️ Metric is too old: {metric.timestamp}")
                return False

            return True

        except Exception:
            return False

    async def _maintain_history_size(self, model_id: str) -> None:
        """Maintain performance history size"""
        try:
            max_history_size = 1000

            if len(self.performance_history[model_id]) > max_history_size:
                # Keep only the most recent metrics
                self.performance_history[model_id] = sorted(
                    self.performance_history[model_id],
                    key=lambda m: m.timestamp,
                    reverse=True,
                )[:max_history_size]

        except Exception as e:
            logger.error(f"❌ Failed to maintain history size: {e}")

    async def _analyze_metric_real_time(self, metric: PerformanceMetric) -> None:
        """Perform real-time analysis of a metric"""
        try:
            # Check for immediate threshold violations
            issue = await self._check_threshold_violation(metric.metric_type, metric.value)
            if issue:
                # Generate alert
                alert = PerformanceAlert(
                    alert_id=f"rt_{metric.model_id}_{metric.metric_type.value}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    severity=AlertSeverity(issue["severity"]),
                    metric_type=metric.metric_type,
                    current_value=metric.value,
                    threshold_value=issue.get("threshold", 0),
                    model_id=metric.model_id,
                    service_name=metric.service_name,
                    timestamp=datetime.utcnow(),
                    message=issue["message"],
                )

                await self.infrastructure.store_alert(alert)

        except Exception as e:
            logger.error(f"❌ Failed to analyze metric real-time: {e}")

    async def _check_threshold_violation(
        self, metric_type: PerformanceMetricType, value: float
    ) -> dict[str, Any] | None:
        """Check if a metric violates thresholds"""
        try:
            if metric_type == PerformanceMetricType.ACCURACY:
                if value < self.thresholds.accuracy_critical:
                    return {
                        "type": "threshold_violation",
                        "severity": "critical",
                        "message": f"Accuracy critically low: {value:.3f}",
                        "threshold": self.thresholds.accuracy_critical,
                    }
                elif value < self.thresholds.accuracy_warning:
                    return {
                        "type": "threshold_violation",
                        "severity": "warning",
                        "message": f"Accuracy below warning threshold: {value:.3f}",
                        "threshold": self.thresholds.accuracy_warning,
                    }

            elif metric_type == PerformanceMetricType.ERROR_RATE:
                if value > self.thresholds.error_rate_critical:
                    return {
                        "type": "threshold_violation",
                        "severity": "critical",
                        "message": f"Error rate critically high: {value:.3f}",
                        "threshold": self.thresholds.error_rate_critical,
                    }
                elif value > self.thresholds.error_rate_warning:
                    return {
                        "type": "threshold_violation",
                        "severity": "warning",
                        "message": f"Error rate above warning threshold: {value:.3f}",
                        "threshold": self.thresholds.error_rate_warning,
                    }

            elif metric_type == PerformanceMetricType.LATENCY:
                if value > self.thresholds.latency_critical:
                    return {
                        "type": "threshold_violation",
                        "severity": "critical",
                        "message": f"Latency critically high: {value:.1f}ms",
                        "threshold": self.thresholds.latency_critical,
                    }
                elif value > self.thresholds.latency_warning:
                    return {
                        "type": "threshold_violation",
                        "severity": "warning",
                        "message": f"Latency above warning threshold: {value:.1f}ms",
                        "threshold": self.thresholds.latency_warning,
                    }

            return None

        except Exception as e:
            logger.error(f"❌ Failed to check threshold violation: {e}")
            return None

    async def _check_trend_degradation(
        self, metric_type: PerformanceMetricType, values: list[float]
    ) -> dict[str, Any] | None:
        """Check for trend-based performance degradation"""
        try:
            if len(values) < 5:
                return None

            # Calculate trend using linear regression
            x = np.array(range(len(values)))
            y = np.array(values)

            # Simple linear regression
            slope = np.polyfit(x, y, 1)[0]

            # Define degradation thresholds based on metric type
            if metric_type in [
                PerformanceMetricType.ACCURACY,
                PerformanceMetricType.PRECISION,
                PerformanceMetricType.RECALL,
            ]:
                # For these metrics, negative slope is bad
                if slope < -0.01:  # 1% degradation per time unit
                    return {
                        "type": "trend_degradation",
                        "severity": "warning",
                        "message": f"{metric_type.value} showing declining trend: {slope:.4f}",
                        "trend_slope": slope,
                    }
            else:
                # For error rate, latency, etc., positive slope is bad
                if slope > 0.01:
                    return {
                        "type": "trend_degradation",
                        "severity": "warning",
                        "message": f"{metric_type.value} showing increasing trend: {slope:.4f}",
                        "trend_slope": slope,
                    }

            return None

        except Exception as e:
            logger.error(f"❌ Failed to check trend degradation: {e}")
            return None

    async def _check_anomaly(
        self, metric_type: PerformanceMetricType, values: list[float]
    ) -> dict[str, Any] | None:
        """Check for anomalous metric values"""
        try:
            if len(values) < 10:
                return None

            # Use simple statistical anomaly detection
            mean_val = statistics.mean(values[:-1])  # Exclude latest value
            std_val = statistics.stdev(values[:-1]) if len(values) > 2 else 0
            latest_val = values[-1]

            if std_val == 0:
                return None

            # Calculate z-score
            z_score = abs(latest_val - mean_val) / std_val

            # Threshold for anomaly detection
            anomaly_threshold = 2.5

            if z_score > anomaly_threshold:
                return {
                    "type": "anomaly_detected",
                    "severity": "warning",
                    "message": f"{metric_type.value} anomaly detected: {latest_val:.3f} (z-score: {z_score:.2f})",
                    "z_score": z_score,
                    "expected_range": [mean_val - 2 * std_val, mean_val + 2 * std_val],
                }

            return None

        except Exception as e:
            logger.error(f"❌ Failed to check anomaly: {e}")
            return None

    async def _assess_model_health(self, model_id: str, metrics: list[PerformanceMetric]) -> str:
        """Assess overall health of a model"""
        try:
            if not metrics:
                return "unknown"

            issues = await self.detect_performance_issues(model_id)

            # Count severity levels
            critical_issues = len([i for i in issues if i.get("severity") == "critical"])
            warning_issues = len([i for i in issues if i.get("severity") == "warning"])

            if critical_issues > 0:
                return "critical"
            elif warning_issues > 0:
                return "warning"
            else:
                return "healthy"

        except Exception as e:
            logger.error(f"❌ Failed to assess model health: {e}")
            return "unknown"

    async def _real_time_monitoring_loop(self) -> None:
        """Background task for real-time monitoring"""
        while self.is_running:
            try:
                await asyncio.sleep(self.config.collection_interval)

                # Check all monitored models
                for model_id in self.monitored_models:
                    issues = await self.detect_performance_issues(model_id)

                    if issues:
                        logger.info(f"🔍 Detected {len(issues)} issues for model {model_id}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in real-time monitoring loop: {e}")

    async def _trend_analysis_loop(self) -> None:
        """Background task for trend analysis"""
        while self.is_running:
            try:
                # Run trend analysis every 5 minutes
                await asyncio.sleep(300)

                for model_id in self.monitored_models:
                    await self._calculate_trends(model_id)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in trend analysis loop: {e}")

    async def _anomaly_detection_loop(self) -> None:
        """Background task for anomaly detection"""
        while self.is_running:
            try:
                # Run anomaly detection every 2 minutes
                await asyncio.sleep(120)

                for model_id in self.monitored_models:
                    await self._update_anomaly_scores(model_id)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in anomaly detection loop: {e}")

    async def _calculate_trends(self, model_id: str) -> None:
        """Calculate performance trends for a model"""
        try:
            if model_id not in self.performance_history:
                return

            metrics = self.performance_history[model_id]
            if len(metrics) < 5:
                return

            # Group by metric type
            metrics_by_type = {}
            for metric in metrics[-20:]:  # Use last 20 metrics
                if metric.metric_type not in metrics_by_type:
                    metrics_by_type[metric.metric_type] = []
                metrics_by_type[metric.metric_type].append(metric.value)

            # Calculate trends
            if model_id not in self.trend_cache:
                self.trend_cache[model_id] = {}

            for metric_type, values in metrics_by_type.items():
                if len(values) >= 5:
                    x = np.array(range(len(values)))
                    y = np.array(values)
                    slope = np.polyfit(x, y, 1)[0]
                    self.trend_cache[model_id][metric_type] = float(slope)

        except Exception as e:
            logger.error(f"❌ Failed to calculate trends for {model_id}: {e}")

    async def _update_anomaly_scores(self, model_id: str) -> None:
        """Update anomaly scores for a model"""
        try:
            if model_id not in self.performance_history:
                return

            metrics = self.performance_history[model_id]
            if len(metrics) < 10:
                return

            # Simple anomaly scoring based on recent deviations
            recent_metrics = metrics[-10:]
            all_values = [m.value for m in metrics]

            if len(all_values) < 10:
                return

            mean_val = statistics.mean(all_values[:-5])
            std_val = statistics.stdev(all_values[:-5]) if len(all_values) > 6 else 0

            if std_val > 0:
                recent_values = [m.value for m in recent_metrics]
                z_scores = [abs(val - mean_val) / std_val for val in recent_values]
                avg_z_score = statistics.mean(z_scores)
                self.anomaly_scores[model_id] = avg_z_score

        except Exception as e:
            logger.error(f"❌ Failed to update anomaly scores for {model_id}: {e}")

    async def shutdown(self) -> None:
        """Shutdown monitoring service"""
        try:
            await self.stop_monitoring()
            logger.info("🛑 Performance monitoring service shutdown complete")

        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")

    def get_service_health(self) -> dict[str, Any]:
        """Get service health status"""
        return {
            "service": "performance_monitoring",
            "status": "healthy" if self.is_running else "stopped",
            "is_running": self.is_running,
            "monitored_models": len(self.monitored_models),
            "active_tasks": len([t for t in self.monitoring_tasks if not t.done()]),
        }

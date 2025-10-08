"""
Monitoring Infrastructure
========================

Infrastructure components for monitoring adaptive learning services.
Provides monitoring, alerting, and health checking capabilities.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class MonitoringConfig:
    """Configuration for monitoring infrastructure"""

    max_metrics_history: int = 1000
    max_alerts: int = 100
    health_check_interval: int = 60  # seconds
    alert_levels: list[str] | None = None

    def __post_init__(self):
        if self.alert_levels is None:
            self.alert_levels = ["info", "warning", "error", "critical"]


class MonitoringInfrastructure:
    """
    Core monitoring infrastructure for adaptive learning services.

    Provides health checking, metrics collection, and alerting capabilities.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.metrics_history = []
        self.alerts = []
        self.logger = logging.getLogger(__name__)

    def collect_metrics(self, service_name: str, metrics: dict[str, Any]) -> None:
        """Collect metrics from a service"""
        try:
            metric_entry = {
                "service": service_name,
                "metrics": metrics,
                "timestamp": datetime.utcnow(),
                "collected_at": datetime.utcnow().isoformat(),
            }

            self.metrics_history.append(metric_entry)

            # Keep only last 1000 entries
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-1000:]

        except Exception as e:
            self.logger.error(f"Failed to collect metrics for {service_name}: {e}")

    def check_service_health(self, service_name: str) -> dict[str, Any]:
        """Check health of a specific service"""
        try:
            # Get recent metrics for the service
            recent_metrics = [
                m
                for m in self.metrics_history[-50:]  # Last 50 entries
                if m["service"] == service_name
            ]

            if not recent_metrics:
                return {
                    "service": service_name,
                    "status": "unknown",
                    "last_seen": None,
                    "message": "No recent metrics available",
                }

            latest_metric = recent_metrics[-1]

            # Simple health determination
            status = "healthy"
            message = "Service operating normally"

            # Check for error indicators in metrics
            if "error_count" in latest_metric["metrics"]:
                error_count = latest_metric["metrics"]["error_count"]
                if error_count > 10:
                    status = "unhealthy"
                    message = f"High error count: {error_count}"
                elif error_count > 5:
                    status = "degraded"
                    message = f"Elevated error count: {error_count}"

            return {
                "service": service_name,
                "status": status,
                "last_seen": latest_metric["timestamp"],
                "message": message,
                "metrics_count": len(recent_metrics),
            }

        except Exception as e:
            self.logger.error(f"Health check failed for {service_name}: {e}")
            return {
                "service": service_name,
                "status": "error",
                "last_seen": None,
                "message": f"Health check error: {e}",
            }

    def get_system_overview(self) -> dict[str, Any]:
        """Get overall system health overview"""
        try:
            # Get unique services
            services = list(set(m["service"] for m in self.metrics_history))

            service_health = {}
            overall_status = "healthy"

            for service in services:
                health = self.check_service_health(service)
                service_health[service] = health

                if health["status"] in ["unhealthy", "error"]:
                    overall_status = "unhealthy"
                elif health["status"] == "degraded" and overall_status == "healthy":
                    overall_status = "degraded"

            return {
                "overall_status": overall_status,
                "services": service_health,
                "total_services": len(services),
                "total_metrics": len(self.metrics_history),
                "last_update": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"System overview failed: {e}")
            return {
                "overall_status": "error",
                "services": {},
                "total_services": 0,
                "total_metrics": 0,
                "error": str(e),
                "last_update": datetime.utcnow().isoformat(),
            }

    def create_alert(self, service: str, level: str, message: str) -> None:
        """Create a monitoring alert"""
        alert = {
            "service": service,
            "level": level,
            "message": message,
            "timestamp": datetime.utcnow(),
            "created_at": datetime.utcnow().isoformat(),
        }

        self.alerts.append(alert)

        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]

        self.logger.warning(f"ALERT [{level}] {service}: {message}")

    def get_recent_alerts(self, limit: int = 20) -> list[dict[str, Any]]:
        """Get recent alerts"""
        return self.alerts[-limit:] if self.alerts else []

    def clear_old_data(self, hours: int = 24) -> int:
        """Clear old monitoring data"""
        from datetime import timedelta

        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        # Clear old metrics
        original_count = len(self.metrics_history)
        self.metrics_history = [m for m in self.metrics_history if m["timestamp"] > cutoff_time]

        # Clear old alerts
        self.alerts = [a for a in self.alerts if a["timestamp"] > cutoff_time]

        cleared = original_count - len(self.metrics_history)
        self.logger.info(f"Cleared {cleared} old metric entries")

        return cleared


# Create default monitoring infrastructure instance
default_monitoring = MonitoringInfrastructure()


def get_monitoring_infrastructure() -> MonitoringInfrastructure:
    """Get the default monitoring infrastructure instance"""
    return default_monitoring


class MonitoringInfrastructureService(MonitoringInfrastructure):
    """
    Legacy service wrapper for MonitoringInfrastructure.

    Provides backward compatibility for existing code that expects
    the MonitoringInfrastructureService class.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.service_name = "MonitoringInfrastructureService"

    def get_service_health(self) -> dict[str, Any]:
        """Get service health status (legacy interface)"""
        return {
            "service": self.service_name,
            "status": "healthy",
            "metrics_count": len(self.metrics_history),
            "alerts_count": len(self.alerts),
            "uptime": "N/A",
            "last_update": datetime.utcnow().isoformat(),
        }


__all__ = [
    "MonitoringInfrastructure",
    "MonitoringInfrastructureService",
    "MonitoringConfig",
    "get_monitoring_infrastructure",
    "default_monitoring",
]

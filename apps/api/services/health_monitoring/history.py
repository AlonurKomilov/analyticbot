"""
Health History Module
Track and analyze health check history and trends
"""

from datetime import datetime, timedelta
from typing import Any

from apps.api.services.health_monitoring.base import (
    HealthStatus,
    MAX_HISTORY_SIZE,
    SystemHealth,
)


class HealthHistory:
    """Health history tracking and trend analysis"""

    def __init__(self, max_history_size: int = MAX_HISTORY_SIZE):
        self.health_history: list[SystemHealth] = []
        self.max_history_size = max_history_size

    def store_health_check(self, health: SystemHealth) -> None:
        """Store health check result in history"""
        self.health_history.append(health)

        # Keep history size under limit
        if len(self.health_history) > self.max_history_size:
            self.health_history = self.health_history[-self.max_history_size :]

    def get_health_trends(self, hours: int = 24) -> dict[str, Any]:
        """
        Get health trends over specified time period

        Returns statistics about component reliability and performance
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_history = [h for h in self.health_history if h.timestamp >= cutoff_time]

        if not recent_history:
            return {"error": "No health data available for specified period"}

        # Calculate reliability metrics
        total_checks = len(recent_history)
        healthy_checks = sum(1 for h in recent_history if h.status == HealthStatus.HEALTHY)
        degraded_checks = sum(1 for h in recent_history if h.status == HealthStatus.DEGRADED)
        unhealthy_checks = sum(1 for h in recent_history if h.status == HealthStatus.UNHEALTHY)

        # Component-specific trends
        component_stats: dict[str, dict[str, Any]] = {}
        for health in recent_history:
            for comp_name, component in health.components.items():
                if comp_name not in component_stats:
                    component_stats[comp_name] = {
                        "total_checks": 0,
                        "healthy_count": 0,
                        "response_times": [],
                    }

                component_stats[comp_name]["total_checks"] += 1
                if component.status == HealthStatus.HEALTHY:
                    component_stats[comp_name]["healthy_count"] += 1
                if component.response_time_ms:
                    component_stats[comp_name]["response_times"].append(component.response_time_ms)

        # Calculate reliability percentages and avg response times
        for comp_name, stats in component_stats.items():
            stats["reliability_percent"] = (stats["healthy_count"] / stats["total_checks"]) * 100
            if stats["response_times"]:
                stats["avg_response_time_ms"] = sum(stats["response_times"]) / len(
                    stats["response_times"]
                )
                stats["max_response_time_ms"] = max(stats["response_times"])
            else:
                stats["avg_response_time_ms"] = 0
                stats["max_response_time_ms"] = 0

        return {
            "period_hours": hours,
            "total_checks": total_checks,
            "system_reliability_percent": (healthy_checks / total_checks) * 100,
            "status_distribution": {
                "healthy": healthy_checks,
                "degraded": degraded_checks,
                "unhealthy": unhealthy_checks,
            },
            "component_trends": component_stats,
            "first_check": recent_history[0].timestamp.isoformat(),
            "last_check": recent_history[-1].timestamp.isoformat(),
        }

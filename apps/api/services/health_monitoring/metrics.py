"""
Health Metrics Module
Calculate system-wide metrics and overall health status
"""

from typing import Any

import psutil

from apps.api.services.health_monitoring.base import ComponentHealth, HealthStatus, HealthThresholds


class HealthMetrics:
    """System health metrics calculation and status determination"""

    def __init__(self, thresholds: HealthThresholds):
        self.thresholds = thresholds

    def calculate_overall_status(
        self, components: dict[str, ComponentHealth]
    ) -> HealthStatus:
        """
        Calculate overall system health based on component statuses

        Logic:
        - Any critical component UNHEALTHY -> system UNHEALTHY
        - Any critical component DEGRADED -> system DEGRADED
        - All critical components HEALTHY -> check non-critical
        - Non-critical issues can only degrade, not make unhealthy
        """
        if not components:
            return HealthStatus.UNKNOWN

        critical_components = {name: comp for name, comp in components.items() if comp.critical}
        non_critical_components = {
            name: comp for name, comp in components.items() if not comp.critical
        }

        # Check critical components first
        critical_unhealthy = any(
            comp.status == HealthStatus.UNHEALTHY for comp in critical_components.values()
        )
        critical_degraded = any(
            comp.status == HealthStatus.DEGRADED for comp in critical_components.values()
        )

        if critical_unhealthy:
            return HealthStatus.UNHEALTHY
        elif critical_degraded:
            return HealthStatus.DEGRADED

        # If critical components are healthy, check non-critical for degradation only
        non_critical_degraded_or_unhealthy = any(
            comp.status in [HealthStatus.DEGRADED, HealthStatus.UNHEALTHY]
            for comp in non_critical_components.values()
        )

        if non_critical_degraded_or_unhealthy:
            return HealthStatus.DEGRADED

        return HealthStatus.HEALTHY

    def calculate_avg_response_time(self, components: dict[str, ComponentHealth]) -> float:
        """Calculate average response time across all components"""
        response_times = [
            comp.response_time_ms
            for comp in components.values()
            if comp.response_time_ms is not None
        ]
        return sum(response_times) / len(response_times) if response_times else 0.0

    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except Exception:
            return 0.0

    def generate_alerts(
        self, components: dict[str, ComponentHealth]
    ) -> list[str]:
        """Generate alerts based on component statuses and performance"""
        alerts = []

        for component in components.values():
            # Status-based alerts
            if component.status == HealthStatus.UNHEALTHY:
                icon = "🔴" if component.critical else "🟠"
                alerts.append(f"{icon} {component.name} is unhealthy: {component.error}")
            elif component.status == HealthStatus.DEGRADED:
                alerts.append(
                    f"🟡 {component.name} is degraded: {component.error or 'High response time'}"
                )

            # Performance-based alerts
            if component.response_time_ms:
                if component.response_time_ms > self.thresholds.response_time_critical_ms:
                    alerts.append(
                        f"⚠️ {component.name} critical response time: {component.response_time_ms:.1f}ms"
                    )
                elif component.response_time_ms > self.thresholds.response_time_warning_ms:
                    alerts.append(
                        f"⏱️ {component.name} slow response time: {component.response_time_ms:.1f}ms"
                    )

        return alerts

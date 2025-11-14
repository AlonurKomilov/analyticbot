"""
Health Monitoring Service
Main orchestration for comprehensive health checking system
"""

import asyncio
import os
import time
import uuid
from collections.abc import Callable
from datetime import datetime
from typing import Any

from apps.api.services.health_monitoring.base import (
    DEFAULT_ENVIRONMENT,
    DEFAULT_SERVICE_NAME,
    DEFAULT_VERSION,
    DependencyType,
    SystemHealth,
    default_thresholds,
    logger,
)
from apps.api.services.health_monitoring.checker import HealthChecker
from apps.api.services.health_monitoring.history import HealthHistory
from apps.api.services.health_monitoring.metrics import HealthMetrics


class HealthMonitoringService:
    """
    Application-layer health monitoring service

    Moved from core/common/health/checker.py to apps/api/services/
    to comply with clean architecture - framework imports belong in apps layer.

    Features:
    - Parallel health checks for optimal performance
    - Configurable dependency registration
    - History tracking and trend analysis
    - Performance metrics collection
    - Alert generation based on thresholds
    - Support for both sync and async health checks
    """

    def __init__(
        self,
        service_name: str = DEFAULT_SERVICE_NAME,
        version: str | None = None,
        thresholds=None,
    ):
        self.service_name = service_name
        self.version = version or os.getenv("APP_VERSION", DEFAULT_VERSION)
        self.environment = os.getenv("ENVIRONMENT", DEFAULT_ENVIRONMENT)
        self.thresholds = thresholds or default_thresholds

        self.start_time = datetime.now()

        # Health check registry
        self.dependencies: dict[str, dict[str, Any]] = {}

        # Initialize sub-components
        self.checker = HealthChecker(self.thresholds)
        self.metrics = HealthMetrics(self.thresholds)
        self.history = HealthHistory()

        logger.info(f"🏥 HealthMonitoringService initialized for {service_name} v{self.version}")

    def register_dependency(
        self,
        name: str,
        check_func: Callable,
        dependency_type: DependencyType,
        critical: bool = True,
        timeout: float | None = None,
    ) -> None:
        """
        Register a dependency for health checking

        Args:
            name: Unique identifier for the dependency
            check_func: Async function that returns health status dict
            dependency_type: Type of dependency (database, cache, etc.)
            critical: Whether failure should mark system as unhealthy
            timeout: Custom timeout for this check (uses default if None)
        """
        self.dependencies[name] = {
            "func": check_func,
            "type": dependency_type,
            "critical": critical,
            "timeout": timeout or self.checker.get_default_timeout(dependency_type),
        }
        logger.debug(
            f"Registered dependency: {name} ({dependency_type.value}, critical={critical})"
        )

    async def get_system_health(self, include_non_critical: bool = True) -> SystemHealth:
        """
        Get comprehensive system health status

        Args:
            include_non_critical: Whether to include non-critical dependencies

        Returns:
            SystemHealth object with all component statuses and metrics
        """
        check_start_time = time.time()
        health_check_id = str(uuid.uuid4())[:8]

        logger.debug(f"🔍 Starting system health check {health_check_id}")

        # Filter dependencies based on critical flag
        deps_to_check = self.dependencies
        if not include_non_critical:
            deps_to_check = {k: v for k, v in self.dependencies.items() if v["critical"]}

        # Perform all health checks in parallel
        component_checks = [
            (name, self.checker.check_dependency(name, config))
            for name, config in deps_to_check.items()
        ]

        # Execute checks with parallel processing
        results = await asyncio.gather(
            *[check_task for _, check_task in component_checks], return_exceptions=True
        )

        # Process results into components dict
        components = {}

        for (name, _), check_result in zip(component_checks, results, strict=False):
            if isinstance(check_result, Exception):
                # Handle unexpected exceptions during health check execution
                from apps.api.services.health_monitoring.base import (
                    ComponentHealth,
                    HealthStatus,
                )

                component_health = ComponentHealth(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    error=f"Health check execution failed: {str(check_result)}",
                    last_check=datetime.now(),
                    dependency_type=self.dependencies[name]["type"],
                    critical=self.dependencies[name]["critical"],
                )
                components[name] = component_health
            else:
                # check_result is ComponentHealth
                components[name] = check_result

        # Generate alerts based on component status
        alerts = self.metrics.generate_alerts(components)

        # Calculate overall system status
        overall_status = self.metrics.calculate_overall_status(components)

        # Performance metrics
        check_duration_ms = (time.time() - check_start_time) * 1000
        performance_metrics = {
            "health_check_duration_ms": check_duration_ms,
            "components_checked": len(components),
            "uptime_seconds": int((datetime.now() - self.start_time).total_seconds()),
            "avg_response_time_ms": self.metrics.calculate_avg_response_time(components),
            "memory_usage_mb": self.metrics.get_memory_usage(),
            "health_check_id": health_check_id,
        }

        # Create system health object
        system_health = SystemHealth(
            status=overall_status,
            timestamp=datetime.now(),
            uptime_seconds=int((datetime.now() - self.start_time).total_seconds()),
            version=self.version or "unknown",
            environment=self.environment,
            service_name=self.service_name,
            components=components,
            performance_metrics=performance_metrics,
            alerts=alerts,
            check_duration_ms=check_duration_ms,
            health_check_id=health_check_id,
        )

        # Store in history
        self.history.store_health_check(system_health)

        logger.info(
            f"✅ Health check {health_check_id} completed: {overall_status.value} "
            f"({len(components)} components, {check_duration_ms:.1f}ms)"
        )

        return system_health

    def get_health_trends(self, hours: int = 24) -> dict[str, Any]:
        """
        Get health trends over specified time period

        Returns statistics about component reliability and performance
        """
        return self.history.get_health_trends(hours)

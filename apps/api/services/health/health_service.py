"""
🏥 Health Monitoring Application Service

Clean architecture health monitoring service that coordinates health checks
without coupling to specific infrastructure implementations.
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Any

from core.ports.health_ports import (
    CacheHealthPort,
    ComponentHealth,
    DatabaseHealthPort,
    ExternalServiceHealthPort,
    HealthMonitoringService,
    HealthStatus,
    SystemHealth,
    SystemResourcesPort,
)

logger = logging.getLogger(__name__)


class HealthService(HealthMonitoringService):
    """
    Application service for comprehensive health monitoring

    Uses ports to check various system components without direct
    infrastructure dependencies.
    """

    def __init__(
        self,
        database_health: DatabaseHealthPort | None = None,
        cache_health: CacheHealthPort | None = None,
        external_service_health: ExternalServiceHealthPort | None = None,
        system_resources: SystemResourcesPort | None = None,
    ):
        self.database_health = database_health
        self.cache_health = cache_health
        self.external_service_health = external_service_health
        self.system_resources = system_resources
        self.custom_checks: dict[str, Any] = {}

    async def check_system_health(self) -> SystemHealth:
        """Perform comprehensive system health check"""
        start_time = time.time()
        components: list[ComponentHealth] = []

        # Collect all health checks
        health_checks = []

        if self.database_health:
            health_checks.extend(
                [
                    ("database_connection", self.database_health.check_connection()),
                    ("database_performance", self.database_health.check_query_performance()),
                ]
            )

        if self.cache_health:
            health_checks.extend(
                [
                    ("cache_connection", self.cache_health.check_connection()),
                    ("cache_memory", self.cache_health.check_memory_usage()),
                ]
            )

        if self.system_resources:
            health_checks.extend(
                [
                    ("cpu_usage", self.system_resources.check_cpu_usage()),
                    ("memory_usage", self.system_resources.check_memory_usage()),
                    ("disk_usage", self.system_resources.check_disk_usage()),
                ]
            )

        # Add custom checks
        for name, check_func in self.custom_checks.items():
            health_checks.append((name, check_func()))

        # Execute all checks concurrently
        if health_checks:
            try:
                results = await asyncio.gather(
                    *[check for _, check in health_checks], return_exceptions=True
                )

                for i, (name, _) in enumerate(health_checks):
                    result = results[i]
                    if isinstance(result, BaseException):
                        # Handle any exception (Exception or BaseException)
                        components.append(
                            ComponentHealth(
                                name=name,
                                status=HealthStatus.UNHEALTHY,
                                message=f"Health check failed: {str(result)}",
                                error=str(result),
                                last_checked=datetime.utcnow(),
                            )
                        )
                    elif isinstance(result, ComponentHealth):
                        # Successful health check result
                        components.append(result)
                    else:
                        # Unexpected result type
                        logger.warning(
                            f"Unexpected health check result type for {name}: {type(result)}"
                        )
                        components.append(
                            ComponentHealth(
                                name=name,
                                status=HealthStatus.UNKNOWN,
                                message=f"Unexpected result type: {type(result).__name__}",
                                last_checked=datetime.utcnow(),
                            )
                        )

            except Exception as e:
                logger.error(f"Error during health checks: {e}")
                components.append(
                    ComponentHealth(
                        name="system",
                        status=HealthStatus.UNHEALTHY,
                        message="Health check system failure",
                        error=str(e),
                        last_checked=datetime.utcnow(),
                    )
                )

        # Calculate overall health status
        response_time_ms = (time.time() - start_time) * 1000
        healthy_count = sum(1 for c in components if c.status == HealthStatus.HEALTHY)
        total_count = len(components)

        overall_status = self._calculate_overall_status(components)

        return SystemHealth(
            status=overall_status,
            timestamp=datetime.utcnow(),
            components=components,
            response_time_ms=response_time_ms,
            healthy_components=healthy_count,
            total_components=total_count,
            system_info=self._get_basic_system_info(),
        )

    async def check_component_health(self, component_name: str) -> ComponentHealth:
        """Check health of specific component"""
        try:
            if component_name == "database_connection" and self.database_health:
                return await self.database_health.check_connection()
            elif component_name == "database_performance" and self.database_health:
                return await self.database_health.check_query_performance()
            elif component_name == "cache_connection" and self.cache_health:
                return await self.cache_health.check_connection()
            elif component_name == "cache_memory" and self.cache_health:
                return await self.cache_health.check_memory_usage()
            elif component_name == "cpu_usage" and self.system_resources:
                return await self.system_resources.check_cpu_usage()
            elif component_name == "memory_usage" and self.system_resources:
                return await self.system_resources.check_memory_usage()
            elif component_name == "disk_usage" and self.system_resources:
                return await self.system_resources.check_disk_usage()
            elif component_name in self.custom_checks:
                return await self.custom_checks[component_name]()
            else:
                return ComponentHealth(
                    name=component_name,
                    status=HealthStatus.UNKNOWN,
                    message=f"Unknown component: {component_name}",
                    last_checked=datetime.utcnow(),
                )

        except Exception as e:
            logger.error(f"Error checking {component_name}: {e}")
            return ComponentHealth(
                name=component_name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                error=str(e),
                last_checked=datetime.utcnow(),
            )

    def register_health_check(self, name: str, check_func: Any, timeout: float = 5.0) -> None:
        """Register custom health check"""

        async def wrapped_check():
            try:
                # Add timeout wrapper
                result = await asyncio.wait_for(check_func(), timeout=timeout)
                return result
            except TimeoutError:
                return ComponentHealth(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Health check timed out after {timeout}s",
                    error="Timeout",
                    last_checked=datetime.utcnow(),
                )
            except Exception as e:
                return ComponentHealth(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Health check failed: {str(e)}",
                    error=str(e),
                    last_checked=datetime.utcnow(),
                )

        self.custom_checks[name] = wrapped_check
        logger.info(f"Registered health check: {name}")

    def _calculate_overall_status(self, components: list[ComponentHealth]) -> HealthStatus:
        """Calculate overall system status from component statuses"""
        if not components:
            return HealthStatus.UNKNOWN

        unhealthy_count = sum(1 for c in components if c.status == HealthStatus.UNHEALTHY)
        degraded_count = sum(1 for c in components if c.status == HealthStatus.DEGRADED)

        if unhealthy_count > 0:
            # If any critical components are unhealthy, system is unhealthy
            return HealthStatus.UNHEALTHY
        elif degraded_count > 0:
            # If any components are degraded, system is degraded
            return HealthStatus.DEGRADED
        else:
            # All components healthy
            return HealthStatus.HEALTHY

    def _get_basic_system_info(self) -> dict[str, Any]:
        """Get basic system information without psutil dependency"""
        try:
            import os

            return {
                "hostname": os.uname().nodename if hasattr(os, "uname") else "unknown",
                "platform": os.name,
                "pid": os.getpid(),
            }
        except Exception:
            return {"hostname": "unknown", "platform": "unknown", "pid": 0}


# Factory function for creating health service with all adapters
def create_health_service(
    database_health: DatabaseHealthPort | None = None,
    cache_health: CacheHealthPort | None = None,
    external_service_health: ExternalServiceHealthPort | None = None,
    system_resources: SystemResourcesPort | None = None,
) -> HealthService:
    """Factory function to create configured health service"""
    return HealthService(
        database_health=database_health,
        cache_health=cache_health,
        external_service_health=external_service_health,
        system_resources=system_resources,
    )

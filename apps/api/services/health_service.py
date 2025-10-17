"""
Health Monitoring Service for API Layer

Comprehensive health checking system moved from core to apps layer.
Provides framework-specific implementations while maintaining all
sophisticated monitoring capabilities.

Features:
- Parallel component checking for performance
- Configurable thresholds and timeouts
- Dependency registration and validation
- Performance metrics and alerting
- History tracking and trend analysis
- Support for database, cache, HTTP endpoint checks
"""

import asyncio
import logging
import os
import shutil
import time
import uuid
from collections.abc import Callable
from datetime import datetime, timedelta
from types import ModuleType
from typing import Any

# Framework-specific imports (now allowed in apps layer)
import asyncpg
import httpx
import psutil

# Redis is optional dependency
redis: ModuleType | None
try:
    import redis.asyncio as redis
except ImportError:
    redis = None

# Import core domain models (these should stay in core)
from core.common.health.models import (
    ComponentHealth,
    DependencyType,
    HealthStatus,
    HealthThresholds,
    SystemHealth,
    default_thresholds,
)

logger = logging.getLogger(__name__)


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
        service_name: str = "analyticbot",
        version: str | None = None,
        thresholds: HealthThresholds | None = None,
    ):
        self.service_name = service_name
        self.version = version or os.getenv("APP_VERSION", "2.1.0")
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.thresholds = thresholds or default_thresholds

        self.logger = logging.getLogger(f"{__name__}.{service_name}")
        self.start_time = datetime.now()

        # Health check registry
        self.dependencies: dict[str, dict[str, Any]] = {}

        # History tracking
        self.health_history: list[SystemHealth] = []
        self.max_history_size = 100

        self.logger.info(
            f"🏥 HealthMonitoringService initialized for {service_name} v{self.version}"
        )

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
            "timeout": timeout or self._get_default_timeout(dependency_type),
        }
        self.logger.debug(
            f"Registered dependency: {name} ({dependency_type.value}, critical={critical})"
        )

    def _get_default_timeout(self, dependency_type: DependencyType) -> float:
        """Get default timeout based on dependency type"""
        timeout_map = {
            DependencyType.DATABASE: self.thresholds.db_connection_timeout,
            DependencyType.CACHE: self.thresholds.redis_timeout,
            DependencyType.EXTERNAL_API: self.thresholds.http_timeout,
            DependencyType.SERVICE: self.thresholds.http_timeout,
        }
        return timeout_map.get(dependency_type, 5.0)

    async def check_dependency(self, name: str, config: dict[str, Any]) -> ComponentHealth:
        """
        Check individual dependency health with timeout and error handling

        Returns ComponentHealth object with detailed status information
        """
        start_time = time.time()

        try:
            # Execute health check with timeout
            check_task = asyncio.create_task(config["func"]())
            result = await asyncio.wait_for(check_task, timeout=config["timeout"])

            response_time_ms = (time.time() - start_time) * 1000

            # Determine status based on result and response time
            base_healthy = result.get("healthy", True) if isinstance(result, dict) else bool(result)
            status = self.thresholds.determine_status_from_response_time(
                response_time_ms, base_healthy
            )

            # Extract error message if available
            error_msg = None
            if not base_healthy:
                error_msg = (
                    result.get("error")
                    if isinstance(result, dict)
                    else "Health check returned false"
                )

            return ComponentHealth(
                name=name,
                status=status,
                response_time_ms=response_time_ms,
                error=error_msg,
                details=result if isinstance(result, dict) else {"result": result},
                last_check=datetime.now(),
                dependency_type=config["type"],
                critical=config["critical"],
            )

        except TimeoutError:
            response_time_ms = (time.time() - start_time) * 1000
            error_msg = f"Health check timed out after {config['timeout']}s"
            self.logger.warning(f"Health check timeout for {name}: {error_msg}")

            return ComponentHealth(
                name=name,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=response_time_ms,
                error=error_msg,
                last_check=datetime.now(),
                dependency_type=config["type"],
                critical=config["critical"],
            )

        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            error_msg = f"Health check failed: {str(e)}"
            self.logger.error(f"Health check error for {name}: {error_msg}")

            return ComponentHealth(
                name=name,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=response_time_ms,
                error=error_msg,
                last_check=datetime.now(),
                dependency_type=config["type"],
                critical=config["critical"],
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

        self.logger.debug(f"🔍 Starting system health check {health_check_id}")

        # Filter dependencies based on critical flag
        deps_to_check = self.dependencies
        if not include_non_critical:
            deps_to_check = {k: v for k, v in self.dependencies.items() if v["critical"]}

        # Perform all health checks in parallel
        component_checks = [
            (name, self.check_dependency(name, config)) for name, config in deps_to_check.items()
        ]

        # Execute checks with parallel processing
        results = await asyncio.gather(
            *[check_task for _, check_task in component_checks], return_exceptions=True
        )

        # Process results into components dict
        components = {}
        alerts = []

        for (name, _), check_result in zip(component_checks, results, strict=False):
            if isinstance(check_result, Exception):
                # Handle unexpected exceptions during health check execution
                component_health = ComponentHealth(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    error=f"Health check execution failed: {str(check_result)}",
                    last_check=datetime.now(),
                    dependency_type=self.dependencies[name]["type"],
                    critical=self.dependencies[name]["critical"],
                )
                components[name] = component_health
                alerts.append(f"❌ {name} health check execution failed: {str(check_result)}")
            elif isinstance(check_result, ComponentHealth):
                # check_result is ComponentHealth
                components[name] = check_result

                # Generate alerts based on component status
                if check_result.status == HealthStatus.UNHEALTHY:
                    icon = "🔴" if check_result.critical else "🟠"
                    alerts.append(f"{icon} {name} is unhealthy: {check_result.error}")
                elif check_result.status == HealthStatus.DEGRADED:
                    alerts.append(
                        f"🟡 {name} is degraded: {check_result.error or 'High response time'}"
                    )

                # Performance-based alerts
                if check_result.response_time_ms:
                    if check_result.response_time_ms > self.thresholds.response_time_critical_ms:
                        alerts.append(
                            f"⚠️ {name} critical response time: {check_result.response_time_ms:.1f}ms"
                        )
                    elif check_result.response_time_ms > self.thresholds.response_time_warning_ms:
                        alerts.append(
                            f"⏱️ {name} slow response time: {check_result.response_time_ms:.1f}ms"
                        )

        # Calculate overall system status
        overall_status = self._calculate_overall_status(components)

        # Performance metrics
        check_duration_ms = (time.time() - check_start_time) * 1000
        performance_metrics = {
            "health_check_duration_ms": check_duration_ms,
            "components_checked": len(components),
            "uptime_seconds": int((datetime.now() - self.start_time).total_seconds()),
            "avg_response_time_ms": self._calculate_avg_response_time(components),
            "memory_usage_mb": self._get_memory_usage(),
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
        self._store_health_history(system_health)

        self.logger.info(
            f"✅ Health check {health_check_id} completed: {overall_status.value} "
            f"({len(components)} components, {check_duration_ms:.1f}ms)"
        )

        return system_health

    def _calculate_overall_status(self, components: dict[str, ComponentHealth]) -> HealthStatus:
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

    def _calculate_avg_response_time(self, components: dict[str, ComponentHealth]) -> float:
        """Calculate average response time across all components"""
        response_times = [
            comp.response_time_ms
            for comp in components.values()
            if comp.response_time_ms is not None
        ]
        return sum(response_times) / len(response_times) if response_times else 0.0

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except Exception:
            return 0.0

    def _store_health_history(self, health: SystemHealth) -> None:
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


# Framework-specific health check implementations
# These can now safely use asyncpg, httpx, redis since we're in the apps layer


async def check_database_health(connection_string: str | None = None) -> dict[str, Any]:
    """Database health check using asyncpg"""
    try:
        # Use provided connection string or environment variable
        conn_str = connection_string or os.getenv("DATABASE_URL")
        if not conn_str:
            return {"healthy": False, "error": "No database connection string configured"}

        # Test database connection
        conn = await asyncpg.connect(conn_str)
        await conn.execute("SELECT 1")
        await conn.close()

        return {"healthy": True, "database_type": "postgresql"}

    except Exception as e:
        return {"healthy": False, "error": f"Database connection failed: {str(e)}"}


async def check_redis_health(
    host: str = "localhost", port: int = 10200, db: int = 0
) -> dict[str, Any]:
    """Redis health check using redis.asyncio

    Updated to use port 10200 (production Redis port) by default
    instead of 6379 (standard Redis port).
    """
    if not redis:
        return {"healthy": False, "error": "Redis client not available"}

    try:
        # Try to get Redis URL from environment first
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            # Parse URL to extract host, port, db
            # Format: redis://host:port/db
            try:
                from urllib.parse import urlparse

                parsed = urlparse(redis_url)
                host = parsed.hostname or host
                port = parsed.port or port
                db = int(parsed.path.lstrip("/")) if parsed.path and parsed.path != "/" else db
            except Exception as e:
                logger.warning(f"Failed to parse REDIS_URL, using defaults: {e}")

        redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        await redis_client.ping()
        await redis_client.close()

        return {"healthy": True, "redis_host": f"{host}:{port}/{db}"}

    except Exception as e:
        return {"healthy": False, "error": f"Redis connection failed: {str(e)}"}


async def check_http_endpoint(url: str, timeout: float = 5.0) -> dict[str, Any]:
    """HTTP endpoint health check using httpx"""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)

        healthy = 200 <= response.status_code < 400
        return {"healthy": healthy, "status_code": response.status_code, "url": url}

    except Exception as e:
        return {"healthy": False, "error": f"HTTP check failed: {str(e)}", "url": url}


async def check_disk_space(path: str = "/", warning_percent: float = 80) -> dict[str, Any]:
    """Disk space health check using shutil"""
    try:
        total, used, free = shutil.disk_usage(path)
        used_percent = (used / total) * 100

        healthy = used_percent < warning_percent

        return {
            "healthy": healthy,
            "used_percent": round(used_percent, 2),
            "free_gb": round(free / (1024**3), 2),
            "total_gb": round(total / (1024**3), 2),
            "path": path,
        }

    except Exception as e:
        return {"healthy": False, "error": f"Disk check failed: {str(e)}", "path": path}


async def check_memory_usage(warning_percent: float = 85) -> dict[str, Any]:
    """Memory usage health check using psutil"""
    try:
        memory = psutil.virtual_memory()
        used_percent = memory.percent

        healthy = used_percent < warning_percent

        return {
            "healthy": healthy,
            "used_percent": used_percent,
            "available_gb": round(memory.available / (1024**3), 2),
            "total_gb": round(memory.total / (1024**3), 2),
        }

    except Exception as e:
        return {"healthy": False, "error": f"Memory check failed: {str(e)}"}


# Default health monitoring service instance
health_service = HealthMonitoringService()

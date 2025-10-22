"""
Health Checker Module
Individual dependency checking with timeout and error handling
"""

import asyncio
import time
from datetime import datetime
from typing import Any

from apps.api.services.health_monitoring.base import (
    ComponentHealth,
    DependencyType,
    HealthStatus,
    HealthThresholds,
    logger,
)


class HealthChecker:
    """Component-level health checking with timeout and error handling"""

    def __init__(self, thresholds: HealthThresholds):
        self.thresholds = thresholds

    def get_default_timeout(self, dependency_type: DependencyType) -> float:
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
            logger.warning(f"Health check timeout for {name}: {error_msg}")

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
            logger.error(f"Health check error for {name}: {error_msg}")

            return ComponentHealth(
                name=name,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=response_time_ms,
                error=error_msg,
                last_check=datetime.now(),
                dependency_type=config["type"],
                critical=config["critical"],
            )

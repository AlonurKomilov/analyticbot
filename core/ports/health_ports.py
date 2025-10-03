"""
🏥 Health Checking Ports - Framework-Independent Health Monitoring

These ports define contracts for health monitoring without coupling
to specific infrastructure like asyncpg, httpx, or Redis.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class HealthStatus(Enum):
    """Health status enumeration"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ComponentHealth:
    """Health status of a single component"""

    name: str
    status: HealthStatus
    message: str
    response_time_ms: float | None = None
    details: dict[str, Any] | None = None
    last_checked: datetime | None = None
    error: str | None = None


@dataclass
class SystemHealth:
    """Overall system health status"""

    status: HealthStatus
    timestamp: datetime
    components: list[ComponentHealth]
    response_time_ms: float
    healthy_components: int
    total_components: int
    system_info: dict[str, Any] | None = None


class DatabaseHealthPort(ABC):
    """Port for checking database connectivity and health"""

    @abstractmethod
    async def check_connection(self) -> ComponentHealth:
        """Check database connection health"""

    @abstractmethod
    async def check_query_performance(self) -> ComponentHealth:
        """Check database query performance"""


class CacheHealthPort(ABC):
    """Port for checking cache system health"""

    @abstractmethod
    async def check_connection(self) -> ComponentHealth:
        """Check cache connection health"""

    @abstractmethod
    async def check_memory_usage(self) -> ComponentHealth:
        """Check cache memory usage"""


class ExternalServiceHealthPort(ABC):
    """Port for checking external service health"""

    @abstractmethod
    async def check_service(self, url: str, timeout: float = 5.0) -> ComponentHealth:
        """Check external service health via HTTP"""


class SystemResourcesPort(ABC):
    """Port for checking system resources"""

    @abstractmethod
    async def check_cpu_usage(self) -> ComponentHealth:
        """Check CPU usage"""

    @abstractmethod
    async def check_memory_usage(self) -> ComponentHealth:
        """Check memory usage"""

    @abstractmethod
    async def check_disk_usage(self, path: str = "/") -> ComponentHealth:
        """Check disk usage"""


class HealthMonitoringService(ABC):
    """Core health monitoring service interface"""

    @abstractmethod
    async def check_system_health(self) -> SystemHealth:
        """Perform comprehensive system health check"""

    @abstractmethod
    async def check_component_health(self, component_name: str) -> ComponentHealth:
        """Check health of specific component"""

    @abstractmethod
    def register_health_check(self, name: str, check_func: Any, timeout: float = 5.0) -> None:
        """Register custom health check"""

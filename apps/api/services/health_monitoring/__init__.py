"""
Health Monitoring Package
Modular health checking system for API layer

Main exports:
- HealthMonitoringService: Main orchestration class
- Health check utilities: check_database_health, check_redis_health, etc.
- Core models: ComponentHealth, SystemHealth, HealthStatus, etc.
"""

from apps.api.services.health_monitoring.service import HealthMonitoringService
from apps.api.services.health_monitoring.utils import (
    check_database_health,
    check_disk_space,
    check_http_endpoint,
    check_memory_usage,
    check_redis_health,
)

# Re-export core models for convenience
from core.common.health.models import (
    ComponentHealth,
    DependencyType,
    HealthStatus,
    HealthThresholds,
    SystemHealth,
    default_thresholds,
)

# Default health monitoring service instance
health_service = HealthMonitoringService()

__all__ = [
    "HealthMonitoringService",
    "health_service",
    "check_database_health",
    "check_redis_health",
    "check_http_endpoint",
    "check_disk_space",
    "check_memory_usage",
    "ComponentHealth",
    "SystemHealth",
    "HealthStatus",
    "HealthThresholds",
    "DependencyType",
    "default_thresholds",
]

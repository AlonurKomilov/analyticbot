"""
Health Service Compatibility Shim
Maintains backward compatibility for existing imports

This module re-exports from the new health_monitoring package.
"""

# Re-export everything from the new package
from apps.api.services.health_monitoring import (
    ComponentHealth,
    DependencyType,
    HealthMonitoringService,
    HealthStatus,
    HealthThresholds,
    SystemHealth,
    check_database_health,
    check_disk_space,
    check_http_endpoint,
    check_memory_usage,
    check_redis_health,
    default_thresholds,
    health_service,
)

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

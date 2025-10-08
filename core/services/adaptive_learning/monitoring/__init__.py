"""
Monitoring Microservice
=====================

Complete performance monitoring and alerting capabilities.
Tracks model performance, detects issues, and generates alerts.
"""

from .monitoring_infrastructure import MonitoringConfig, MonitoringInfrastructureService
from .performance_monitoring import (
    MonitoringServiceConfig,
    PerformanceMonitoringService,
    PerformanceThresholds,
)

__all__ = [
    # Main service
    "PerformanceMonitoringService",
    "MonitoringServiceConfig",
    "PerformanceThresholds",
    # Infrastructure
    "MonitoringInfrastructureService",
    "MonitoringConfig",
]

# Microservice metadata
__microservice__ = {
    "name": "monitoring",
    "version": "1.0.0",
    "description": "Complete performance monitoring with real-time alerting and trend analysis",
    "components": ["PerformanceMonitoringService", "MonitoringInfrastructureService"],
}

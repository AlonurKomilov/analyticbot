"""
Core metrics services module.

This module provides Clean Architecture-compliant metrics collection
services that are independent of specific metrics backends.
"""

from core.services.bot.metrics.business_metrics_service import BusinessMetricsService
from core.services.bot.metrics.decorators import (
    collect_system_metrics_decorator,
    metrics_timer,
)
from core.services.bot.metrics.health_check_service import HealthCheckService
from core.services.bot.metrics.metrics_collector_service import MetricsCollectorService
from core.services.bot.metrics.models import (
    BusinessMetrics,
    CeleryTaskMetric,
    DatabaseQueryMetric,
    HealthCheckResult,
    HTTPRequestMetric,
    MetricDefinition,
    MetricType,
    MetricValue,
    SystemMetrics,
    TelegramAPIMetric,
    TelegramUpdateMetric,
)
from core.services.bot.metrics.protocols import (
    CeleryMetricsPort,
    DatabaseMetricsPort,
    MetricsBackendPort,
    SystemMetricsPort,
)
from core.services.bot.metrics.system_metrics_service import SystemMetricsService

__all__ = [
    # Services
    "MetricsCollectorService",
    "BusinessMetricsService",
    "HealthCheckService",
    "SystemMetricsService",
    # Models
    "MetricType",
    "MetricDefinition",
    "MetricValue",
    "HTTPRequestMetric",
    "TelegramAPIMetric",
    "TelegramUpdateMetric",
    "DatabaseQueryMetric",
    "CeleryTaskMetric",
    "BusinessMetrics",
    "SystemMetrics",
    "HealthCheckResult",
    # Protocols
    "MetricsBackendPort",
    "SystemMetricsPort",
    "DatabaseMetricsPort",
    "CeleryMetricsPort",
    # Decorators
    "metrics_timer",
    "collect_system_metrics_decorator",
]

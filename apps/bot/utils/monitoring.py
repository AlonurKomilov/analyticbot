"""
Monitoring utilities - DEPRECATED

This module has been moved to apps/shared/monitoring.py to comply with clean architecture.

⚠️ DEPRECATED: Import from apps.shared.monitoring instead.
This file remains for backward compatibility but will be removed in a future version.
"""

import warnings

# Issue deprecation warning
warnings.warn(
    "apps.bot.utils.monitoring is deprecated. Use 'from apps.shared.monitoring import ...' instead. "
    "This module has been moved to the shared layer to comply with clean architecture.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from shared layer for backward compatibility
from apps.shared.monitoring import (  # noqa: F401, E402
    HealthMonitor,
    MetricData,
    MetricsCollector,
    PerformanceStats,
    health_monitor,
    metrics,
    record_performance,
    setup_default_health_checks,
)

__all__ = [
    "MetricData",
    "PerformanceStats",
    "MetricsCollector",
    "metrics",
    "record_performance",
    "HealthMonitor",
    "health_monitor",
    "setup_default_health_checks",
]

"""Monitoring Protocol Interfaces"""

from .reporting_protocols import (
    AlertSeverity,
    DataCollectorProtocol,
    MetricsCollectorProtocol,
    MonitoringAlert,
    MonitoringProtocol,
    PerformanceTrackerProtocol,
)

# Additional monitoring-specific types
LiveMetrics = dict
CollectorConfig = dict

__all__ = [
    "MonitoringProtocol",
    "MetricsCollectorProtocol",
    "DataCollectorProtocol",
    "PerformanceTrackerProtocol",
    "MonitoringAlert",
    "AlertSeverity",
    "LiveMetrics",
    "CollectorConfig",
]

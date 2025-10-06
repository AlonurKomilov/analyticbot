"""
Live Monitoring Microservice Package
====================================

Real-time monitoring and alerts microservice.
Single responsibility: Live monitoring only.
"""

from .live_monitoring_service import LiveMonitoringService

__all__ = ["LiveMonitoringService"]

# Microservice metadata
__microservice__ = {
    "name": "monitoring",
    "version": "1.0.0",
    "description": "Real-time monitoring and alerts",
    "responsibility": "Live monitoring and alerting only",
    "components": ["LiveMonitoringService"],
}

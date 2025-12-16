"""
Monitoring Microservices Package
================================

Real-time monitoring and metrics collection services.

Services:
- LiveMonitoringService: Real-time metrics collection and live data monitoring

Single Responsibility: Pure monitoring focus without alerts logic or competitive analysis.
"""

from ..live_monitoring_service import LiveMonitoringService

__all__ = ["LiveMonitoringService"]

# Metadata
__version__ = "1.0.0"
__purpose__ = "Real-time monitoring microservices"
__responsibility__ = "Live metrics and monitoring only"

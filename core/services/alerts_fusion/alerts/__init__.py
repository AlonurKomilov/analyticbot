"""
Alerts Microservices Package
============================

Alert management and intelligent alerting services.

Services:
- AlertsManagementService: Alert configuration, rules, and real-time checking

Single Responsibility: Pure alerts management without monitoring or competitive analysis.
"""

from .alerts_management_service import AlertsManagementService

__all__ = ["AlertsManagementService"]

# Metadata
__version__ = "1.0.0"
__purpose__ = "Alert management microservices"
__responsibility__ = "Alert configuration and checking only"

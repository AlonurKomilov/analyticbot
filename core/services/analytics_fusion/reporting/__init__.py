"""
Reporting Microservice Package
==============================

Report generation and dashboard microservice.
Single responsibility: Reporting only.
"""

from .reporting_service import ReportingService

__all__ = ["ReportingService"]

# Microservice metadata
__microservice__ = {
    "name": "reporting",
    "version": "1.0.0",
    "description": "Report generation and dashboards",
    "responsibility": "Report creation and formatting only",
    "components": ["ReportingService"],
}

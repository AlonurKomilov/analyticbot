"""
Bot Services - Core Business Logic for Bot Domain

This package contains all bot-related business logic services following Clean Architecture principles.

Services are organized by functional area:
- analytics: Analytics batch processing and data aggregation
- reporting: Multi-format report generation (PDF, Excel, HTML, JSON)
- dashboard: Interactive dashboard and visualization services
- scheduling: Post and notification scheduling (Phase 3.1)
- alerts: Alert conditions and rule management (Phase 3.2)
- content: Content protection and watermarking (Phase 3.3)
- subscription: Subscription business logic (Phase 3.5)

All services are framework-agnostic and can be used by any adapter (Telegram, API, CLI, etc.).

Architecture:
- Pure business logic (no framework dependencies)
- Repository pattern for data access (via protocols)
- Testable in isolation
- Type-safe with full type hints
- Single Responsibility Principle

Usage:
    from core.services.bot.analytics import AnalyticsBatchProcessor
    from core.services.bot.reporting import ReportingService
    from core.services.bot.dashboard import DashboardService

    # Or import multiple at once
    from core.services.bot import analytics, reporting, dashboard
"""

# Analytics services
from core.services.bot.analytics.analytics_batch_processor import (
    AnalyticsBatchProcessor,
)

# Dashboard services
from core.services.bot.dashboard.dashboard_service import (
    RealTimeDashboard as DashboardService,
)

# Reporting services
from core.services.bot.reporting.reporting_service import (
    AutomatedReportingSystem as ReportingService,
)

__all__ = [
    # Analytics
    "AnalyticsBatchProcessor",
    # Reporting
    "ReportingService",
    # Dashboard
    "DashboardService",
]

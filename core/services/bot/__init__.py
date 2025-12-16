"""
Bot Services - Core Business Logic for Bot Domain

This package contains all bot-related business logic services following Clean Architecture principles.

Services are organized by functional area:
- moderation: Anti-spam, auto-delete joins, banned words, warnings
- analytics: Analytics batch processing and data aggregation
- reporting: Multi-format report generation (PDF, Excel, HTML, JSON)
- dashboard: Interactive dashboard and visualization services
- scheduling: Post and notification scheduling
- alerts: Alert conditions and rule management
- content: Content protection and watermarking
- metrics: Health checks, business metrics, system metrics

All services are framework-agnostic and can be used by any adapter (Telegram, API, CLI, etc.).

Architecture:
- Pure business logic (no framework dependencies)
- Repository pattern for data access (via protocols)
- Testable in isolation
- Type-safe with full type hints
- Single Responsibility Principle

Usage:
    from core.services.bot.moderation import BotFeaturesManager, AntiSpamService
    from core.services.bot.analytics import AnalyticsBatchProcessor
    from core.services.bot.reporting import ReportingService
    from core.services.bot.dashboard import DashboardService
"""

# Moderation services (bot features)
from core.services.bot.moderation.bot_features_manager import BotFeaturesManager
from core.services.bot.moderation.base_bot_service import BaseBotService
from core.services.bot.moderation.anti_spam_service import AntiSpamService
from core.services.bot.moderation.auto_delete_joins_service import AutoDeleteJoinsService

# Analytics services
from core.services.bot.analytics.analytics_batch_processor import AnalyticsBatchProcessor

# Dashboard services
from core.services.bot.dashboard.dashboard_service import RealTimeDashboard as DashboardService

# Reporting services
from core.services.bot.reporting.reporting_service import (
    AutomatedReportingSystem as ReportingService,
)

__all__ = [
    # Moderation
    "BotFeaturesManager",
    "BaseBotService",
    "AntiSpamService",
    "AutoDeleteJoinsService",
    # Analytics
    "AnalyticsBatchProcessor",
    # Reporting
    "ReportingService",
    # Dashboard
    "DashboardService",
]


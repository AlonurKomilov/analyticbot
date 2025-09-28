"""
Centralized Mock Service Registration

This module registers all mock services with the registry for easy access.
"""

from .registry import mock_registry
from .services.mock_admin_service import MockAdminService
from .services.mock_ai_service import MockAIService
from .services.mock_analytics_service import MockAnalyticsService
from .services.mock_auth_service import MockAuthService
from .services.mock_database_service import MockDatabaseService
from .services.mock_demo_data_service import MockDemoDataService
from .services.mock_email_service import MockEmailService
from .services.mock_payment_service import MockPaymentService
from .services.mock_telegram_service import MockTelegramService


def register_all_services():
    """Register all mock services with the registry"""

    # Core services
    mock_registry.register_service("analytics", MockAnalyticsService)
    mock_registry.register_service("payment", MockPaymentService)
    mock_registry.register_service("email", MockEmailService)
    mock_registry.register_service("telegram", MockTelegramService)
    mock_registry.register_service("auth", MockAuthService)
    mock_registry.register_service("admin", MockAdminService)
    mock_registry.register_service("ai", MockAIService)
    mock_registry.register_service("demo_data", MockDemoDataService)
    mock_registry.register_service("database", MockDatabaseService)


# Auto-register on import
register_all_services()

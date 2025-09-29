"""
Mock Services Package
Mock implementations for all service protocols
"""

from .mock_admin_service import MockAdminService
from .mock_ai_service import MockAIService
from .mock_analytics_service import MockAnalyticsService
from .mock_auth_service import MockAuthService
from .mock_demo_data_service import MockDemoDataService
from .mock_email_service import MockEmailService
from .mock_payment_service import MockPaymentService
from .mock_telegram_service import MockTelegramService

__all__ = [
    "MockAnalyticsService",
    "MockPaymentService",
    "MockEmailService",
    "MockTelegramService",
    "MockAuthService",
    "MockAdminService",
    "MockAIService",
    "MockDemoDataService",
]

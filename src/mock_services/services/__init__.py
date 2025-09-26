"""
Consolidated Mock Services

All mock services consolidated from scattered locations:
- src/api_service/application/services/__mocks__/
- src/api_service/infrastructure/testing/services/
- src/bot_service/application/services/adapters/ (mock adapters)
"""

from .mock_analytics_service import MockAnalyticsService
from .mock_payment_service import MockPaymentService
from .mock_email_service import MockEmailService
from .mock_ai_service import MockAIService
from .mock_admin_service import MockAdminService
from .mock_auth_service import MockAuthService
from .mock_demo_data_service import MockDemoDataService
from .mock_telegram_service import MockTelegramService
from .mock_database_service import MockDatabaseService

__all__ = [
    "MockAnalyticsService",
    "MockPaymentService",
    "MockEmailService", 
    "MockAIService",
    "MockAdminService",
    "MockAuthService",
    "MockDemoDataService",
    "MockTelegramService",
    "MockDatabaseService"
]
"""
Auto-registration for mock services
"""

from .registry import mock_registry

# Import all mock services
from ..services.mock_analytics_service import MockAnalyticsService
from ..services.mock_payment_service import MockPaymentService 
from ..services.mock_email_service import MockEmailService
from ..services.mock_ai_service import MockAIService
from ..services.mock_admin_service import MockAdminService
from ..services.mock_auth_service import MockAuthService
from ..services.mock_demo_data_service import MockDemoDataService
from ..services.mock_telegram_service import MockTelegramService
from ..services.mock_database_service import MockDatabaseService


def register_all_services():
    """Register all mock services with the registry"""
    # Register core services
    mock_registry.register('analytics', MockAnalyticsService)
    mock_registry.register('payment', MockPaymentService)
    mock_registry.register('email', MockEmailService)
    
    # Register additional services
    mock_registry.register('ai', MockAIService)
    mock_registry.register('admin', MockAdminService)
    mock_registry.register('auth', MockAuthService)
    mock_registry.register('demo_data', MockDemoDataService)
    mock_registry.register('telegram', MockTelegramService)
    mock_registry.register('database', MockDatabaseService)


# Auto-register all services on import
register_all_services()
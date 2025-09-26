"""
Auto-Registration for Consolidated Mock Services

Registers all available mock services with the central registry.
"""

from .registry import mock_registry
from ..services.mock_analytics_service import MockAnalyticsService
from ..services.mock_payment_service import MockPaymentService
from ..services.mock_email_service import MockEmailService

def register_all_services():
    """Register all available mock services with the registry"""
    
    # Core services
    mock_registry.register_service("analytics", MockAnalyticsService)
    mock_registry.register_service("payment", MockPaymentService)
    mock_registry.register_service("email", MockEmailService)
    
    # TODO: Register remaining services as they are migrated
    # mock_registry.register_service("telegram", MockTelegramService)
    # mock_registry.register_service("auth", MockAuthService)
    # mock_registry.register_service("admin", MockAdminService)
    # mock_registry.register_service("ai", MockAIService)
    # mock_registry.register_service("demo_data", MockDemoDataService)
    # mock_registry.register_service("database", MockDatabaseService)

# Auto-register on import
register_all_services()
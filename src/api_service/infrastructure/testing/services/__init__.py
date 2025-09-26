"""
Mock Services Package
Mock implementations for all service protocols
"""

from src.mock_services.services import MockAnalyticsService
from src.mock_services.services import MockPaymentService
from src.mock_services.services import MockEmailService
from src.mock_services.services import MockTelegramService
from src.mock_services.services import MockAuthService
from src.mock_services.services import MockAdminService
from src.mock_services.services import MockAIService
from src.mock_services.services import MockDemoDataService

__all__ = [
    'MockAnalyticsService',
    'MockPaymentService', 
    'MockEmailService',
    'MockTelegramService',
    'MockAuthService',
    'MockAdminService',
    'MockAIService',
    'MockDemoDataService'
]
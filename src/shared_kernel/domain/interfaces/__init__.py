"""
Shared Domain Interfaces
"""

# Module service interfaces
from .analytics_service import AnalyticsService as AnalyticsModuleService
from .bot_service_service import BotService as BotModuleService
from .channels_service import ChannelService as ChannelsModuleService
from .identity_service import IdentityService as IdentityModuleService
from .payments_service import PaymentService as PaymentsModuleService

# Repository interfaces
from .repositories import AnalyticsRepository, PaymentRepository, UserRepository

# Service interfaces
from .services import AnalyticsService, AuthenticationService, PaymentService

__all__ = [
    # Repository interfaces
    "UserRepository",
    "PaymentRepository",
    "AnalyticsRepository",
    # Service interfaces
    "AuthenticationService",
    "PaymentService",
    "AnalyticsService",
    # Module service interfaces
    "AnalyticsModuleService",
    "IdentityModuleService",
    "PaymentsModuleService",
    "ChannelsModuleService",
    "BotModuleService",
]

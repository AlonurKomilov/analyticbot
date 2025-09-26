"""
Shared Domain Interfaces
"""

# Repository interfaces
from .repositories import UserRepository, PaymentRepository, AnalyticsRepository

# Service interfaces  
from .services import AuthenticationService, PaymentService, AnalyticsService

# Module service interfaces
from .analytics_service import AnalyticsService as AnalyticsModuleService
from .identity_service import IdentityService as IdentityModuleService
from .payments_service import PaymentService as PaymentsModuleService
from .channels_service import ChannelService as ChannelsModuleService
from .bot_service_service import BotService as BotModuleService

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
    "BotModuleService"
]

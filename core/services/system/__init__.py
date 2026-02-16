"""
System Services Module
======================

Core system services for infrastructure, authentication, caching, and utilities:
- analytics: Analytics fusion, statistical analysis, trend analysis
- alerts: Alert fusion, live monitoring, competitive intelligence
- optimization: Performance optimization and recommendations
- auth: Authentication service
- cache: Public cache, catalog, materialized views

Usage:
    from core.services.system import BackupService, EncryptionService
    from core.services.system.analytics import StatisticalAnalysisService
    from core.services.system.alerts import LiveMonitoringService
"""

from core.services.system.admin_bot_service import (
    AdminBotService,
    get_admin_bot_service,
)

# Core system services (at root of system/)
from core.services.system.backup_service import BackupService
from core.services.system.channel_service import ChannelData, ChannelService
from core.services.system.encryption_service import (
    EncryptionService,
    get_encryption_service,
)
from core.services.system.enhanced_delivery_service import EnhancedDeliveryService
from core.services.system.feature_gate_service import FeatureGateService
from core.services.system.marketplace_service import MarketplaceService
from core.services.system.owner_service import OwnerService
from core.services.system.rate_limit_monitoring_service import (
    DEFAULT_RATE_LIMITS,
    RateLimitConfig,
    RateLimitMonitoringService,
    RateLimitService,
    RateLimitStats,
    get_rate_limit_service,
)
from core.services.system.user_bot_service import UserBotService, get_user_bot_service

__all__ = [
    "BackupService",
    "EncryptionService",
    "get_encryption_service",
    "FeatureGateService",
    "MarketplaceService",
    "ChannelService",
    "ChannelData",
    "OwnerService",
    "AdminBotService",
    "get_admin_bot_service",
    "UserBotService",
    "get_user_bot_service",
    "EnhancedDeliveryService",
    "RateLimitMonitoringService",
    "get_rate_limit_service",
    "RateLimitService",
    "RateLimitStats",
    "RateLimitConfig",
    "DEFAULT_RATE_LIMITS",
]

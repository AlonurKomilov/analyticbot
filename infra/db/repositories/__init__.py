"""
Repository Implementations
==========================

Concrete implementations of repository interfaces for database access.
Organized by domain with asyncpg (high-performance) implementations.

Usage:
    from infra.db.repositories import MarketplaceServiceRepository
    repo = MarketplaceServiceRepository(pool)
    services = await repo.get_all_services()
"""

# Core repositories
from .admin_repository import AsyncpgAdminRepository, SQLAlchemyAdminRepository
from .analytics_repository import AsyncpgAnalyticsRepository
from .channel_repository import AsyncpgChannelRepository
from .payment_repository import AsyncpgPaymentRepository
from .plan_repository import AsyncpgPlanRepository
from .schedule_repository import AsyncpgDeliveryRepository, AsyncpgScheduleRepository
from .user_repository import AsyncpgUserRepository, SQLAlchemyUserRepository

# Alert system
from .alert_repository import AsyncpgAlertSubscriptionRepository, AsyncpgAlertSentRepository

# Credit system
from .credit_repository import CreditRepository

# Marketplace
from .marketplace_repository import MarketplaceRepository
from .marketplace_service_repository import MarketplaceServiceRepository

# Analytics
from .channel_daily_repository import AsyncpgChannelDailyRepository
from .channel_mtproto_repository import ChannelMTProtoRepository
from .post_repository import AsyncpgPostRepository
from .post_metrics_repository import AsyncpgPostMetricsRepository
from .stats_raw_repository import AsyncpgStatsRawRepository
from .shared_reports_repository import AsyncPgSharedReportsRepository

# User bot system
from .user_bot_repository import UserBotRepository
from .user_bot_repository_factory import UserBotRepositoryFactory
from .user_bot_service_repository import UserBotServiceRepository
from .user_bot_service_repository_factory import UserBotServiceRepositoryFactory

__all__ = [
    # Core
    "AsyncpgUserRepository",
    "SQLAlchemyUserRepository",
    "AsyncpgAdminRepository",
    "SQLAlchemyAdminRepository",
    "AsyncpgScheduleRepository",
    "AsyncpgDeliveryRepository",
    "AsyncpgAnalyticsRepository",
    "AsyncpgChannelRepository",
    "AsyncpgPaymentRepository",
    "AsyncpgPlanRepository",
    # Alert
    "AsyncpgAlertSubscriptionRepository",
    "AsyncpgAlertSentRepository",
    # Credit
    "CreditRepository",
    # Marketplace
    "MarketplaceRepository",
    "MarketplaceServiceRepository",
    # Analytics
    "AsyncpgChannelDailyRepository",
    "ChannelMTProtoRepository",
    "AsyncpgPostRepository",
    "AsyncpgPostMetricsRepository",
    "AsyncpgStatsRawRepository",
    "AsyncPgSharedReportsRepository",
    # User Bot
    "UserBotRepository",
    "UserBotRepositoryFactory",
    "UserBotServiceRepository",
    "UserBotServiceRepositoryFactory",
]

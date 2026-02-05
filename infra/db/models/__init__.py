# infra/db/models/__init__.py
"""
Database ORM Models
===================

Organized by domain:
- analytics/   - Channels, posts, metrics, stats
- credits/     - User credits, transactions, achievements
- marketplace/ - Services, subscriptions, items, bundles
- owner/       - Admin panel models
- users/       - User accounts, plans, alerts

Legacy files (to be migrated):
- database_models.py - Core table definitions (SQLAlchemy Core)
- user_bot_orm.py - Bot credentials, MTProto settings
- user_bot_service_orm.py - Bot moderation features
- bot_health_orm.py - Bot health metrics
- telegram_storage.py - Telegram media storage
"""

# Analytics models
from .analytics import (
    ChannelDailyORM,
    ChannelORM,
    ChannelStatsCacheORM,
    PostMetricsORM,
    PostORM,
    StatsRawORM,
)
from .base import Base

# Health models
from .bot_health_orm import BotHealthMetricOrm

# Credit system models
from .credits import (
    AchievementORM,
    CreditPackageORM,
    CreditServiceORM,
    CreditTransactionORM,
    UserAchievementORM,
    UserCreditsORM,
    UserReferralORM,
)
from .database_models import metadata

# Marketplace models
from .marketplace import (
    BundleItemORM,
    ItemReviewORM,
    MarketplaceBundleORM,
    MarketplaceCategoryORM,
    MarketplaceItemORM,
    MarketplaceServiceORM,
    ServiceUsageLogORM,
    UserPurchaseORM,
    UserServiceSubscriptionORM,
)

# Telegram storage models
from .telegram_storage import TelegramMedia, UserStorageChannel

# Bot models (legacy location)
from .user_bot_orm import (
    AdminBotActionORM,
    ChannelMTProtoSettings,
    MTProtoAuditLog,
    UserBotCredentialsORM,
)

# Bot service models (legacy location)
from .user_bot_service_orm import (
    UserBotBannedWordORM,
    UserBotInviteTrackingORM,
    UserBotServiceLogORM,
    UserBotSettingsORM,
    UserBotWarningORM,
    UserBotWelcomeMessageORM,
)

# User models
from .users import (
    AlertSentORM,
    PlanORM,
    SubscriptionORM,
    UserAlertPreferenceORM,
    UserORM,
)

__all__ = [
    # Core
    "metadata",
    "Base",
    # Analytics
    "ChannelORM",
    "PostORM",
    "PostMetricsORM",
    "StatsRawORM",
    "ChannelDailyORM",
    "ChannelStatsCacheORM",
    # Credits
    "UserCreditsORM",
    "CreditTransactionORM",
    "CreditPackageORM",
    "CreditServiceORM",
    "AchievementORM",
    "UserAchievementORM",
    "UserReferralORM",
    # Marketplace
    "MarketplaceServiceORM",
    "UserServiceSubscriptionORM",
    "ServiceUsageLogORM",
    "MarketplaceItemORM",
    "UserPurchaseORM",
    "ItemReviewORM",
    "MarketplaceBundleORM",
    "BundleItemORM",
    "MarketplaceCategoryORM",
    # Users
    "UserORM",
    "PlanORM",
    "SubscriptionORM",
    "UserAlertPreferenceORM",
    "AlertSentORM",
    # Bot
    "UserBotCredentialsORM",
    "AdminBotActionORM",
    "MTProtoAuditLog",
    "ChannelMTProtoSettings",
    # Bot services
    "UserBotSettingsORM",
    "UserBotBannedWordORM",
    "UserBotInviteTrackingORM",
    "UserBotWarningORM",
    "UserBotServiceLogORM",
    "UserBotWelcomeMessageORM",
    # Health
    "BotHealthMetricOrm",
    # Storage
    "UserStorageChannel",
    "TelegramMedia",
]

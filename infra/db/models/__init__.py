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

from .database_models import metadata
from .base import Base

# Analytics models
from .analytics import (
    ChannelORM,
    PostORM,
    PostMetricsORM,
    StatsRawORM,
    ChannelDailyORM,
    ChannelStatsCacheORM,
)

# Credit system models
from .credits import (
    UserCreditsORM,
    CreditTransactionORM,
    CreditPackageORM,
    CreditServiceORM,
    AchievementORM,
    UserAchievementORM,
    UserReferralORM,
)

# Marketplace models
from .marketplace import (
    MarketplaceServiceORM,
    UserServiceSubscriptionORM,
    ServiceUsageLogORM,
    MarketplaceItemORM,
    UserPurchaseORM,
    ItemReviewORM,
    MarketplaceBundleORM,
    BundleItemORM,
    MarketplaceCategoryORM,
)

# User models
from .users import (
    UserORM,
    PlanORM,
    SubscriptionORM,
    UserAlertPreferenceORM,
    AlertSentORM,
)

# Bot models (legacy location)
from .user_bot_orm import (
    UserBotCredentialsORM,
    AdminBotActionORM,
    MTProtoAuditLog,
    ChannelMTProtoSettings,
)

# Bot service models (legacy location)
from .user_bot_service_orm import (
    UserBotSettingsORM,
    UserBotBannedWordORM,
    UserBotInviteTrackingORM,
    UserBotWarningORM,
    UserBotServiceLogORM,
    UserBotWelcomeMessageORM,
)

# Health models
from .bot_health_orm import BotHealthMetricOrm

# Telegram storage models
from .telegram_storage import UserStorageChannel, TelegramMedia

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

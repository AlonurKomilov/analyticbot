# Database Organization Guide

## Overview

The database layer follows Clean Architecture principles with a well-organized folder structure that supports easy extension for marketplace services.

## Folder Structure

```
infra/db/
├── __init__.py
├── connection.py           # Database connection utilities
├── connection_manager.py   # Connection pooling and management
├── health_utils.py         # Health check utilities
├── metadata.py             # SQLAlchemy metadata
├── performance.py          # Query performance monitoring
├── sqlite_engine.py        # SQLite support (testing)
│
├── adapters/               # Repository adapters (Clean Architecture)
│   └── mtproto_repository_adapter.py
│
├── alembic/                # Database migrations
│   ├── env.py
│   └── versions/           # Migration files (0001-0054+)
│
├── init/                   # Database initialization scripts
│
├── migrations/             # Legacy SQL migrations
│
├── models/                 # ORM Models (organized by domain)
│   ├── __init__.py         # Main exports
│   ├── base.py             # Base ORM class
│   │
│   ├── analytics/          # 📊 Analytics domain
│   │   ├── __init__.py
│   │   └── analytics_orm.py
│   │       ├── ChannelORM
│   │       ├── PostORM
│   │       ├── PostMetricsORM
│   │       ├── StatsRawORM
│   │       ├── ChannelDailyORM
│   │       └── ChannelStatsCacheORM
│   │
│   ├── credits/            # 💰 Credit system domain
│   │   ├── __init__.py
│   │   └── credit_orm.py
│   │       ├── UserCreditsORM
│   │       ├── CreditTransactionORM
│   │       ├── CreditPackageORM
│   │       ├── CreditServiceORM
│   │       ├── AchievementORM
│   │       ├── UserAchievementORM
│   │       └── UserReferralORM
│   │
│   ├── marketplace/        # 🏪 Marketplace domain
│   │   ├── __init__.py
│   │   └── marketplace_orm.py
│   │       ├── MarketplaceCategoryORM
│   │       ├── MarketplaceServiceORM
│   │       ├── UserServiceSubscriptionORM
│   │       ├── ServiceUsageLogORM
│   │       ├── MarketplaceItemORM
│   │       ├── UserPurchaseORM
│   │       ├── ItemReviewORM
│   │       ├── MarketplaceBundleORM
│   │       └── BundleItemORM
│   │
│   ├── users/              # 👤 User domain
│   │   ├── __init__.py
│   │   └── users_orm.py
│   │       ├── UserORM
│   │       ├── PlanORM
│   │       ├── SubscriptionORM
│   │       ├── UserAlertPreferenceORM
│   │       └── AlertSentORM
│   │
│   ├── owner/              # 🔐 Admin panel domain
│   │   ├── __init__.py
│   │   ├── owner_orm.py
│   │   └── owner_mapper.py
│   │
│   └── (legacy files)      # To be migrated
│       ├── database_models.py
│       ├── user_bot_orm.py
│       ├── user_bot_service_orm.py
│       ├── bot_health_orm.py
│       └── telegram_storage.py
│
└── repositories/           # Repository implementations
    ├── __init__.py
    ├── admin_repository.py
    ├── alert_repository.py
    ├── analytics_repository.py
    ├── channel_repository.py
    ├── credit_repository.py
    ├── marketplace_repository.py
    ├── marketplace_service_repository.py
    ├── payment_repository.py
    ├── post_repository.py
    ├── user_repository.py
    └── ...
```

## How to Add a New Marketplace Service

### 1. Database Level

No migration needed! Services are stored in `marketplace_services` table.

```python
# Insert via repository or migration
INSERT INTO marketplace_services (
    service_key,           # Unique identifier: 'my_new_service'
    name,                  # Display name: 'My New Service'
    description,           # Full description
    category,              # 'bot_service', 'mtproto_services', 'ai_services'
    price_credits_monthly, # e.g., 100
    price_credits_yearly,  # e.g., 1000 (optional, ~17% off)
    features,              # JSONB: ["Feature 1", "Feature 2"]
    usage_quota_daily,     # NULL = unlimited, or integer
    usage_quota_monthly,   # NULL = unlimited, or integer
    requires_bot,          # Does it need bot connection?
    requires_mtproto,      # Does it need MTProto?
    is_active,             # Enable/disable
) VALUES (...);
```

### 2. Service Implementation

Create a new service following the `BaseMTProtoService` pattern:

```python
# core/services/myservice/my_new_service.py
from core.services.mtproto.features.base_mtproto_service import BaseMTProtoService

class MyNewService(BaseMTProtoService):
    SERVICE_KEY = "my_new_service"
    
    async def execute(self, user_id: int, **params):
        # Check feature access (subscription + quota)
        access = await self.check_access(user_id)
        if not access.allowed:
            return access.error
        
        # Do the work
        result = await self._do_work(**params)
        
        # Log usage
        await self.log_usage(user_id, "action_name", success=True)
        
        return result
```

### 3. Register in DI Container

```python
# apps/di/containers.py
from core.services.myservice import MyNewService

class Container:
    my_new_service = providers.Factory(
        MyNewService,
        marketplace_repo=marketplace_service_repository,
        mtproto_pool=mtproto_pool,
    )
```

## Database Tables by Worker

### Bot Worker Tables
- `user_bot_credentials` - Bot tokens, MTProto credentials
- `user_bot_settings` - Per-chat moderation settings
- `user_bot_banned_words` - Banned word lists
- `user_bot_warnings` - User warnings
- `user_bot_moderation_log` - Moderation actions
- `user_bot_invite_tracking` - Invite tracking
- `user_bot_welcome_messages` - Welcome messages
- `bot_health_metrics` - Health monitoring

### MTProto Worker Tables
- `posts` - Collected messages
- `post_metrics` - Time-series engagement data
- `stats_raw` - Raw API responses
- `channel_daily` - Daily aggregates
- `mtproto_audit_log` - Security audit trail
- `channel_mtproto_settings` - Per-channel settings

### AI Worker Tables
Uses marketplace infrastructure:
- `marketplace_services` - Service definitions
- `user_service_subscriptions` - User subscriptions
- `service_usage_log` - Usage tracking

### Marketplace Tables
- `marketplace_services` - Subscription services
- `user_service_subscriptions` - User subscriptions
- `service_usage_log` - Usage logging
- `marketplace_items` - One-time purchase items
- `user_purchases` - User purchases
- `item_reviews` - Product reviews
- `marketplace_bundles` - Bundle deals
- `bundle_items` - Bundle contents
- `marketplace_categories` - Categories

### Credit System Tables
- `user_credits` - User balances
- `credit_transactions` - Transaction history
- `credit_packages` - Purchasable packages
- `credit_services` - Per-use services
- `achievements` - Achievement definitions
- `user_achievements` - User progress
- `user_referrals` - Referral tracking

## Best Practices

1. **Always use ORM models** for new tables
2. **Create migrations** with Alembic for schema changes
3. **Use repositories** for data access, never raw SQL in services
4. **Follow naming conventions**: `snake_case` for tables, `PascalCaseORM` for models
5. **Add indexes** for frequently queried columns
6. **Use JSONB** for flexible metadata (column name: `extra_data`)
7. **Add foreign key constraints** for referential integrity
8. **Include timestamps** (`created_at`, `updated_at`) on all tables

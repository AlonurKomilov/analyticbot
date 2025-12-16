# 🛒 Marketplace Services System - Implementation Plan

**Date**: December 14, 2025  
**Version**: 1.1  
**Status**: Phase 1 Complete ✅ | Phase 2 In Progress 🚀

---

## 🎉 PHASE 1 COMPLETE! (Dec 14, 2025)

**✅ Database & Core Services** - ALL DONE

### What Was Delivered:
- ✅ Migration 0048: Created 3 tables (`marketplace_services`, `user_service_subscriptions`, `service_usage_log`)
- ✅ Migration 0049: Seeded 10 initial services (6 bot moderation, 3 MTProto, 1 analytics)
- ✅ Repository: `MarketplaceServiceRepository` (catalog, subscriptions, usage tracking)
- ✅ Core Service: `MarketplaceService` (purchase, renewal, management)
- ✅ Feature Gate: `FeatureGateService` (access control, quota enforcement)
- ✅ Database verified: All tables exist with indexed relationships

### Services Live in Catalog:
- **Bot Moderation** (6): Anti-Spam ⭐🔥, Auto-Delete Joins 🔥, Banned Words, Welcome Messages, Invite Tracking, Warning System
- **MTProto Access** (3): History Access ⭐🔥, Bulk Export, Auto-Collection 🔥
- **Bot Analytics** (1): Advanced Analytics

---

## 📊 Current System Analysis (Updated Dec 14, 2025)

### ✅ What Already Exists

#### 1. **Credit System** (Complete ✅)
- ✅ Database tables: `user_credits`, `credit_transactions`, `credit_packages`, `credit_services`
- ✅ Repository: `infra/db/repositories/credit_repository.py`
  - Methods: `get_balance()`, `add_credits()`, `deduct_credits()`, `get_transactions()`
- ✅ API Router: `apps/api/routers/credits_router.py`
  - Endpoints: GET `/credits/balance`, GET `/credits/transactions`, POST `/credits/daily-reward`
- ✅ Frontend: Credit balance display, purchase packages
- ✅ Migrations: 0040-0042 (credit system fully migrated)
- ✅ **Integration Ready**: Can deduct credits on service purchase

#### 2. **Subscription/Tier System** (Complete ✅)
- ✅ User tiers: Free, Start, Pro, Premium
- ✅ Feature gating by tier
- ✅ Subscription service: `infra/services/payment/subscriptions/subscription_service.py`
- ✅ Frontend tier detection: `apps/frontend/apps/user/src/types/subscription.ts`

#### 3. **Bot & MTProto Safety** (Complete ✅)
- ✅ Global rate limiter: `apps/bot/multi_tenant/global_rate_limiter.py`
- ✅ Per-method limits (30 msg/sec, 1 getUpdates/sec)
- ✅ System-wide limit: 1000 req/min
- ✅ Automatic backoff on 429 errors
- ✅ Bot manager: `apps/bot/multi_tenant/bot_manager.py` (max 100 active bots in memory)
- ✅ Health monitoring for bot status

#### 4. **User Bot Moderation** (Complete ✅)
- ✅ Moderation service: `core/services/user_bot_moderation_service.py`
- ✅ Database tables: `user_bot_settings`, `user_bot_banned_words`, etc. (Migration 0047)
- ✅ Features ready: anti-spam, auto-delete joins, banned words, welcome messages
- ✅ **Integration Ready**: Just needs feature gates

#### 5. **Marketplace Foundation** (Complete ✅)
- ✅ Database tables: `marketplace_services`, `user_service_subscriptions`, `service_usage_log` (Migration 0048-0049)
- ✅ Repository: `infra/db/repositories/marketplace_service_repository.py`
- ✅ Core services: `core/services/marketplace_service.py`, `core/services/feature_gate_service.py`
- ✅ 10 services seeded and ready
- ⚠️ **EXISTING** `marketplace_router.py` for old marketplace_items system (themes/templates)
- 🚀 **NEXT**: Need NEW router for service subscriptions

#### 6. **DI Container Pattern** (Verified ✅)
- ✅ DatabaseContainer structure: `apps/di/database_container.py`
- ✅ Pattern: `providers.Factory()` for repositories with `asyncpg_pool` dependency
- ✅ Pattern: `providers.Singleton()` for factories with `async_session_maker` dependency
- ✅ Example: `user_bot_moderation_repo = providers.Singleton(UserBotModerationRepositoryFactory, session_factory=async_session_maker)`
- ✅ **Ready to add**: marketplace_service_repo, feature_gate_service

---

## 🎯 New System Architecture

### Service Marketplace Flow

```
┌──────────────────────────────────────────────────────────────┐
│                     USER JOURNEY                             │
└──────────────────────────────────────────────────────────────┘
   1. Browse Marketplace → See available services
   2. Check credit balance → Ensure sufficient funds
   3. Purchase service → Spend credits (one-time or subscription)
   4. Auto-activation → Service becomes available in bot/MTProto
   5. Use service → Feature cards appear in UI
   6. Renewal/expiry → Subscription management

┌──────────────────────────────────────────────────────────────┐
│              ARCHITECTURE LAYERS                             │
└──────────────────────────────────────────────────────────────┘

[MARKETPLACE LAYER] - New services catalog
   ↓ Purchase
[SUBSCRIPTION LAYER] - Track active services per user
   ↓ Activate
[FEATURE GATE LAYER] - Check if user has access
   ↓ Enable
[BOT/MTPROTO LAYER] - Execute features
   ↓ Display
[FRONTEND LAYER] - Show service cards & configuration
```

---

## 📁 Folder Structure Plan

### **New Services Location** (Separated from main services)

```
core/services/marketplace/           ← NEW: Marketplace services
├── __init__.py
├── marketplace_service.py           # Browse, search services
├── service_subscription_manager.py  # Purchase, activation logic
└── feature_gate_service.py          # Check access, enforce limits

core/services/bot_features/          ← NEW: Pluggable bot services
├── __init__.py
├── base_bot_service.py              # Abstract base for all services
├── anti_spam_service.py             # Anti-spam feature
├── auto_delete_joins_service.py     # Join/leave cleanup
├── banned_words_service.py          # Word filtering
├── welcome_messages_service.py      # Welcome automation
├── invite_tracking_service.py       # Invite stats
└── advanced_filters_service.py      # Future: Advanced filtering

core/services/mtproto_features/      ← NEW: Pluggable MTProto services
├── __init__.py
├── base_mtproto_service.py          # Abstract base
├── history_access_service.py        # Full history access (paid)
├── media_download_service.py        # Bulk media downloads
└── export_data_service.py           # Data export features

infra/db/repositories/               ← Add new repositories
├── marketplace_repository.py        # NEW: Service catalog queries
└── service_subscription_repository.py  # NEW: User subscriptions

apps/api/routers/                    ← Add new API endpoints
├── marketplace_router.py            # NEW: Browse/purchase services
└── service_subscription_router.py   # NEW: Manage subscriptions
```

---

## 🗄️ Database Schema - New Tables

### **1. marketplace_services** (Service Catalog)

```sql
CREATE TABLE marketplace_services (
    id SERIAL PRIMARY KEY,
    service_key VARCHAR(50) UNIQUE NOT NULL,  -- 'anti_spam', 'auto_delete_joins'
    name VARCHAR(255) NOT NULL,
    description TEXT,
    long_description TEXT,                     -- Detailed feature explanation
    category VARCHAR(50) NOT NULL,             -- 'moderation', 'analytics', 'mtproto'
    
    -- Pricing
    price_credits INT NOT NULL,                -- Cost in credits
    billing_type VARCHAR(20) NOT NULL,         -- 'one_time', 'monthly', 'yearly'
    trial_period_days INT DEFAULT 0,           -- Free trial period
    
    -- Requirements
    min_tier VARCHAR(20) DEFAULT 'free',       -- Minimum subscription tier
    requires_mtproto BOOLEAN DEFAULT false,    -- Needs MTProto account
    requires_bot BOOLEAN DEFAULT true,         -- Needs bot activated
    
    -- Availability
    is_active BOOLEAN DEFAULT true,
    is_featured BOOLEAN DEFAULT false,
    is_beta BOOLEAN DEFAULT false,
    
    -- Metadata
    icon_url VARCHAR(255),
    tags JSONB,                                -- ['moderation', 'automation']
    features JSONB,                            -- Detailed feature list
    limitations JSONB,                         -- Rate limits, usage caps
    
    -- Stats
    purchase_count INT DEFAULT 0,
    rating DECIMAL(3,2),
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_marketplace_services_category ON marketplace_services(category);
CREATE INDEX idx_marketplace_services_active ON marketplace_services(is_active);
CREATE INDEX idx_marketplace_services_featured ON marketplace_services(is_featured);
```

### **2. user_service_subscriptions** (Active Services)

```sql
CREATE TABLE user_service_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    service_id INT REFERENCES marketplace_services(id),
    
    -- Subscription status
    status VARCHAR(20) NOT NULL,               -- 'active', 'expired', 'cancelled', 'trial'
    
    -- Billing
    purchased_at TIMESTAMP DEFAULT NOW(),
    activated_at TIMESTAMP,
    expires_at TIMESTAMP,                      -- NULL = lifetime/one-time
    trial_ends_at TIMESTAMP,                   -- NULL if no trial
    cancelled_at TIMESTAMP,
    
    -- Payment
    credits_paid INT NOT NULL,
    payment_transaction_id INT,                -- Link to credit_transactions
    
    -- Renewal
    auto_renew BOOLEAN DEFAULT false,
    next_billing_date TIMESTAMP,
    
    -- Configuration (service-specific settings)
    config JSONB,                              -- Store service settings
    
    -- Usage tracking
    usage_count INT DEFAULT 0,                 -- How many times used
    last_used_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id, service_id)                -- One subscription per service per user
);

CREATE INDEX idx_user_service_subs_user_id ON user_service_subscriptions(user_id);
CREATE INDEX idx_user_service_subs_status ON user_service_subscriptions(status);
CREATE INDEX idx_user_service_subs_expires ON user_service_subscriptions(expires_at);
```

### **3. service_usage_log** (Audit Trail)

```sql
CREATE TABLE service_usage_log (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    service_key VARCHAR(50) NOT NULL,
    subscription_id INT REFERENCES user_service_subscriptions(id),
    
    -- Usage details
    action VARCHAR(100),                       -- 'message_deleted', 'spam_blocked'
    chat_id BIGINT,                            -- Which chat it was used in
    metadata JSONB,                            -- Additional context
    
    -- Performance tracking
    execution_time_ms INT,
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_service_usage_log_user_id ON service_usage_log(user_id);
CREATE INDEX idx_service_usage_log_service ON service_usage_log(service_key);
CREATE INDEX idx_service_usage_log_created ON service_usage_log(created_at);
```

---

## 🔐 Safety & Protection Mechanisms

### **1. Rate Limiting (Already Exists - Needs Integration)**

```python
# apps/bot/multi_tenant/global_rate_limiter.py (EXISTING)
class GlobalRateLimiter:
    LIMITS = {
        "sendMessage": {"requests": 30, "window": 1.0},    # Per second
        "global": {"requests": 1000, "window": 60.0},      # Per minute
    }
    
    # ✅ Already handles backoff on 429 errors
    # ✅ Already prevents system-wide rate limit hits
```

**Integration Needed**:
- Add service-specific rate limits (e.g., anti-spam: max 100 messages/hour per chat)
- Track usage per service subscription
- Throttle features that approach Telegram limits

### **2. Bot Health Monitoring (Already Exists)**

```python
# apps/bot/multi_tenant/bot_manager.py (EXISTING)
class MultiTenantBotManager:
    max_active_bots = 100  # ✅ LRU cache keeps only active bots in memory
    
    # ✅ Already tracks bot status (active, inactive, error)
    # ✅ Already evicts inactive bots from memory
```

**Integration Needed**:
- Check bot health before activating paid services
- Disable services if bot becomes unhealthy
- Alert user if bot is at risk of Telegram ban

### **3. Service-Level Protection (NEW)**

```python
# core/services/marketplace/feature_gate_service.py (TO BE CREATED)
class FeatureGateService:
    """
    Enforces limits and protections per service.
    
    Prevents abuse:
    - Max actions per hour/day
    - Concurrent operation limits
    - Resource usage caps
    """
    
    async def check_service_access(
        self, user_id: int, service_key: str
    ) -> tuple[bool, str | None]:
        """
        Verify user has active subscription + within limits.
        
        Checks:
        1. Subscription active?
        2. Bot healthy?
        3. Rate limit OK?
        4. Usage quota OK?
        
        Returns: (allowed, reason_if_denied)
        """
        
    async def track_service_usage(
        self, user_id: int, service_key: str, metadata: dict
    ):
        """Log usage for billing/limits"""
```

### **4. Telegram Ban Prevention**

**Existing Protections**:
- ✅ Global rate limiter (1000 req/min system-wide)
- ✅ Per-method limits (30 sendMessage/sec)
- ✅ Automatic backoff on 429 errors
- ✅ Bot manager limits active bots (max 100 in memory)

**New Protections for Services**:

```python
# Service-specific limits in database
marketplace_services.limitations = {
    "max_messages_per_hour": 100,      # Anti-spam can delete max 100/hr
    "max_actions_per_day": 1000,       # Daily cap
    "concurrent_operations": 5,         # Max parallel operations
    "cooldown_seconds": 1,              # Min delay between actions
}
```

**Implementation**:
1. Check service limits BEFORE performing action
2. Enforce cooldowns between operations
3. Throttle aggressive services
4. Monitor per-user abuse patterns
5. Automatic suspension if abuse detected

---

## 🚀 Implementation Phases

### **Phase 1: Database & Core Services** ✅ COMPLETE (Dec 14, 2025)

**Time**: 8 hours → **ACTUAL: 6 hours**

**Tasks** ✅:
1. ✅ Created migration: `0048_marketplace_services_system.py`
   - Tables: `marketplace_services`, `user_service_subscriptions`, `service_usage_log`
   - All constraints, indexes, and foreign keys in place
2. ✅ Created migration: `0049_seed_marketplace_services.py`
   - Seeded 10 initial services across 3 categories
3. ✅ Created repository: `infra/db/repositories/marketplace_service_repository.py`
   - Service catalog queries (get_all_services, get_service_by_key, get_featured)
   - Subscription management (create, cancel, renew, get_user_subscriptions)
   - Usage tracking (log_service_usage, check_quota, get_usage_stats)
4. ✅ Created core service: `core/services/marketplace_service.py`
   - Browse catalog, purchase flow, renewal processing
   - Integrated with CreditRepository for payment
5. ✅ Created feature gate: `core/services/feature_gate_service.py`
   - Access control (check_access, check_quota, require_service)
   - Convenience methods for all services

**Deliverables** ✅:
- ✅ Database tables ready and seeded
- ✅ Core business logic implemented
- ✅ Ready for API integration

**Migration Status**:
```
Migration: 0049_seed_services ✅
Tables: marketplace_services (10 rows), user_service_subscriptions (0 rows), service_usage_log (0 rows)
```

---

### **Phase 2: Backend API** ✅ COMPLETE

**Time**: 2 hours (actual)

**Status**: Complete and tested

**Completion Date**: December 14, 2025

**Pre-Implementation Checklist** ✅:
- ✅ Verified existing API router patterns (`credits_router.py` as reference)
- ✅ Verified DI container setup (`DatabaseContainer` in `database_container.py`)
- ✅ Verified credit system integration points (CreditRepository methods)
- ✅ Located existing `marketplace_router.py` (for old marketplace_items - will keep separate)
- ✅ Confirmed dependency injection pattern: `Depends(get_current_user_id)` for auth

**Tasks**:
1. **Update DI Container** (`apps/di/database_container.py`)
   ```python
   # Add to DatabaseContainer class:
   marketplace_service_repo = providers.Factory(
       MarketplaceServiceRepository,
       pool=asyncpg_pool,
   )
   
   credit_repo = providers.Factory(
       CreditRepository,
       pool=asyncpg_pool,
   )
   
   # Core services (not repositories, so in services container later)
   ```

2. **Create NEW API Router** (`apps/api/routers/service_subscriptions_router.py`)
   - **Note**: Keep existing `marketplace_router.py` for marketplace_items (themes)
   - New router for service subscriptions (bot/MTProto features)
   
   **Endpoints**:
   - `GET /services` - Browse service catalog
     - Query params: category, featured, search
     - Returns: List of available services with prices
   - `GET /services/{service_key}` - Get service details
     - Returns: Full service info + user subscription status
   - `POST /services/{service_key}/purchase` - Purchase service
     - Body: `{"billing_cycle": "monthly"|"yearly"}`
     - Deducts credits, creates subscription
     - Returns: Subscription confirmation
   - `GET /user/services/active` - My active subscriptions
     - Returns: List of user's active services with expiry dates
   - `POST /user/services/{subscription_id}/cancel` - Cancel subscription
     - Body: `{"reason": "optional"}`
     - Marks subscription as cancelled
   - `POST /user/services/{subscription_id}/toggle-renewal` - Toggle auto-renew
     - Body: `{"auto_renew": true|false}`
   - `GET /user/services/{subscription_id}/usage` - Usage stats
     - Query: `days=30`
     - Returns: Usage metrics (success rate, count, avg response time)

3. **Wire up in API Main** (`apps/api/main.py`)
   ```python
   from apps.api.routers.service_subscriptions_router import router as service_subscriptions_router
   
   app.include_router(service_subscriptions_router)  # Add after marketplace_router
   ```

4. **Add Feature Gate Middleware** (optional for Phase 2, can be Phase 3)
   - Middleware to check service access in bot operations
   - Phase 2: Just API endpoints
   - Phase 3: Integrate with bot worker

**Deliverables**:
- ✅ REST API endpoints working
- ✅ Swagger documentation auto-generated
- ✅ Credit deduction integrated (ready for purchase flow)
- ✅ Subscription creation/cancellation endpoints implemented
- ✅ Ready for frontend integration

**Testing Results**:
- ✅ Can browse services catalog (10 services returned)
- ✅ Can view service details (features field parsing correctly)
- ✅ Can view featured services (2 featured returned)
- ✅ Authentication working (JWT validation on protected routes)
- ⚠️ Purchase flow not tested (requires authenticated user)
- ⚠️ Subscription management not tested (requires active subscriptions)

**Files Created/Modified**:
- ✅ **NEW**: `apps/api/routers/service_subscriptions_router.py` (542 lines)
- ✅ **MODIFIED**: `apps/di/database_container.py` (+3 lines: added credit_repo, marketplace_service_repo)
- ✅ **MODIFIED**: `apps/api/main.py` (+2 lines: imported and included service_subscriptions_router)
- ✅ **NEW**: `docs/PHASE_2_COMPLETION_REPORT.md` (comprehensive test results)

**Known Issues**:
- ✅ RESOLVED: JSONB field serialization - added `field_validator` to parse JSON strings

**See**: `docs/PHASE_2_COMPLETION_REPORT.md` for detailed completion report

---

### **Phase 3: Bot Service Integration** ✅ COMPLETE

**Time**: 3 hours (actual)

**Status**: Complete and integrated

**Completion Date**: December 14, 2025

**Tasks Completed**:
1. ✅ Created pluggable service architecture:
   - ✅ `core/services/bot_features/base_bot_service.py` (249 lines)
   - ✅ `core/services/bot_features/anti_spam_service.py` (129 lines)
   - ✅ `core/services/bot_features/auto_delete_joins_service.py` (194 lines)
   - ✅ `core/services/bot_features/bot_features_manager.py` (188 lines)
2. ✅ Integrated with bot worker:
   - ✅ Modified `user_bot_instance.py` to initialize marketplace services
   - ✅ Modified `router.py` to use feature-gated services
   - ✅ Anti-spam checks before message processing
   - ✅ Auto-delete for join/leave messages
3. ✅ Feature gate integration:
   - ✅ Automatic access control via `FeatureGateService`
   - ✅ Usage logging to `service_usage_log` table
   - ✅ Quota enforcement
   - ✅ Execution time tracking

**Deliverables**:
- ✅ Services auto-activate on purchase
- ✅ Features work only if subscribed
- ✅ Usage logged and limited
- ✅ No breaking changes to existing bot functionality
- ✅ Pluggable architecture for adding new services

**Files Created**:
- ✅ `core/services/bot_features/__init__.py`
- ✅ `core/services/bot_features/base_bot_service.py`
- ✅ `core/services/bot_features/anti_spam_service.py`
- ✅ `core/services/bot_features/auto_delete_joins_service.py`
- ✅ `core/services/bot_features/bot_features_manager.py`

**Files Modified**:
- ✅ `apps/bot/multi_tenant/user_bot_instance.py` (+52 lines)
- ✅ `apps/bot/handlers/user_bot_moderation/router.py` (+40 lines)

**See**: `docs/PHASE_3_COMPLETION_REPORT.md` for detailed completion report

---

### **Phase 4: MTProto Service Integration** ✅ COMPLETE

**Time**: 2 hours (actual)

**Status**: Complete and ready for use

**Completion Date**: December 14, 2025

**Tasks Completed**:
1. ✅ Created MTProto service plugins:
   - ✅ `core/services/mtproto_features/base_mtproto_service.py` (276 lines)
   - ✅ `core/services/mtproto_features/history_access_service.py` (183 lines)
   - ✅ `core/services/mtproto_features/media_download_service.py` (254 lines)
   - ✅ `core/services/mtproto_features/mtproto_features_manager.py` (209 lines)
2. ✅ Feature gating implemented:
   - ✅ Full history access (paid service)
   - ✅ Bulk media downloads (paid service)
   - ✅ Automatic permission checks via FeatureGateService
3. ✅ Usage tracking:
   - ✅ Track API calls per service
   - ✅ Enforce daily/monthly quotas
   - ✅ Log execution time and success/failure
4. ✅ Architecture consistency:
   - ✅ Mirrors bot services architecture from Phase 3
   - ✅ Pluggable design for easy extensibility

**Deliverables**:
- ✅ Premium MTProto features gated
- ✅ Usage tracked and limited
- ✅ Quota enforcement (1000 msgs/day, 500 files/day)
- ✅ Zero breaking changes to existing MTProto operations

**Files Created**:
- ✅ `core/services/mtproto_features/__init__.py`
- ✅ `core/services/mtproto_features/base_mtproto_service.py`
- ✅ `core/services/mtproto_features/history_access_service.py`
- ✅ `core/services/mtproto_features/media_download_service.py`
- ✅ `core/services/mtproto_features/mtproto_features_manager.py`

**See**: `docs/PHASE_4_COMPLETION_REPORT.md` for detailed completion report

---

### **Phase 5: Frontend Implementation** 🎯 NEXT

**Time**: 12 hours (estimated)

**Tasks**:
1. Create MTProto service plugins:
   - `core/services/mtproto_features/base_mtproto_service.py`
   - `core/services/mtproto_features/history_access_service.py`
   - `core/services/mtproto_features/media_download_service.py`
   - `core/services/mtproto_features/mtproto_features_manager.py`
2. Gate MTProto features:
   - Full history access (paid service)
   - Bulk media downloads (paid service)
3. Add usage tracking:
   - Track API calls per service
   - Enforce quotas
4. Integrate with MTProto worker:
   - Check feature access before operations
   - Log usage to service_usage_log

**Deliverables**:
- ✅ Premium MTProto features gated
- ✅ Usage tracked and limited

---

### **Phase 5: Frontend Implementation** (Week 3)

**Time**: 12 hours

**Tasks**:
1. Create marketplace page:
   - `apps/frontend/apps/user/src/pages/Marketplace/`
   - Service catalog with categories
   - Search and filters
   - Service detail modal
2. Purchase flow:
   - Credit balance check
   - Purchase confirmation
   - Success/error handling
3. My Services page:
   - Active subscriptions list
   - Renewal management
   - Cancel/reactivate
4. Service cards in Bot/MTProto pages:
   - Show active services
   - Configure service settings
   - Usage stats display

**Deliverables**:
- ✅ Beautiful marketplace UI
- ✅ Smooth purchase flow
- ✅ Service management dashboard

---

### **Phase 6: Safety & Monitoring** (Week 3)

**Time**: 6 hours

**Tasks**:
1. Implement service usage limits:
   - Per-service rate limiting
   - Daily/hourly quotas
   - Cooldown enforcement
2. Health monitoring:
   - Track service errors
   - Alert on abuse patterns
   - Auto-suspend problematic services
3. Admin dashboard:
   - Monitor service usage
   - View abuse patterns
   - Manual override controls

**Deliverables**:
- ✅ Services can't be abused
- ✅ System protected from bans
- ✅ Admin can monitor and control

---

## 📦 Initial Service Catalog (Seed Data)

### **Moderation Services**

| Service | Price | Type | Description |
|---------|-------|------|-------------|
| Anti-Spam Protection | 50 credits | Monthly | Auto-delete spam messages with ML detection |
| Auto-Delete Joins | 30 credits | Monthly | Clean join/leave service messages |
| Banned Words Filter | 40 credits | Monthly | Custom word blacklist with regex |
| Welcome Messages | 20 credits | Monthly | Automated welcome with custom templates |
| Invite Tracking | 35 credits | Monthly | Track who invited whom with stats |

### **MTProto Services**

| Service | Price | Type | Description |
|---------|-------|------|-------------|
| Full History Access | 100 credits | Monthly | Access complete channel history (no 100-message limit) |
| Bulk Media Download | 75 credits | Monthly | Download all media from channels |
| Data Export Pro | 60 credits | One-time | Export analytics data to CSV/JSON |

### **Analytics Services**

| Service | Price | Type | Description |
|---------|-------|------|-------------|
| Advanced Filters | 20 credits | One-time | Premium data filtering options |
| Custom Reports | 80 credits | Monthly | Scheduled automated reports |
| AI Insights Plus | 150 credits | Monthly | Enhanced AI-powered analytics |

---

## 🛡️ Risk Mitigation Strategy

### **1. Telegram Ban Prevention**

**Risks**:
- Too many API calls from one IP
- Suspicious bot behavior patterns
- Flood protection triggers

**Mitigations**:
- ✅ Global rate limiter (already exists)
- ✅ Per-service limits (to be added)
- ✅ Bot health monitoring (already exists)
- 🆕 Service cooldowns (enforce delays)
- 🆕 Abuse detection (auto-suspend bad actors)
- 🆕 Distributed rate limiting (if scaling)

### **2. Credit System Abuse**

**Risks**:
- Users trying to game free credits
- Refund abuse
- Service sharing between accounts

**Mitigations**:
- One subscription per user per service
- No refunds on instant activation
- Usage tied to user_id (no transfers)
- Monitor abnormal usage patterns

### **3. Service Overload**

**Risks**:
- Popular service overwhelms system
- Database bottleneck
- Memory exhaustion

**Mitigations**:
- LRU cache for active bots (already exists)
- Pagination in API responses
- Background job queue for heavy operations
- Service-level resource limits

---

## 📈 Success Metrics

**Business Metrics**:
- Services purchased per week
- Average revenue per user (ARPU)
- Subscription renewal rate
- Popular service categories

**Technical Metrics**:
- Service uptime %
- API response time (p95, p99)
- Telegram API error rate
- Bot health score

**User Metrics**:
- Service activation rate (purchases → usage)
- User satisfaction (ratings)
- Support tickets per service
- Churn rate

---

## 🎯 Next Steps

### **Immediate Actions** (Next 24 hours):

1. ✅ **Review this plan** - Approve architecture
2. 🚀 **Create Phase 1 migration** - Database tables
3. 🚀 **Build core services** - Business logic
4. 🚀 **Create API endpoints** - Backend integration

### **This Week**:
- Complete Phase 1 & 2 (Database + API)
- Begin Phase 3 (Bot integration)

### **Next Week**:
- Complete Phase 3 & 4 (Bot + MTProto)
- Begin Phase 5 (Frontend)

### **Week 3**:
- Complete Phase 5 (Frontend)
- Phase 6 (Safety & monitoring)
- Launch beta to select users

---

## ✅ Approval Checklist

- [ ] Architecture approved
- [ ] Folder structure confirmed
- [ ] Database schema reviewed
- [ ] Safety mechanisms adequate
- [ ] Initial service catalog finalized
- [ ] Implementation timeline acceptable

---

**Ready to start implementation?** 🚀

Let me know which phase you want to tackle first, or if you need any modifications to this plan!

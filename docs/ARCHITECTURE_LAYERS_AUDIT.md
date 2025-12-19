# Architecture Layers Audit & Refactoring Plan

## Current State Analysis

### Layer Definitions (Your System)

| Layer | Purpose | Current State |
|-------|---------|---------------|
| **apps/** | User-facing, multi-tenant, integration-ready | ⚠️ Mixed |
| **core/** | Business logic, marketplace services, integrable things | ⚠️ Mixed |
| **infra/** | Infrastructure, database, main system components | ✅ Mostly correct |

---

## 1. CURRENT STRUCTURE AUDIT

### apps/ Layer (User-facing, Multi-tenant)

```
apps/
├── api/                    # ✅ CORRECT - User API endpoints
├── bot/                    # ⚠️ MIXED
│   ├── multi_tenant/       # ✅ CORRECT - User bot management
│   │   ├── bot_manager.py
│   │   ├── user_bot_instance.py
│   │   └── session_pool.py
│   ├── services/           # ⚠️ MIXED - Some should be in core
│   │   ├── auth_service.py         # ✅ User-specific
│   │   ├── guard_service.py        # ✅ User-specific
│   │   └── subscription_service.py # ✅ User-specific
│   └── handlers/           # ✅ CORRECT - User bot handlers
│
├── mtproto/                # ⚠️ MIXED
│   ├── multi_tenant/       # ✅ CORRECT - User MTProto management
│   │   └── user_mtproto_service.py
│   ├── services/           # ⚠️ Should be in core?
│   │   └── data_collection_service.py  # Needs review
│   ├── collectors/         # ✅ CORRECT - User data collection
│   └── worker.py           # ✅ CORRECT - User worker
│
└── frontend/               # ✅ CORRECT - User frontend
```

### core/ Layer (Business Logic, Marketplace)

```
core/
├── marketplace/            # ✅ CORRECT LOCATION
│   ├── domain/             # ✅ Marketplace entities
│   ├── ports/              # ✅ Interfaces
│   └── services/           # ⚠️ INCOMPLETE
│       ├── marketplace_service.py  # ✅ Generic marketplace
│       └── feature_gate_service.py # ✅ Access control
│       # ❌ MISSING: mtproto/, bot/, ai/ service folders
│
├── services/               # ⚠️ WRONG ORGANIZATION
│   ├── bot/                # ❌ WRONG - Marketplace services here
│   │   ├── moderation/     # ❌ These are MARKETPLACE services!
│   │   │   ├── anti_spam_service.py
│   │   │   ├── auto_delete_joins_service.py
│   │   │   └── base_bot_service.py
│   │   ├── analytics/      # ⚠️ MIXED - Some basic, some marketplace
│   │   └── ...
│   │
│   ├── mtproto/            # ❌ WRONG - Marketplace services here
│   │   ├── features/       # ❌ These are MARKETPLACE services!
│   │   │   ├── history_access_service.py
│   │   │   ├── media_download_service.py
│   │   │   └── base_mtproto_service.py
│   │   └── mtproto_service.py  # ⚠️ UNCLEAR - basic or marketplace?
│   │
│   ├── ai/                 # ⚠️ MIXED
│   │   ├── ai_chat_service.py     # Could be marketplace
│   │   └── insights/              # Could be marketplace
│   │
│   └── system/             # ✅ CORRECT - System services
│
└── domain/                 # ✅ CORRECT - Core domain entities
```

### infra/ Layer (Infrastructure)

```
infra/
├── bot/                    # ✅ CORRECT - Bot infrastructure
│   ├── multi_tenant_bot_manager.py
│   └── user_bot_instance.py
│
├── marketplace/            # ✅ CORRECT - Marketplace DB
│   └── repositories/
│       ├── items.py
│       └── services.py
│
├── db/                     # ✅ CORRECT - Database infrastructure
├── cache/                  # ✅ CORRECT - Cache infrastructure
├── telegram/               # ✅ CORRECT - Telegram infrastructure
└── ...
```

---

## 2. PROBLEMS IDENTIFIED

### Problem 1: Marketplace Services in Wrong Location

| Service | Current Location | Should Be |
|---------|------------------|-----------|
| `anti_spam_service.py` | `core/services/bot/moderation/` | `core/marketplace/services/bot/` |
| `auto_delete_joins_service.py` | `core/services/bot/moderation/` | `core/marketplace/services/bot/` |
| `history_access_service.py` | `core/services/mtproto/features/` | `core/marketplace/services/mtproto/` |
| `media_download_service.py` | `core/services/mtproto/features/` | `core/marketplace/services/mtproto/` |
| `ai_chat_service.py` | `core/services/ai/` | `core/marketplace/services/ai/` |

### Problem 2: No Clear "Required Services" vs "Marketplace Services"

Currently no distinction between:
- **Required Services** (FREE by default - system needs them to work)
- **Marketplace Services** (FREE or PAID - user chooses to enable)

### Problem 3: core/services/ Confusion

`core/services/` contains:
- System services (should stay)
- Marketplace services (should move to `core/marketplace/services/`)

---

## 3. PROPOSED ARCHITECTURE

### Layer Responsibilities

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                 APPS LAYER                                   │
│                    (User-facing, Multi-tenant, Integration)                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  apps/bot/           │  apps/mtproto/        │  apps/api/                   │
│  - multi_tenant/     │  - multi_tenant/      │  - User API endpoints        │
│  - handlers/         │  - collectors/        │  - Auth, subscriptions       │
│  - User bot logic    │  - User MTProto logic │                              │
│                      │                        │                              │
│  ↓ Uses services from core/marketplace/      │                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                 CORE LAYER                                   │
│                    (Business Logic, Marketplace Services)                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  core/marketplace/                          │  core/domain/                 │
│  ├── domain/                                │  └── (Core entities)          │
│  │   └── entities.py                        │                               │
│  ├── services/                              │  core/ports/                  │
│  │   ├── marketplace_service.py             │  └── (Interfaces)             │
│  │   ├── feature_gate_service.py            │                               │
│  │   │                                      │                               │
│  │   ├── bot/          ← ALL BOT MARKETPLACE SERVICES                       │
│  │   │   ├── required/      (FREE - system needs)                           │
│  │   │   │   └── basic_moderation.py                                        │
│  │   │   └── premium/       (FREE or PAID - user choice)                    │
│  │   │       ├── anti_spam_service.py                                       │
│  │   │       ├── auto_delete_service.py                                     │
│  │   │       └── advanced_analytics.py                                      │
│  │   │                                      │                               │
│  │   ├── mtproto/      ← ALL MTPROTO MARKETPLACE SERVICES                   │
│  │   │   ├── required/      (FREE - system needs)                           │
│  │   │   │   ├── connection_service.py                                      │
│  │   │   │   ├── channel_info_service.py                                    │
│  │   │   │   └── basic_collection_service.py                                │
│  │   │   └── premium/       (FREE or PAID - user choice)                    │
│  │   │       ├── history_access_service.py                                  │
│  │   │       ├── media_download_service.py                                  │
│  │   │       ├── bulk_export_service.py                                     │
│  │   │       └── auto_collect_service.py                                    │
│  │   │                                      │                               │
│  │   ├── ai/           ← ALL AI MARKETPLACE SERVICES                        │
│  │   │   ├── required/                                                      │
│  │   │   │   └── basic_insights.py                                          │
│  │   │   └── premium/                                                       │
│  │   │       ├── content_optimizer.py                                       │
│  │   │       └── sentiment_analyzer.py                                      │
│  │   │                                      │                               │
│  │   ├── themes/       ← ALL THEME MARKETPLACE                              │
│  │   │   └── ...                            │                               │
│  │   │                                      │                               │
│  │   └── widgets/      ← ALL WIDGET MARKETPLACE                             │
│  │       └── ...                            │                               │
│  │                                          │                               │
│  └── adapters/                              │                               │
│      ├── bot_adapter.py                     │                               │
│      ├── mtproto_adapter.py                 │                               │
│      └── ai_adapter.py                      │                               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                INFRA LAYER                                   │
│                    (Infrastructure, Database, System Core)                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  infra/bot/           │  infra/mtproto/       │  infra/ai/                  │
│  - Bot infrastructure │  - MTProto infra      │  - AI infrastructure        │
│  - Session management │  - Connection pool    │  - Model management         │
│                       │                        │                             │
│  infra/db/            │  infra/marketplace/   │  infra/cache/               │
│  - Database repos     │  - Marketplace DB     │  - Redis/cache              │
│  - Migrations         │  - Service repos      │                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. SERVICE CLASSIFICATION

### Bot Services

| Service | Type | Price | Location |
|---------|------|-------|----------|
| Basic bot commands | Required | FREE (always) | `core/marketplace/services/bot/required/` |
| Channel management | Required | FREE (always) | `core/marketplace/services/bot/required/` |
| Anti-Spam Protection | Premium | FREE tier / PAID advanced | `core/marketplace/services/bot/premium/` |
| Auto-Delete Joins | Premium | FREE / PAID | `core/marketplace/services/bot/premium/` |
| Banned Words Filter | Premium | PAID | `core/marketplace/services/bot/premium/` |
| Welcome Messages | Premium | FREE / PAID | `core/marketplace/services/bot/premium/` |
| Advanced Analytics | Premium | PAID | `core/marketplace/services/bot/premium/` |

### MTProto Services

| Service | Type | Price | Location |
|---------|------|-------|----------|
| Session Connection | Required | FREE (always) | `core/marketplace/services/mtproto/required/` |
| Channel Info | Required | FREE (always) | `core/marketplace/services/mtproto/required/` |
| Basic Collection | Required | FREE (always) | `core/marketplace/services/mtproto/required/` |
| Health Monitoring | Required | FREE (always) | `core/marketplace/services/mtproto/required/` |
| History Access (full) | Premium | PAID | `core/marketplace/services/mtproto/premium/` |
| Media Download (bulk) | Premium | PAID | `core/marketplace/services/mtproto/premium/` |
| Bulk Export | Premium | PAID | `core/marketplace/services/mtproto/premium/` |
| Auto-Collection | Premium | FREE / PAID | `core/marketplace/services/mtproto/premium/` |

### AI Services

| Service | Type | Price | Location |
|---------|------|-------|----------|
| Basic Insights | Required | FREE (always) | `core/marketplace/services/ai/required/` |
| Content Optimizer | Premium | PAID | `core/marketplace/services/ai/premium/` |
| Sentiment Analyzer | Premium | PAID | `core/marketplace/services/ai/premium/` |
| Smart Replies | Premium | PAID | `core/marketplace/services/ai/premium/` |

---

## 5. MIGRATION PLAN

### Phase 1: Create New Structure in core/marketplace/

```bash
# Create new directories
core/marketplace/services/
├── bot/
│   ├── __init__.py
│   ├── required/           # System-required services (FREE always)
│   │   └── __init__.py
│   └── premium/            # Marketplace services (FREE or PAID)
│       └── __init__.py
├── mtproto/
│   ├── __init__.py
│   ├── required/
│   │   └── __init__.py
│   └── premium/
│       └── __init__.py
├── ai/
│   ├── __init__.py
│   ├── required/
│   │   └── __init__.py
│   └── premium/
│       └── __init__.py
├── themes/
│   └── __init__.py
└── widgets/
    └── __init__.py
```

### Phase 2: Move Services

| From | To |
|------|-----|
| `core/services/bot/moderation/anti_spam_service.py` | `core/marketplace/services/bot/premium/` |
| `core/services/bot/moderation/auto_delete_joins_service.py` | `core/marketplace/services/bot/premium/` |
| `core/services/mtproto/features/history_access_service.py` | `core/marketplace/services/mtproto/premium/` |
| `core/services/mtproto/features/media_download_service.py` | `core/marketplace/services/mtproto/premium/` |

### Phase 3: Create Required Services

Create new "required" services that the system needs:

**MTProto Required:**
- `core/marketplace/services/mtproto/required/connection_service.py`
- `core/marketplace/services/mtproto/required/channel_info_service.py`
- `core/marketplace/services/mtproto/required/health_service.py`
- `core/marketplace/services/mtproto/required/basic_collection_service.py`

**Bot Required:**
- `core/marketplace/services/bot/required/command_service.py`
- `core/marketplace/services/bot/required/channel_management_service.py`

### Phase 4: Update Imports

Update all files that import from old locations to use new paths.

### Phase 5: Update Database

Add `is_required` column to `marketplace_services` table:
- `is_required = true` → Always FREE, system needs it
- `is_required = false` → Can be FREE or PAID (user choice)

---

## 6. DATABASE SCHEMA UPDATE

```sql
ALTER TABLE marketplace_services ADD COLUMN is_required BOOLEAN DEFAULT false;
ALTER TABLE marketplace_services ADD COLUMN service_tier VARCHAR(20) DEFAULT 'premium';
-- service_tier: 'required' | 'premium'

-- Update required services
UPDATE marketplace_services 
SET is_required = true, service_tier = 'required', price_credits_monthly = 0
WHERE service_key IN (
    'mtproto_connection',
    'mtproto_channel_info', 
    'mtproto_health',
    'mtproto_basic_collection',
    'bot_commands',
    'bot_channel_management'
);
```

---

## 7. SUMMARY

### Current Problems:
1. ❌ Marketplace services are inside `core/services/` instead of `core/marketplace/services/`
2. ❌ No separation between "required" (always free) and "premium" services
3. ❌ Confusing folder names (`features/`, `moderation/`)

### Solution:
1. ✅ Move all marketplace services to `core/marketplace/services/{bot,mtproto,ai}/`
2. ✅ Create `required/` and `premium/` subfolders
3. ✅ Required services = FREE always (system needs them)
4. ✅ Premium services = FREE or PAID (marketplace choice)

### Benefits:
- **Clear separation**: apps/ uses services from core/marketplace/
- **Scalable**: Easy to add new services to marketplace
- **Isolated**: Marketplace is completely isolated
- **Flexible pricing**: Required = free, Premium = configurable

---

## Files to Move

### Bot Services
- [ ] `core/services/bot/moderation/anti_spam_service.py` → `core/marketplace/services/bot/premium/`
- [ ] `core/services/bot/moderation/auto_delete_joins_service.py` → `core/marketplace/services/bot/premium/`
- [ ] `core/services/bot/moderation/base_bot_service.py` → `core/marketplace/services/bot/`
- [ ] `core/services/bot/moderation/bot_features_manager.py` → `core/marketplace/services/bot/`

### MTProto Services
- [ ] `core/services/mtproto/features/history_access_service.py` → `core/marketplace/services/mtproto/premium/`
- [ ] `core/services/mtproto/features/media_download_service.py` → `core/marketplace/services/mtproto/premium/`
- [ ] `core/services/mtproto/features/base_mtproto_service.py` → `core/marketplace/services/mtproto/`
- [ ] `core/services/mtproto/features/mtproto_features_manager.py` → `core/marketplace/services/mtproto/`

### Imports to Update (estimate)
- ~20-30 files will need import updates

---

*Document generated: December 18, 2025*

# MTProto Services Audit & Integration Plan

## Executive Summary

This document provides a comprehensive audit of the current MTProto multi-tenant system and proposes an integration plan to prepare the platform for marketplace service scalability.

---

## Part 1: Current System Audit

### 1.1 MTProto Services Overview

| Service Key | Status | Backend | Frontend | DB Seeded | Category |
|-------------|--------|---------|----------|-----------|----------|
| `mtproto_history_access` | ✅ Implemented | ✅ | ✅ | ✅ | Marketplace (Premium) |
| `mtproto_media_download` | ✅ Implemented | ✅ | ✅ | ✅ | Marketplace (Premium) |
| `mtproto_bulk_export` | ⚠️ Partial | ❌ | ✅ | ✅ | Marketplace (Enterprise) |
| `mtproto_auto_collect` | ⚠️ Partial | ❌ | ✅ | ✅ | Marketplace (Premium) |

### 1.2 Backend Architecture

#### Core Services Location
```
/core/services/mtproto/
├── mtproto_service.py              # Core MTProto operations (channels, audit)
├── collection/                     # (Empty - placeholder for collection logic)
└── features/
    ├── __init__.py
    ├── base_mtproto_service.py     # Abstract base for marketplace services
    ├── history_access_service.py   # ✅ Full history access (mtproto_history_access)
    ├── media_download_service.py   # ✅ Media download (mtproto_media_download)
    └── mtproto_features_manager.py # Coordinates services with feature gates
```

#### API Routes Location
```
/apps/api/routers/
├── user_mtproto/
│   ├── router.py                   # Main aggregator
│   ├── status.py                   # GET /status
│   ├── setup.py                    # POST /setup, /verify, /qr-*
│   ├── verification.py             # POST /verify
│   ├── connection.py               # POST /connect, /disconnect, /test-connection
│   ├── toggle.py                   # POST /toggle
│   ├── channel_settings.py         # Channel-level MTProto settings
│   ├── deps.py                     # Dependencies
│   └── models.py                   # Pydantic models
└── user_mtproto_monitoring_router.py  # GET /monitoring/* endpoints
```

#### Infrastructure
```
/infra/
├── db/
│   ├── repositories/
│   │   └── marketplace_service_repository.py
│   └── alembic/versions/
│       ├── 0048_marketplace_services_system.py  # Core tables
│       ├── 0049_seed_marketplace_services.py    # Service definitions
│       ├── 0053_add_mtproto_media_download_service.py
│       └── 0054_add_ai_services_to_marketplace.py
└── marketplace/
    └── repositories/
        └── services.py                          # MarketplaceServiceRepository
```

### 1.3 Frontend Architecture

#### MTProto Monitoring Page
```
/apps/frontend/apps/user/src/pages/MTProtoMonitoringPage/
├── index.tsx                       # Main page
├── hooks.ts                        # Data fetching hooks
├── types.ts                        # TypeScript types
├── utils.ts                        # Utilities
└── components/
    ├── AccountInfoCard.tsx         # Account overview + quick actions
    ├── SessionHealthCard.tsx       # Session status
    ├── WorkerStatusCard.tsx        # Worker monitoring
    ├── CollectionProgressCard.tsx  # Collection statistics
    ├── CollectionControlCard.tsx   # Boost/speed controls
    ├── ChannelStatisticsCard.tsx   # Per-channel stats
    ├── IntervalBoostCard.tsx       # Collection interval boost
    ├── ActiveMTProtoServicesCard.tsx    # Active marketplace services
    └── AvailableMTProtoUpgradesCard.tsx # Available upgrades
```

#### Service Config Pages
```
/apps/frontend/apps/user/src/pages/services/configs/mtproto/
├── index.ts
├── HistoryAccessConfig.tsx         # mtproto_history_access config UI
├── AutoCollectConfig.tsx           # mtproto_auto_collect config UI
├── BulkExportConfig.tsx            # mtproto_bulk_export config UI
└── MediaDownloadConfig.tsx         # mtproto_media_download config UI
```

#### Service Registry
```
/apps/frontend/apps/user/src/features/marketplace/registry.tsx
```
- Contains `SERVICE_REGISTRY` with all service metadata
- Maps service keys to config components and icons

### 1.4 Database Schema (Marketplace)

```sql
-- Main service catalog
marketplace_services (
    id, service_key, name, description, short_description,
    price_credits_monthly, price_credits_yearly,
    category, subcategory, features,
    usage_quota_daily, usage_quota_monthly, rate_limit_per_minute,
    requires_bot, requires_mtproto, min_tier,
    icon, color, is_featured, is_popular, is_new, sort_order,
    is_active, is_beta, documentation_url, demo_video_url, metadata,
    active_subscriptions, total_subscriptions,
    created_at, updated_at
)

-- User subscriptions
user_service_subscriptions (
    id, user_id, service_id, billing_cycle, price_paid,
    status, expires_at, auto_renew,
    usage_count, last_usage_at,
    created_at, updated_at
)
```

---

## Part 2: Gap Analysis

### 2.1 ❌ Missing Backend Services

| Service | Issue | Priority |
|---------|-------|----------|
| `mtproto_bulk_export` | No `bulk_export_service.py` | HIGH |
| `mtproto_auto_collect` | No `auto_collect_service.py` | HIGH |

### 2.2 ❌ Missing System Services (Non-Marketplace)

These are **basic MTProto capabilities** that should be FREE for all MTProto users:

| System Service | Description | Priority |
|----------------|-------------|----------|
| `mtproto_system_health` | Session health check, connection diagnostics | CRITICAL |
| `mtproto_channel_admin_check` | Check if user is admin in channel | HIGH |
| `mtproto_channel_info` | Get channel metadata (title, description, members) | HIGH |
| `mtproto_member_count` | Get accurate member counts | MEDIUM |
| `mtproto_message_count` | Get total message count in channel | MEDIUM |
| `mtproto_permissions_check` | Check user permissions in channel | HIGH |

### 2.3 ⚠️ Architecture Issues

1. **No clear separation between System vs Marketplace services**
   - Current: All services are marketplace-based
   - Needed: Free system services + paid marketplace services

2. **Empty `/core/services/mtproto/collection/` folder**
   - Suggests collection logic was planned but not implemented

3. **Feature Manager only knows 4 services**
   - `mtproto_features_manager.py` hardcodes service list
   - Not extensible for future services

4. **No unified MTProto capability registry**
   - Services are scattered across frontend registry + backend + migrations

---

## Part 3: Integration Architecture Plan

### 3.1 Proposed Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      User MTProto System                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              LAYER 1: System Services (FREE)             │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │   │
│  │  │ Health      │ │ Admin Check │ │ Channel     │        │   │
│  │  │ Monitor     │ │ Service     │ │ Info        │        │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘        │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │   │
│  │  │ Permissions │ │ Member      │ │ Message     │        │   │
│  │  │ Check       │ │ Count       │ │ Count       │        │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         LAYER 2: Marketplace Services (PAID)             │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │   │
│  │  │ History     │ │ Media       │ │ Bulk        │        │   │
│  │  │ Access      │ │ Download    │ │ Export      │        │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘        │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │   │
│  │  │ Auto        │ │ Content     │ │ Sentiment   │        │   │
│  │  │ Collection  │ │ Analytics   │ │ Analysis    │        │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              LAYER 3: Core MTProto Engine                │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │  UserMTProtoService (Multi-tenant Pool Manager)  │   │   │
│  │  │  - Session management                             │   │   │
│  │  │  - Connection pooling                             │   │   │
│  │  │  - Rate limiting                                  │   │   │
│  │  │  - Error handling                                 │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Implementation Plan

#### Phase 1: System Services Foundation (Week 1-2)

**Create base system service structure:**

```
/core/services/mtproto/
├── system/                         # NEW: System services (FREE)
│   ├── __init__.py
│   ├── base_system_service.py      # Base class (no feature gate)
│   ├── health_check_service.py     # Connection diagnostics
│   ├── channel_info_service.py     # Get channel metadata
│   ├── admin_check_service.py      # Check admin status
│   ├── permissions_service.py      # Check permissions
│   └── stats_service.py            # Member/message counts
├── marketplace/                    # RENAME: features/ → marketplace/
│   ├── __init__.py
│   ├── base_marketplace_service.py # Base class (with feature gate)
│   ├── history_access_service.py
│   ├── media_download_service.py
│   ├── bulk_export_service.py      # NEW
│   └── auto_collect_service.py     # NEW
└── mtproto_service_registry.py     # NEW: Unified service registry
```

**Backend Tasks:**
- [ ] Create `base_system_service.py` (no feature gate required)
- [ ] Implement `health_check_service.py`
- [ ] Implement `channel_info_service.py`
- [ ] Implement `admin_check_service.py`
- [ ] Implement `permissions_service.py`
- [ ] Add API endpoints: `/user-mtproto/system/health`, `/system/channel-info`, etc.

#### Phase 2: Complete Marketplace Services (Week 2-3)

**Backend Tasks:**
- [ ] Implement `bulk_export_service.py`
- [ ] Implement `auto_collect_service.py`
- [ ] Update `mtproto_features_manager.py` to be dynamic

**Frontend Tasks:**
- [ ] Ensure all config UIs work with backend
- [ ] Add service status indicators

#### Phase 3: Unified Service Registry (Week 3-4)

**Create `mtproto_service_registry.py`:**

```python
class MTProtoServiceRegistry:
    """Unified registry for all MTProto services"""
    
    SYSTEM_SERVICES = {
        "mtproto_system_health": HealthCheckService,
        "mtproto_channel_info": ChannelInfoService,
        "mtproto_admin_check": AdminCheckService,
        "mtproto_permissions": PermissionsService,
        "mtproto_stats": StatsService,
    }
    
    MARKETPLACE_SERVICES = {
        "mtproto_history_access": HistoryAccessService,
        "mtproto_media_download": MediaDownloadService,
        "mtproto_bulk_export": BulkExportService,
        "mtproto_auto_collect": AutoCollectService,
    }
    
    @classmethod
    def get_service(cls, service_key: str, **kwargs):
        """Get service instance by key"""
        if service_key in cls.SYSTEM_SERVICES:
            return cls.SYSTEM_SERVICES[service_key](**kwargs)
        if service_key in cls.MARKETPLACE_SERVICES:
            return cls.MARKETPLACE_SERVICES[service_key](**kwargs)
        raise ValueError(f"Unknown service: {service_key}")
    
    @classmethod
    def is_system_service(cls, service_key: str) -> bool:
        return service_key in cls.SYSTEM_SERVICES
```

#### Phase 4: Plugin Architecture (Week 4-5)

**For future marketplace services, create plugin system:**

```python
# /core/services/mtproto/plugins/__init__.py

class MTProtoPlugin(ABC):
    """Base class for third-party MTProto plugins"""
    
    @property
    @abstractmethod
    def service_key(self) -> str: ...
    
    @property
    @abstractmethod
    def requires_subscription(self) -> bool: ...
    
    @abstractmethod
    async def execute(self, client: TelegramClient, **kwargs): ...
```

---

## Part 4: API Endpoints Plan

### 4.1 Current Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/user-mtproto/status` | Get MTProto status |
| POST | `/user-mtproto/setup` | Initiate setup |
| POST | `/user-mtproto/verify` | Verify code |
| POST | `/user-mtproto/connect` | Connect client |
| POST | `/user-mtproto/disconnect` | Disconnect client |
| POST | `/user-mtproto/test-connection` | Test connection |
| POST | `/user-mtproto/toggle` | Enable/disable |
| GET | `/user-mtproto/monitoring/*` | Monitoring endpoints |

### 4.2 Proposed New Endpoints

#### System Services (FREE)
```
GET  /user-mtproto/system/health           # Detailed health diagnostics
GET  /user-mtproto/system/channel/{id}     # Channel info
GET  /user-mtproto/system/channel/{id}/admins    # Check admins
GET  /user-mtproto/system/channel/{id}/permissions  # User permissions
GET  /user-mtproto/system/channel/{id}/stats     # Member/message counts
```

#### Marketplace Services (PAID)
```
POST /user-mtproto/services/{service_key}/run    # Run any marketplace service
GET  /user-mtproto/services/{service_key}/status # Service-specific status
GET  /user-mtproto/services/{service_key}/usage  # Usage stats
```

---

## Part 5: Frontend Changes

### 5.1 MTProto Dashboard Reorganization

```
MTProto Monitoring Page
├── 🔧 System Health Section (FREE)
│   ├── Session Health Card (existing)
│   ├── Connection Diagnostics Card (NEW)
│   └── Quick Health Check Button
│
├── 📊 Channel Overview Section (FREE)
│   ├── Channel Admin Status
│   ├── Channel Permissions
│   └── Basic Channel Stats
│
├── 🛒 Marketplace Services Section (PAID)
│   ├── Active Services Card (existing)
│   ├── Available Upgrades Card (existing)
│   └── Service Config Links
│
└── ⚡ Worker & Collection Section
    ├── Worker Status Card (existing)
    ├── Collection Progress Card (existing)
    └── Collection Controls (existing)
```

### 5.2 Service Config Page Updates

Add visual indicators for:
- System service (FREE badge)
- Marketplace service (tier badge)
- Backend implementation status

---

## Part 6: Migration Checklist

### Database Migrations Needed

- [ ] Add `is_system_service` column to `marketplace_services`
- [ ] Seed system services with `is_system_service = true`
- [ ] Update existing MTProto services with correct metadata

### Backend Files to Create

1. [ ] `/core/services/mtproto/system/__init__.py`
2. [ ] `/core/services/mtproto/system/base_system_service.py`
3. [ ] `/core/services/mtproto/system/health_check_service.py`
4. [ ] `/core/services/mtproto/system/channel_info_service.py`
5. [ ] `/core/services/mtproto/system/admin_check_service.py`
6. [ ] `/core/services/mtproto/system/permissions_service.py`
7. [ ] `/core/services/mtproto/system/stats_service.py`
8. [ ] `/core/services/mtproto/marketplace/bulk_export_service.py`
9. [ ] `/core/services/mtproto/marketplace/auto_collect_service.py`
10. [ ] `/core/services/mtproto/mtproto_service_registry.py`
11. [ ] `/apps/api/routers/user_mtproto/system.py` (new endpoints)

### Frontend Files to Update

1. [ ] Update `registry.tsx` with system service category
2. [ ] Create system service config components
3. [ ] Update MTProto monitoring page layout

---

## Part 7: Success Metrics

| Metric | Target | Timeline |
|--------|--------|----------|
| System services implemented | 5/5 | Week 2 |
| Marketplace services complete | 4/4 | Week 3 |
| API endpoint coverage | 100% | Week 3 |
| Frontend integration | 100% | Week 4 |
| Plugin architecture ready | Yes | Week 5 |

---

## Appendix A: Current Service Details

### mtproto_history_access
- **Price:** 100 credits/month
- **Quotas:** 1000/day, 20000/month
- **Features:** Full history, media download, search, filters, export

### mtproto_media_download
- **Price:** 75 credits/month (in code), seeded via migration 0053
- **Quotas:** 500 files/day, 10000 files/month
- **Features:** Bulk download, format filtering, organized storage

### mtproto_bulk_export
- **Price:** 150 credits/month
- **Quotas:** 5000/day, 100000/month
- **Features:** Multi-chat export, parallel processing, resume support

### mtproto_auto_collect
- **Price:** 80 credits/month
- **Quotas:** Unlimited
- **Features:** Real-time collection, webhooks, scheduling

---

## Appendix B: File Reference

| Purpose | Path |
|---------|------|
| Core MTProto Service | `/core/services/mtproto/mtproto_service.py` |
| Feature Manager | `/core/services/mtproto/features/mtproto_features_manager.py` |
| Base Marketplace Service | `/core/services/mtproto/features/base_mtproto_service.py` |
| History Access Service | `/core/services/mtproto/features/history_access_service.py` |
| Media Download Service | `/core/services/mtproto/features/media_download_service.py` |
| API Router | `/apps/api/routers/user_mtproto/router.py` |
| Monitoring Router | `/apps/api/routers/user_mtproto_monitoring_router.py` |
| Frontend Registry | `/apps/frontend/apps/user/src/features/marketplace/registry.tsx` |
| Frontend Page | `/apps/frontend/apps/user/src/pages/MTProtoMonitoringPage/` |
| Service Configs | `/apps/frontend/apps/user/src/pages/services/configs/mtproto/` |
| DB Migration (Seed) | `/infra/db/alembic/versions/0049_seed_marketplace_services.py` |
| Marketplace Repo | `/infra/marketplace/repositories/services.py` |

---

*Document generated: December 18, 2025*
*Author: System Audit*

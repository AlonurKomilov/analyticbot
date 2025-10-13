# Phase 2: DI Migration Status

**Date:** October 13, 2025
**Status:** IN PROGRESS - Phase 2.1 Complete
**Goal:** Migrate all legacy DI imports to new modular `apps.di` architecture

---

## 📊 Migration Audit Results

### Files Requiring Migration

#### 1. **API DI Container Imports** (9 files)
Files importing from `apps.api.di_container`:
- ✅ `apps/api/routers/statistics_core_router.py`
- ✅ `apps/api/routers/admin_users_router.py`
- ✅ `apps/api/routers/insights_engagement_router.py`
- ✅ `apps/api/routers/insights_predictive_router.py`
- ✅ `apps/api/routers/statistics_reports_router.py`
- ✅ `apps/api/routers/channels_router.py`
- ✅ `apps/api/routers/admin_system_router.py`
- ✅ `apps/api/routers/insights_orchestration_router.py`
- ✅ `apps/api/routers/admin_channels_router.py`

**Note:** User created `apps/api/di_analytics.py` - a new standalone DI for Analytics V2 API. These routers are already using the new pattern!

#### 2. **API Deps Imports** (7 files)
Files importing from `apps.api.deps`:
- ⏳ `apps/api/routers/superadmin_router.py` - Uses `get_db_connection`
- ⏳ `apps/api/routers/analytics_live_router.py` - Uses `get_analytics_fusion_service`
- ⏳ `apps/api/routers/insights_predictive_router.py` - Uses `get_predictive_analytics_engine`
- ⏳ `apps/api/routers/system_router.py` - Uses `get_delivery_service`, `get_schedule_service`
- ⏳ `apps/api/main.py` - Uses `cleanup_db_pool`
- ⏳ `apps/shared/api/content_protection_router.py` - Uses `get_current_user`
- ⏳ `apps/api/routers/system_router.py` - Also imports from `apps.api.deps_factory`

#### 3. **Bot Container Imports** (1 file)
Files importing from `apps.bot.container`:
- ⏳ `apps/bot/bot.py` - Main bot initialization

#### 4. **Bot DI Imports** (5 files)
Files importing from `apps.bot.di`:
- ⏳ `apps/bot/container.py` - Imports `configure_bot_container` (wrapper file)
- ⏳ `apps/bot/services/prometheus_service.py` - Imports `configure_bot_container`
- ⏳ `apps/bot/tasks.py` - Imports `configure_bot_container`
- ⏳ `apps/shared/api/payment_router.py` - Imports `BotContainer`
- ⏳ `apps/celery/tasks/bot_tasks.py` - Imports `configure_bot_container`

---

## 🎯 Migration Strategy

### Phase 2.2: API Layer Migration
**Priority:** HIGH (analytics V2 already done!)

Most API routers are already using `apps/api/di_analytics.py` which follows the new pattern.

**Remaining files to migrate:**
1. `apps/api/routers/analytics_live_router.py` - Switch from `apps.api.deps` to `apps.api.di_analytics`
2. `apps/api/routers/insights_predictive_router.py` - Already using `di_analytics`, just verify
3. `apps/api/routers/system_router.py` - Migrate `get_delivery_service`, `get_schedule_service` to `apps.di`
4. `apps/api/routers/superadmin_router.py` - Migrate `get_db_connection` to `apps.di`
5. `apps/shared/api/content_protection_router.py` - Migrate `get_current_user` to `apps.di`
6. `apps/api/main.py` - Migrate cleanup function to `apps.di`

### Phase 2.3: Bot Layer Migration
**Priority:** HIGH

**Files to migrate:**
1. `apps/bot/bot.py` - Main bot initialization (switch from `apps.bot.container` to `apps.di`)
2. `apps/bot/services/prometheus_service.py` - Switch to `apps.di`
3. `apps/bot/tasks.py` - Switch to `apps.di`
4. `apps/celery/tasks/bot_tasks.py` - Switch to `apps.di`
5. `apps/shared/api/payment_router.py` - Switch to `apps.di`

**Legacy files to deprecate after migration:**
- `apps/bot/container.py` (256 lines) - Wrapper around `apps.bot.di`
- `apps/bot/di.py` (424 lines) - Old bot DI container

---

## 📝 Decision: Keep apps/api/di_analytics.py

**Rationale:**
- User already created a well-structured Analytics V2 DI file
- It's focused on Analytics V2 API dependencies (single responsibility)
- Already handles PostgreSQL connection, repositories, and services properly
- Follows the new modular pattern (even if not in `apps.di/` directory)

**Action:** Continue using `apps/api/di_analytics.py` for Analytics V2 API routers

---

## ✅ Next Steps

1. **Complete Phase 2.2:** Migrate remaining API files (6 files)
2. **Execute Phase 2.3:** Migrate bot files (5 files)
3. **Test all migrations:** Type check + integration tests
4. **Mark legacy containers deprecated:** Add warnings to old files
5. **Final cleanup:** Delete legacy containers after 1-week verification period

---

**Estimated Time:** 2-3 hours for all remaining migrations

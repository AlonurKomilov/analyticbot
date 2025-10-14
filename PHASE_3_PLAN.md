# Phase 3 - Business Logic Migration Plan (REVISED)

**Date:** October 14, 2025
**Revised:** October 14, 2025 - Better organization under `core/services/bot/`
**Status:** 🔄 **IN PROGRESS (40% Complete)**
**Estimated Duration:** 1-2 weeks

## 📊 Progress Summary

| Phase | Status | Lines | Services | Completion |
|-------|--------|-------|----------|------------|
| **3.1: SchedulerService** | ✅ Complete | 289 → 1,196 | 5 services | Oct 14, 2025 |
| **3.2: AlertingService** | ✅ Complete | 329 → 889 | 4 services | Oct 14, 2025 |
| **3.3: ContentProtection** | ⏳ Pending | 350 lines | TBD | Not Started |
| **3.4: PrometheusService** | ⏳ Pending | 337 lines | TBD | Not Started |
| **3.5: Review & Cleanup** | ⏳ Pending | - | TBD | Not Started |
| **Total** | **40%** | **618 → 2,085** | **9 services** | **2/5 phases** |

---

## 🎯 Objectives

Complete the migration of remaining business logic from `apps/bot/services/` to `core/services/bot/`, following the same Clean Architecture patterns established in Phase 1-2.

**Key Improvement:** All bot-related services will be organized under `core/services/bot/` namespace for better clarity and organization.

**Success Criteria:**
- ✅ All business logic moved to core layer
- ✅ Thin adapters remain in apps layer
- ✅ 100% type safe
- ✅ Zero breaking changes
- ✅ Full test coverage
- ✅ Documentation updated

---

## 📊 Current State Analysis

### Services Already Migrated (Phase 1) ✅

**From apps/bot/services/ to core/services/:**
1. ✅ `analytics_service.py` (814 lines) → `core/services/analytics/analytics_batch_processor.py`
2. ✅ `reporting_service.py` (784 lines) → `core/services/reporting/reporting_service.py`
3. ✅ `dashboard_service.py` (648 lines) → `core/services/dashboard/dashboard_service.py`

**Total Migrated:** 2,246 lines (Phase 1)

**⚠️ Note:** These will be reorganized under `core/services/bot/` in Phase 3.0 (see below)

### Services Still in Apps Layer 🔄

**Priority Services (Need Migration):**

1. **SchedulerService** (288 lines) - `apps/bot/services/scheduler_service.py`
   - **Type:** Business logic (scheduling, posting, notification)
   - **Dependencies:** Bot (Telegram API), scheduler_repo, analytics_repo
   - **Complexity:** Medium-High (mixed responsibilities)
   - **Issues:** God Service - does scheduling, sending, error handling, analytics
   - **Target:** Split into multiple services in `core/services/bot/scheduling/`

2. **AlertingService** (328 lines) - `apps/bot/services/alerting_service.py`
   - **Type:** Business logic (alert conditions, rule management)
   - **Dependencies:** None (pure business logic)
   - **Complexity:** Medium
   - **Issues:** Should be in core, not apps
   - **Target:** Move to `core/services/bot/alerts/` (consolidate with existing core alerts)

3. **ContentProtectionService** (350 lines) - `apps/bot/services/content_protection.py`
   - **Type:** Business logic (image processing, watermarking)
   - **Dependencies:** PIL, file system
   - **Complexity:** Medium
   - **Issues:** Business logic in apps layer
   - **Target:** Move to `core/services/bot/content/content_protection_service.py`

4. **PrometheusService** (337 lines) - `apps/bot/services/prometheus_service.py`
   - **Type:** Monitoring/Infrastructure
   - **Dependencies:** prometheus_client
   - **Complexity:** Medium
   - **Issues:** Should be in infra layer
   - **Target:** Move to `infra/monitoring/prometheus_service.py` (NOT in bot namespace)

**Lower Priority Services (May Stay in Apps):**

5. **SubscriptionService** (88 lines) - `apps/bot/services/subscription_service.py`
   - **Type:** Business logic (subscription management)
   - **Complexity:** Low
   - **Decision:** Review if this is Telegram-specific adapter or pure business logic

6. **GuardService** (76 lines) - `apps/bot/services/guard_service.py`
   - **Type:** Adapter (Telegram-specific access control)
   - **Complexity:** Low
   - **Decision:** Likely stays as adapter (framework-specific)

7. **AuthService** (62 lines) - `apps/bot/services/auth_service.py`
   - **Type:** Adapter (Telegram-specific authentication)
   - **Complexity:** Low
   - **Decision:** Likely stays as adapter (framework-specific)

### Remaining Work

**Total Lines to Migrate:** ~1,303 lines (4 services)
**Current apps/bot/services/:** 3,786 lines
**After migration target:** ~1,000 lines (adapters only)
**Business logic → Core:** ~2,800 lines total (2,246 done + 1,303 remaining)

---

## 🗺️ Phase 3 Execution Plan

### **Sub-Phase 3.0: Reorganize Existing Services (1 day)** 🔥 **DO FIRST**

**Problem:** Current services scattered in top-level core/services/
- `core/services/analytics/analytics_batch_processor.py`
- `core/services/reporting/reporting_service.py`
- `core/services/dashboard/dashboard_service.py`

**Solution:** Move all bot-related services under `core/services/bot/` namespace

**New Organized Structure:**
```
core/services/bot/
├── __init__.py
├── analytics/
│   ├── __init__.py
│   └── analytics_batch_processor.py (moved from core/services/analytics/)
├── reporting/
│   ├── __init__.py
│   └── reporting_service.py (moved from core/services/reporting/)
├── dashboard/
│   ├── __init__.py
│   └── dashboard_service.py (moved from core/services/dashboard/)
├── scheduling/
│   ├── __init__.py
│   ├── schedule_manager.py (NEW - from SchedulerService)
│   ├── post_scheduler.py (NEW - from SchedulerService)
│   ├── notification_scheduler.py (NEW - from SchedulerService)
│   ├── retry_handler.py (NEW - from SchedulerService)
│   └── protocols.py
├── alerts/
│   ├── __init__.py
│   └── alert_service.py (NEW - from AlertingService + consolidation)
├── content/
│   ├── __init__.py
│   ├── content_protection_service.py (NEW - from ContentProtectionService)
│   └── watermark_config.py
└── subscription/
    ├── __init__.py
    └── subscription_service.py (NEW - if business logic)
```

**Benefits:**
- ✅ Clear namespace: All bot services in one place
- ✅ Easy navigation: `core/services/bot/analytics/`, not scattered
- ✅ Better IDE support: Auto-complete shows related services
- ✅ Logical grouping: Bot domain separated from other domains
- ✅ Scalability: Easy to add more bot services

**Steps:**
1. Create `core/services/bot/` directory structure
2. Move existing 3 services (analytics, reporting, dashboard)
3. Update all imports in:
   - DI containers (`apps/di/core_services_container.py`)
   - Bot adapters (`apps/bot/adapters/`)
   - Test files
4. Update `__init__.py` exports
5. Verify all tests pass
6. Commit changes

**Estimated Time:** 1 day (careful refactoring with testing)

---

### **Sub-Phase 3.1: SchedulerService Refactoring (3-4 days)** 🔥 HIGH PRIORITY

**Problem:** God Service with 5+ responsibilities
- Scheduling logic
- Message sending
- Analytics tracking
- Error handling
- Retry logic

**Solution:** Split into focused services following SRP

**Target Architecture:**
```
core/services/bot/scheduling/
├── __init__.py
├── schedule_manager.py (Core scheduling logic)
├── post_scheduler.py (Post scheduling business rules)
├── notification_scheduler.py (Notification scheduling)
├── retry_handler.py (Retry logic)
└── protocols.py (Abstractions)

apps/bot/adapters/
├── telegram_scheduler_adapter.py (Bot API calls)
└── schedule_notification_adapter.py (Telegram notifications)
```

**Steps:**
1. Create core scheduling services (200-250 lines)
2. Create protocols for external dependencies
3. Create thin Telegram adapters (80-100 lines)
4. Update DI container wiring
5. Update all callers (handlers, tasks)
6. Add comprehensive tests
7. Remove old SchedulerService

**Estimated Time:** 3-4 days

---

### **Sub-Phase 3.2: AlertingService Migration (2-3 days)** ✅ **COMPLETE**

**Completion Date:** October 14, 2025
**Actual Time:** 1 day (faster than estimated due to clear Phase 3.1 patterns)

**Original State:**
- `apps/bot/services/alerting_service.py` (329 lines) - Monolithic service
- Mixed responsibilities (15 methods, 5+ concerns)

**Problem:** God Service with multiple responsibilities
- Alert condition checking
- Alert rule management (CRUD)
- Alert event lifecycle
- Alert notification
- Alert statistics

**Solution Implemented:** Split into focused services following SRP

**New Architecture:**
```
core/services/bot/alerts/
├── __init__.py
├── protocols.py (AlertRepository, AlertNotificationPort)
├── alert_condition_evaluator.py (259 lines)
├── alert_rule_manager.py (245 lines)
└── alert_event_manager.py (230 lines)

apps/bot/adapters/
└── alert_adapters.py (TelegramAlertNotifier - 155 lines)
```

**Completed Steps:**
1. ✅ Created alert protocols (2 protocols, 11 methods)
2. ✅ Implemented AlertConditionEvaluator (metric evaluation)
3. ✅ Implemented AlertRuleManager (CRUD operations)
4. ✅ Implemented AlertEventManager (event lifecycle)
5. ✅ Created TelegramAlertNotifier adapter
6. ✅ Updated DI containers (4 new providers)
7. ✅ Updated middleware for service injection
8. ✅ Migrated handlers to use new services
9. ✅ Fixed all errors without type ignore (6 issues)
10. ✅ Archived legacy service with migration guide

**Results:**
- **Lines Migrated:** 329 → 889 lines (focused, testable code)
- **Services Created:** 4 services (3 core + 1 adapter)
- **Type Safety:** 100% (zero type: ignore used)
- **Architecture:** Clean Architecture compliant
- **Tests:** DI wiring validation script created

**Documentation:**
- ✅ `docs/PHASE_3.2_COMPLETE_SUMMARY.md`
- ✅ `docs/PHASE_3.2_ERROR_FIXES.md`
- ✅ `docs/PHASE_3.2_ERROR_FIX_REPORT.md`
- ✅ `archive/phase3_alerting_legacy_20251014/ARCHIVE_README.md`

**Git Commit:** a4b61ca - "fix(phase3.2): Fix all errors in alert services without type ignore"

**Status:** ✅ Production Ready

---

### **Sub-Phase 3.3: ContentProtectionService Migration (2 days)** 🔥 MEDIUM PRIORITY

**Current State:**
- `apps/bot/services/content_protection.py` (350 lines)
- Pure business logic (PIL image processing, watermarking)
- No Telegram-specific code

**Solution:** Direct migration to core bot services

**Target Architecture:**
```
core/services/bot/content/
├── __init__.py
├── content_protection_service.py (Watermarking, image processing)
├── watermark_config.py (Configuration models)
└── protocols.py (File abstractions)

apps/bot/adapters/
└── content_delivery_adapter.py (Send protected content via Telegram)
```

**Steps:**
1. Create `core/services/bot/content/content_protection_service.py`
2. Move all image processing logic
3. Create file system abstraction (Protocol)
4. Create Telegram delivery adapter
5. Update DI containers
6. Update routers (content_protection_router.py)
7. Remove old service

**Estimated Time:** 2 days

---

### **Sub-Phase 3.4: PrometheusService Migration (1-2 days)** 🟡 LOW PRIORITY

**Current State:**
- `apps/bot/services/prometheus_service.py` (337 lines)
- Infrastructure concern (monitoring)
- Belongs in infra layer, not apps

**Solution:** Move to infra layer

**Target:**
```
infra/monitoring/
├── __init__.py
├── prometheus_service.py (Metrics collection)
├── metrics_registry.py (Metric definitions)
└── protocols.py (Monitoring abstractions)
```

**Steps:**
1. Create `infra/monitoring/prometheus_service.py`
2. Move all metrics logic
3. Update DI container (database_container or new monitoring_container)
4. Update all callers
5. Remove old service

**Estimated Time:** 1-2 days

---

### **Sub-Phase 3.5: Service Review & Cleanup (1 day)** 🟡 LOW PRIORITY

Review remaining services and decide:
- **SubscriptionService** - If business logic → `core/services/bot/subscription/`
- **GuardService** - Likely stays as adapter (Telegram-specific access control)
- **AuthService** - Likely stays as adapter (Telegram-specific authentication)

**Potential Additional Structure:**
```
core/services/bot/subscription/
├── __init__.py
├── subscription_service.py (Business logic only)
└── protocols.py
```

**Steps:**
1. Audit each service
2. Determine if business logic or adapter
3. Migrate if needed to `core/services/bot/`
4. Document decisions

**Estimated Time:** 1 day

---

## 📋 Phase 3 Task Breakdown

### Week 1 (Days 1-5)

**Day 1: Reorganize Existing Services (Sub-Phase 3.0)**
- [ ] Create `core/services/bot/` directory structure
- [ ] Move analytics, reporting, dashboard to bot namespace
- [ ] Update all imports (DI containers, adapters, tests)
- [ ] Update `__init__.py` exports
- [ ] Run all tests to verify
- [ ] Commit reorganization

**Day 2-3: SchedulerService Analysis & Design**
- [ ] Audit SchedulerService responsibilities
- [ ] Design core scheduling services (5 services)
- [ ] Create service protocols
- [ ] Review architecture

**Day 4-5: SchedulerService Implementation**
- [ ] Create `core/services/bot/scheduling/` (5 services)
- [ ] Create Telegram adapters
- [ ] Update DI containers
- [ ] Update handlers/tasks
- [ ] Write tests
- [ ] Verify no regressions

### Week 2 (Days 6-11)

**Day 6-7: AlertingService Consolidation**
- [ ] Audit both alert services
- [ ] Consolidate into `core/services/bot/alerts/`
- [ ] Create Telegram adapter
- [ ] Update router
- [ ] Remove duplicates

**Day 8-9: ContentProtectionService Migration**
- [ ] Move to `core/services/bot/content/`
- [ ] Create file abstractions
- [ ] Update DI containers
- [ ] Update routers
- [ ] Test watermarking

**Day 10: PrometheusService Migration**
- [ ] Move PrometheusService to `infra/monitoring/`
- [ ] Update DI containers
- [ ] Update all callers
- [ ] Test metrics collection

**Day 11: Review & Final Cleanup**
- [ ] Review remaining services (Subscription, Guard, Auth)
- [ ] Migrate SubscriptionService if business logic
- [ ] Update all documentation
- [ ] Final verification of all services
- [ ] Verify `core/services/bot/` structure is complete

---

## 🎯 Success Metrics

### Code Quality Targets

| Metric | Current | Target | Change |
|--------|---------|--------|--------|
| **Business Logic in Apps** | 60% (2,246/3,786) | 25% (~1,000/3,786) | -35% |
| **Average Service Size** | 320 lines | <200 lines | Improvement |
| **Services Following SRP** | 70% | 100% | +30% |
| **Type Safety** | 100% | 100% | Maintain |
| **Test Coverage** | 45% | >70% | +25% |

### Architecture Targets

- ✅ All business logic in core layer
- ✅ Only adapters remain in apps layer
- ✅ Clear separation of concerns
- ✅ Framework-agnostic core
- ✅ Easy to test and maintain
- ✅ No God Services (all split using SRP)

---

## 🚨 Risks & Mitigations

### Risk 1: SchedulerService Complexity
**Risk:** 288 lines with 5+ responsibilities is complex to split
**Mitigation:**
- Detailed analysis before coding
- Incremental splitting (one responsibility at a time)
- Comprehensive tests for each split
- Keep old service until new services verified

### Risk 2: AlertingService Duplication
**Risk:** Two different alert services with different APIs
**Mitigation:**
- Careful audit to identify all unique logic
- Create unified API that covers both use cases
- Gradual migration (one caller at a time)
- Keep both during transition

### Risk 3: Breaking Changes
**Risk:** Services used by multiple handlers/routers
**Mitigation:**
- Backward compatibility wrappers
- Deprecation warnings
- Grace period before removal
- Thorough testing

### Risk 4: Time Estimation
**Risk:** May take longer than 2 weeks
**Mitigation:**
- Focus on highest priority (SchedulerService) first
- Can defer PrometheusService if needed
- Incremental delivery (one service at a time)
- Daily progress tracking

---

## 📚 Documentation Requirements

For each migrated service, create/update:
1. **Service documentation** (docstrings, examples)
2. **Architecture decision record** (why split, how split)
3. **Migration guide** (old API → new API)
4. **Test documentation** (test coverage report)
5. **DI container updates** (wiring documentation)

---

## 🔄 Integration with Previous Work

This phase builds on:
- ✅ **Phase 1** - Service migration patterns established
- ✅ **Phase 2** - Modular DI architecture in place
- ✅ **Clean Architecture** - Core/Apps/Infra layers defined
- ✅ **Type Safety** - 100% type checking compliance

New services will follow same patterns:
- Repository factory pattern for data access
- Protocol-based abstractions
- Adapter pattern for framework integration
- Single Responsibility Principle
- Comprehensive type hints

---

## 📅 Timeline Summary

| Sub-Phase | Days | Priority | Status |
|-----------|------|----------|--------|
| 3.0: Reorganize Existing Services | 1 | 🔥 **CRITICAL** | 🔄 **DO FIRST** |
| 3.1: SchedulerService Refactoring | 3-4 | 🔥 HIGH | ✅ **COMPLETE** |
| 3.2: AlertingService Migration | 2-3 | 🔥 MEDIUM | ✅ **COMPLETE** |
| 3.3: ContentProtectionService | 2 | 🔥 MEDIUM | ⏳ Pending |
| 3.4: PrometheusService | 1-2 | 🟡 LOW | ⏳ Pending |
| 3.5: Review & Cleanup | 1 | 🟡 LOW | ⏳ Pending |
| **Total** | **10-13 days** | | **40% Complete** |

**Estimated Completion:** October 29, 2025 (2 weeks at current velocity)

---

## ✅ Ready to Start

**Prerequisites Met:**
- ✅ Phase 2 complete (modular DI in place)
- ✅ Clean Architecture layers defined
- ✅ Migration patterns established
- ✅ Type safety tools configured
- ✅ Test infrastructure ready

**Next Action:**
Start with **Sub-Phase 3.1: SchedulerService Refactoring** (highest priority, highest impact)

---

---

## 🎨 **New Organization Benefits**

### Before (Scattered Structure)
```
core/services/
├── analytics/
│   └── analytics_batch_processor.py
├── reporting/
│   └── reporting_service.py
├── dashboard/
│   └── dashboard_service.py
├── ai_insights_fusion/
├── alerts_fusion/
├── analytics_fusion/
└── ... (many other services)
```
**Problems:**
- ❌ Hard to find bot-related services (scattered across top level)
- ❌ Mixing different domains (bot, API, ML, analytics fusion, etc.)
- ❌ No clear ownership (which services belong to bot?)
- ❌ Difficult to navigate (20+ folders at top level)

### After (Organized Structure)
```
core/services/
├── bot/  ⭐ NEW - All bot services here!
│   ├── analytics/
│   │   └── analytics_batch_processor.py
│   ├── reporting/
│   │   └── reporting_service.py
│   ├── dashboard/
│   │   └── dashboard_service.py
│   ├── scheduling/
│   │   ├── schedule_manager.py
│   │   ├── post_scheduler.py
│   │   └── notification_scheduler.py
│   ├── alerts/
│   │   └── alert_service.py
│   ├── content/
│   │   └── content_protection_service.py
│   └── subscription/
│       └── subscription_service.py
├── ai_insights_fusion/
├── alerts_fusion/
├── analytics_fusion/
└── ... (other domain services)
```
**Benefits:**
- ✅ **Clear namespace:** All bot services under `core/services/bot/`
- ✅ **Easy discovery:** One place to find all bot business logic
- ✅ **Logical grouping:** Related services together by domain
- ✅ **Better IDE support:** Auto-complete shows bot services grouped
- ✅ **Scalability:** Easy to add more bot services without cluttering
- ✅ **Clean imports:** `from core.services.bot.analytics import ...`
- ✅ **Domain separation:** Bot, API, ML services clearly separated

### Import Examples

**Before:**
```python
from core.services.analytics.analytics_batch_processor import AnalyticsBatchProcessor
from core.services.reporting.reporting_service import ReportingService
from core.services.dashboard.dashboard_service import DashboardService
```

**After (Clean & Clear):**
```python
from core.services.bot.analytics import AnalyticsBatchProcessor
from core.services.bot.reporting import ReportingService
from core.services.bot.dashboard import DashboardService
# OR
from core.services.bot import analytics, reporting, dashboard
```

---

**Created:** October 14, 2025
**Revised:** October 14, 2025 - Better organization under `core/services/bot/`
**Status:** Ready for approval and execution 🚀

# Phase 3 - Business Logic Migration Plan

**Date:** October 14, 2025
**Status:** 🔄 **READY TO START**
**Estimated Duration:** 1-2 weeks

---

## 🎯 Objectives

Complete the migration of remaining business logic from `apps/bot/services/` to `core/services/`, following the same Clean Architecture patterns established in Phase 1-2.

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

### Services Still in Apps Layer 🔄

**Priority Services (Need Migration):**

1. **SchedulerService** (288 lines) - `apps/bot/services/scheduler_service.py`
   - **Type:** Business logic (scheduling, posting, notification)
   - **Dependencies:** Bot (Telegram API), scheduler_repo, analytics_repo
   - **Complexity:** Medium-High (mixed responsibilities)
   - **Issues:** God Service - does scheduling, sending, error handling, analytics
   - **Target:** Split into multiple services in `core/services/scheduling/`

2. **AlertingService** (328 lines) - `apps/bot/services/alerting_service.py`
   - **Type:** Business logic (alert conditions, rule management)
   - **Dependencies:** None (pure business logic)
   - **Complexity:** Medium
   - **Issues:** Should be in core, not apps
   - **Target:** Move to `core/services/alerts/` (AlertsManagementService already exists, may need consolidation)

3. **ContentProtectionService** (350 lines) - `apps/bot/services/content_protection.py`
   - **Type:** Business logic (image processing, watermarking)
   - **Dependencies:** PIL, file system
   - **Complexity:** Medium
   - **Issues:** Business logic in apps layer
   - **Target:** Move to `core/services/content/content_protection_service.py`

4. **PrometheusService** (337 lines) - `apps/bot/services/prometheus_service.py`
   - **Type:** Monitoring/Infrastructure
   - **Dependencies:** prometheus_client
   - **Complexity:** Medium
   - **Issues:** Should be in infra layer
   - **Target:** Move to `infra/monitoring/prometheus_service.py`

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
core/services/scheduling/
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

### **Sub-Phase 3.2: AlertingService Migration (2-3 days)** 🔥 MEDIUM PRIORITY

**Current State:**
- `apps/bot/services/alerting_service.py` (328 lines)
- `core/services/alerts_fusion/alerts/alerts_management_service.py` (already exists)

**Problem:** Duplicate alert logic in two places
- Bot AlertingService: check_alert_conditions, create_alert_rule, etc.
- Core AlertsManagementService: check_real_time_alerts, setup_intelligent_alerts
- Different APIs, overlapping responsibilities

**Solution:** Consolidate into core service

**Steps:**
1. **Audit both services** (identify overlaps and unique logic)
2. **Consolidate into core** (`core/services/alerts/alert_service.py`)
   - Merge condition checking logic
   - Merge rule management
   - Unified alert event generation
3. **Create Telegram adapter** (`apps/bot/adapters/alert_notification_adapter.py`)
   - Send alerts via Telegram
   - Format alert messages
4. **Update DI containers**
5. **Update router** (`apps/api/routers/analytics_alerts_router.py`)
6. **Remove duplicate** (`apps/bot/services/alerting_service.py`)

**Estimated Time:** 2-3 days

---

### **Sub-Phase 3.3: ContentProtectionService Migration (2 days)** 🔥 MEDIUM PRIORITY

**Current State:**
- `apps/bot/services/content_protection.py` (350 lines)
- Pure business logic (PIL image processing, watermarking)
- No Telegram-specific code

**Solution:** Direct migration to core

**Target Architecture:**
```
core/services/content/
├── __init__.py
├── content_protection_service.py (Watermarking, image processing)
├── watermark_config.py (Configuration models)
└── protocols.py (File abstractions)

apps/bot/adapters/
└── content_delivery_adapter.py (Send protected content via Telegram)
```

**Steps:**
1. Create `core/services/content/content_protection_service.py`
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
- SubscriptionService - Keep as adapter or move to core?
- GuardService - Likely stays (Telegram-specific)
- AuthService - Likely stays (Telegram-specific)

**Steps:**
1. Audit each service
2. Determine if business logic or adapter
3. Migrate if needed
4. Document decisions

**Estimated Time:** 1 day

---

## 📋 Phase 3 Task Breakdown

### Week 1 (Days 1-5)

**Day 1-2: Planning & SchedulerService Analysis**
- [ ] Audit SchedulerService responsibilities
- [ ] Design core scheduling services (5 services)
- [ ] Create service protocols
- [ ] Review with stakeholders

**Day 3-5: SchedulerService Implementation**
- [ ] Create core/services/scheduling/ (5 services)
- [ ] Create Telegram adapters
- [ ] Update DI containers
- [ ] Update handlers/tasks
- [ ] Write tests
- [ ] Verify no regressions

### Week 2 (Days 6-10)

**Day 6-7: AlertingService Consolidation**
- [ ] Audit both alert services
- [ ] Consolidate into core
- [ ] Create Telegram adapter
- [ ] Update router
- [ ] Remove duplicates

**Day 8-9: ContentProtectionService Migration**
- [ ] Move to core/services/content/
- [ ] Create file abstractions
- [ ] Update DI containers
- [ ] Update routers
- [ ] Test watermarking

**Day 10: PrometheusService + Cleanup**
- [ ] Move PrometheusService to infra/monitoring/
- [ ] Review remaining services
- [ ] Documentation updates
- [ ] Final verification

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
| 3.1: SchedulerService Refactoring | 3-4 | 🔥 HIGH | 🔄 Next |
| 3.2: AlertingService Migration | 2-3 | 🔥 MEDIUM | ⏳ Pending |
| 3.3: ContentProtectionService | 2 | 🔥 MEDIUM | ⏳ Pending |
| 3.4: PrometheusService | 1-2 | 🟡 LOW | ⏳ Pending |
| 3.5: Review & Cleanup | 1 | 🟡 LOW | ⏳ Pending |
| **Total** | **9-12 days** | | |

**Estimated Completion:** October 28, 2025 (2 weeks at current velocity)

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

**Created:** October 14, 2025
**Status:** Ready for approval and execution 🚀

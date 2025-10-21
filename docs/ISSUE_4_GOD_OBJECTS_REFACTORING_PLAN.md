# Issue #4: God Objects Refactoring Plan 🔨

**Created:** October 21, 2025
**Status:** 📋 Planning Phase
**Priority:** 🔴 HIGH (Code Maintainability & Technical Debt)
**Estimated Time:** 26-30 hours
**Target:** All files < 400 lines

---

## 📊 Current State Analysis

### Files Requiring Refactoring (8 files, 5,214 total lines)

| # | File | Lines | Priority | Est. Time | Complexity |
|---|------|-------|----------|-----------|------------|
| 1 | `apps/di/bot_container.py` | 910 | 🔴 HIGH | 5h | 🟡 Medium |
| 2 | `apps/bot/handlers/content_protection.py` | 841 | 🔴 HIGH | 5h | 🔴 High |
| 3 | `apps/api/routers/auth_router.py` | 679 | 🟠 MEDIUM | 4h | 🟡 Medium |
| 4 | `apps/api/routers/insights_predictive_router.py` | 620 | 🟠 MEDIUM | 4h | 🟡 Medium |
| 5 | `apps/bot/utils/data_processor.py` | 636 | 🟠 MEDIUM | 3h | 🟢 Low |
| 6 | `apps/jobs/alerts/runner.py` | 566 | 🟢 LOW | 2h | 🟢 Low |
| 7 | `apps/api/services/health_service.py` | 553 | 🟢 LOW | 2h | 🟢 Low |
| 8 | `apps/bot/handlers/alerts.py` | 543 | 🟢 LOW | 1h | 🟢 Low |

**Note:** `apps/bot/di.py` (502 lines) is marked deprecated and scheduled for removal (can skip).

---

## 🎯 Success Criteria

- ✅ **All files < 400 lines** (target: 200-300 lines per file)
- ✅ **Single Responsibility Principle** (each file has one clear purpose)
- ✅ **No functionality lost** (all features work after refactoring)
- ✅ **All tests passing** (100% test pass rate)
- ✅ **Import statements updated** (all references fixed)
- ✅ **Clean architecture maintained** (no architecture violations)
- ✅ **Zero mypy/ruff errors** (type safety preserved)

---

## 📋 Phased Implementation Plan

### **Phase 1: DI Container Split** (5 hours) 🔴 HIGH PRIORITY

**File:** `apps/di/bot_container.py` (910 lines → 5 files)

**Problem Analysis:**
- Contains 40+ factory functions (adapters, services, repositories)
- Mixed concerns: bot infrastructure, services, adapters, repositories
- Hard to navigate and maintain
- Growing with every new service addition

**Refactoring Strategy:**

```
apps/di/bot_container.py (910 lines)
└─→ Split into modular structure:

apps/di/
├── bot_container.py                    # Core container only (~150 lines)
│   └── Imports providers and wires dependencies
├── providers/
│   ├── __init__.py
│   ├── bot_infrastructure.py          # Bot client, dispatcher (~120 lines)
│   ├── adapters.py                    # Analytics, reporting, dashboard (~180 lines)
│   ├── telegram_services.py           # Message sender, markup builder (~150 lines)
│   ├── core_services.py               # Guard, subscription, payment (~180 lines)
│   └── alert_services.py              # Alert system factories (~130 lines)
└── factories/
    ├── __init__.py
    └── media_processors.py             # Image/video/file processors (~100 lines)
```

**Implementation Steps:**

1. **Extract Infrastructure Providers** (`bot_infrastructure.py`)
   - `_create_bot_client()` - Bot client creation
   - `_create_dispatcher()` - Dispatcher setup
   - Configuration management
   - **Lines:** ~120

2. **Extract Adapter Providers** (`adapters.py`)
   - `_create_bot_analytics_adapter()`
   - `_create_bot_reporting_adapter()`
   - `_create_bot_dashboard_adapter()`
   - Thin wrappers over core services
   - **Lines:** ~180

3. **Extract Telegram Service Providers** (`telegram_services.py`)
   - `_create_aiogram_message_sender()`
   - `_create_aiogram_markup_builder()`
   - Telegram-specific utilities
   - **Lines:** ~150

4. **Extract Core Service Providers** (`core_services.py`)
   - `_create_guard_service()`
   - `_create_subscription_service()`
   - `_create_payment_orchestrator()`
   - `_create_analytics_service()`
   - `_create_channel_management_service()`
   - Business logic services
   - **Lines:** ~180

5. **Extract Alert Service Providers** (`alert_services.py`)
   - `_create_schedule_manager()`
   - `_create_delivery_status_tracker()`
   - `_create_alert_condition_evaluator()`
   - `_create_alert_rule_manager()`
   - `_create_alert_event_manager()`
   - `_create_telegram_alert_notifier()`
   - Alert system factories
   - **Lines:** ~130

6. **Extract Media Processor Factories** (`media_processors.py`)
   - `_create_image_processor()`
   - `_create_video_processor()`
   - `_create_file_system_adapter()`
   - Media handling utilities
   - **Lines:** ~100

7. **Refactor Core Container** (`bot_container.py`)
   - Import all provider modules
   - Wire dependencies
   - Expose unified container interface
   - **Lines:** ~150

**Testing Strategy:**
- ✅ All bot handlers still work
- ✅ DI container resolves all services
- ✅ No circular dependencies
- ✅ Import linter passes (clean architecture)

**Success Metrics:**
- 910 lines → 1,010 lines (6 files, but better organized)
- Each file < 200 lines
- Clear separation of concerns
- Easy to add new services

---

### **Phase 2: Content Protection Handler Split** (5 hours) 🔴 HIGH PRIORITY

**File:** `apps/bot/handlers/content_protection.py` (841 lines → 7 files)

**Problem Analysis:**
- 20 handler functions in one file
- Mixed concerns: watermarking, theft detection, premium features, usage tracking
- Contains direct DB imports (violation of clean architecture - Issue #4 technical debt)
- Hard to test individual features

**Refactoring Strategy:**

```
apps/bot/handlers/content_protection.py (841 lines)
└─→ Split by feature domain:

apps/bot/handlers/content_protection/
├── __init__.py                         # Re-export all routers (~20 lines)
├── router.py                           # Main router aggregation (~30 lines)
├── states.py                           # FSM states (~20 lines)
├── models.py                           # Shared validation models (~50 lines)
├── watermarking.py                     # Watermark handlers (~250 lines)
│   ├── cmd_protect_content()
│   ├── handle_image_watermark_start()
│   ├── handle_watermark_image_upload()
│   ├── handle_default_watermark()
│   ├── handle_custom_watermark_text()
│   └── handle_custom_watermark_apply()
├── premium_features.py                 # Premium emoji handlers (~150 lines)
│   ├── handle_custom_emoji_start()
│   ├── handle_custom_emoji_format()
│   └── handle_upgrade_premium()
├── theft_detection.py                  # Theft detection handlers (~150 lines)
│   ├── handle_theft_check_start()
│   └── handle_theft_check_analyze()
├── usage_tracking.py                   # Usage stats & limits (~180 lines)
│   ├── handle_usage_stats()
│   ├── _check_feature_usage_limit()
│   ├── _increment_feature_usage()
│   └── _get_current_usage()
└── services/                           # Business logic services
    ├── __init__.py
    ├── tier_service.py                 # User tier management (~100 lines)
    │   └── _get_user_subscription_tier()
    └── validation.py                   # State validators (~60 lines)
        ├── validate_callback_state()
        └── validate_message_state()
```

**Implementation Steps:**

1. **Create Package Structure**
   - Create `apps/bot/handlers/content_protection/` directory
   - Add `__init__.py` for re-exports

2. **Extract Shared Components** (`states.py`, `models.py`, `validation.py`)
   - FSM states (ContentProtectionStates)
   - Validation helpers
   - Type guards
   - **Lines:** ~130 total

3. **Extract Watermarking Module** (`watermarking.py`)
   - All watermark-related handlers (6 functions)
   - Image processing logic
   - Watermark application workflows
   - **Lines:** ~250

4. **Extract Premium Features** (`premium_features.py`)
   - Premium emoji handlers (3 functions)
   - Upgrade prompts
   - Premium tier validation
   - **Lines:** ~150

5. **Extract Theft Detection** (`theft_detection.py`)
   - Theft check handlers (2 functions)
   - Content analysis workflows
   - **Lines:** ~150

6. **Extract Usage Tracking** (`usage_tracking.py`)
   - Usage statistics display (1 function)
   - Feature limit checking (1 function)
   - Usage increment tracking (1 function)
   - Current usage queries (1 function)
   - **Lines:** ~180

7. **Extract Tier Service** (`services/tier_service.py`)
   - User subscription tier lookup
   - **TODO:** Remove direct DB imports (technical debt)
   - Inject UserRepository via DI
   - **Lines:** ~100

8. **Create Router Aggregation** (`router.py`)
   - Import all sub-routers
   - Combine into single router
   - Register all handlers
   - **Lines:** ~30

9. **Update Import References**
   - Find all imports of `apps.bot.handlers.content_protection`
   - Update to new module paths
   - Test all handlers

**Clean Architecture Fix (Technical Debt):**
- **Current:** Direct imports from `infra.db.connection_manager` and `infra.db.repositories.user_repository`
- **Target:** Inject services via DI container
- **Action:**
  - Move DB logic to `apps/bot/services/tier_service.py`
  - Inject via DI in handlers
  - Remove `ignore_imports` from import linter config

**Testing Strategy:**
- ✅ All /protect command workflows work
- ✅ Watermarking (image + custom text) functional
- ✅ Premium emoji features work
- ✅ Theft detection operational
- ✅ Usage tracking accurate
- ✅ No direct DB imports (clean architecture)

**Success Metrics:**
- 841 lines → 1,080 lines (9 files, better organized)
- Each file < 250 lines
- Clean architecture violations fixed
- Clear feature separation

---

### **Phase 3: Auth Router Split** (4 hours) 🟠 MEDIUM PRIORITY

**File:** `apps/api/routers/auth_router.py` (679 lines → 5 files)

**Problem Analysis:**
- Multiple authentication concerns in one file
- Login, registration, password reset, admin operations mixed together
- Growing complexity with MFA, OAuth providers, role management

**Refactoring Strategy:**

```
apps/api/routers/auth_router.py (679 lines)
└─→ Split by authentication domain:

apps/api/routers/auth/
├── __init__.py                         # Re-export all routers (~20 lines)
├── router.py                           # Main router aggregation (~30 lines)
├── models.py                           # Shared Pydantic models (~80 lines)
│   ├── LoginRequest
│   ├── RegisterRequest
│   ├── AuthResponse
│   └── UserResponse
├── login.py                            # Login endpoints (~180 lines)
│   ├── POST /login
│   ├── POST /refresh
│   └── POST /logout
├── registration.py                     # Registration endpoints (~150 lines)
│   ├── POST /register
│   └── POST /verify-email
├── password.py                         # Password management (~150 lines)
│   ├── POST /forgot-password
│   ├── POST /reset-password
│   └── PUT /change-password
└── profile.py                          # User profile endpoints (~140 lines)
    ├── GET /me
    ├── PUT /me
    └── DELETE /me
```

**Implementation Steps:**

1. **Create Package Structure**
   - Create `apps/api/routers/auth/` directory
   - Add `__init__.py`

2. **Extract Shared Models** (`models.py`)
   - All Pydantic models
   - Request/response schemas
   - **Lines:** ~80

3. **Extract Login Module** (`login.py`)
   - Login endpoint
   - Token refresh endpoint
   - Logout endpoint
   - **Lines:** ~180

4. **Extract Registration Module** (`registration.py`)
   - User registration endpoint
   - Email verification
   - **Lines:** ~150

5. **Extract Password Module** (`password.py`)
   - Forgot password workflow
   - Reset password endpoint
   - Change password endpoint
   - **Lines:** ~150

6. **Extract Profile Module** (`profile.py`)
   - Get current user
   - Update profile
   - Delete account
   - **Lines:** ~140

7. **Create Router Aggregation** (`router.py`)
   - Import all sub-routers
   - Combine with prefix `/auth`
   - **Lines:** ~30

8. **Update Import References**
   - Find all `from apps.api.routers.auth_router import`
   - Update to new paths

**Testing Strategy:**
- ✅ Login/logout work
- ✅ Registration functional
- ✅ Password reset works
- ✅ Profile endpoints operational
- ✅ JWT tokens valid

**Success Metrics:**
- 679 lines → 730 lines (7 files)
- Each file < 200 lines
- Clear feature boundaries

---

### **Phase 4: Insights Predictive Router Split** (4 hours) 🟠 MEDIUM PRIORITY

**File:** `apps/api/routers/insights_predictive_router.py` (620 lines → 4 files)

**Problem Analysis:**
- Multiple prediction types in one file
- Engagement, growth, content, anomaly predictions all mixed
- Large endpoint handlers with complex logic

**Refactoring Strategy:**

```
apps/api/routers/insights_predictive_router.py (620 lines)
└─→ Split by prediction type:

apps/api/routers/insights/predictive/
├── __init__.py                         # Re-exports (~20 lines)
├── router.py                           # Main router (~30 lines)
├── engagement.py                       # Engagement predictions (~200 lines)
│   ├── GET /predict/engagement
│   └── POST /predict/engagement/custom
├── growth.py                           # Growth predictions (~180 lines)
│   ├── GET /predict/growth
│   └── POST /predict/growth/scenarios
├── content.py                          # Content recommendations (~180 lines)
│   ├── GET /predict/content/optimal-time
│   └── GET /predict/content/recommendations
└── anomalies.py                        # Anomaly detection (~150 lines)
    └── GET /predict/anomalies
```

**Implementation Steps:**

1. **Create Package Structure**
   - Create `apps/api/routers/insights/predictive/`
   - Add `__init__.py`

2. **Extract Engagement Module** (`engagement.py`)
   - Engagement prediction endpoints
   - **Lines:** ~200

3. **Extract Growth Module** (`growth.py`)
   - Growth prediction endpoints
   - Scenario modeling
   - **Lines:** ~180

4. **Extract Content Module** (`content.py`)
   - Content recommendation endpoints
   - Optimal timing predictions
   - **Lines:** ~180

5. **Extract Anomalies Module** (`anomalies.py`)
   - Anomaly detection endpoints
   - **Lines:** ~150

6. **Create Router Aggregation** (`router.py`)
   - Combine all sub-routers
   - **Lines:** ~30

**Testing Strategy:**
- ✅ All prediction endpoints work
- ✅ Response formats unchanged
- ✅ Analytics integration intact

**Success Metrics:**
- 620 lines → 740 lines (6 files)
- Each file < 200 lines
- Clear prediction type boundaries

---

### **Phase 5: Data Processor Split** (3 hours) 🟠 MEDIUM PRIORITY

**File:** `apps/bot/utils/data_processor.py` (636 lines → 3 files)

**Problem Analysis:**
- Multiple processing concerns: validation, transformation, aggregation
- Mixed data types: analytics, messages, media
- Could be split by processing stage

**Refactoring Strategy:**

```
apps/bot/utils/data_processor.py (636 lines)
└─→ Split by processing stage:

apps/bot/utils/data_processing/
├── __init__.py                         # Re-exports (~20 lines)
├── validators.py                       # Data validation (~220 lines)
│   ├── validate_analytics_data()
│   ├── validate_message_data()
│   └── validate_media_data()
├── transformers.py                     # Data transformation (~220 lines)
│   ├── transform_to_analytics()
│   ├── normalize_timestamps()
│   └── format_user_data()
└── aggregators.py                      # Data aggregation (~220 lines)
    ├── aggregate_by_channel()
    ├── aggregate_by_time_period()
    └── calculate_statistics()
```

**Implementation Steps:**

1. **Analyze Current Structure**
   - Identify validation functions
   - Identify transformation functions
   - Identify aggregation functions

2. **Create Package Structure**
   - Create `apps/bot/utils/data_processing/`
   - Add `__init__.py`

3. **Extract Validators** (`validators.py`)
   - All validation logic
   - **Lines:** ~220

4. **Extract Transformers** (`transformers.py`)
   - All transformation logic
   - **Lines:** ~220

5. **Extract Aggregators** (`aggregators.py`)
   - All aggregation logic
   - **Lines:** ~220

6. **Update Import References**
   - Find all imports
   - Update to new module paths

**Testing Strategy:**
- ✅ Data validation works
- ✅ Transformations accurate
- ✅ Aggregations correct

**Success Metrics:**
- 636 lines → 660 lines (4 files)
- Each file < 250 lines
- Clear processing stages

---

### **Phase 6: Remaining Files** (6 hours) 🟢 LOW PRIORITY

**Files:**
- `apps/jobs/alerts/runner.py` (566 lines) → 3 files
- `apps/api/services/health_service.py` (553 lines) → 3 files
- `apps/bot/handlers/alerts.py` (543 lines) → 3 files

**Strategy:** Similar pattern-based splits

**Runner Split** (2 hours):
```
apps/jobs/alerts/runner.py (566 lines)
└─→ apps/jobs/alerts/
    ├── runner.py                       # Main runner (~150 lines)
    ├── scheduler.py                    # Schedule management (~200 lines)
    └── executor.py                     # Task execution (~220 lines)
```

**Health Service Split** (2 hours):
```
apps/api/services/health_service.py (553 lines)
└─→ apps/api/services/health/
    ├── checker.py                      # Health checks (~200 lines)
    ├── metrics.py                      # Metrics collection (~180 lines)
    └── reporter.py                     # Status reporting (~180 lines)
```

**Alert Handlers Split** (2 hours):
```
apps/bot/handlers/alerts.py (543 lines)
└─→ apps/bot/handlers/alerts/
    ├── commands.py                     # Alert commands (~180 lines)
    ├── callbacks.py                    # Callback handlers (~180 lines)
    └── management.py                   # Alert management (~190 lines)
```

---

## 📅 Implementation Timeline

### Week 1 (Days 1-3): High Priority Files
- **Day 1 (5h):** Phase 1 - DI Container Split
- **Day 2 (5h):** Phase 2 - Content Protection Handler Split
- **Day 3 (4h):** Phase 3 - Auth Router Split

### Week 2 (Days 4-5): Medium Priority Files
- **Day 4 (4h):** Phase 4 - Insights Predictive Router Split
- **Day 5 (3h):** Phase 5 - Data Processor Split

### Week 3 (Days 6-7): Low Priority Files + Testing
- **Day 6 (4h):** Phase 6 Part 1 - Runner + Health Service
- **Day 7 (2h):** Phase 6 Part 2 - Alert Handlers
- **Day 7 (1h):** Final testing and validation

**Total:** 28 hours (vs 26-30h estimate)

---

## 🎯 Quick Wins Strategy

**If time is limited, prioritize these:**

1. **Phase 2 First** - Content Protection Handler (5h)
   - Fixes clean architecture violations
   - High business impact (premium features)
   - Removes import linter exceptions

2. **Phase 1 Second** - DI Container (5h)
   - Makes adding new services easier
   - Improves developer experience
   - Reduces merge conflicts

3. **Phase 3 Third** - Auth Router (4h)
   - Improves security code maintainability
   - Clear authentication boundaries

**Quick Win Total:** 14 hours (50% of work, 60% of impact)

---

## ✅ Pre-Implementation Checklist

- [ ] Review all 8 files to understand current structure
- [ ] Create feature branch: `refactor/issue-4-god-objects`
- [ ] Run full test suite to establish baseline
- [ ] Document current import patterns
- [ ] Create rollback plan (git tags)

---

## 🔧 Post-Implementation Tasks

- [ ] Update all import statements across codebase
- [ ] Run full test suite (target: 100% pass rate)
- [ ] Validate import linter (all contracts passing)
- [ ] Run mypy type checking (0 errors)
- [ ] Update documentation
- [ ] Remove import linter exceptions (content_protection)
- [ ] Update TOP_10 plan with completion metrics
- [ ] Create PR with comprehensive description

---

## 🚀 Expected Benefits

**Code Quality:**
- ✅ 25% reduction in file complexity
- ✅ 40% improvement in code navigability
- ✅ 100% single responsibility compliance

**Developer Experience:**
- ✅ Faster feature development (clear boundaries)
- ✅ Easier onboarding (smaller files to understand)
- ✅ Reduced merge conflicts (distributed changes)

**Architecture:**
- ✅ Clean architecture violations fixed
- ✅ Better testability (isolated modules)
- ✅ Easier to mock dependencies

**Maintenance:**
- ✅ Clearer debugging paths
- ✅ Easier to locate bugs
- ✅ Simplified code reviews

---

## 📊 Success Metrics Dashboard

| Metric | Before | Target | After |
|--------|--------|--------|-------|
| **Files > 500 lines** | 8 | 0 | TBD |
| **Files > 400 lines** | 9 | 0 | TBD |
| **Max file size** | 910 lines | 300 lines | TBD |
| **Avg file size** | 652 lines | 200 lines | TBD |
| **Total files** | 8 | 40-50 | TBD |
| **Architecture violations** | 4 | 0 | TBD |
| **Import exceptions** | 6 | 0 | TBD |
| **Test pass rate** | 100% | 100% | TBD |

---

## 🎉 Phase Completion Criteria

**Each phase is complete when:**
1. ✅ All files < 400 lines (target: 200-300)
2. ✅ All tests passing (100%)
3. ✅ Import linter passing (all contracts)
4. ✅ Mypy type checking passing (0 errors)
5. ✅ All imports updated throughout codebase
6. ✅ Git commit with clear description
7. ✅ No functionality regression

---

**Next Steps:**
1. Review this plan with team
2. Create feature branch
3. Start with Phase 2 (Content Protection) for quick win
4. Proceed with Phase 1 (DI Container)
5. Continue with remaining phases

**Estimated Completion:** 3-4 days (with focused work sessions)

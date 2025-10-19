# Apps Folder Refactoring - Action Plan

**Start Date:** October 19, 2025  
**Target Completion:** November 16, 2025 (4 weeks)  
**Status:** 🚧 IN PROGRESS

---

## Overview

This plan addresses the top 10 critical issues identified in the apps folder architecture analysis. Work is organized by priority (P0 → P3) to maximize impact and minimize risk.

---

## 🔴 Phase 1: Critical Fixes (Week 1) - P0 Issues

**Goal:** Stabilize the architecture foundation - fix breaking issues

### Task 1.1: Consolidate DI System ✅ STARTED
**Issue:** Multiple competing DI containers (#1)  
**Time:** 2 days  
**Owner:** Dev Team

**Actions:**
- [x] Document `apps/di/` as the canonical DI system
- [ ] Create migration guide from old containers to new
- [ ] Add deprecation warnings to all old containers
- [ ] Update all imports in api/main.py to use apps/di
- [ ] Update all imports in bot/bot.py to use apps/di
- [ ] Update celery tasks to use apps/di
- [ ] Test that all services still work

**Files to Update:**
- `apps/api/main.py` - Already uses `apps/di` ✅
- `apps/bot/bot.py` - Already uses `apps/di` ✅
- `apps/bot/run_bot.py` - Needs migration
- `apps/bot/tasks.py` - Already uses `apps/di` ✅
- `apps/celery/tasks/*.py` - Needs migration
- `apps/jobs/worker.py` - Uses jobs/di.py

**Files to Delete (after migration):**
- `apps/bot/di.py` (already deprecated, removal scheduled)
- `apps/api/di.py` (merge into apps/di if needed)

---

### Task 1.2: Fix Critical Circular Dependencies
**Issue:** Apps importing from infra (#2)  
**Time:** 2 days  
**Owner:** Dev Team

**Actions:**
- [ ] Audit all `from infra.` imports in apps/
- [ ] Move infra imports to DI containers only
- [ ] Use repository factory pattern in apps/shared/factory.py
- [ ] Update all direct infra imports to use DI injection
- [ ] Add import linter rules to prevent future violations

**Critical Files:**
```
apps/shared/di.py          → imports infra.db.connection_manager
apps/di/database_container.py → imports infra.db.connection_manager  
apps/api/di_analytics.py   → imports multiple infra.db.repositories
apps/bot/di.py            → imports infra.cache, infra.services
```

**Strategy:**
1. Keep infra imports ONLY in DI containers (apps/di/)
2. All other apps code gets dependencies via injection
3. Use factory pattern for repositories

---

### Task 1.3: Break Apps Internal Circular Dependencies
**Issue:** apps/shared ↔ apps/api/bot cycles (#2)  
**Time:** 1 day  
**Owner:** Dev Team

**Actions:**
- [ ] Move shared models from apps/bot/models to core/domain
- [ ] Move shared API routers from apps/shared/api to apps/api/routers
- [ ] Update all imports after moving files
- [ ] Verify no circular imports remain

**Files to Move:**
```
apps/shared/api/content_protection_router.py → apps/api/routers/
apps/shared/api/payment_router.py → apps/api/routers/
apps/bot/models/content_protection.py → core/domain/models/
apps/shared/models/twa.py → core/domain/models/ (if truly shared)
```

---

## 🟡 Phase 2: High Priority (Week 2) - P1 Issues

**Goal:** Enable safe refactoring and reduce technical debt

### Task 2.1: Add Critical Test Coverage
**Issue:** Zero tests in apps folder (#4)  
**Time:** 3 days  
**Owner:** Dev Team

**Actions:**
- [ ] Set up pytest infrastructure for apps/
- [ ] Add integration tests for API endpoints (10 critical endpoints)
- [ ] Add integration tests for bot handlers (5 critical handlers)
- [ ] Add unit tests for DI container configuration
- [ ] Add tests for repository factory
- [ ] Set up CI to run tests on PR
- [ ] Require 60% coverage for new code

**Test Structure:**
```
apps/
  tests/
    __init__.py
    conftest.py              # Shared fixtures
    test_api/
      test_main.py           # API startup
      test_routers/
        test_auth.py
        test_channels.py
        test_analytics.py
    test_bot/
      test_bot.py            # Bot startup
      test_handlers/
        test_user_handlers.py
        test_admin_handlers.py
    test_di/
      test_containers.py     # DI wiring
      test_factory.py        # Repository factory
```

**Priority Tests:**
1. API health endpoint
2. User authentication flow
3. Channel CRUD operations
4. Bot command handling
5. DI container initialization

---

### Task 2.2: Remove All Deprecated Code
**Issue:** 150+ TODOs/DEPRECATEDs (#3)  
**Time:** 2 days  
**Owner:** Dev Team

**Actions:**
- [ ] Create inventory of all DEPRECATED files (see list below)
- [ ] Verify no active usage of deprecated code
- [ ] Delete all DEPRECATED files
- [ ] Remove all legacy handler includes
- [ ] Update imports in files that referenced deleted code
- [ ] Test that nothing broke

**Files to DELETE:**
```python
# Deprecated adapters/services
apps/bot/services/adapters/bot_ml_facade.py
apps/bot/services/adapters/ml_coordinator.py
apps/bot/services/adapters/ml_coordinator_compat.py
apps/bot/services/adapters/bot_ml_facade_compat.py
apps/bot/services/adapters/payment_adapter_factory.py
apps/bot/services/adapters/base_adapter.py

# Deprecated API routes
apps/bot/api/payment_router.py
apps/bot/api/content_protection_router.py
apps/bot/api/health_router.py

# Deprecated clients
apps/bot/clients/analytics_client.py

# Deprecated utils
apps/bot/utils/monitoring.py  # Use apps/shared/monitoring

# Deprecated models
apps/bot/models/twa.py  # Use apps/shared/models/twa

# Deprecated DI (after Task 1.1 complete)
apps/bot/di.py
```

**Legacy Router Cleanup:**
```python
# Remove these from bot handlers:
apps/bot/handlers/phase_45_integration.py → Delete or merge
apps/bot/handlers/bot_microhandlers.py → Clean up legacy includes
```

---

### Task 2.3: Resolve All TODOs
**Issue:** 40+ TODO comments (#3)  
**Time:** 2 days  
**Owner:** Dev Team

**Strategy:**
1. **Implement** - If TODO is critical and quick (<2 hours)
2. **Create Issue** - If TODO requires significant work
3. **Delete** - If TODO is outdated/not needed

**High Priority TODOs to Address:**
```python
# apps/celery/tasks/ml_tasks.py
# TODO: ContentAnalyzer service not yet implemented
→ Create issue: "Implement ContentAnalyzer service"

# apps/jobs/alerts/runner.py
# TODO: Implement proper alert sent tracking
→ Implement using AlertSentRepository (quick fix)

# apps/shared/api/content_protection_router.py
# TODO: Integrate with payment system (Phase 2.2)
→ Create issue: "Payment system integration"

# apps/bot/handlers/exports.py
channel_id = "@demo_channel"  # TODO: Get from user settings
→ Implement: Read from database or config

# Multiple files
# TODO: Add delivery repo when available
→ Create issue: "Implement delivery repository"
```

---

## 🟢 Phase 3: Medium Priority (Week 3) - P2 Issues

**Goal:** Simplify and clarify architecture

### Task 3.1: Simplify DI Containers
**Issue:** Over-engineered DI (#6)  
**Time:** 2 days  
**Owner:** Dev Team

**Actions:**
- [ ] Refactor bot_container.py (691 lines → <300 lines)
- [ ] Remove excessive try-except blocks
- [ ] Use configuration for optional features
- [ ] Lazy-load heavy dependencies
- [ ] Extract common patterns to utilities

**bot_container.py Refactoring:**
```python
# BEFORE (691 lines with 30+ try-except blocks)
try:
    from aiogram import Bot as _AioBot
    def create_bot(...):
        # 20 lines
except ImportError:
    # 10 lines of error handling

# AFTER (cleaner approach)
def create_bot(...):
    """Create bot instance. Raises ImportError if aiogram not installed."""
    from aiogram import Bot
    return Bot(...)

# Let DI container handle the exception at startup, fail fast
```

---

### Task 3.2: Remove Duplicate Code
**Issue:** Multiple implementations (#5)  
**Time:** 2 days  
**Owner:** Dev Team

**Actions:**
- [ ] Delete deprecated ML coordinators (keep only apps/shared/adapters/)
- [ ] Consolidate router organization (choose ONE pattern)
- [ ] Remove duplicate analytics services
- [ ] Extract common DI logic to shared utilities

**Files to Consolidate:**
```
ML Coordinators (keep only 1):
✅ KEEP: apps/shared/adapters/ml_coordinator.py
❌ DELETE: apps/bot/services/adapters/ml_coordinator.py
❌ DELETE: apps/bot/services/adapters/ml_coordinator_compat.py

Analytics Services (keep only 1):
✅ KEEP: apps/shared/analytics_service.py
❌ ARCHIVED: core.services.bot.analytics (already in archive)

Router Organization:
✅ KEEP: apps/api/routers/*.py (standard FastAPI pattern)
❌ CLEANUP: Remove "microrouter" and "phase 4.5" references
```

---

### Task 3.3: Standardize Error Handling
**Issue:** Inconsistent error handling (#7)  
**Time:** 2 days  
**Owner:** Dev Team

**Actions:**
- [ ] Create custom exception hierarchy in core/exceptions.py
- [ ] Add error middleware for API (FastAPI exception handlers)
- [ ] Add error middleware for bot (Aiogram error handlers)
- [ ] Replace all `except: pass` with proper error handling
- [ ] Add structured logging for errors

**Error Handling Pattern:**
```python
# core/exceptions.py
class ApplicationError(Exception):
    """Base exception for all application errors"""
    pass

class DatabaseError(ApplicationError):
    """Database operation failed"""
    pass

class ServiceUnavailableError(ApplicationError):
    """External service unavailable"""
    pass

# Usage in apps/
try:
    result = await critical_operation()
except DatabaseError as e:
    logger.error(f"Database error: {e}", exc_info=True)
    raise  # Let middleware handle it
except ServiceUnavailableError as e:
    logger.warning(f"Service unavailable: {e}")
    # Return cached data or error response
```

---

### Task 3.4: Clarify apps/shared Responsibilities
**Issue:** Unclear module responsibilities (#8)  
**Time:** 1 day  
**Owner:** Dev Team

**Actions:**
- [ ] Define clear rules for what belongs in apps/shared
- [ ] Move API routers from apps/shared/api to apps/api/routers
- [ ] Remove or consolidate apps/shared/di.py
- [ ] Document apps/shared purpose in README

**Decision Tree for apps/shared:**
```
Should this code be in apps/shared?
│
├─ Used by BOTH bot AND api? → YES, goes in apps/shared/
│
├─ Only used by bot? → NO, goes in apps/bot/
│
├─ Only used by api? → NO, goes in apps/api/
│
└─ Core business logic? → NO, goes in core/
```

**Files to Move:**
```
apps/shared/api/content_protection_router.py → apps/api/routers/
apps/shared/api/payment_router.py → apps/api/routers/
apps/shared/di.py → Delete or merge into apps/di/
```

---

## 🔵 Phase 4: Documentation & Polish (Week 4) - P3 Issues

**Goal:** Make codebase maintainable and onboardable

### Task 4.1: Centralize Configuration
**Issue:** Hardcoded configuration (#9)  
**Time:** 1 day  
**Owner:** Dev Team

**Actions:**
- [ ] Audit all hardcoded values
- [ ] Move to centralized config/settings.py
- [ ] Use Pydantic BaseSettings for validation
- [ ] Create .env.example with all required variables
- [ ] Document all configuration options

**Configuration Consolidation:**
```python
# config/settings.py (enhance existing)
class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    DATABASE_POOL_MIN: int = 10
    DATABASE_POOL_MAX: int = 20
    
    # Redis
    REDIS_URL: str
    REDIS_CACHE_DB: int = 1  # ✅ No more hardcoded .replace("/0", "/1")
    REDIS_CELERY_DB: int = 0
    
    # Bot
    BOT_TOKEN: SecretStr
    BOT_WEBHOOK_URL: HttpUrl | None = None
    
    # Features
    ENABLE_DEMO_MODE: bool = False
    ENABLE_PAYMENT_FEATURES: bool = True
    
    # Retry Configuration
    CELERY_TASK_MAX_RETRIES: int = 3
    CELERY_TASK_RETRY_DELAY: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True
```

---

### Task 4.2: Write Architecture Documentation
**Issue:** Missing documentation (#10)  
**Time:** 2 days  
**Owner:** Dev Team

**Documents to Create:**

1. **apps/ARCHITECTURE.md** (Main architecture guide)
   - Folder structure and responsibilities
   - DI system usage guide
   - Import rules and layer boundaries
   - How to add new features
   - Decision log

2. **apps/api/README.md**
   - API structure overview
   - How to add new endpoints
   - Authentication/authorization
   - Testing guidelines

3. **apps/bot/README.md**
   - Bot structure overview
   - How to add new handlers
   - Middleware usage
   - Testing guidelines

4. **apps/di/README.md**
   - DI container guide
   - How to add new services
   - Container composition pattern
   - Troubleshooting

5. **MIGRATION_GUIDE.md**
   - How to migrate from legacy DI to new DI
   - Common patterns and examples
   - Breaking changes

---

### Task 4.3: Add Code Quality Checks
**Issue:** Prevention of future violations  
**Time:** 1 day  
**Owner:** Dev Team

**Actions:**
- [ ] Add import linter (flake8-import-order)
- [ ] Add complexity checker (radon, mccabe)
- [ ] Add type checking (mypy) for apps/
- [ ] Add pre-commit hooks
- [ ] Update CI/CD pipeline

**Code Quality Rules:**
```python
# .flake8
[flake8]
max-line-length = 100
max-complexity = 10
import-order-style = google

# Prevent apps → infra imports
per-file-ignores =
    apps/di/*.py:  # Only DI containers can import infra
    apps/shared/factory.py:  # Factory can import infra

# pyproject.toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[[tool.mypy.overrides]]
module = "apps.*"
disallow_any_unimported = true  # Catch infra imports
```

---

## Progress Tracking

### Metrics Dashboard

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| DI Containers | 7 | 1 | 🔴 |
| Deprecated Files | ~50 | 0 | 🔴 |
| TODO Comments | 40 | <10 | 🔴 |
| Test Coverage | 0% | 60% | 🔴 |
| Circular Dependencies | 5+ | 0 | 🔴 |
| Import Violations | 20+ | 0 | 🔴 |
| Avg File Size | 180 lines | <150 | 🟡 |
| Documentation Pages | 2 | 8 | 🔴 |

### Weekly Goals

**Week 1 (Oct 19-25):**
- [ ] Task 1.1: Consolidate DI System
- [ ] Task 1.2: Fix circular dependencies
- [ ] Task 1.3: Break internal cycles

**Week 2 (Oct 26 - Nov 1):**
- [ ] Task 2.1: Add test coverage
- [ ] Task 2.2: Remove deprecated code
- [ ] Task 2.3: Resolve TODOs

**Week 3 (Nov 2-8):**
- [ ] Task 3.1: Simplify DI containers
- [ ] Task 3.2: Remove duplicates
- [ ] Task 3.3: Standardize errors
- [ ] Task 3.4: Clarify shared responsibilities

**Week 4 (Nov 9-16):**
- [ ] Task 4.1: Centralize configuration
- [ ] Task 4.2: Write documentation
- [ ] Task 4.3: Add quality checks
- [ ] Final review and cleanup

---

## Risk Management

### High Risk Items
1. **Breaking existing functionality** during DI migration
   - Mitigation: Add tests BEFORE major changes
   - Mitigation: Test in staging environment

2. **Incomplete migration** leaving mixed state
   - Mitigation: Complete one container at a time
   - Mitigation: Use feature flags if needed

3. **Team resistance** to changes
   - Mitigation: Document WHY changes are needed
   - Mitigation: Provide clear migration examples

---

## Success Criteria

✅ **Week 1 Success:**
- Single DI system in use
- No circular dependencies
- All tests passing

✅ **Week 2 Success:**
- >60% test coverage on critical paths
- Zero deprecated files
- <10 TODO comments

✅ **Week 3 Success:**
- All DI files <300 lines
- No duplicate implementations
- Consistent error handling

✅ **Week 4 Success:**
- Complete documentation
- CI/CD with quality checks
- Clean architecture audit passes

---

## Next Steps

1. ✅ Review this plan with team
2. ✅ Start with Task 1.1 (DI consolidation)
3. ✅ Daily standup to track progress
4. ✅ Weekly retrospective to adjust plan

**Let's start! 🚀**

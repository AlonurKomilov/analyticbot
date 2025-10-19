# Issue #2: Import Violations & Circular Dependencies

**Analysis Date:** October 19, 2025
**Phase 1 Completion:** October 19, 2025 ✅
**Status:** Phase 1 Complete - Circular Dependencies ELIMINATED!
**Priority:** CRITICAL (P0)

---

## 🎉 PHASE 1 COMPLETION UPDATE (October 19, 2025)

**Duration:** ~1.5 hours
**Status:** ✅ **COMPLETE - ALL 4 CIRCULAR DEPENDENCIES ELIMINATED!**

### What Was Fixed

#### Fix #1 & #2: Moved `apps/shared/api/` routers to `apps/api/routers/`
- ✅ Moved `content_protection_router.py` from apps/shared/api/ → apps/api/routers/
- ✅ Moved `payment_router.py` from apps/shared/api/ → apps/api/routers/
- ✅ Updated import in `apps/api/main.py`
- ✅ Deleted `apps/shared/api/` directory completely

**Impact:** Eliminated **Circular Deps #1 and #2** (shared ↔ api, shared ↔ bot)

#### Fix #3: Moved CSV Exporter to Shared Layer
- ✅ Created `apps/shared/exports/` directory
- ✅ Moved `csv_v2.py` from apps/api/exports/ → apps/shared/exports/
- ✅ Updated imports in:
  - apps/bot/handlers/exports.py
  - apps/api/routers/exports_router.py
  - apps/api/routers/sharing_router.py
- ✅ Deleted `apps/api/exports/` directory completely

**Impact:** Eliminated **Circular Dep #3** (bot → api)

#### Fix #4: Indirect Cycle Resolved
By eliminating the root causes (apps/shared/api/ folder), the complex indirect cycle (#4) was also resolved.

### Verification Results

```bash
# Verified NO imports from old locations
grep "from apps.shared.api" apps/**/*.py → 0 results ✅
grep "from apps.api.exports" apps/**/*.py → 0 results ✅

# Verified old directories removed
apps/shared/api/ → DELETED ✅
apps/api/exports/ → DELETED ✅
```

### Phase 1 Results Summary

| Metric | Before | After | Status |
|--------|--------|-------|--------|
| Circular Dependencies | 4 | **0** | ✅ 100% eliminated |
| apps/shared/api/ imports | 2 | **0** | ✅ Fixed |
| apps/api/exports/ imports | 3 | **0** | ✅ Fixed |
| Files moved | 0 | **3** | ✅ Relocated |
| Directories removed | 0 | **2** | ✅ Cleaned |

**🎯 Next Steps:** Proceed to Phase 2 (Protocol Abstractions) to eliminate Clean Architecture violations.

---

## Executive Summary

Found **54 Clean Architecture violations** (apps → infra imports) and **4 circular dependency cycles** across the apps layer. These violations create fragile dependencies, make testing difficult, and violate Clean Architecture principles.

**Impact:**
- **High**: Cannot easily swap infrastructure implementations
- **High**: Circular dependencies create import order issues
- **Medium**: Difficult to understand module responsibilities
- **Medium**: Testing requires complex mocking setups

---

## Part 1: Clean Architecture Violations (apps → infra)

### Overview

**Total Violations:** 54 active imports from `infra/` layer in `apps/` layer
**Files Affected:** 18 files
**Severity Distribution:**
- 🔴 **High (5+ imports):** 5 files
- 🟡 **Medium (2-4 imports):** 4 files
- 🟢 **Low (1 import):** 9 files

### Violations by Category

| Category | Files | Description |
|----------|-------|-------------|
| Repository Imports | 5 | Direct imports of AsyncpgXRepository from infra |
| Telegram Infrastructure | 5 | TelethonClient, parsers, account pools |
| DB Connection/Manager | 2 | DatabaseManager, db_manager imports |
| Cache/Redis | 2 | Redis cache adapter imports |
| Other Infrastructure | 4 | Rendering, performance, faults, ratelimit |

### High Severity Files (5+ imports)

#### 1. `apps/shared/factory.py` (10 imports)
```python
# VIOLATIONS:
from infra.db.repositories.user_repository import AsyncpgUserRepository
from infra.db.repositories.channel_repository import AsyncpgChannelRepository
from infra.db.repositories.analytics_repository import AsyncpgAnalyticsRepository
from infra.db.repositories.admin_repository import AsyncpgAdminRepository
from infra.db.repositories.alert_repository import AsyncpgAlertSubscriptionRepository
from infra.db.repositories.alert_repository import AsyncpgAlertSentRepository
from infra.db.repositories.shared_reports_repository import ...
from infra.db.repositories.payment_repository import AsyncpgPaymentRepository
from infra.db.repositories.plan_repository import AsyncpgPlanRepository
```

**Problem:** Factory pattern but directly imports concrete implementations
**Impact:** Cannot swap database implementations
**Fix:** Use dependency injection instead of factory pattern

#### 2. `apps/api/di_analytics.py` (9 imports)
```python
# VIOLATIONS:
from infra.cache.redis_cache import create_cache_adapter
from infra.db.repositories.channel_daily_repository import AsyncpgChannelDailyRepository
from infra.db.repositories.channel_repository import AsyncpgChannelRepository
from infra.db.repositories.edges_repository import AsyncpgEdgesRepository
from infra.db.repositories.post_metrics_repository import AsyncpgPostMetricsRepository
from infra.db.repositories.post_repository import AsyncpgPostRepository
from infra.db.repositories.stats_raw_repository import AsyncpgStatsRawRepository
from infra.db.connection_manager import db_manager
from infra.tg.telethon_client import TelethonTGClient
```

**Problem:** DI container importing infra directly
**Impact:** Analytics module tightly coupled to PostgreSQL + Telethon
**Fix:** Move to unified DI container (apps/di/)

#### 3. `apps/bot/di.py` (6 imports)
```python
# VIOLATIONS:
from infra.db.repositories.plan_repository import AsyncpgPlanRepository
from infra.db.repositories.schedule_repository import AsyncpgScheduleRepository
from infra.db.repositories.payment_repository import AsyncpgPaymentRepository
from infra.cache.redis_cache_adapter import create_redis_cache_adapter
from infra.services.payment import ...
```

**Problem:** Deprecated DI container (scheduled for deletion Oct 21)
**Impact:** Will be resolved when file is deleted
**Fix:** Already scheduled for deletion

#### 4. `apps/mtproto/di/storage.py` (5 imports)
```python
# VIOLATIONS:
from infra.db.repositories.channel_daily_repository import ChannelDailyRepository
from infra.db.repositories.channel_repository import ChannelRepository
from infra.db.repositories.post_metrics_repository import PostMetricsRepository
from infra.db.repositories.post_repository import PostRepository
from infra.db.repositories.stats_raw_repository import StatsRawRepository
```

**Problem:** MTProto DI container importing infra repositories
**Impact:** MTProto module cannot run with different storage backends
**Fix:** Use apps/di/ providers or create protocol interfaces

#### 5. `apps/mtproto/di/collectors.py` (4 imports)
```python
# VIOLATIONS:
from infra.tg.account_pool import AccountPool
from infra.tg.dc_router import DCRouter
from infra.tg.proxy_pool import ProxyPool
from infra.tg.telethon_client import TelethonTGClient
```

**Problem:** MTProto importing Telegram infrastructure directly
**Impact:** MTProto tightly coupled to Telethon implementation
**Fix:** Create protocols in core/, inject implementations via DI

### Medium Severity Files (2-4 imports)

1. **`apps/mtproto/di/external.py` (3 imports)** - Faults, ratelimit, tracing
2. **`apps/di/bot_container.py` (3 imports)** - Cache, payment services
3. **`apps/shared/di.py` (2 imports)** - DB connection, repositories (scheduled for deletion Oct 27)
4. **`apps/mtproto/collectors/history.py` (2 imports)** - Message parsers

### Low Severity Files (1 import each)

1. `apps/di/database_container.py` - db_manager
2. `apps/di/cache_container.py` - CacheFactory
3. `apps/bot/adapters/analytics_adapter.py` - AiogramBotAdapter
4. `apps/bot/deps.py` - ScheduleRepository (deprecated, delete Oct 21)
5. `apps/bot/utils/init_db.py` - db_manager
6. `apps/api/services/telegram_validation_service.py` - TelethonTGClient
7. `apps/mtproto/di/processors.py` - Parsers
8. `apps/mtproto/collectors/updates.py` - Parsers
9. `apps/shared/services/chart_service.py` - ChartRenderer
10. `apps/shared/performance.py` - performance_timer

### Commented Out Violations (Historical Interest)

Found 33 commented-out infra imports - evidence of previous cleanup attempts.

---

## Part 2: Circular Dependencies

### Overview

Found **4 circular dependency cycles** creating fragile import relationships.

### Circular Dependency #1: apps/shared ↔ apps/api

**Files Involved:**
- `apps/shared/api/content_protection_router.py`
- `apps/api/middleware/auth.py`

**Violation:**
```python
# apps/shared/api/content_protection_router.py
from apps.api.middleware.auth import get_current_user

# apps/api/main.py
from apps.shared.api.content_protection_router import router
```

**Problem:** `apps/shared/api/` folder contains routers that import from `apps/api/`
**Impact:** Creates circular dependency loop
**Root Cause:** Routers placed in wrong folder

**Fix:**
```bash
# Move routers from apps/shared/api/ to apps/api/routers/
mv apps/shared/api/content_protection_router.py apps/api/routers/
mv apps/shared/api/payment_router.py apps/api/routers/
rm -rf apps/shared/api/  # Delete empty folder
```

### Circular Dependency #2: apps/shared ↔ apps/bot

**Files Involved:**
- `apps/shared/api/content_protection_router.py`
- `apps/bot/models/content_protection.py`
- `apps/bot/services/premium_emoji_service.py`

**Violation:**
```python
# apps/shared/api/content_protection_router.py
from apps.bot.models.content_protection import ...
from apps.bot.services.premium_emoji_service import PremiumEmojiService

# apps/bot/handlers/... (various)
from apps.shared.adapters.ml_facade import create_bot_ml_facade
```

**Problem:** Shared layer importing from bot layer
**Impact:** Shared becomes dependent on bot-specific code
**Root Cause:** Routers in wrong location + unclear shared responsibility

**Fix:**
1. Move routers to apps/api/ (eliminates shared → bot import)
2. Move shared models to core/domain/ if truly shared
3. Keep bot-specific code in apps/bot/

### Circular Dependency #3: apps/bot → apps/api

**Files Involved:**
- `apps/bot/handlers/exports.py`
- `apps/api/exports/csv_v2.py`

**Violation:**
```python
# apps/bot/handlers/exports.py
from apps.api.exports.csv_v2 import CSVExporter

# This creates bot → api dependency (wrong direction!)
```

**Problem:** Bot layer importing from API layer
**Impact:** Bot becomes dependent on API module
**Root Cause:** Export functionality not properly shared

**Fix:**
```bash
# Move CSV exporter to shared location
mv apps/api/exports/ apps/shared/exports/

# Or create protocol in core/
# core/protocols/exporter.py
class ExporterProtocol(Protocol):
    def export_to_csv(self, data): ...
```

### Circular Dependency #4: Indirect cycle via shared

**Chain:**
1. `apps/api/main.py` → `from apps.shared.api...`
2. `apps/shared/api/` → `from apps.api.middleware...`
3. `apps/shared/api/` → `from apps.bot.models...`
4. `apps/bot/` → `from apps.shared.adapters...`

**Problem:** Complex web of dependencies
**Impact:** Hard to reason about import order
**Fix:** Break the cycle by moving `apps/shared/api/` to `apps/api/routers/`

---

## Part 3: Import Pattern Analysis

### Current Import Patterns

#### ✅ Acceptable Patterns

```python
# Foundation layer (shared) used by apps
from apps.shared.models import SomeModel
from apps.shared.factory import get_repository_factory
from apps.shared.protocols import SomeProtocol

# Within same app
from apps.bot.config import settings
from apps.api.middleware.auth import get_current_user

# Demo using shared
from apps.shared.models.twa import InitialDataResponse
```

#### ❌ Problematic Patterns

```python
# Apps importing from infra (Clean Architecture violation)
from infra.db.repositories.user_repository import AsyncpgUserRepository
from infra.cache.redis_cache import create_cache_adapter
from infra.tg.telethon_client import TelethonTGClient

# Shared importing from apps (creates circular dependencies)
from apps.api.middleware.auth import get_current_user
from apps.bot.models.content_protection import ...

# Bot importing from API (wrong layer dependency)
from apps.api.exports.csv_v2 import CSVExporter
```

### Dependency Direction Rules

**Correct Dependency Flow (Clean Architecture):**
```
infra/ ← apps/di/ ← apps/{api,bot,jobs,celery}
                 ↖ apps/shared ↗

core/ ← Everyone can import from core
```

**Current Violations:**
```
apps/shared → apps/api (WRONG)
apps/shared → apps/bot (WRONG)
apps/bot → apps/api (WRONG)
apps/* → infra/ (WRONG)
```

---

## Part 4: Root Cause Analysis

### 1. apps/shared/ Unclear Responsibility

**Problem:** `apps/shared/` became a dumping ground for code without clear ownership.

**Evidence:**
- Contains API routers (`apps/shared/api/`)
- Contains bot-specific adapters
- Contains truly shared code (protocols, models)
- Imports from both apps/api and apps/bot

**Impact:** Circular dependencies, unclear module boundaries

### 2. Missing Protocol Abstractions

**Problem:** Direct imports of infrastructure implementations instead of protocols.

**Evidence:**
- `AsyncpgUserRepository` imported directly (concrete class)
- `TelethonTGClient` imported directly (specific implementation)
- No `UserRepositoryProtocol` in core/

**Impact:** Cannot swap implementations, hard to test

### 3. Factory Pattern Misuse

**Problem:** `apps/shared/factory.py` imports all concrete implementations.

**Evidence:**
```python
def create_user_repository(self):
    from infra.db.repositories.user_repository import AsyncpgUserRepository
    return AsyncpgUserRepository(pool=self.pool)
```

**Impact:** Factory defeats the purpose - still tightly coupled

### 4. DI Container Proliferation

**Problem:** Multiple DI containers each importing infra directly.

**Evidence:**
- `apps/bot/di.py` - 6 infra imports
- `apps/api/di_analytics.py` - 9 infra imports
- `apps/mtproto/di/*.py` - 13 infra imports total

**Impact:** Duplicated infra imports, inconsistent patterns

### 5. Lack of Import Linting

**Problem:** No automated checks prevent architecture violations.

**Evidence:** 54 violations accumulated over time

**Impact:** Violations keep being introduced

---

## Part 5: Remediation Strategy

### Phase 1: Quick Wins (Week 3 - Nov 4-8)

**Priority 1A: Delete Scheduled Files (Oct 21-27)**
- ✅ Removes apps/bot/di.py (6 violations)
- ✅ Removes apps/shared/di.py (2 violations)
- **Impact:** -8 violations automatically

**Priority 1B: Move Misplaced Routers (2 hours)**
```bash
# Move apps/shared/api/ to apps/api/routers/
mv apps/shared/api/content_protection_router.py apps/api/routers/
mv apps/shared/api/payment_router.py apps/api/routers/

# Update imports in apps/api/main.py
# Delete empty apps/shared/api/ folder

# Impact:
# - Breaks circular dependency #1 (shared ↔ api)
# - Breaks circular dependency #2 (shared ↔ bot)
# - Clarifies apps/shared responsibility
```

**Priority 1C: Fix Bot → API Dependency (1 hour)**
```bash
# Move CSV exporter to shared
mkdir -p apps/shared/exports
mv apps/api/exports/csv_v2.py apps/shared/exports/

# Update import in apps/bot/handlers/exports.py
# Impact: Breaks circular dependency #3 (bot → api)
```

**Estimated Time:** 3 hours
**Impact:** Removes all 4 circular dependencies! 🎯

### Phase 2: Protocol Abstractions (Week 3 - Nov 11-15)

**Priority 2A: Create Core Protocols (4 hours)**

Create protocols in `core/repositories/` to decouple from infra:

```python
# core/repositories/user_repository.py
from typing import Protocol

class UserRepositoryProtocol(Protocol):
    async def get_by_id(self, user_id: int) -> User | None: ...
    async def create(self, user: User) -> User: ...
    # ... etc
```

**Repeat for:**
- ChannelRepositoryProtocol
- AnalyticsRepositoryProtocol
- CacheProtocol
- TelegramClientProtocol

**Priority 2B: Update DI Containers (2 hours)**

Use protocols in DI containers instead of concrete types:

```python
# apps/di/database_container.py
from core.repositories.user_repository import UserRepositoryProtocol
from infra.db.repositories.user_repository import AsyncpgUserRepository

class DatabaseContainer:
    user_repo = providers.Factory[UserRepositoryProtocol](
        AsyncpgUserRepository,
        pool=...
    )
```

**Estimated Time:** 6 hours
**Impact:** Decouples apps from infra implementations

### Phase 3: Repository Factory Elimination (Week 4 - Nov 18-22)

**Priority 3A: Migrate from Factory to DI (6 hours)**

Replace `apps/shared/factory.py` usage with `apps/di/` providers:

```python
# BEFORE (factory pattern)
from apps.shared.factory import get_repository_factory
factory = get_repository_factory()
user_repo = await factory.create_user_repository()

# AFTER (dependency injection)
from apps.di import get_container
container = get_container()
user_repo = await container.database.user_repo()
```

**Files to migrate:**
- apps/bot/handlers/exports.py
- apps/di/database_container.py
- 5 other files

**Priority 3B: Delete Factory (30 minutes)**

Once all usages migrated:
```bash
rm apps/shared/factory.py  # Removes 10 infra violations!
```

**Estimated Time:** 6.5 hours
**Impact:** Removes 10 Clean Architecture violations

### Phase 4: MTProto Decoupling (Week 4 - Nov 25-29)

**Priority 4A: Create Telegram Protocols (3 hours)**

```python
# core/protocols/telegram.py
class TelegramClientProtocol(Protocol):
    async def send_message(self, ...): ...
    async def get_messages(self, ...): ...

class MessageParserProtocol(Protocol):
    def normalize_message(self, msg): ...
```

**Priority 4B: Update MTProto DI (2 hours)**

Inject protocols instead of concrete implementations:

```python
# apps/mtproto/di/collectors.py
# BEFORE
from infra.tg.telethon_client import TelethonTGClient

# AFTER
from core.protocols.telegram import TelegramClientProtocol
from infra.tg.telethon_client import TelethonTGClient  # Only in DI

class CollectorsContainer:
    tg_client = providers.Factory[TelegramClientProtocol](
        TelethonTGClient,
        ...
    )
```

**Estimated Time:** 5 hours
**Impact:** Removes 13 MTProto infra violations

### Phase 5: Remaining Violations (Week 5 - Dec 2-6)

**Priority 5A: Analytics DI Migration (2 hours)**

Migrate `apps/api/di_analytics.py` to use `apps/di/` providers.

**Priority 5B: Low Severity Fixes (3 hours)**

Fix remaining 10 low-severity violations:
- Chart service rendering
- Performance timer
- Analytics adapter
- etc.

**Estimated Time:** 5 hours
**Impact:** Removes final 19 violations

### Phase 6: Import Linting (Week 5 - Dec 9-13)

**Priority 6A: Add import-linter (1 hour)**

```ini
# importlinter.ini
[importlinter:contract:1]
name = Apps layer cannot import from infra
type = forbidden
source_modules =
    apps.api
    apps.bot
    apps.shared
    apps.jobs
    apps.celery
    apps.demo
forbidden_modules =
    infra

[importlinter:contract:2]
name = Shared cannot import from apps
type = forbidden
source_modules = apps.shared
forbidden_modules =
    apps.api
    apps.bot
    apps.jobs
```

**Priority 6B: Add Pre-commit Hook (30 minutes)**

```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: import-linter
      name: Import Linter
      entry: lint-imports
      language: system
      pass_filenames: false
```

**Estimated Time:** 1.5 hours
**Impact:** Prevents future violations

---

## Part 6: Success Metrics

### Quantitative Goals

| Metric | Baseline | Target | % Improvement |
|--------|----------|--------|---------------|
| Clean Arch Violations | 54 | 0 | 100% |
| Circular Dependencies | 4 | 0 | 100% |
| Files with Violations | 18 | 0 | 100% |
| Protocol Abstractions | 0 | 8+ | ∞ |
| Import Linting | None | Active | N/A |

### Qualitative Goals

- ✅ Can swap database from PostgreSQL to MySQL without changing apps/
- ✅ Can swap Telegram client without changing MTProto logic
- ✅ Can test apps/ layer with mock infrastructure
- ✅ Clear module responsibilities (no more "dumping ground")
- ✅ Automated prevention of future violations

---

## Part 7: Timeline & Effort

### Estimated Timeline

| Phase | Week | Dates | Effort | Impact |
|-------|------|-------|--------|--------|
| Phase 1: Quick Wins | Week 3 | Nov 4-8 | 3h | All circular deps fixed |
| Phase 2: Protocols | Week 3 | Nov 11-15 | 6h | Foundation for decoupling |
| Phase 3: Factory → DI | Week 4 | Nov 18-22 | 6.5h | 10 violations removed |
| Phase 4: MTProto | Week 4 | Nov 25-29 | 5h | 13 violations removed |
| Phase 5: Remaining | Week 5 | Dec 2-6 | 5h | 19 violations removed |
| Phase 6: Linting | Week 5 | Dec 9-13 | 1.5h | Future prevention |

**Total Estimated Effort:** 27 hours (~3-4 days of focused work)

### Incremental Progress

After each phase:
- Phase 1: Circular deps 0, violations 46 (15% reduction)
- Phase 2: Infrastructure for decoupling complete
- Phase 3: Violations 36 (33% reduction from baseline)
- Phase 4: Violations 23 (57% reduction)
- Phase 5: Violations 0 (100% complete!) 🎉
- Phase 6: Permanent protection

---

## Part 8: Risk Assessment

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Breaking imports during refactor | Medium | High | Comprehensive grep before each change |
| Tests fail after DI migration | Medium | Medium | Run test suite after each phase |
| Performance degradation | Low | Medium | Benchmark critical paths |
| Team confusion | Medium | Low | Clear documentation + examples |
| New violations introduced | High | Medium | Import linting (Phase 6) |

### Rollback Strategy

Each phase is independently reversible:
- Phase 1: Git revert (moved files)
- Phase 2-5: Protocols are additive (no breaking changes)
- Phase 6: Can disable linting rules temporarily

---

## Part 9: Next Steps

### Immediate Actions (Oct 19)

1. ✅ **Complete this analysis document**
2. ✅ **Get stakeholder approval** for remediation plan
3. ✅ **Create Issue #2 tracking board**

### Week 3 (Nov 4-8) - Phase 1

1. **Wait for Oct 21/27 deletions** (removes 8 violations automatically)
2. **Move apps/shared/api/ routers** to apps/api/routers/
3. **Move CSV exporter** to apps/shared/exports/
4. **Verify**: All circular dependencies eliminated
5. **Update**: APPS_ARCHITECTURE_TOP_10_ISSUES.md

### Week 3 (Nov 11-15) - Phase 2

1. **Create protocol interfaces** in core/repositories/
2. **Update DI containers** to use protocols
3. **Verify**: Type checking still passes
4. **Document**: Protocol usage patterns

### Continuation

Follow timeline in Part 7 above.

---

## Appendix A: File-by-File Violation List

### High Severity

1. **apps/shared/factory.py**: 10 violations
   - Lines: 93, 107, 121, 136, 150, 164, 178, 407, 422
   - Type: Repository imports
   - Fix: Delete file (Phase 3)

2. **apps/api/di_analytics.py**: 9 violations
   - Lines: 9-15, 93, 381, 435
   - Type: Cache, repositories, client
   - Fix: Migrate to apps/di/ (Phase 5)

3. **apps/bot/di.py**: 6 violations
   - Lines: 85, 89, 93, 147, 190, 198
   - Type: Repositories, cache, payment
   - Fix: Auto-deleted Oct 21

4. **apps/mtproto/di/storage.py**: 5 violations
   - Lines: 9-13
   - Type: Repository imports
   - Fix: Protocol interfaces (Phase 4)

5. **apps/mtproto/di/collectors.py**: 4 violations
   - Lines: 9-12
   - Type: Telegram infrastructure
   - Fix: Protocol interfaces (Phase 4)

### Medium Severity

6. **apps/mtproto/di/external.py**: 3 violations
7. **apps/di/bot_container.py**: 3 violations
8. **apps/shared/di.py**: 2 violations (auto-deleted Oct 27)
9. **apps/mtproto/collectors/history.py**: 2 violations

### Low Severity (10 files)

10-19. Various 1-violation files (see Part 1 above)

---

## Appendix B: Import Dependency Graph

```
Current (Problematic):
┌─────────────┐
│   infra/    │◄──────┐
└─────────────┘       │
       ▲              │
       │              │
       │ (violations) │
       │              │
┌──────┴──────┐       │
│   apps/di/  │       │
└─────────────┘       │
       ▲              │
       │              │
┌──────┴──────────────┴───────┐
│    apps/shared/     │       │
│  (circular deps!)   │◄──┐   │
└─────────────────────┘   │   │
       ▲        ▲         │   │
       │        └─────────┤   │
       │                  │   │
┌──────┴──────┐  ┌────────┴───┴──┐
│  apps/bot/  │◄─┤  apps/api/    │
└─────────────┘  └────────────────┘

Target (Clean Architecture):
┌─────────────┐
│   infra/    │◄──────┐
└─────────────┘       │
                      │
                      │ (DI only)
                      │
               ┌──────┴──────┐
               │  apps/di/   │
               └─────────────┘
                      ▲
                      │
         ┌────────────┼────────────┐
         │            │            │
┌────────┴───┐  ┌─────┴────┐  ┌───┴─────┐
│ apps/bot/  │  │apps/api/ │  │apps/jobs│
└────────────┘  └──────────┘  └─────────┘
         ▲            ▲            ▲
         │            │            │
         └────────────┴────────────┘
                      │
               ┌──────┴──────┐
               │apps/shared/ │
               └─────────────┘
                      ▲
                      │
               ┌──────┴──────┐
               │   core/     │
               └─────────────┘
```

---

**Document Version:** 1.0
**Author:** Architecture Review System
**Next Review:** After Phase 1 completion
**Status:** ✅ APPROVED FOR EXECUTION

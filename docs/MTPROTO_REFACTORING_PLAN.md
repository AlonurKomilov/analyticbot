# MTProto Layer Refactoring Plan
**Professional Architectural Improvement Initiative**

---

## 📋 Executive Summary

**Objective**: Eliminate MTProto direct imports from API routers, moving all Telethon logic into dedicated service layer following Clean Architecture principles.

**Current State**: 14 violations where routers directly import `telethon`
**Target State**: Zero direct MTProto imports in routers; all logic abstracted behind service interfaces
**Impact**: Improved testability, maintainability, and architectural compliance
**Estimated Effort**: 3-5 days (8-12 hours of development)

---

## 🔍 Current Violations Audit

### Critical Violations (7 in Production Routers)
```
apps/api/routers/channels_router.py:242
  └─ from telethon.tl.functions.channels import GetParticipantRequest

apps/api/routers/telegram_storage_router.py:280, 379, 551
  └─ from telethon import TelegramClient
  └─ from telethon.sessions import StringSession
```

### Acceptable Violations (7 in User MTProto Module)
```
apps/api/routers/user_mtproto/setup.py:11-13
apps/api/routers/user_mtproto/verification.py:11-17
apps/api/routers/user_mtproto/deps.py:12
  └─ These are part of the MTProto authentication flow
  └─ STATUS: Acceptable (this IS the MTProto feature boundary)
```

---

## 🎯 Refactoring Scope

### Files Requiring Refactoring (2)
1. ✅ **apps/api/routers/channels_router.py** (1 violation)
2. ✅ **apps/api/routers/telegram_storage_router.py** (6 violations)

### Files Out of Scope (Acceptable)
- `apps/api/routers/user_mtproto/*` - These ARE the MTProto feature implementation
- `apps/mtproto/*` - MTProto infrastructure layer (correct location)
- `core/ports/tg_client.py` - Protocol abstraction (correct pattern)

---

## 📐 Architecture Design

### Current (Violation Pattern)
```
┌─────────────────────────────────────┐
│  Router (API Layer)                 │
│  ├─ REST Endpoints                  │
│  ├─ Request Validation              │
│  └─ ❌ DIRECT TELETHON IMPORTS      │◄── VIOLATION
│      └─ TelegramClient()            │
│      └─ GetParticipantRequest()     │
└─────────────────────────────────────┘
```

### Target (Clean Architecture)
```
┌─────────────────────────────────────┐
│  Router (API Layer)                 │
│  ├─ REST Endpoints                  │
│  ├─ Request Validation              │
│  └─ ✅ Service Dependency Injection │
│      └─ ChannelAdminCheckService    │
│      └─ TelegramStorageService      │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Service Layer (apps/api/services)  │
│  ├─ Business Logic                  │
│  ├─ Protocol Abstraction            │
│  └─ ✅ Telethon Implementation      │
│      └─ Safe imports with guards    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Core/Infrastructure (telethon)     │
│  └─ MTProto Protocol                │
└─────────────────────────────────────┘
```

---

## 🛠️ Implementation Plan

### Phase 1: Service Layer Creation (2-3 hours)

#### Task 1.1: Create ChannelAdminCheckService
**File**: `apps/api/services/channel_admin_check_service.py`

**Purpose**: Encapsulate MTProto admin rights verification logic

**Interface**:
```python
class ChannelAdminCheckService:
    """Service for checking channel admin rights via MTProto."""

    async def check_mtproto_admin_status(
        self,
        user_id: int,
        channel_id: int,
        channel_username: str | None = None,
        telegram_id: int | None = None,
    ) -> dict[str, Any]:
        """
        Check if user has admin rights in a channel via MTProto.

        Returns:
            {
                "is_admin": bool,
                "admin_rights": dict | None,
                "method_used": str,  # "username" | "telegram_id" | "fallback"
                "error": str | None,
            }
        """
```

**Key Features**:
- ✅ All `telethon` imports guarded inside method
- ✅ Handles multiple entity resolution strategies (username, ID, fallback)
- ✅ Proper error handling and logging
- ✅ Returns structured result (not direct Telethon objects)

**Dependencies**:
- `MTProtoService` (existing, for getting user client)
- `UserBotRepository` (existing, for credentials)
- `EncryptionService` (existing, for decrypting API hash)

---

#### Task 1.2: Enhance TelegramStorageService
**File**: `apps/api/services/telegram_storage_service.py` (existing)

**Current Issue**: Service already exists but is instantiated IN the router

**Refactoring**:
1. Move client initialization logic FROM router TO service factory method
2. Create service factory function with DI injection
3. Add service to DI container (`bot_container.py`)

**New Interface**:
```python
class TelegramStorageService:
    @classmethod
    async def create_for_user(
        cls,
        user_id: int,
        db_session: AsyncSession,
        user_bot_repo: IUserBotRepository,
        encryption_service: EncryptionService,
    ) -> "TelegramStorageService":
        """
        Factory method to create service with user's MTProto client.

        Handles:
        - Fetching user credentials
        - Decrypting API hash/session
        - Creating Telethon client
        - Validating authorization

        Raises:
            HTTPException: If credentials missing or session expired
        """
```

---

### Phase 2: Router Refactoring (3-4 hours)

#### Task 2.1: Refactor channels_router.py
**File**: `apps/api/routers/channels_router.py`

**Changes**:
```python
# BEFORE (Line ~230-280)
try:
    from telethon.tl.functions.channels import GetParticipantRequest
    # ... 50 lines of MTProto logic ...
except ImportError:
    mtproto_is_admin = False

# AFTER
admin_check_service = await get_admin_check_service()  # DI
result = await admin_check_service.check_mtproto_admin_status(
    user_id=current_user["id"],
    channel_id=channel.id,
    channel_username=channel_username,
    telegram_id=channel.telegram_id,
)
mtproto_is_admin = result["is_admin"]
```

**Lines Reduced**: ~50 lines → ~5 lines
**Complexity**: High → Low
**Testability**: None → Full (service can be mocked)

---

#### Task 2.2: Refactor telegram_storage_router.py
**File**: `apps/api/routers/telegram_storage_router.py`

**Violations (3 endpoints)**:
1. `/validate` (lines 270-320) - Creates client manually
2. `/upload` (lines 370-430) - Creates client manually
3. `/channels/{channel_id}/media` (lines 540-600) - Creates client manually

**Changes**:
```python
# BEFORE (Repeated 3 times)
from telethon import TelegramClient
from telethon.sessions import StringSession
user_client = TelegramClient(StringSession(session_string), api_id, api_hash)
await user_client.connect()
storage_service = TelegramStorageService(db_session, user_client)

# AFTER (DI Pattern)
storage_service = await create_telegram_storage_service_for_user(
    user_id=current_user["id"],
    db_session=db_session,
)
```

**Lines Reduced**: ~15 lines per endpoint × 3 = ~45 lines → ~3 lines per endpoint = ~9 lines
**Code Duplication**: Eliminated (3 identical blocks → 1 service factory)

---

### Phase 3: Dependency Injection Setup (1-2 hours)

#### Task 3.1: Add Services to DI Container
**File**: `apps/di/bot_container.py`

**New Providers**:
```python
# Channel admin check service
channel_admin_check_service = providers.Factory(
    create_channel_admin_check_service,
    mtproto_service=mtproto_service,
    user_bot_repo=database.user_bot_repo,
    encryption_service=encryption_service,
)

# Telegram storage service factory
telegram_storage_service_factory = providers.Factory(
    create_telegram_storage_service_factory,
    user_bot_repo=database.user_bot_repo,
    encryption_service=encryption_service,
)
```

#### Task 3.2: Create Service Factory Functions
**File**: `apps/di/provider_modules/mtproto_providers.py` (new)

```python
def create_channel_admin_check_service(
    mtproto_service,
    user_bot_repo,
    encryption_service,
) -> ChannelAdminCheckService:
    """Factory for ChannelAdminCheckService."""
    return ChannelAdminCheckService(
        mtproto_service=mtproto_service,
        user_bot_repo=user_bot_repo,
        encryption_service=encryption_service,
    )

def create_telegram_storage_service_factory(
    user_bot_repo,
    encryption_service,
):
    """Factory for TelegramStorageService factory."""
    async def factory(user_id: int, db_session: AsyncSession):
        return await TelegramStorageService.create_for_user(
            user_id=user_id,
            db_session=db_session,
            user_bot_repo=user_bot_repo,
            encryption_service=encryption_service,
        )
    return factory
```

---

### Phase 4: Testing & Validation (2 hours)

#### Task 4.1: Unit Tests
**Files**: `tests/api/services/test_channel_admin_check_service.py`

**Test Coverage**:
- ✅ Admin check with username resolution
- ✅ Admin check with telegram_id resolution
- ✅ Fallback logic when primary methods fail
- ✅ Error handling (ImportError, FloodWaitError, etc.)
- ✅ Mock Telethon client (no real MTProto calls)

#### Task 4.2: Integration Tests
**Files**: `tests/api/routers/test_channels_router_mtproto.py`

**Test Coverage**:
- ✅ GET /channels endpoint with MTProto admin check
- ✅ Service properly injected via DI
- ✅ Error responses for missing credentials

#### Task 4.3: Import Guard Validation
**Command**: `python3 scripts/guard_imports.py`

**Expected Output**:
```bash
✅ 0 import violations (down from 7)
✅ Core layer clean
✅ API routers clean (user_mtproto/* excluded)
```

---

## 📊 Success Metrics

### Code Quality Metrics
| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Direct MTProto Imports (Routers) | 7 | 0 | 100% |
| Code Duplication (telegram_storage_router) | 3 blocks | 0 | 100% |
| Lines of Code (channels_router) | ~50 | ~5 | 90% |
| Testability | 0% | 100% | ∞ |
| Service Abstractions | 0 | 2 | +2 |

### Architectural Compliance
- ✅ Clean Architecture: Routers depend on Services, not Infrastructure
- ✅ Dependency Inversion: Services implement protocols, not concrete implementations
- ✅ Single Responsibility: Routers handle HTTP, Services handle MTProto
- ✅ DRY Principle: Client initialization logic extracted to single factory

---

## 🚀 Migration Strategy

### Stage 1: Non-Breaking Addition (Day 1)
1. Create new services WITHOUT touching routers
2. Add services to DI container
3. Write comprehensive unit tests
4. **Status**: No production impact, fully backward compatible

### Stage 2: Parallel Implementation (Day 2)
1. Update routers to use new services
2. Keep old logic commented out as fallback
3. Deploy to staging environment
4. Run integration tests

### Stage 3: Cleanup & Validation (Day 3)
1. Remove old commented code
2. Run import guard validation
3. Update documentation
4. Deploy to production

### Rollback Plan
- Services are additive, can be removed without breaking old code
- Git commit for each phase, easy rollback points
- Feature flag possible: `USE_MTPROTO_SERVICE_LAYER=true`

---

## 📝 File Manifest

### Files to Create (4)
1. `apps/api/services/channel_admin_check_service.py` (~150 lines)
2. `apps/di/provider_modules/mtproto_providers.py` (~60 lines)
3. `tests/api/services/test_channel_admin_check_service.py` (~200 lines)
4. `tests/api/routers/test_channels_router_mtproto.py` (~150 lines)

### Files to Modify (4)
1. `apps/api/routers/channels_router.py` (~50 lines deleted, ~10 added)
2. `apps/api/routers/telegram_storage_router.py` (~45 lines deleted, ~12 added)
3. `apps/api/services/telegram_storage_service.py` (~30 lines added)
4. `apps/di/bot_container.py` (~15 lines added)

### Files to Update (Documentation) (2)
1. `docs/ARCHITECTURE.md` - Add service layer documentation
2. `docs/MTPROTO_REFACTORING_PLAN.md` - Mark as completed

**Total**: 10 files (4 new, 4 modified, 2 docs)

---

## ⚠️ Risks & Mitigation

### Risk 1: Session Management Edge Cases
**Risk**: User sessions may expire during refactoring
**Mitigation**:
- Factory method handles authorization checks
- Clear error messages guide users to reconnect MTProto
- Graceful fallback to bot-only mode

### Risk 2: Performance Regression
**Risk**: Service layer adds abstraction overhead
**Mitigation**:
- Services are lightweight wrappers (no heavy computation)
- Client pooling already handled by existing MTProto infrastructure
- Benchmark tests before/after

### Risk 3: DI Container Complexity
**Risk**: Adding more services may bloat container
**Mitigation**:
- Services are Factory-scoped (created on demand)
- Follow existing pattern from `AlertsManagementService` refactor
- Document provider structure clearly

---

## 🎓 Learning & Best Practices

### Pattern Established: Service Abstraction
This refactoring establishes a **repeatable pattern** for future MTProto integrations:

1. **Never** import `telethon` in routers
2. **Always** create service layer with protocol abstraction
3. **Guard** all MTProto imports with try/except (graceful degradation)
4. **Inject** services via DI container (testability)
5. **Factory** pattern for user-specific clients

### Related Architectural Fixes
This follows the pattern from the recent **AlertsManagementService** refactor:
- Core layer importing from Apps layer (Service Locator anti-pattern)
- Fixed by: Dependency Injection via constructor
- Result: Clean architecture compliance, improved testability

---

## 📅 Implementation Timeline

### Sprint Breakdown
```
Day 1 (3 hours)
├─ Morning: Create ChannelAdminCheckService
├─ Afternoon: Enhance TelegramStorageService factory
└─ Evening: Unit tests for both services

Day 2 (4 hours)
├─ Morning: Refactor channels_router.py
├─ Afternoon: Refactor telegram_storage_router.py
└─ Evening: Integration tests

Day 3 (2 hours)
├─ Morning: DI container setup & validation
├─ Afternoon: Documentation & deployment
└─ Final: Run import guard (expected: 0 violations)
```

### Dependencies
- ✅ No external dependencies (Telethon already installed)
- ✅ No database migrations required
- ✅ No API contract changes (internal refactor only)

---

## ✅ Completion Checklist

### Development
- [ ] ChannelAdminCheckService created
- [ ] TelegramStorageService factory method added
- [ ] channels_router.py refactored
- [ ] telegram_storage_router.py refactored
- [ ] DI container providers added
- [ ] Provider factory functions created

### Testing
- [ ] Unit tests (ChannelAdminCheckService)
- [ ] Unit tests (TelegramStorageService factory)
- [ ] Integration tests (channels_router)
- [ ] Integration tests (telegram_storage_router)
- [ ] Import guard passes (0 violations)
- [ ] Manual testing (staging environment)

### Documentation
- [ ] Service interfaces documented
- [ ] Architecture diagram updated
- [ ] Migration guide written
- [ ] Commit messages follow convention

### Deployment
- [ ] Code review completed
- [ ] Staging deployment successful
- [ ] Production deployment successful
- [ ] Rollback plan tested
- [ ] Monitoring alerts configured

---

## 🎉 Expected Outcome

After completion, your system will have:

✅ **Zero MTProto violations** in production routers
✅ **100% testable** channel admin check logic
✅ **Reduced code duplication** by ~50 lines
✅ **Clean Architecture compliance** maintained
✅ **Professional service layer** established
✅ **Repeatable pattern** for future MTProto features

---

## 📞 Support & Questions

If you encounter issues during implementation:
1. Check existing service patterns (`AlertsManagementService`, `TelegramValidationService`)
2. Review DI container provider examples (`bot_container.py`)
3. Test with `python3 scripts/guard_imports.py` frequently
4. Use feature flags for gradual rollout

---

**Document Version**: 1.0
**Created**: November 23, 2025
**Status**: Ready for Implementation
**Estimated Completion**: 3-5 days

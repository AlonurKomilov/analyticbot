# DI Migration Inventory

**Generated:** October 19, 2025  
**Purpose:** Track all files that need DI migration

---

## Summary

- **apps/bot/di.py imports:** 1 file (self-reference only)
- **apps/api/di.py imports:** 6 files
- **apps/shared/di.py imports:** 10 files
- **Total files to migrate:** 15 unique files

---

## Files Using apps/shared/di.py (10 files) - HIGH PRIORITY

These are the most common and need migration first:

1. ✅ `apps/api/main.py` - **ALREADY MIGRATED**
   - Uses: `from apps/shared/di import close_container, get_container`
   - Status: Main API already uses apps/di, but also imports from shared
   - Action: Remove apps/shared/di imports, use apps/di exclusively

2. `apps/api/deps.py` - **NEEDS MIGRATION**
   - Uses: `from apps/shared/di import Settings as DISettings, init_container`
   - Action: Replace with apps/di container

3. `apps/api/middleware/auth.py` - **NEEDS MIGRATION**
   - Uses: `from apps/shared.di import get_container` (2 imports)
   - Action: Change to `from apps.di import get_container`

4. `apps/api/services/initial_data_service.py` - **NEEDS MIGRATION**
   - Uses: `from apps.shared.di import get_container`
   - Action: Change to `from apps.di import get_container`

5. `apps/api/services/startup_health_check.py` - **NEEDS MIGRATION**
   - Uses: `from apps.shared.di import get_container`
   - Action: Change to `from apps.di import get_container`

6. `apps/bot/di.py` - **TO BE DELETED**
   - Uses: `from apps.shared.di import get_container` (2 imports)
   - Status: Already deprecated, scheduled for deletion
   - Action: Delete entire file after migration

7. `apps/shared/factory.py` - **NEEDS MIGRATION**
   - Uses: `from apps.shared.di import get_container`
   - Action: Change to `from apps.di import get_container`

8. `apps/shared/health.py` - **NEEDS MIGRATION**
   - Uses: `from apps.shared.di import Container, get_container`
   - Action: Change to `from apps.di import get_container`

---

## Files Using apps/api/di.py (6 files) - MEDIUM PRIORITY

1. `apps/api/deps.py` - **NEEDS MIGRATION**
   - Uses: `from apps.api.di import container` (3 imports)
   - Action: Replace with apps/di

2. `apps/api/main.py` - **NEEDS CLEANUP**
   - Uses: `import apps.api.di as api_di`
   - Action: Remove this import (already uses apps/di and apps/shared/di)

3. `apps/api/routers/system_router.py` - **NEEDS MIGRATION**
   - Uses: `from apps.api.di import container`
   - Action: Replace with apps/di

4. `apps/demo/routers/main.py` - **NEEDS MIGRATION**
   - Uses: `from apps.api.di import configure_services, container`
   - Action: Replace with apps/di

---

## Files Using apps/bot/di.py (1 file) - LOW PRIORITY

1. `apps/bot/di.py` - **SELF-REFERENCE**
   - This is the deprecated file itself
   - Action: Delete after verifying no external usage

---

## Migration Order

### Phase 1: Critical API Files (Day 1)
1. ✅ `apps/api/middleware/auth.py` - Auth is critical
2. ✅ `apps/api/deps.py` - Used by all endpoints
3. ✅ `apps/api/main.py` - Entry point (cleanup)

### Phase 2: API Services (Day 1)
4. ✅ `apps/api/services/startup_health_check.py`
5. ✅ `apps/api/services/initial_data_service.py`
6. ✅ `apps/api/routers/system_router.py`

### Phase 3: Shared Code (Day 2)
7. ✅ `apps/shared/factory.py` - Used by many services
8. ✅ `apps/shared/health.py`

### Phase 4: Demo & Cleanup (Day 2)
9. ✅ `apps/demo/routers/main.py`
10. ✅ Delete `apps/bot/di.py`
11. ✅ Consider: Delete or deprecate `apps/api/di.py`
12. ✅ Consider: Delete or refactor `apps/shared/di.py`

---

## Migration Template

For each file, follow this pattern:

**BEFORE:**
```python
from apps.shared.di import get_container

async def my_function():
    container = get_container()
    user_repo = await container.user_repository()
```

**AFTER:**
```python
from apps.di import get_container

async def my_function():
    container = get_container()
    user_repo = await container.database.user_repo()  # Note namespace change
```

---

## Verification Steps

After each migration:

1. ✅ Update imports
2. ✅ Fix namespace (container.X → container.database.X)
3. ✅ Add await if needed
4. ✅ Run file through Python syntax checker
5. ✅ Test the specific functionality
6. ✅ Update this tracking document

---

## Completion Criteria

- [ ] All 15 files migrated
- [ ] No imports from apps/bot/di.py
- [ ] No imports from apps/api/di.py (or file deleted)
- [ ] Minimal imports from apps/shared/di.py (or file refactored)
- [ ] All tests passing
- [ ] Documentation updated

---

**Status:** 🚧 IN PROGRESS  
**Next Action:** Start Phase 1 - migrate auth.py

# 🚀 Infrastructure Refactoring - Safe Migration Plan

**Date:** December 24, 2025  
**Goal:** Reorganize infra/ to prevent duplicates and improve maintainability

---

## 📊 Pre-Migration Analysis

### Files to Move/Delete Summary

| Action | Count | Impact |
|--------|-------|--------|
| Delete exact duplicates | 2 files | ✅ Safe (no imports) |
| Consolidate cache files | 5 files → 1 | 🔴 6 imports to update |
| Delete marketplace duplicate | 1 file | ✅ Safe (import via __init__) |
| Reorganize observability | 4 folders → 1 | ⚠️ Low impact |

### Import Dependencies Found

**Cache imports (6 locations):**
1. `apps/api/main.py` - `from infra.security.adapters import RedisCache`
2. `apps/di/__init__.py` - `from infra.security.adapters import RedisCache`
3. `apps/di/analytics_container.py` - `from infra.cache.redis_cache import create_cache_adapter`
4. `apps/di/provider_modules/bot_services.py` - `from infra.cache.redis_cache_adapter import create_redis_cache_adapter`
5. `infra/factories/repository_factory.py` - `from infra.cache.redis_cache import create_cache_adapter`
6. `tests/unit/test_cache_adapter.py` - `from infra.cache.redis_cache_adapter import InMemoryCacheAdapter`

**Marketplace imports:**
- All imports use `from infra.marketplace import MarketplaceServiceRepository` (via __init__.py)
- ✅ Safe to delete duplicate and update __init__.py

---

## 🎯 Phase-by-Phase Migration Plan

### Phase 0: Preparation & Backup ✅
- [x] Create audit report
- [x] Analyze all imports
- [x] Create migration plan
- [ ] Create backup branch
- [ ] Run full test suite baseline

### Phase 1: Safe Deletions (Zero Impact)

**Delete exact duplicate file:**
```bash
rm infra/adapters/analytics/tg_analytics_adapter.py
```

**Impact:** ✅ None - file not imported anywhere

**Test:** Grep search confirms no imports

---

### Phase 2: Marketplace Consolidation

**Delete duplicate repository:**
```bash
rm infra/marketplace/repositories/services.py
```

**Update export:**
```python
# infra/marketplace/__init__.py
from infra.db.repositories.marketplace_service_repository import MarketplaceServiceRepository
```

**Impact:** ✅ Low - all apps import via `infra.marketplace` __init__

**Test:**
```bash
python -c "from infra.marketplace import MarketplaceServiceRepository; print('OK')"
pytest apps/tests/test_api/test_routers/test_credits.py -v
```

---

### Phase 3: Cache Consolidation (CRITICAL)

**Step 3.1: Create unified cache module**

Create `infra/caching/cache_service.py`:
```python
"""
Unified Redis Cache Service
===========================

This is the ONLY cache implementation to use.
DO NOT create alternative cache implementations.

Usage:
    from infra.caching import CacheService
    
    cache = CacheService()
    await cache.set("key", "value", ttl=3600)
    value = await cache.get("key")
"""

import redis.asyncio as redis
from typing import Any, Optional
import json
from core.ports.cache_port import AsyncCachePort

class CacheService(AsyncCachePort):
    """Unified async Redis cache service."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self._client: Optional[redis.Redis] = None
    
    async def connect(self):
        if not self._client:
            self._client = await redis.from_url(self.redis_url, decode_responses=True)
    
    async def get(self, key: str) -> Optional[Any]:
        await self.connect()
        value = await self._client.get(key)
        if value:
            try:
                return json.loads(value)
            except:
                return value
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        await self.connect()
        serialized = json.dumps(value) if not isinstance(value, str) else value
        if ttl:
            return await self._client.setex(key, ttl, serialized)
        return await self._client.set(key, serialized)
    
    async def delete(self, key: str) -> bool:
        await self.connect()
        return bool(await self._client.delete(key))
    
    async def exists(self, key: str) -> bool:
        await self.connect()
        return bool(await self._client.exists(key))
    
    async def clear(self) -> bool:
        await self.connect()
        await self._client.flushdb()
        return True

# In-memory cache for testing
class InMemoryCacheAdapter(AsyncCachePort):
    def __init__(self):
        self._cache = {}
    
    async def get(self, key: str) -> Optional[Any]:
        return self._cache.get(key)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        self._cache[key] = value
        return True
    
    async def delete(self, key: str) -> bool:
        self._cache.pop(key, None)
        return True
    
    async def exists(self, key: str) -> bool:
        return key in self._cache
    
    async def clear(self) -> bool:
        self._cache.clear()
        return True
```

**Step 3.2: Create folder structure**
```bash
mkdir -p infra/caching
touch infra/caching/__init__.py
touch infra/caching/README.md
```

**Step 3.3: Create __init__.py**
```python
# infra/caching/__init__.py
"""
Caching Infrastructure
======================

USE THIS for all caching needs:
    from infra.caching import CacheService
    
DO NOT create alternative cache implementations.
"""

from infra.caching.cache_service import CacheService, InMemoryCacheAdapter

__all__ = [
    "CacheService",
    "InMemoryCacheAdapter",
]
```

**Step 3.4: Update all 6 imports**

1. `apps/api/main.py:71`
   ```python
   # OLD: from infra.security.adapters import RedisCache
   # NEW: from infra.caching import CacheService
   ```

2. `apps/di/__init__.py:142`
   ```python
   # OLD: from infra.security.adapters import RedisCache
   # NEW: from infra.caching import CacheService
   ```

3. `apps/di/analytics_container.py:41`
   ```python
   # OLD: from infra.cache.redis_cache import create_cache_adapter
   # NEW: from infra.caching import CacheService
   ```

4. `apps/di/provider_modules/bot_services.py:39`
   ```python
   # OLD: from infra.cache.redis_cache_adapter import create_redis_cache_adapter
   # NEW: from infra.caching import CacheService
   ```

5. `infra/factories/repository_factory.py:83`
   ```python
   # OLD: from infra.cache.redis_cache import create_cache_adapter
   # NEW: from infra.caching import CacheService
   ```

6. `tests/unit/test_cache_adapter.py:6`
   ```python
   # OLD: from infra.cache.redis_cache_adapter import InMemoryCacheAdapter, create_redis_cache_adapter
   # NEW: from infra.caching import InMemoryCacheAdapter, CacheService
   ```

**Step 3.5: Archive old cache files**
```bash
mkdir -p infra/cache_old_backup
mv infra/cache/*.py infra/cache_old_backup/
```

**Step 3.6: Test cache consolidation**
```bash
# Test imports
python -c "from infra.caching import CacheService; print('OK')"

# Test API
./scripts/dev-start.sh api
sleep 3
curl http://localhost:11400/health

# Test Bot (if needed)
# ./scripts/dev-start.sh bot

# Run cache tests
pytest tests/unit/test_cache_adapter.py -v
```

---

### Phase 4: Empty Folder Cleanup

**Delete empty bot placeholder:**
```bash
rm -rf infra/bot/
```

**Impact:** ✅ None - only contains empty __init__.py

---

### Phase 5: Process Manager (Choose One)

**Option A: Using systemd (recommended for VPS)**
```bash
mkdir -p infra/deployment/systemd
mv infra/systemd/*.service infra/deployment/systemd/
rm -rf infra/supervisor/
rm -rf infra/systemd/
```

**Option B: Using Docker/K8s**
```bash
# Don't need either
rm -rf infra/supervisor/
rm -rf infra/systemd/
```

**Test:** Check current deployment method first

---

### Phase 6: Observability Consolidation (Optional)

**Only if time permits - lower priority**

```bash
mkdir -p infra/observability/{logging,metrics,tracing,health}
mv infra/logging/* infra/observability/logging/
mv infra/obs/* infra/observability/tracing/
mv infra/monitoring/* infra/observability/metrics/
mv infra/health/* infra/observability/health/
```

**Impact:** ⚠️ Medium - several imports to update

**Decision:** Skip for now, do in separate PR

---

## ✅ Testing Checklist

After each phase:

```bash
# 1. Import test
python -c "from infra.caching import CacheService; print('Cache OK')"
python -c "from infra.marketplace import MarketplaceServiceRepository; print('Marketplace OK')"

# 2. API health check
./scripts/dev-start.sh api
sleep 3
curl http://localhost:11400/health
curl http://localhost:11400/api/v1/channels

# 3. Run targeted tests
pytest apps/tests/test_api/test_routers/test_credits.py -v
pytest apps/tests/test_api/test_routers/test_marketplace.py -v
pytest tests/unit/test_cache_adapter.py -v

# 4. Check for errors
grep -r "ModuleNotFoundError" logs/ 2>/dev/null | head -5
grep -r "ImportError" logs/ 2>/dev/null | head -5

# 5. Git status (ensure no accidental deletions)
git status
```

---

## 🔄 Rollback Plan

If anything breaks:

```bash
# Quick rollback
git checkout HEAD -- infra/

# Or restore from backup branch
git checkout backup-before-refactor -- infra/
```

---

## 📝 Execution Order

**TODAY (Safe changes):**
1. ✅ Phase 0: Create backup
2. ✅ Phase 1: Delete duplicate analytics file
3. ✅ Phase 2: Marketplace consolidation
4. ✅ Test after Phase 2

**TOMORROW (If Phase 1-2 stable):**
5. Phase 3: Cache consolidation (most complex)
6. Test thoroughly after Phase 3
7. Phase 4: Empty folder cleanup
8. Phase 5: Process manager cleanup

**LATER (Separate PR):**
9. Phase 6: Observability consolidation

---

## 🎯 Success Criteria

- [ ] All tests passing
- [ ] API starts without errors
- [ ] Bot starts without errors
- [ ] No import errors in logs
- [ ] Health checks return 200
- [ ] Git diff shows intentional changes only
- [ ] No accidental deletions
- [ ] Documentation updated

---

## 📞 Emergency Contacts

If something breaks badly:
1. Stop all services
2. Check logs: `tail -f logs/*.log`
3. Rollback: `git checkout HEAD -- infra/`
4. Restart services

---

*Next Step: Create backup branch and begin Phase 1*

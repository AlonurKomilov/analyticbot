# Phase 2 & 3 Implementation Plan

**Status**: 🚧 In Progress  
**Start Date**: December 24, 2025  
**Estimated Completion**: 3-4 days

---

## Phase 2: Full Dynamic Rate Limits (No Restart)

### Goal
Enable true hot-reload of rate limit configurations without requiring API restart. Changes made by admins take effect within 30 seconds across all instances.

### Architecture Changes

#### 1. Cached Config Loader ✅
```python
class RateLimitConfigCache:
    """In-memory cache with 30-second TTL"""
    - Stores loaded configs in memory
    - Refreshes every 30 seconds from Redis
    - Thread-safe with asyncio locks
    - Automatic cache invalidation
```

#### 2. Dynamic Decorator
```python
@dynamic_rate_limit(service="bot_operations", default="100/minute")
async def create_bot():
    """Decorator checks cache at request time"""
```

**How it works**:
1. Request arrives
2. Decorator checks cache for config
3. If cache expired (>30s), reload from Redis
4. Apply current limit dynamically
5. Continue with request

#### 3. Benefits
- ✅ No restart required
- ✅ Changes apply within 30 seconds
- ✅ Works across multiple API instances
- ✅ Performance impact minimal (cache hits)
- ✅ Backward compatible with existing decorators

### Implementation Steps

1. **Create rate_limit_cache.py** - Config cache with TTL
2. **Add dynamic_rate_limit decorator** - Runtime config lookup
3. **Update middleware** - Support dynamic limits
4. **Migrate endpoints** - Replace @limiter.limit with @dynamic_rate_limit
5. **Add cache invalidation** - Force reload on admin updates
6. **Test hot-reload** - Verify no restart needed

---

## Phase 3: Database Persistence & Audit Trail

### Goal
Store rate limit configurations in PostgreSQL with full audit trail. Track who changed what and when.

### Database Schema

#### Table: `rate_limit_configs`
```sql
CREATE TABLE rate_limit_configs (
    id SERIAL PRIMARY KEY,
    service_key VARCHAR(100) UNIQUE NOT NULL,  -- e.g., "bot_operations"
    service_name VARCHAR(200) NOT NULL,        -- e.g., "Bot Operations"
    limit_value INTEGER NOT NULL,              -- e.g., 500
    period VARCHAR(20) NOT NULL,               -- e.g., "minute"
    enabled BOOLEAN DEFAULT TRUE,
    description TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),                   -- Admin user ID
    updated_by VARCHAR(100)                    -- Admin user ID
);
```

#### Table: `rate_limit_audit_log`
```sql
CREATE TABLE rate_limit_audit_log (
    id SERIAL PRIMARY KEY,
    service_key VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,               -- "create", "update", "delete", "reset"
    
    old_limit INTEGER,                         -- Previous value
    new_limit INTEGER,                         -- New value
    old_period VARCHAR(20),
    new_period VARCHAR(20),
    
    changed_by VARCHAR(100) NOT NULL,          -- Admin user ID
    changed_by_username VARCHAR(200),
    changed_by_ip VARCHAR(50),
    
    change_reason TEXT,                        -- Optional explanation
    metadata JSONB,                            -- Additional context
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Table: `rate_limit_stats`
```sql
CREATE TABLE rate_limit_stats (
    id SERIAL PRIMARY KEY,
    service_key VARCHAR(100) NOT NULL,
    ip_address VARCHAR(50) NOT NULL,
    
    requests_made INTEGER DEFAULT 0,
    requests_blocked INTEGER DEFAULT 0,
    last_request_at TIMESTAMP,
    last_blocked_at TIMESTAMP,
    
    window_start TIMESTAMP NOT NULL,
    window_end TIMESTAMP NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(service_key, ip_address, window_start)
);
```

### Implementation Steps

1. **Create SQLAlchemy models** - Define ORM classes
2. **Create migration script** - Alembic migration
3. **Create repository** - CRUD operations for configs
4. **Create audit service** - Log all changes
5. **Migrate from Redis** - Copy existing configs to DB
6. **Update admin service** - Use database instead of Redis
7. **Add audit endpoints** - View change history
8. **Update UI** - Show audit trail in dashboard

---

## Implementation Timeline

### Day 1: Phase 2 Core (Today)

**Morning** (4 hours):
- [x] Create implementation plan
- [ ] Design cache architecture
- [ ] Implement `RateLimitConfigCache` class
- [ ] Add TTL and refresh logic

**Afternoon** (4 hours):
- [ ] Create `dynamic_rate_limit` decorator
- [ ] Test decorator with mock configs
- [ ] Add cache invalidation endpoint
- [ ] Update middleware for dynamic support

### Day 2: Phase 2 Migration

**Morning** (4 hours):
- [ ] Identify all endpoints using rate limits
- [ ] Create migration script for decorators
- [ ] Migrate 50% of endpoints

**Afternoon** (4 hours):
- [ ] Migrate remaining endpoints
- [ ] Test all endpoints with dynamic limits
- [ ] Verify no restart needed
- [ ] Load testing (performance impact)

### Day 3: Phase 3 Database

**Morning** (4 hours):
- [ ] Create SQLAlchemy models
- [ ] Create Alembic migration
- [ ] Run migration in development
- [ ] Create repository class

**Afternoon** (4 hours):
- [ ] Implement audit logging
- [ ] Migrate data from Redis to PostgreSQL
- [ ] Update admin service
- [ ] Test database persistence

### Day 4: Phase 3 UI & Docs

**Morning** (4 hours):
- [ ] Create audit trail endpoints
- [ ] Update admin dashboard UI
- [ ] Add "View History" feature
- [ ] Test audit trail

**Afternoon** (4 hours):
- [ ] Update all documentation
- [ ] Create admin training guide
- [ ] Production deployment plan
- [ ] Final testing

---

## Technical Specifications

### Phase 2: Cache Implementation

```python
# apps/api/middleware/rate_limit_cache.py

import asyncio
import time
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class CachedConfig:
    """Single cached config with metadata"""
    limit: int
    period: str
    enabled: bool
    cached_at: float
    
    def is_expired(self, ttl: int = 30) -> bool:
        """Check if cache entry is older than TTL seconds"""
        return time.time() - self.cached_at > ttl

class RateLimitConfigCache:
    """
    In-memory cache for rate limit configurations
    - 30-second TTL
    - Thread-safe with asyncio locks
    - Automatic refresh from Redis
    """
    
    def __init__(self, ttl: int = 30):
        self._cache: Dict[str, CachedConfig] = {}
        self._lock = asyncio.Lock()
        self._ttl = ttl
    
    async def get(self, service_key: str) -> Optional[CachedConfig]:
        """Get config from cache, refresh if expired"""
        async with self._lock:
            cached = self._cache.get(service_key)
            
            # Return if fresh
            if cached and not cached.is_expired(self._ttl):
                return cached
            
            # Refresh if expired
            await self._refresh(service_key)
            return self._cache.get(service_key)
    
    async def _refresh(self, service_key: str):
        """Reload config from Redis"""
        from core.services.system import get_rate_limit_service
        service = get_rate_limit_service()
        config = await service.get_config(service_key)
        
        if config:
            self._cache[service_key] = CachedConfig(
                limit=config["limit"],
                period=config["period"],
                enabled=config.get("enabled", True),
                cached_at=time.time()
            )
    
    async def invalidate(self, service_key: Optional[str] = None):
        """Clear cache for one or all services"""
        async with self._lock:
            if service_key:
                self._cache.pop(service_key, None)
            else:
                self._cache.clear()

# Global cache instance
_config_cache = RateLimitConfigCache(ttl=30)
```

### Phase 2: Dynamic Decorator

```python
# apps/api/middleware/rate_limiter.py

from functools import wraps
from typing import Callable
from fastapi import Request

def dynamic_rate_limit(service: str, default: str = "100/minute"):
    """
    Dynamic rate limit decorator that checks cache at request time
    
    Usage:
        @router.post("/bots")
        @dynamic_rate_limit(service="bot_creation", default="5/hour")
        async def create_bot():
            pass
    
    Args:
        service: Service key (e.g., "bot_operations")
        default: Fallback limit if config not found
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current config from cache
            config = await _config_cache.get(service)
            
            if config and config.enabled:
                limit = f"{config.limit}/{config.period}"
            else:
                limit = default
            
            # Apply rate limit dynamically
            # (Implementation depends on slowapi internals)
            # For now, we'll use a custom approach
            
            request = kwargs.get("request")
            if request:
                await _check_rate_limit(request, service, limit)
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator
```

### Phase 3: SQLAlchemy Models

```python
# core/models/rate_limiting.py

from sqlalchemy import Column, Integer, String, Boolean, Text, TIMESTAMP, JSON
from sqlalchemy.sql import func
from core.models.base import Base

class RateLimitConfig(Base):
    """Rate limit configuration stored in database"""
    __tablename__ = "rate_limit_configs"
    
    id = Column(Integer, primary_key=True)
    service_key = Column(String(100), unique=True, nullable=False, index=True)
    service_name = Column(String(200), nullable=False)
    limit_value = Column(Integer, nullable=False)
    period = Column(String(20), nullable=False)
    enabled = Column(Boolean, default=True)
    description = Column(Text)
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    created_by = Column(String(100))
    updated_by = Column(String(100))

class RateLimitAuditLog(Base):
    """Audit trail for all rate limit changes"""
    __tablename__ = "rate_limit_audit_log"
    
    id = Column(Integer, primary_key=True)
    service_key = Column(String(100), nullable=False, index=True)
    action = Column(String(50), nullable=False)  # create, update, delete, reset
    
    old_limit = Column(Integer)
    new_limit = Column(Integer)
    old_period = Column(String(20))
    new_period = Column(String(20))
    
    changed_by = Column(String(100), nullable=False)
    changed_by_username = Column(String(200))
    changed_by_ip = Column(String(50))
    
    change_reason = Column(Text)
    metadata = Column(JSON)
    
    created_at = Column(TIMESTAMP, server_default=func.now())

class RateLimitStats(Base):
    """Statistics about rate limit usage"""
    __tablename__ = "rate_limit_stats"
    
    id = Column(Integer, primary_key=True)
    service_key = Column(String(100), nullable=False, index=True)
    ip_address = Column(String(50), nullable=False, index=True)
    
    requests_made = Column(Integer, default=0)
    requests_blocked = Column(Integer, default=0)
    last_request_at = Column(TIMESTAMP)
    last_blocked_at = Column(TIMESTAMP)
    
    window_start = Column(TIMESTAMP, nullable=False)
    window_end = Column(TIMESTAMP, nullable=False)
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
```

---

## Migration Strategy

### Backward Compatibility

**Phase 2** is fully backward compatible:
- Old `@limiter.limit()` decorators still work
- New `@dynamic_rate_limit()` can be added gradually
- Both can coexist during migration

**Phase 3** requires data migration:
- Copy configs from Redis to PostgreSQL
- Run migration script
- Switch admin service to database
- Keep Redis for cache (performance)

### Rollback Plan

**Phase 2**:
- Remove dynamic decorator
- Revert to static decorators
- Clear cache

**Phase 3**:
- Revert to Redis-only storage
- Drop database tables
- Use Phase 1/2 implementation

---

## Testing Strategy

### Phase 2 Tests

1. **Cache TTL Test**: Verify 30-second expiration
2. **Hot Reload Test**: Update config, wait 30s, verify applied
3. **Multi-Instance Test**: Update on one instance, verify others pick up
4. **Performance Test**: Measure cache hit rate and latency
5. **Failover Test**: Redis down, verify defaults used

### Phase 3 Tests

1. **Migration Test**: Verify all configs moved to database
2. **Audit Trail Test**: Verify all changes logged
3. **History Test**: View audit log in admin UI
4. **Rollback Test**: Revert to previous config
5. **Performance Test**: Compare database vs Redis speed

---

## Success Metrics

### Phase 2 Success Criteria

- ✅ Config updates apply within 30 seconds
- ✅ No API restart required
- ✅ Cache hit rate > 95%
- ✅ Latency increase < 5ms
- ✅ Works across multiple instances

### Phase 3 Success Criteria

- ✅ All configs persisted in database
- ✅ Full audit trail captured
- ✅ Admin can view change history
- ✅ No data loss during migration
- ✅ Performance comparable to Phase 2

---

## Documentation Updates

### Files to Update

1. **ADMIN_RATE_LIMITS_GUIDE.md** - Add hot-reload instructions
2. **PHASE_1_COMPLETE.md** - Mark as superseded by Phase 2
3. **API_DOCUMENTATION_UPDATED.md** - Document new endpoints
4. **architecture.md** - Update rate limiting section

### New Files to Create

1. **PHASE_2_HOT_RELOAD_GUIDE.md** - Hot-reload admin guide
2. **PHASE_3_AUDIT_TRAIL_GUIDE.md** - Audit trail admin guide
3. **RATE_LIMIT_MIGRATION.md** - Migration instructions
4. **RATE_LIMIT_TROUBLESHOOTING.md** - Advanced troubleshooting

---

## Next Steps

1. **Review this plan** ✅
2. **Start Phase 2 implementation** - Create cache class
3. **Test Phase 2** - Verify hot-reload works
4. **Start Phase 3 implementation** - Create database models
5. **Test Phase 3** - Verify audit trail
6. **Deploy to production** - Full system

**Estimated total time**: 3-4 days  
**Current status**: Starting Phase 2 implementation now


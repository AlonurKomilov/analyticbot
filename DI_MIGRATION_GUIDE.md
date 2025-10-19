# DI System Migration Guide

**Version:** 1.0
**Date:** October 19, 2025
**Status:** Official Guide

---

## Overview

This guide explains how to migrate from the old DI system to the new unified `apps/di/` system.

## The Problem

We had **7 different DI containers**:
1. `apps/di/` - ✅ **NEW canonical system**
2. `apps/bot/di.py` - ❌ DEPRECATED
3. `apps/api/di.py` - ❌ DEPRECATED
4. `apps/shared/di.py` - ⚠️ To be merged/removed
5. `apps/jobs/di.py` - ⚠️ Specialized, keep for now
6. `apps/celery/di_celery.py` - ⚠️ Specialized, keep for now
7. `apps/mtproto/di/` - ⚠️ Specialized, keep for now

## The Solution

**Use `apps/di/` for ALL cross-cutting concerns.**

Specialized containers (jobs, celery, mtproto) can remain but should use `apps/di/` as their foundation.

---

## How to Use the New DI System

### 1. Basic Usage

```python
# ✅ CORRECT - New way
from apps.di import get_container

# Get the container
container = get_container()

# Access services through domain containers
bot_service = await container.bot.bot_client()
user_repo = await container.database.user_repo()
cache = await container.cache.redis_pool()

# Access core services
analytics = await container.core_services.analytics_fusion_service()
```

### 2. In FastAPI (API Layer)

```python
# apps/api/main.py
from apps.di import get_container

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    container = get_container()
    db_manager = await container.database.database_manager()
    await db_manager.initialize()

    yield

    # Shutdown
    await db_manager.cleanup()

app = FastAPI(lifespan=lifespan)
```

### 3. In Aiogram (Bot Layer)

```python
# apps/bot/bot.py
from apps.di import get_container

async def main():
    container = get_container()

    # Get bot and dependencies
    bot = await container.bot.bot_client()
    pool = await container.database.asyncpg_pool()

    # Setup dispatcher with middleware
    dp = Dispatcher(storage=storage)
    dp.update.outer_middleware(DependencyMiddleware(container))

    await dp.start_polling(bot)
```

### 4. In Celery Tasks

```python
# apps/celery/tasks/ml_tasks.py
from apps.di import get_container

@celery_app.task
async def train_model(channel_id: int):
    container = get_container()
    ml_service = await container.ml.ml_coordinator()

    result = await ml_service.train_model(channel_id)
    return result
```

### 5. Dependency Injection in Endpoints

```python
# apps/api/routers/channels_router.py
from fastapi import Depends
from apps.di import get_container

async def get_channel_repo():
    """Dependency injection for channel repository"""
    container = get_container()
    return await container.database.channel_repo()

@router.get("/channels/{channel_id}")
async def get_channel(
    channel_id: int,
    channel_repo = Depends(get_channel_repo)
):
    channel = await channel_repo.get_by_id(channel_id)
    return channel
```

---

## Container Structure

The new container follows **Domain-Driven Design** principles:

```
ApplicationContainer
├── config                    # Configuration
├── database                  # Database & repositories
│   ├── database_manager()
│   ├── asyncpg_pool()
│   ├── user_repo()
│   ├── channel_repo()
│   ├── analytics_repo()
│   └── admin_repo()
├── cache                     # Redis & caching
│   ├── redis_pool()
│   └── cache_factory()
├── core_services             # Business logic services
│   ├── analytics_fusion_service()
│   ├── analytics_batch_processor()
│   ├── schedule_service()
│   └── delivery_service()
├── ml                        # ML/AI services
│   ├── ml_coordinator()
│   ├── bot_ml_facade()
│   └── churn_intelligence()
├── bot                       # Bot-specific services
│   ├── bot_client()
│   ├── dispatcher()
│   ├── guard_service()
│   ├── subscription_service()
│   ├── schedule_manager()
│   └── content_protection()
└── api                       # API-specific services
    ├── analytics_coordinator()
    └── verify_token()
```

---

## Migration Examples

### Example 1: Migrating from apps/bot/di.py

**BEFORE (apps/bot/di.py - DEPRECATED):**
```python
from apps.bot.di import configure_bot_container

container = configure_bot_container()
bot = container.bot_client()
user_repo = container.user_repo()
```

**AFTER (apps/di/):**
```python
from apps.di import get_container

container = get_container()
bot = await container.bot.bot_client()
user_repo = await container.database.user_repo()
```

### Example 2: Migrating from apps/api/di.py

**BEFORE (apps/api/di.py - DEPRECATED):**
```python
from apps.api.di import get_container

container = get_container()
analytics = container.analytics_fusion_service()
```

**AFTER (apps/di/):**
```python
from apps.di import get_container

container = get_container()
analytics = await container.core_services.analytics_fusion_service()
```

### Example 3: Migrating from apps/shared/di.py

**BEFORE (apps/shared/di.py):**
```python
from apps.shared.di import get_container, Container

container = get_container()
pool = await container.asyncpg_pool()
user_repo = await container.user_repository()
```

**AFTER (apps/di/):**
```python
from apps.di import get_container

container = get_container()
pool = await container.database.asyncpg_pool()
user_repo = await container.database.user_repo()
```

---

## Key Differences

### 1. Namespace Organization

**OLD:** Flat structure - everything at container root
```python
container.bot_client()
container.user_repo()
container.analytics_service()
```

**NEW:** Domain-organized - grouped by concern
```python
container.bot.bot_client()
container.database.user_repo()
container.core_services.analytics_service()
```

### 2. Async/Await

**OLD:** Some providers were sync
```python
bot = container.bot_client()  # Sync
```

**NEW:** All providers are async
```python
bot = await container.bot.bot_client()  # Async
```

### 3. Configuration

**OLD:** Config passed during container creation
```python
container = configure_bot_container(config=my_config)
```

**NEW:** Config loaded automatically from settings
```python
container = get_container()  # Auto-loads from config/settings.py
```

---

## Testing with DI

### Unit Tests

```python
# tests/test_services.py
import pytest
from apps.di import get_container

@pytest.fixture
async def container():
    """Provide DI container for tests"""
    container = get_container()
    yield container
    # Cleanup if needed

async def test_user_service(container):
    user_repo = await container.database.user_repo()
    user = await user_repo.create_user(telegram_id=123)
    assert user.telegram_id == 123
```

### Mocking Dependencies

```python
# tests/test_with_mocks.py
from unittest.mock import AsyncMock
from apps.di import get_container

async def test_with_mock_repo():
    container = get_container()

    # Override a provider with a mock
    mock_repo = AsyncMock()
    mock_repo.get_by_id.return_value = {"id": 1, "name": "Test"}

    container.database.user_repo.override(mock_repo)

    # Test code that uses user_repo
    result = await some_service(container)

    assert mock_repo.get_by_id.called
    container.database.user_repo.reset_override()
```

---

## Troubleshooting

### Issue: "Cannot import get_container"

**Cause:** Old import path
**Solution:**
```python
# ❌ OLD
from apps.bot.di import get_container

# ✅ NEW
from apps.di import get_container
```

### Issue: "AttributeError: 'ApplicationContainer' has no attribute 'user_repo'"

**Cause:** Using old flat structure
**Solution:**
```python
# ❌ OLD
container.user_repo()

# ✅ NEW
container.database.user_repo()
```

### Issue: "RuntimeError: coroutine never awaited"

**Cause:** Forgot to await async provider
**Solution:**
```python
# ❌ OLD
bot = container.bot.bot_client()

# ✅ NEW
bot = await container.bot.bot_client()
```

### Issue: "Provider not found"

**Cause:** Service not registered in container
**Solution:** Add the provider to appropriate container in `apps/di/`

---

## Best Practices

### 1. ✅ DO: Use domain-specific containers

```python
# Group by domain
user_repo = await container.database.user_repo()
bot = await container.bot.bot_client()
ml = await container.ml.ml_coordinator()
```

### 2. ✅ DO: Inject dependencies, don't create them

```python
# Good - dependency injection
async def get_user_service(container):
    user_repo = await container.database.user_repo()
    return UserService(user_repo)

# Bad - direct instantiation
def get_user_service():
    from infra.db.repositories import AsyncpgUserRepository
    return UserService(AsyncpgUserRepository())  # ❌
```

### 3. ✅ DO: Use get_container() sparingly

```python
# In main entry points only
# - apps/api/main.py
# - apps/bot/bot.py
# - apps/celery/tasks/*.py

# Everywhere else: accept container as parameter
async def my_service(container):
    repo = await container.database.user_repo()
```

### 4. ❌ DON'T: Import from infra in apps

```python
# ❌ Bad
from infra.db.repositories import AsyncpgUserRepository
repo = AsyncpgUserRepository(pool)

# ✅ Good
from apps.di import get_container
container = get_container()
repo = await container.database.user_repo()
```

### 5. ❌ DON'T: Create multiple containers

```python
# ❌ Bad - creates new container each time
for i in range(10):
    container = get_container()  # 10 containers!

# ✅ Good - reuse same container
container = get_container()
for i in range(10):
    await use_container(container)
```

---

## FAQ

**Q: Why can't I use the old apps/bot/di.py anymore?**
A: It's deprecated to consolidate on one DI system. Use `apps/di/` instead.

**Q: What about apps/jobs/di.py and apps/celery/di_celery.py?**
A: These are specialized containers for those subsystems. They should eventually use `apps/di/` as a foundation but can remain separate.

**Q: Do I need to update my code immediately?**
A: Yes for new code. Old code will continue to work until removal date (Oct 21, 2025).

**Q: How do I add a new service to the container?**
A: Add it to the appropriate domain container in `apps/di/`:
- Database concerns → `database_container.py`
- Bot concerns → `bot_container.py`
- API concerns → `api_container.py`
- Business logic → `core_services_container.py`

**Q: Can I access infra layer from apps/?**
A: No. Only DI containers can import from infra. Apps code should get dependencies via injection.

---

## Getting Help

- Read: `APPS_ARCHITECTURE_TOP_10_ISSUES.md`
- Read: `APPS_REFACTORING_ACTION_PLAN.md`
- Check: `apps/di/README.md` (coming soon)
- Ask: Team lead or architecture channel

---

**Last Updated:** October 19, 2025
**Next Review:** November 19, 2025

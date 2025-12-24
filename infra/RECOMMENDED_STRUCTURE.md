# 🏗️ Recommended Infrastructure Folder Structure

**Goal:** Create a structure that prevents duplicates and is intuitive for both junior developers and AI assistants.

---

## 🎯 Key Principles for AI & Developer-Friendly Structure

### 1. **Single Responsibility Principle**
- Each folder has ONE clear purpose
- No overlapping concerns
- If a developer thinks "where does X go?", there should be ONE obvious answer

### 2. **Clear, Unambiguous Names**
- Avoid similar names like `cache/` and `redis/` → confuses AI
- Use specific names: `database/`, `caching/`, `messaging/`
- No abbreviations: `obs/` → `observability/`

### 3. **Consistent Depth & Pattern**
- Keep 2-3 levels max where possible
- Use same pattern everywhere: `category/feature/implementation.py`
- Example: `database/repositories/user_repository.py`

### 4. **README in Every Folder**
- Each folder has `README.md` explaining its purpose
- Include examples of what DOES and DOESN'T belong there
- AI assistants read these to understand context

### 5. **Explicit Exports**
- Strong `__init__.py` files that export canonical implementations
- Makes it clear which class/function is the "official" one
- Prevents AI from creating alternatives

---

## 📂 Proposed Clean Structure

```
infra/
│
├── README.md                          # 📘 Overview of entire infra layer
│
├── adapters/                          # 🔌 External service adapters
│   ├── README.md                      # "Adapters for external APIs and services"
│   ├── __init__.py                    # Export all adapters
│   ├── telegram/
│   │   ├── bot_api.py                 # Aiogram/python-telegram-bot adapter
│   │   ├── mtproto_client.py          # Pyrogram/Telethon adapter
│   │   └── analytics.py               # Telegram analytics adapter
│   ├── notifications/
│   │   ├── telegram_notifier.py
│   │   └── email_notifier.py
│   └── payments/
│       ├── stripe_adapter.py
│       └── payment_protocols.py
│
├── caching/                           # 💾 ALL caching logic here
│   ├── README.md                      # "Redis caching implementations"
│   ├── __init__.py                    # Export ONE CacheService
│   ├── redis_client.py                # Single Redis client
│   ├── cache_service.py               # Main cache service (USE THIS)
│   └── decorators.py                  # @cached, @cache_invalidate
│
├── database/                          # 🗄️ ALL database logic here
│   ├── README.md                      # "Database layer - models, repos, migrations"
│   ├── __init__.py                    # Export connection, repositories
│   ├── connection.py                  # DB pool, connection management
│   ├── models/                        # SQLAlchemy/ORM models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── channel.py
│   │   └── ...
│   ├── repositories/                  # Data access layer
│   │   ├── __init__.py
│   │   ├── user_repository.py
│   │   ├── channel_repository.py
│   │   └── marketplace_repository.py  # ONLY ONE
│   └── migrations/                    # Alembic migrations
│       └── versions/
│
├── observability/                     # 📊 ALL monitoring/logging here
│   ├── README.md                      # "Logging, metrics, tracing, health"
│   ├── __init__.py                    # Export logger, metrics
│   ├── logging/
│   │   ├── setup.py                   # Structlog configuration
│   │   └── formatters.py
│   ├── metrics/
│   │   ├── prometheus.py              # Prometheus metrics
│   │   └── collectors.py              # Custom collectors
│   ├── tracing/
│   │   └── opentelemetry.py           # OpenTelemetry setup
│   ├── health/
│   │   ├── checks.py                  # Health check implementations
│   │   └── endpoints.py               # Health check endpoints
│   └── dashboards/                    # Grafana/monitoring configs
│       └── grafana/
│
├── messaging/                         # 📨 Message queues & async tasks
│   ├── README.md                      # "Celery, RabbitMQ, Redis pub/sub"
│   ├── __init__.py
│   ├── celery_app.py                  # Celery configuration
│   ├── tasks/                         # Celery tasks
│   └── queues.py                      # Queue definitions
│
├── security/                          # 🔐 Authentication & authorization
│   ├── README.md                      # "JWT, rate limiting, encryption"
│   ├── __init__.py
│   ├── jwt_service.py                 # JWT token management
│   ├── rate_limiter.py                # Rate limiting (ONLY ONE)
│   └── encryption.py                  # Encryption utilities
│
├── storage/                           # 📁 File storage
│   ├── README.md                      # "S3, local storage, file uploads"
│   ├── __init__.py
│   ├── s3_client.py
│   └── local_storage.py
│
├── deployment/                        # 🚀 Deployment configurations
│   ├── README.md                      # "Choose ONE: k8s OR docker-compose"
│   ├── kubernetes/                    # Kubernetes manifests (if using K8s)
│   │   ├── base/
│   │   └── overlays/
│   ├── docker/                        # Docker compose files (if using Docker)
│   │   └── docker-compose.yml
│   ├── nginx/                         # Nginx configs
│   │   └── analyticbot.conf
│   ├── scripts/                       # Deployment scripts
│   │   ├── deploy.sh
│   │   └── rollback.sh
│   └── terraform/                     # Infrastructure as code
│       └── main.tf
│
├── services/                          # 🎯 Business infrastructure services
│   ├── README.md                      # "High-level business services"
│   ├── __init__.py
│   ├── payment/
│   │   ├── gateway.py
│   │   └── processor.py
│   └── analytics/
│       └── report_generator.py
│
└── testing/                           # 🧪 Test utilities & fixtures
    ├── README.md                      # "Test helpers, mocks, fixtures"
    ├── __init__.py
    ├── factories.py                   # Test data factories
    ├── mocks/                         # Mock implementations
    └── fixtures/                      # Pytest fixtures
```

---

## 📝 Folder Purpose Definitions

### Clear Boundaries

| Folder | Contains | Does NOT Contain |
|--------|----------|------------------|
| `adapters/` | Wrappers for external APIs | Business logic |
| `caching/` | Redis, cache decorators | Database logic |
| `database/` | Models, repositories, migrations | Cache, API calls |
| `observability/` | Logging, metrics, tracing, health | Alerts (use adapters) |
| `messaging/` | Celery tasks, queues | HTTP endpoints |
| `security/` | Auth, JWT, rate limiting | User business logic |
| `deployment/` | K8s/Docker, nginx, scripts | Application code |
| `services/` | High-level coordinating services | Low-level adapters |

---

## 🚫 What to Avoid (Anti-Patterns)

### ❌ BAD: Multiple similar folders
```
infra/
├── cache/           # Which one for caching?
├── redis/           # Is this different from cache?
└── storage/         # Or is caching here?
```

### ✅ GOOD: Single clear folder
```
infra/
└── caching/         # All caching logic here
    ├── redis_client.py
    └── cache_service.py
```

---

### ❌ BAD: Multiple implementations of same thing
```
caching/
├── redis_cache.py           # Which one to use?
├── redis_cache_service.py   # AI will create another!
├── redis_cache_adapter.py   # Confusing!
└── async_redis_client.py    # Too many choices
```

### ✅ GOOD: Single canonical implementation
```
caching/
├── __init__.py              # from .cache_service import CacheService
├── cache_service.py         # THE cache implementation
└── decorators.py            # Helper decorators
```

---

### ❌ BAD: Overlapping concerns
```
infra/
├── logging/         # 
├── monitoring/      # All related to observability
├── health/          # 
└── obs/             # Abbreviation unclear
```

### ✅ GOOD: Consolidated by domain
```
infra/
└── observability/
    ├── logging/
    ├── metrics/
    ├── tracing/
    └── health/
```

---

## 📘 README Template for Each Folder

Every folder should have a README like this:

```markdown
# {Folder Name}

## Purpose
Brief description of what this folder contains.

## What Goes Here
- ✅ Example 1
- ✅ Example 2
- ✅ Example 3

## What Does NOT Go Here
- ❌ Thing that belongs in another folder
- ❌ Another example

## Main Components
- `file1.py` - Description
- `file2.py` - Description

## Usage Example
\`\`\`python
from infra.{folder} import MainClass

service = MainClass()
\`\`\`

## Related Folders
- `../other_folder/` - For related functionality
```

---

## 🎯 Strong `__init__.py` Pattern

Each folder should export canonical implementations:

```python
# infra/caching/__init__.py
"""
Caching Infrastructure
======================

USE THIS:
    from infra.caching import CacheService
    
    cache = CacheService()
    await cache.set("key", "value")
"""

from .cache_service import CacheService
from .decorators import cached, cache_invalidate

# Export ONLY the official implementations
__all__ = [
    "CacheService",      # ← THE cache service to use
    "cached",            # ← Decorator for caching
    "cache_invalidate",  # ← Decorator for invalidation
]
```

This makes it impossible for AI to create duplicates because:
1. Import path is clear: `from infra.caching import CacheService`
2. Only one class exported
3. Documentation shows what to use

---

## 🤖 AI-Friendly Rules

### 1. **One File Per Class (mostly)**
```
✅ GOOD:
repositories/
├── user_repository.py       # UserRepository
├── channel_repository.py    # ChannelRepository
└── post_repository.py       # PostRepository

❌ BAD:
repositories/
└── repositories.py          # 10 repository classes in one file
```

### 2. **Descriptive File Names**
```
✅ GOOD: telegram_analytics_adapter.py
❌ BAD: tg_analytics_adapter.py (AI creates both!)
```

### 3. **No "Utils" or "Helpers" Dumps**
```
❌ BAD:
common/
└── utils.py  # 500 random functions

✅ GOOD:
common/
├── string_utils.py
├── date_utils.py
└── validation.py
```

### 4. **Explicit Patterns**
```python
# Repository pattern - always use this structure
class {Entity}Repository:
    async def get_by_id(self, id: int) -> {Entity}: ...
    async def get_all(self) -> list[{Entity}]: ...
    async def create(self, data: dict) -> {Entity}: ...
    async def update(self, id: int, data: dict) -> {Entity}: ...
    async def delete(self, id: int) -> bool: ...
```

---

## 🔄 Migration Strategy

### Phase 1: Create New Structure (Parallel)
1. Create new folder structure
2. Copy ONE canonical implementation to each
3. Add README.md to each folder
4. Add strong `__init__.py` exports

### Phase 2: Update Imports
1. Search all imports: `from infra.cache import`
2. Update to new structure: `from infra.caching import CacheService`
3. Use IDE refactoring tools

### Phase 3: Delete Old Files
1. Archive old structure to `infra_old/`
2. Verify tests pass
3. Delete after 1 week of stability

---

## ✅ Quality Checklist

Before committing any infra changes:

- [ ] Is there only ONE implementation of this concern?
- [ ] Is the folder name clear and unambiguous?
- [ ] Does the folder have a README.md?
- [ ] Does `__init__.py` export canonical implementations?
- [ ] Are file names descriptive (no abbreviations)?
- [ ] Is the concern clearly separated from others?
- [ ] Would a junior developer know where this goes?
- [ ] Would an AI assistant know where to create this?

---

## 💡 Examples for Common Tasks

### "Where do I add a new cache implementation?"
```
❌ DON'T create: infra/cache2/ or infra/redis_new/
✅ DO modify: infra/caching/cache_service.py
```

### "Where do I add health checks?"
```
❌ DON'T create: infra/health_checks/
✅ DO add to: infra/observability/health/checks.py
```

### "Where do I add a new payment provider?"
```
❌ DON'T create: infra/stripe/ or infra/payments/
✅ DO add to: infra/adapters/payments/stripe_adapter.py
```

### "Where do I add database queries?"
```
❌ DON'T create: infra/queries/ or infra/db_utils/
✅ DO add to: infra/database/repositories/{entity}_repository.py
```

---

## 🎓 Training Junior Developers

### Week 1: Structure Overview
- Walk through entire `infra/` structure
- Explain purpose of each top-level folder
- Show README files and examples

### Week 2: Adding Features
- Task: "Add a new repository for Posts"
- Expected path: `infra/database/repositories/post_repository.py`
- Review: Check if they created duplicate or used wrong folder

### Week 3: Code Review
- Focus on checking folder placement
- Question: "Is this in the right folder?"
- Teach: "Look at existing similar features"

---

*This structure prioritizes clarity over flexibility - it's better to be opinionated and consistent than flexible and confusing.*

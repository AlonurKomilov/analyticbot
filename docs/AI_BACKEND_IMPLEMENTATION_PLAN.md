# User AI Backend Implementation Plan
**Started:** December 21, 2025  
**Timeline:** 10-12 Days  
**Status:** Day 1 - Foundation Complete

---

## ✅ PHASE 1: FOUNDATION (COMPLETED - Day 1)

### Database Schema ✅
**Location:** `/infra/db/models/ai/user_ai_orm.py`

Created 5 tables:
1. ✅ `user_ai_config` - User AI configuration and tier
2. ✅ `user_ai_usage` - Daily usage tracking
3. ✅ `user_ai_hourly_usage` - Hourly rate limiting
4. ✅ `user_ai_services` - Active marketplace services
5. ✅ `ai_request_log` - Request logging for debugging/analytics

### Migration ✅
**Location:** `/infra/db/alembic/versions/0055_add_user_ai_tables.py`

- ✅ Created migration file
- ⏳ **NEXT:** Run migration: `make -f Makefile.dev dev-migrate`

### ORM Models ✅
**Location:** `/infra/db/models/ai/`

- ✅ `UserAIConfigORM` - Configuration model
- ✅ `UserAIUsageORM` - Usage tracking model
- ✅ `UserAIHourlyUsageORM` - Rate limiting model
- ✅ `UserAIServiceORM` - Service subscriptions model
- ✅ `AIRequestLogORM` - Request logging model
- ✅ `__init__.py` - Module exports

### AI Agent & Config ✅ (Already Exists)
**Location:** `/apps/ai/user/`

- ✅ `config.py` - AITier, AIFeature, UserAILimits, UserAISettings, UserAIConfig
- ✅ `agent.py` - UserAIAgent class with methods (need implementation)

### Frontend ✅ (Already Complete)
**Location:** `/apps/frontend/apps/user/src/features/ai/`

- ✅ All components working
- ✅ API client ready
- ✅ Routing configured
- ✅ Styling consistent

---

## 📋 PHASE 2: REPOSITORIES & PERSISTENCE (Days 2-3)

### Task 2.1: Create AI Config Repository
**File:** `/core/repositories/user_ai_config_repository.py`

```python
class UserAIConfigRepository:
    async def get_by_user_id(user_id: int) -> UserAIConfigORM | None
    async def create(user_id: int, tier: str, settings: dict) -> UserAIConfigORM
    async def update(user_id: int, settings: dict) -> UserAIConfigORM
    async def update_tier(user_id: int, tier: str) -> UserAIConfigORM
    async def get_or_create_default(user_id: int) -> UserAIConfigORM
```

**Estimate:** 4 hours

### Task 2.2: Create AI Usage Repository
**File:** `/core/repositories/user_ai_usage_repository.py`

```python
class UserAIUsageRepository:
    async def get_today(user_id: int) -> UserAIUsageORM | None
    async def increment_usage(user_id: int, tokens: int) -> UserAIUsageORM
    async def get_current_hour(user_id: int) -> UserAIHourlyUsageORM | None
    async def increment_hourly(user_id: int) -> UserAIHourlyUsageORM
    async def get_usage_history(user_id: int, days: int) -> list[UserAIUsageORM]
    async def can_make_request(user_id: int, limits: dict) -> tuple[bool, str]
```

**Estimate:** 4 hours

### Task 2.3: Create AI Services Repository
**File:** `/core/repositories/user_ai_services_repository.py`

```python
class UserAIServicesRepository:
    async def get_active_services(user_id: int) -> list[UserAIServiceORM]
    async def activate_service(user_id: int, service_key: str, expires_at: datetime) -> UserAIServiceORM
    async def deactivate_service(user_id: int, service_key: str) -> bool
    async def is_service_active(user_id: int, service_key: str) -> bool
    async def update_usage(user_id: int, service_key: str) -> UserAIServiceORM
```

**Estimate:** 3 hours

### Task 2.4: Create AI Request Log Repository
**File:** `/core/repositories/ai_request_log_repository.py`

```python
class AIRequestLogRepository:
    async def log_request(user_id: int, request_data: dict) -> AIRequestLogORM
    async def get_user_logs(user_id: int, limit: int) -> list[AIRequestLogORM]
    async def get_error_logs(hours: int) -> list[AIRequestLogORM]
    async def get_cost_stats(user_id: int, days: int) -> dict
```

**Estimate:** 2 hours

**Total Phase 2:** ~13 hours (1.5 days)

---

## 📋 PHASE 3: DI CONTAINER & SERVICE LAYER (Days 3-4)

### Task 3.1: Add Repositories to DI Container
**File:** `/apps/di/container.py`

```python
# Add to DatabaseContainer
async def user_ai_config_repo(self):
    pool = await self.asyncpg_pool()
    return UserAIConfigRepository(pool)

async def user_ai_usage_repo(self):
    pool = await self.asyncpg_pool()
    return UserAIUsageRepository(pool)

async def user_ai_services_repo(self):
    pool = await self.asyncpg_pool()
    return UserAIServicesRepository(pool)

async def ai_request_log_repo(self):
    pool = await self.asyncpg_pool()
    return AIRequestLogRepository(pool)
```

**Estimate:** 1 hour

### Task 3.2: Update UserAIConfig to Use Database
**File:** `/apps/ai/user/config.py`

```python
# Update from_database() method to actually query DB
@classmethod
async def from_database(cls, user_id: int, repo: UserAIConfigRepository):
    config_orm = await repo.get_or_create_default(user_id)
    # Convert ORM to dataclass
    return cls(
        user_id=config_orm.user_id,
        tier=AITier(config_orm.tier),
        limits=UserAILimits.from_tier(AITier(config_orm.tier)),
        settings=UserAISettings.from_dict(config_orm.settings or {}),
        # ... etc
    )

# Update save_to_database() to actually save
async def save_to_database(self, repo: UserAIConfigRepository):
    await repo.update(self.user_id, self.settings.to_dict())
```

**Estimate:** 2 hours

### Task 3.3: Update user_ai_router.py to Use Repositories
**File:** `/apps/api/routers/user_ai_router.py`

Major changes:
1. Add repository dependencies to endpoints
2. Replace `get_user_ai_agent()` helper to load from DB
3. Save settings changes to DB
4. Track usage in DB
5. Log all requests

**Estimate:** 4 hours

**Total Phase 3:** ~7 hours (1 day)

---

## 📋 PHASE 4: MULTI-PROVIDER AI SYSTEM (Days 5-8)

**UPDATED APPROACH:** Support multiple AI providers (OpenAI, Claude, Gemini, Grok) with user-provided API keys.

See detailed architecture: `/docs/AI_MULTI_PROVIDER_ARCHITECTURE.md`

### Task 4.1: Provider Abstraction Layer (Day 5)
**Files to Create:**
- `/core/services/ai/base_provider.py` - Abstract base class
- `/core/services/ai/provider_registry.py` - Dynamic provider registry
- `/core/services/ai/models.py` - AIMessage, AIResponse, AIProviderConfig
- `/core/security/encryption.py` - API key encryption (Fernet)

**Components:**
1. `BaseAIProvider` abstract class with methods:
   - `complete()` - Generate AI completion
   - `count_tokens()` - Count tokens
   - `calculate_cost()` - Calculate USD cost
   - `available_models` property

2. `AIProviderRegistry` for registering providers dynamically

3. Unified response format across all providers

**Estimate:** 6 hours

### Task 4.2: Core Provider Adapters (Day 6)
**Files to Create:**
- `/core/services/ai/providers/openai_provider.py`
- `/core/services/ai/providers/claude_provider.py`
- `/core/services/ai/providers/gemini_provider.py`
- `/core/services/ai/providers/grok_provider.py`

**Each Provider Implements:**
1. Authentication with provider API
2. Message formatting (convert to provider format)
3. Response parsing (convert to unified format)
4. Token counting (provider-specific)
5. Cost calculation based on pricing

**Pricing Tables:**
- OpenAI: gpt-4-turbo ($10/$30 per 1M tokens)
- Claude: claude-3-5-sonnet ($3/$15 per 1M tokens)
- Gemini: gemini-1.5-pro ($1.25/$5 per 1M tokens)
- Grok: TBD

**Estimate:** 8 hours

### Task 4.3: User Provider Management (Day 7)
**Database Migration:**
- Create `user_ai_providers` table
- Store encrypted API keys per user
- Support multiple providers per user
- Track spending per provider

**Repository:**
- `/core/repositories/user_ai_providers_repository.py`
- Methods: add_provider(), remove_provider(), get_active_provider(), decrypt_api_key()

**API Endpoints:**
- `GET /user/ai/providers/available` - List supported providers
- `GET /user/ai/providers/mine` - List user's configured providers
- `POST /user/ai/providers/add` - Add API key for provider
- `PUT /user/ai/providers/{name}/set-default` - Set default provider
- `DELETE /user/ai/providers/{name}` - Remove provider

**Security:**
- Encrypt API keys using Fernet symmetric encryption
- Validate API keys before saving (test API call)
- Never return full API keys in responses
- Support budget limits per provider

**Estimate:** 8 hours

### Task 4.4: Channel Analysis Integration (Day 8)
**File:** `/apps/ai/user/agent.py` - `analyze_channel()`

Steps:
1. Fetch channel data from database (posts, metrics, engagement)
2. Process with AI model (OpenAI/Claude)
3. Generate insights (top posts, engagement patterns, audience analysis)
4. Return structured recommendations

**Technologies:**
- OpenAI GPT-4o-mini for analysis
- Prompt engineering for consistent output
- Result caching (Redis) for performance

**Estimate:** 8 hours

### Task 4.2: Implement Content Suggestions
**File:** `/apps/ai/user/agent.py` - `suggest_content()`

Steps:
1. Analyze channel's top-performing content
2. Identify successful patterns (topics, tone, length)
3. Generate content ideas with AI
4. Format as actionable suggestions

**Estimate:** 6 hours

### Task 4.3: Implement Posting Recommendations
**File:** `/apps/ai/user/agent.py` - `get_posting_recommendations()`

Steps:
1. Analyze posting times and engagement correlation
2. Identify optimal posting windows
3. Suggest frequency based on audience activity
4. Recommend content mix (text, media, polls)

**Estimate:** 6 hours

### Task 4.4: Implement Custom Queries (Pro/Enterprise)
**File:** `/apps/ai/user/agent.py` - `custom_query()`

Steps:
1. Validate tier (Pro/Enterprise only)
2. Fetch relevant data based on query context
3. Use AI to answer natural language questions
4. Return formatted response with citations

**Estimate:** 8 hours

**Total Phase 4:** ~28 hours (3.5 days)

---

## 📋 PHASE 5: MARKETPLACE INTEGRATION (Days 8-9)

### Task 5.1: Update Marketplace Services
**Migration:** Add detailed AI service definitions to `marketplace_services` table

Services to add/update:
- `ai_content_scheduler` - AI-powered scheduling
- `ai_auto_reply` - Intelligent auto-replies
- `ai_competitor_analysis` - Competitor tracking
- `ai_trend_detection` - Trend alerts

**Estimate:** 2 hours

### Task 5.2: Service Activation Handlers
**File:** `/core/services/marketplace/ai_service_handler.py`

```python
class AIServiceActivationHandler:
    async def on_service_purchased(user_id: int, service_key: str)
    async def on_service_expired(user_id: int, service_key: str)
    async def check_service_quota(user_id: int, service_key: str) -> bool
```

**Estimate:** 4 hours

### Task 5.3: Update Frontend Marketplace Integration
**Files:** `/apps/frontend/apps/user/src/features/ai/components/`

- Link "Get More" buttons to marketplace
- Show real service prices
- Handle purchase flow
- Display active subscriptions

**Estimate:** 3 hours

**Total Phase 5:** ~9 hours (1 day)

---

## 📋 PHASE 6: RATE LIMITING & SECURITY (Day 10)

### Task 6.1: Add Rate Limiting Middleware
**File:** `/apps/api/middleware/ai_rate_limiter.py`

```python
class AIRateLimiterMiddleware:
    async def __call__(request: Request, call_next):
        user_id = get_current_user_id()
        can_proceed, message = await check_rate_limits(user_id)
        if not can_proceed:
            raise HTTPException(429, message)
        return await call_next(request)
```

**Estimate:** 3 hours

### Task 6.2: Tier-Based Access Control
**File:** `/apps/api/middleware/ai_tier_check.py`

```python
def require_tier(min_tier: AITier):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            user_tier = await get_user_tier(user_id)
            if user_tier < min_tier:
                raise HTTPException(403, "Upgrade required")
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

**Estimate:** 2 hours

### Task 6.3: Request Logging & Monitoring
**File:** `/apps/api/routers/user_ai_router.py`

Add to all endpoints:
- Request start time tracking
- Success/failure logging
- Token usage tracking
- Cost calculation
- Error reporting

**Estimate:** 3 hours

**Total Phase 6:** ~8 hours (1 day)

---

## 📋 PHASE 7: TESTING & VALIDATION (Days 11-12)

### Task 7.1: Unit Tests
**Files:** `/tests/api/test_user_ai_*.py`

Tests for:
- Repository CRUD operations
- Usage tracking logic
- Rate limiting
- Tier validation
- Service activation

**Estimate:** 6 hours

### Task 7.2: Integration Tests
**Files:** `/tests/integration/test_ai_flow.py`

Test complete flows:
- User creates account → Gets free tier
- User upgrades tier → Limits updated
- User makes AI request → Usage tracked
- User hits limit → Request blocked
- User purchases service → Service activated

**Estimate:** 4 hours

### Task 7.3: Frontend Integration Testing
**Manual Testing:**

1. Run migration
2. Start backend
3. Test all frontend flows:
   - View AI dashboard
   - Change settings (verify DB save)
   - Make AI request (verify response)
   - Check usage tracking
   - Purchase service (if marketplace ready)

**Estimate:** 4 hours

### Task 7.4: Performance Testing
**Load Testing:**

- 100 concurrent users making AI requests
- Response time < 2s for simple queries
- Response time < 5s for complex analysis
- Rate limiting works under load

**Estimate:** 2 hours

**Total Phase 7:** ~16 hours (2 days)

---

## 📊 TOTAL TIMELINE

| Phase | Tasks | Estimate | Days |
|-------|-------|----------|------|
| ✅ Phase 1 | Foundation | ✅ Done | 1 |
| Phase 2 | Repositories | 13 hours | 1.5 |
| Phase 3 | DI & Service | 7 hours | 1 |
| Phase 4 | AI Logic | 28 hours | 3.5 |
| Phase 5 | Marketplace | 9 hours | 1 |
| Phase 6 | Security | 8 hours | 1 |
| Phase 7 | Testing | 16 hours | 2 |
| **TOTAL** | | **81 hours** | **~11 days** |

---

## 🔧 REQUIRED BEFORE STARTING

### 1. Environment Setup
- [ ] OpenAI API key configured in `.env`
- [ ] Database connection working
- [ ] Redis cache available (optional but recommended)

### 2. Run Migration
```bash
make -f Makefile.dev dev-migrate
```

### 3. Verify Tables Created
```bash
psql -h localhost -p 10100 -U abc_app -d abc_analyticbot -c "\dt user_ai*"
psql -h localhost -p 10100 -U abc_app -d abc_analyticbot -c "\dt ai_*"
```

---

## 📝 DAILY PROGRESS TRACKING

### Day 1 (Dec 21) ✅
- ✅ Created ORM models
- ✅ Created migration
- ✅ Verified frontend ready
- ✅ Created implementation plan

### Day 2 (Dec 22) - Planned
- [ ] Run migration
- [ ] Create UserAIConfigRepository
- [ ] Create UserAIUsageRepository

### Day 3 (Dec 23) - Planned
- [ ] Create remaining repositories
- [ ] Update DI container
- [ ] Update UserAIConfig.from_database()

... (continue for 11 days)

---

## 🎯 SUCCESS CRITERIA

When complete, users should be able to:

1. ✅ **View AI Dashboard** - Shows real tier, usage, limits
2. ✅ **Change Settings** - Persisted to database
3. ✅ **Make AI Requests** - Returns real insights (not mock)
4. ✅ **Track Usage** - See daily/hourly request counts
5. ✅ **Hit Rate Limits** - Blocked when limit reached
6. ✅ **Purchase Services** - Activate from marketplace
7. ✅ **Upgrade Tier** - Change tier and see new limits

---

## 🚀 QUICK START (After Completing All Phases)

```python
# 1. User visits /workers/ai
# 2. Frontend loads AI dashboard
# 3. Backend:
#    - Loads config from user_ai_config table
#    - Checks usage from user_ai_usage table
#    - Returns real data
# 4. User clicks "Analyze Channel"
# 5. Backend:
#    - Checks rate limits (user_ai_hourly_usage)
#    - Fetches channel data
#    - Calls OpenAI API
#    - Generates insights
#    - Logs request (ai_request_log)
#    - Updates usage (user_ai_usage)
# 6. Frontend displays insights
```

---

**Last Updated:** December 21, 2025  
**Next Update:** December 22, 2025 (after Day 2 progress)

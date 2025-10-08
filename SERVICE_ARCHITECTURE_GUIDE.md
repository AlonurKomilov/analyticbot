# 🏗️ CORE SERVICES ARCHITECTURE GUIDE

**Date:** October 6, 2025
**Purpose:** Understanding how core/services connect to apps and serve users

---

## 📋 TABLE OF CONTENTS

1. [Service Architecture Overview](#service-architecture-overview)
2. [How Services Connect to Apps](#how-services-connect-to-apps)
3. [Real Connection Examples](#real-connection-examples)
4. [Service Independence Rules](#service-independence-rules)
5. [Coordination Patterns](#coordination-patterns)
6. [Predictive Modeling Service Audit](#predictive-modeling-service-audit)
7. [FAQ](#faq)

---

## 1. SERVICE ARCHITECTURE OVERVIEW

### 🎯 The Flow: User → Apps → Core Services → Infrastructure

```
┌──────────────────────────────────────────────────────────────────┐
│                        USER REQUEST                               │
│                  (REST API / Telegram / MTProto)                  │
└───────────────────────────────┬──────────────────────────────────┘
                                ↓
┌──────────────────────────────────────────────────────────────────┐
│                     APPS LAYER (Entry Points)                     │
│                                                                   │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐  │
│  │ apps/api/  │  │ apps/bot/  │  │apps/mtproto│  │apps/demo/│  │
│  │ FastAPI    │  │ Telegram   │  │ MTProto    │  │ Demo UI  │  │
│  │ REST API   │  │ Bot        │  │ Direct API │  │          │  │
│  └────────────┘  └────────────┘  └────────────┘  └──────────┘  │
│                                                                   │
│  Role: Protocol handling, authentication, routing                │
└───────────────────────────────┬──────────────────────────────────┘
                                ↓
┌──────────────────────────────────────────────────────────────────┐
│              DEPENDENCY INJECTION LAYER                           │
│                                                                   │
│  • apps/api/di_analytics.py                                      │
│  • apps/api/di_container/                                        │
│  • apps/api/deps.py                                              │
│                                                                   │
│  Role: Service instantiation and dependency management           │
└───────────────────────────────┬──────────────────────────────────┘
                                ↓
┌──────────────────────────────────────────────────────────────────┐
│                 CORE/SERVICES LAYER                               │
│                  (Business Logic - Framework Agnostic)            │
│                                                                   │
│  • analytics_fusion/        - Analytics & intelligence            │
│  • anomaly_analysis/        - 5 microservices (NEW ✨)           │
│  • nlg/                     - 5 microservices (NEW ✨)           │
│  • adaptive_learning/       - ML & versioning                     │
│  • deep_learning/           - DL models & predictions             │
│  • predictive_intelligence/ - Predictive analytics                │
│  • optimization_fusion/     - Performance optimization            │
│                                                                   │
│  Role: Domain logic, business rules, orchestration               │
└───────────────────────────────┬──────────────────────────────────┘
                                ↓
┌──────────────────────────────────────────────────────────────────┐
│                  INFRASTRUCTURE LAYER                             │
│                                                                   │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐  │
│  │ Database   │  │ Cache      │  │ Celery     │  │ External │  │
│  │ PostgreSQL │  │ Redis      │  │ Tasks      │  │ APIs     │  │
│  └────────────┘  └────────────┘  └────────────┘  └──────────┘  │
│                                                                   │
│  Role: Data persistence, caching, async tasks                    │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. HOW SERVICES CONNECT TO APPS

### ✅ THE RULE: Apps Import Services (Never Reverse)

```python
# ✅ CORRECT: Apps import from core
from core.services.analytics_fusion import AnalyticsOrchestratorService

# ❌ WRONG: Core services never import from apps
# core/services should NEVER have:
from apps.api import something  # FORBIDDEN!
```

### Connection Pattern

**1. Apps Layer (apps/api, apps/bot, apps/mtproto)**
- Handles user requests (HTTP, Telegram messages, MTProto)
- Validates input
- Authenticates users
- **Imports and calls core services**
- Formats responses

**2. Core Services Layer (core/services)**
- Pure business logic
- Framework-agnostic
- No knowledge of HTTP/Telegram/MTProto
- **Used by all apps**
- Returns data structures

**3. Infrastructure Layer**
- Database access
- Caching
- External API calls
- **Used by core services**

---

## 3. REAL CONNECTION EXAMPLES

### Example 1: API → Analytics Service

**File:** `apps/api/routers/statistics_core_router.py`

```python
# Step 1: Import core service
from core.services.analytics_fusion import AnalyticsOrchestratorService

# Step 2: Define endpoint with DI
@router.get("/channel/{channel_id}/statistics")
async def get_statistics(
    channel_id: int,
    # Step 3: Inject service via dependency
    analytics_service: AnalyticsOrchestratorService = Depends(get_analytics_service)
):
    # Step 4: Call core service
    result = await analytics_service.get_comprehensive_analytics(
        channel_id=channel_id,
        timeframe="30d"
    )

    # Step 5: Return data (FastAPI handles JSON serialization)
    return result
```

**Flow:**
1. User: `GET /api/channel/123/statistics`
2. FastAPI router receives request
3. DI container provides `AnalyticsOrchestratorService`
4. Service processes analytics logic
5. Service queries database via repositories
6. JSON response sent to user

---

### Example 2: Celery Task → Deep Learning Service

**File:** `apps/celery/tasks/ml_tasks.py`

```python
from core.services.deep_learning.growth import GrowthForecasterService

@celery_app.task(name="train_growth_model", bind=True)
def train_growth_model(self, channel_id: int, training_data: dict):
    """Background ML training task."""

    # Step 1: Instantiate core service
    forecaster = GrowthForecasterService(
        gpu_config=GPUConfigService(),
        model_loader=ModelLoader()
    )

    # Step 2: Execute long-running ML task
    model = forecaster.train_model(
        channel_id=channel_id,
        training_data=training_data
    )

    # Step 3: Return results
    return {
        "model_id": model.id,
        "metrics": model.metrics,
        "status": "completed"
    }
```

**Flow:**
1. API triggers: `train_growth_model.delay(123, data)`
2. Celery worker picks up task
3. Worker instantiates core service
4. Service trains ML model (CPU-intensive)
5. Task completes in background
6. API polls task status

---

### Example 3: Telegram Bot → Delivery Service

**File:** `apps/bot/services/scheduler_service.py`

```python
from core.services.enhanced_delivery_service import EnhancedDeliveryService

class BotSchedulerService:
    def __init__(self):
        # Inject core service
        self.delivery_service = EnhancedDeliveryService()

    async def handle_schedule_command(self, message: Message):
        """Handle /schedule command from Telegram."""

        # Parse bot command
        channel_id = message.chat.id
        content = message.text.replace("/schedule", "").strip()

        # Call core service
        result = await self.delivery_service.schedule_delivery(
            channel_id=channel_id,
            content=content,
            scheduled_time=datetime.now() + timedelta(hours=1)
        )

        # Send Telegram response
        await message.reply(f"✅ Scheduled! ID: {result['schedule_id']}")
```

**Flow:**
1. User sends: `/schedule Hello world`
2. Telegram bot receives message
3. Bot service calls core delivery service
4. Core service schedules content
5. Bot sends confirmation message

---

## 4. SERVICE INDEPENDENCE RULES

### ✅ Allowed Dependencies

```
✅ Apps → Core Services
   apps/api → core/services/analytics_fusion ✅
   apps/bot → core/services/nlg ✅
   apps/celery → core/services/deep_learning ✅

✅ Core Services → Infrastructure
   core/services → core/repositories ✅
   core/services → core/common/cache ✅
   core/services → infra/adapters ✅

✅ Core Services → Core Services
   analytics_fusion → anomaly_analysis ✅
   adaptive_learning → versioning ✅
   (via orchestrators and protocols)
```

### ❌ Forbidden Dependencies

```
❌ Core Services → Apps
   core/services → apps/api ❌ NEVER!
   core/services → apps/bot ❌ NEVER!

   Why? Breaks portability and testability
```

### Benefits of This Structure

1. **Reusability** ✅
   - Same analytics service for API, bot, mtproto
   - Write once, use everywhere

2. **Testability** ✅
   - Test services without HTTP server
   - Mock infrastructure easily
   - Unit test business logic in isolation

3. **Scalability** ✅
   - Scale API independently from bot
   - Scale ML services on GPU machines
   - Deploy services separately

4. **Maintainability** ✅
   - Change API without changing services
   - Swap Telegram for Discord
   - Business logic remains stable

5. **Portability** ✅
   - Add GraphQL without changing services
   - Add gRPC without changing services
   - Migrate frameworks easily

---

## 5. COORDINATION PATTERNS

### Pattern 1: Orchestrator Coordination

**Used when:** Multiple services need to work together

```python
class AnalyticsOrchestratorService:
    """Coordinates multiple analytics microservices."""

    def __init__(
        self,
        analytics_core: AnalyticsCoreService,
        intelligence: IntelligenceService,
        monitoring: LiveMonitoringService,
        reporting: ReportingService
    ):
        # Inject all required services
        self.analytics_core = analytics_core
        self.intelligence = intelligence
        self.monitoring = monitoring
        self.reporting = reporting

    async def get_comprehensive_analytics(self, channel_id: int):
        """Coordinate multiple services to build complete analytics."""

        # Call services in parallel
        core_task = self.analytics_core.calculate(channel_id)
        intelligence_task = self.intelligence.analyze(channel_id)
        monitoring_task = self.monitoring.get_live_data(channel_id)

        # Wait for all
        core_metrics, intelligence, monitoring = await asyncio.gather(
            core_task,
            intelligence_task,
            monitoring_task
        )

        # Combine results
        return {
            "metrics": core_metrics,
            "intelligence": intelligence,
            "monitoring": monitoring,
            "generated_at": datetime.utcnow()
        }
```

### Pattern 2: Protocol-Based Communication

**Used when:** Loose coupling needed between services

```python
# Define protocol (interface)
from core.protocols import AnalyticsProtocol

class ReportingService:
    def __init__(self, analytics: AnalyticsProtocol):
        # Accept any implementation of AnalyticsProtocol
        self.analytics = analytics

    async def generate_report(self, channel_id: int):
        # Use protocol methods (any implementation works)
        data = await self.analytics.get_analytics(channel_id)
        return self.format_report(data)
```

### Pattern 3: Event-Driven Communication

**Used when:** Asynchronous reactions needed

```python
from core.common.events import EventBus

# Service 1: Emits events
class DriftDetectionService:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

    async def detect_drift(self, model_id: str):
        if self.is_drift_detected():
            # Emit event
            await self.event_bus.emit("model.drift_detected", {
                "model_id": model_id,
                "severity": "high",
                "timestamp": datetime.utcnow()
            })

# Service 2: Listens to events
class AdaptiveLearningService:
    def __init__(self, event_bus: EventBus):
        # Subscribe to events
        event_bus.subscribe("model.drift_detected", self.handle_drift)

    async def handle_drift(self, event_data):
        # React automatically
        model_id = event_data["model_id"]
        await self.retrain_model(model_id)
```

---

## 6. PREDICTIVE MODELING SERVICE AUDIT

### 🔴 STATUS: CONFIRMED FAT SERVICE

**File:** `core/services/predictive_intelligence/modeling/predictive_modeling_service.py`
**Current Size:** **866 lines**
**Priority:** **#4** in refactoring roadmap

### Current Responsibilities (Too Many!)

```python
class PredictiveModelingService:
    """FAT SERVICE - Violates Single Responsibility Principle"""

    # 1. Enhanced prediction generation (~200 lines)
    async def generate_enhanced_predictions(...)

    # 2. Prediction confidence calculation (~180 lines)
    async def calculate_prediction_confidence(...)

    # 3. Natural language narratives (~150 lines)
    async def generate_prediction_narrative(...)

    # 4. Accuracy validation (~150 lines)
    async def validate_prediction_accuracy(...)

    # 5. Intelligent forecasting (~200 lines)
    async def generate_intelligent_forecast(...)
```

### ✅ RECOMMENDED REFACTORING

Split into **5 focused microservices:**

```
predictive_intelligence/modeling/
├── __init__.py                              (Exports)
├── models.py                                (~50 lines - Dataclasses)
│
├── prediction/
│   ├── __init__.py
│   └── prediction_generator.py             (~200 lines)
│       • generate_predictions()
│       • apply_confidence_filters()
│       • aggregate_predictions()
│
├── confidence/
│   ├── __init__.py
│   └── confidence_calculator.py            (~180 lines)
│       • calculate_confidence()
│       • assess_data_quality()
│       • adjust_for_uncertainty()
│
├── narrative/
│   ├── __init__.py
│   └── narrative_builder.py                (~150 lines)
│       • build_narrative()
│       • format_insights()
│       • integrate_with_nlg()
│
├── validation/
│   ├── __init__.py
│   └── accuracy_validator.py               (~150 lines)
│       • validate_accuracy()
│       • compare_to_historical()
│       • calculate_error_metrics()
│
└── orchestrator/
    ├── __init__.py
    └── modeling_orchestrator.py            (~200 lines)
        • coordinate_modeling()
        • integrate_results()
        • provide_backwards_compatibility()
```

### Benefits of Refactoring

| Before | After |
|--------|-------|
| 1 file, 866 lines | 5 services, ~200 lines each |
| Multiple responsibilities | Single responsibility each |
| Hard to test | Easy unit testing |
| Tight coupling | Loose coupling via DI |
| Difficult to extend | Easy to add features |

### Estimated Effort

- **Time:** 6-8 hours
- **Difficulty:** Medium
- **Risk:** Low (backwards compatibility maintained)
- **Priority:** **High** (next in roadmap)

---

## 7. FAQ

### Q: How do core services work?

**A:** Core services are **pure business logic** modules that:
- ✅ Implement domain functionality (analytics, ML, predictions)
- ✅ Use protocol-based interfaces
- ✅ Accept dependencies via constructor injection
- ✅ Are framework-agnostic (no FastAPI/Telegram code)
- ✅ Can be tested in isolation
- ✅ Can be reused across all apps

---

### Q: Do core services connect to apps (bot/mtproto/api)?

**A:** **NO** - It's the other way around!

```
✅ CORRECT:
apps/api     → imports → core/services
apps/bot     → imports → core/services
apps/mtproto → imports → core/services

❌ WRONG:
core/services → imports → apps/api  (NEVER!)
```

**All apps use the SAME core services, just different entry points!**

---

### Q: Do services need dependencies to work?

**A:** **Yes, but only infrastructure dependencies:**

**✅ Required Dependencies:**
- Database repositories (data access layer)
- Cache managers (Redis, in-memory)
- ML libraries (torch, scikit-learn, numpy)
- Logging infrastructure
- Configuration management

**❌ NOT Required:**
- FastAPI (no HTTP knowledge)
- Telegram SDK (no bot knowledge)
- MTProto library (no protocol knowledge)
- Any app-specific code

This separation enables:
- Same service used by API, Bot, and MTProto
- Easy unit testing (mock infrastructure)
- Independent deployment and scaling
- Framework portability

---

### Q: How do services provide functionality to users?

**A:** **Indirectly through apps:**

```
Step-by-Step Flow:

1. User makes request:
   • HTTP: POST /api/analytics/123
   • Telegram: /analyze 123
   • MTProto: analyticbot.getAnalytics(123)

2. Apps layer receives and validates:
   • apps/api validates HTTP request
   • apps/bot validates Telegram message
   • apps/mtproto validates MTProto call

3. Apps call core service:
   analytics_service.get_analytics(123)

4. Core service processes:
   • Queries database
   • Performs calculations
   • Applies business rules
   • Returns data object

5. Apps format response:
   • API: JSON with HTTP status
   • Bot: Telegram message with buttons
   • MTProto: Binary MTProto response

6. User receives formatted response
```

---

### Q: Can I add a new app without changing core services?

**A:** **YES! That's the whole point!**

Example: Adding a Discord bot

```python
# apps/discord/bot.py
from core.services.analytics_fusion import AnalyticsOrchestratorService

@bot.command()
async def analytics(ctx, channel_id: int):
    # Reuse existing service
    service = AnalyticsOrchestratorService(...)
    result = await service.get_comprehensive_analytics(channel_id)

    # Format for Discord
    embed = discord.Embed(title="Analytics")
    embed.add_field(name="Metrics", value=result["metrics"])
    await ctx.send(embed=embed)
```

**No changes to core services needed!** ✅

---

### Q: Should predictive_modeling_service.py be refactored?

**A:** **YES - Strongly recommended!**

**Reasons:**
1. 866 lines violates SRP (should be <400 lines)
2. Multiple responsibilities mixed together
3. Hard to test individual components
4. Difficult to extend or modify
5. Priority #4 in roadmap

**Next Steps:**
1. Follow same pattern as anomaly_analysis, nlg, versioning
2. Create 5 microservices with clear responsibilities
3. Maintain backwards compatibility
4. Verify 0 errors after refactoring

---

## 8. PRODUCTION DEPLOYMENT

### How Services Are Used in Production

```yaml
# docker-compose.yml
services:
  api:
    # FastAPI app
    command: uvicorn apps.api.main:app
    depends_on:
      - db
      - redis
    # Uses: All core services

  bot:
    # Telegram bot
    command: python apps/bot/main.py
    depends_on:
      - db
      - redis
    # Uses: Same core services as API

  celery_worker:
    # Background tasks
    command: celery -A apps.celery worker
    depends_on:
      - redis
      - db
    # Uses: Deep learning and ML services

  db:
    # PostgreSQL
    image: postgres:15

  redis:
    # Cache and Celery broker
    image: redis:7
```

**Key Points:**
- API, Bot, and Celery all use same core services
- Core services deployed with each app container
- Infrastructure (DB, Redis) shared across apps
- Services scale independently

---

## 9. SUMMARY

### ✅ Core Services Are:
- Pure business logic modules
- Framework-agnostic
- Reusable across all apps
- Testable in isolation
- Independent of app layer

### ✅ Apps Layer Is:
- Entry points (HTTP, Telegram, MTProto)
- Protocol handlers
- Service consumers
- Response formatters

### ✅ The Flow Is:
```
User → App → Core Service → Infrastructure → Data
     ←     ←              ←                ←
```

### ✅ Next Actions:
1. ✅ System is production ready
2. ⚠️  Refactor predictive_modeling_service.py (866 lines)
3. ⚠️  Continue fat services refactoring (35 remaining)
4. ✅ All connections working properly
5. ✅ Zero blocking issues

---

**End of Guide**

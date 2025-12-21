# AI System Architecture - System & User Separation

## Overview

The AI system follows the same pattern as `bot` and `mtproto`:
- **ai/system** - Infrastructure-level AI (admin only, env configured)
- **ai/user** - User-facing AI services (user configurable, marketplace ready)
- **ai/shared** - Common components used by both

## Current Implementation Status

✅ **Phase 1 Complete:** Foundation & Separation
- System AI Controller with env-based config
- User AI Agent with tier-based limits
- Analytics and Content AI services
- Marketplace adapter interface
- Shared models

✅ **Phase 2 Complete:** Monitoring & Analysis
- Tools framework (BaseTool, ToolRegistry, ToolDefinition)
- Monitoring tools (HealthCheck, MetricsCollector, LogAnalyzer)
- Scaling tools (ScaleWorker, AdjustInterval)
- Config tools (GetConfig, UpdateConfig)
- Memory store (file-based persistence with TTL)
- Metrics store (time-series with aggregation)
- Pattern detector (spikes, trends, anomalies)
- Alert manager (multi-channel with deduplication)

✅ **Phase 3 Complete:** User AI
- User AI Agent enhancements
- Analytics AI Service integration
- Content AI Service integration
- User AI API Router (/user/ai/*)
  - Settings management
  - Channel analysis
  - Content suggestions
  - Posting recommendations
  - Custom queries (Pro/Enterprise)
  - AI status and usage tracking

```
apps/ai/
├── __init__.py                 # Main exports (v2.0.0)
├── examples.py                 # Usage examples
│
├── shared/                     # Shared components
│   ├── __init__.py
│   └── models/                 # Data models
│       ├── __init__.py
│       ├── worker.py           # Worker definitions
│       ├── decision.py         # AI decisions
│       ├── action.py           # AI actions
│       └── metric.py           # Metrics
│
├── system/                     # System-level AI (admin/infrastructure)
│   ├── __init__.py             # System AI exports
│   ├── config.py               # Env-based SystemAIConfig
│   ├── controller.py           # SystemAIController
│   ├── registry/               # Worker registry
│   │   ├── __init__.py
│   │   └── worker_registry.py
│   ├── agent/                  # Legacy compatibility
│   ├── memory/                 # ✅ Phase 2: Memory & Persistence
│   │   ├── __init__.py
│   │   ├── store.py            # MemoryStore (file-based)
│   │   ├── metrics.py          # MetricsStore (time-series)
│   │   ├── patterns.py         # PatternDetector
│   │   └── alerting.py         # AlertManager
│   └── tools/                  # ✅ Phase 2: AI Tools
│       ├── __init__.py
│       ├── base.py             # BaseTool, ToolRegistry
│       ├── monitoring.py       # HealthCheck, Metrics, Logs
│       ├── scaling.py          # ScaleWorker, AdjustInterval
│       └── config.py           # GetConfig, UpdateConfig
│
└── user/                       # User-facing AI
    ├── __init__.py             # User AI exports
    ├── config.py               # UserAIConfig (tier-based)
    ├── agent.py                # UserAIAgent
    ├── services/               # AI services
    │   ├── __init__.py
    │   ├── analytics.py        # AnalyticsAIService
    │   └── content.py          # ContentAIService
    └── marketplace/            # Marketplace integration
        ├── __init__.py
        ├── adapter.py          # MarketplaceServiceAdapter
        └── registry.py         # MarketplaceServiceRegistry
```

## System AI (ai/system)

### Purpose
- Infrastructure management
- Worker auto-scaling
- Resource optimization
- System health monitoring
- Configured via environment variables
- Admin-only access

### Configuration (env-based)
```bash
# .env.development or .env.production
AI_SYSTEM_ENABLED=true
AI_SYSTEM_AUTO_SCALE=true
AI_SYSTEM_DRY_RUN=false
AI_SYSTEM_APPROVAL_LEVEL=review  # auto, review, approval
AI_SYSTEM_MAX_WORKERS=10
AI_SYSTEM_MEMORY_LIMIT_MB=4096
AI_SYSTEM_CPU_THRESHOLD=80
```

### Features
- Auto-discover workers (MTProto, Bot, API, Celery)
- Monitor health and performance
- Make scaling decisions
- Execute approved actions
- Learn from outcomes

## User AI (ai/user)

### Purpose
- Per-user AI assistant
- Service integration (analytics, content, etc.)
- Marketplace service AI enhancement
- User-configurable from frontend
- Extensible for any marketplace service

### User Configuration (database/frontend)
```python
# Each user has AI settings in database
class UserAISettings:
    user_id: int
    ai_enabled: bool = True
    
    # Analytics AI
    analytics_ai_enabled: bool = True
    analytics_suggestions: bool = True
    analytics_auto_reports: bool = False
    
    # Content AI
    content_ai_enabled: bool = False
    content_suggestions: bool = True
    content_auto_post: bool = False  # Premium feature
    
    # Marketplace Service AI
    marketplace_ai_services: list[str] = []  # ["content_scheduler", "seo_optimizer"]
    
    # AI Behavior
    ai_aggressiveness: str = "conservative"  # conservative, balanced, aggressive
    notification_preferences: dict = {}
```

### User AI Features

#### 1. Analytics AI
```python
# Automatic analysis of user's channel data
- Detect engagement patterns
- Suggest best posting times
- Identify trending topics
- Generate performance reports
- Predict future growth
```

#### 2. Content AI
```python
# Help users create/schedule content
- Generate post suggestions
- Optimize post timing
- A/B test variations
- Auto-schedule posts (if enabled)
- Content calendar AI
```

#### 3. Insights AI
```python
# Personalized recommendations
- "Your channel grew 15% this week"
- "Best performing posts have images"
- "Post 2 hours earlier for more views"
- Competitor analysis (if marketplace service)
```

#### 4. Marketplace AI Integration
```python
# Any marketplace service can be AI-enhanced
class MarketplaceAIAdapter:
    """Interface for AI-enhancing marketplace services"""
    
    async def analyze(self, service_data: dict) -> Analysis
    async def suggest(self, context: dict) -> list[Suggestion]
    async def automate(self, action: Action) -> Result
    async def learn(self, outcome: Outcome)
```

## Marketplace Service Integration

### How It Works

1. **Service Creator** defines AI capabilities:
```python
@marketplace_service(
    name="content_scheduler",
    ai_capabilities=["scheduling", "optimization", "prediction"]
)
class ContentSchedulerService:
    """Marketplace service with AI features"""
    
    async def get_ai_suggestions(self, user_id: int) -> list[Suggestion]:
        # AI analyzes user's content patterns
        # Returns optimal posting schedule
        pass
    
    async def ai_auto_schedule(self, user_id: int, enabled: bool):
        # AI automatically schedules posts
        pass
```

2. **User** enables AI for the service:
```
Frontend: Services → Content Scheduler → AI Settings
- [ ] Enable AI suggestions
- [ ] Enable auto-scheduling
- [ ] Notification when AI posts
```

3. **AI** works with the service:
```python
# AI User Agent coordinates everything
user_ai = UserAIAgent(user_id=123)

# Get suggestions from marketplace service
suggestions = await user_ai.get_service_suggestions(
    service="content_scheduler"
)

# Execute with user's approval (or auto if enabled)
if user.settings.content_auto_post:
    await user_ai.execute_service_action(
        service="content_scheduler",
        action="schedule_post",
        params=suggestions[0]
    )
```

## API Endpoints

### System AI (Admin only)
```
GET  /api/admin/ai/system/status
GET  /api/admin/ai/system/workers
POST /api/admin/ai/system/decisions/approve
GET  /api/admin/ai/system/metrics
POST /api/admin/ai/system/config
```

### User AI (Per user)
```
GET  /api/user/ai/settings              # Get AI settings
PUT  /api/user/ai/settings              # Update AI settings
GET  /api/user/ai/suggestions           # Get AI suggestions
POST /api/user/ai/suggestions/{id}/apply # Apply suggestion
GET  /api/user/ai/insights              # Get AI insights
GET  /api/user/ai/services              # List AI-enabled services
POST /api/user/ai/services/{name}/enable # Enable AI for service
```

## Frontend Integration

### Admin Panel (System AI)
```
/admin/ai/
├── dashboard      # System AI overview
├── workers        # Worker management
├── decisions      # Decision approval
└── config         # System AI configuration
```

### User Dashboard (User AI)
```
/services/ai/
├── overview       # AI features overview
├── analytics      # Analytics AI settings
├── content        # Content AI settings
├── insights       # AI insights dashboard
└── marketplace    # Marketplace AI services
```

## Benefits

### For System (ai/system)
- ✅ 24/7 infrastructure management
- ✅ Auto-scaling without human intervention
- ✅ Cost optimization
- ✅ Predictive maintenance
- ✅ Configured once via env, runs automatically

### For Users (ai/user)
- ✅ Personalized AI assistant per user
- ✅ Smart analytics and insights
- ✅ Content suggestions and automation
- ✅ Marketplace service AI enhancement
- ✅ User controls everything from frontend

### For Marketplace (ai/user/marketplace)
- ✅ Any service can be AI-enabled
- ✅ Standard adapter interface
- ✅ Easy to create AI-powered services
- ✅ Users choose which services have AI
- ✅ Flexible automation levels

## Implementation Priority

### Phase 1: Foundation ✅ (Complete - Dec 2025)
- [x] Basic AI structure
- [x] Worker registry
- [x] Decision framework
- [x] Models and types
- [x] System/User separation
- [x] Shared components

### Phase 2: Monitoring & Analysis ✅ (Complete - Dec 2025)
- [x] Tools framework (BaseTool, ToolRegistry)
- [x] Monitoring tools (HealthCheck, MetricsCollector, LogAnalyzer)
- [x] Scaling tools (ScaleWorker, AdjustInterval)
- [x] Config tools (GetConfig, UpdateConfig)
- [x] Memory store with persistence
- [x] Metrics store (time-series)
- [x] Pattern detection system
- [x] Alert manager integration

### Phase 3: User AI ✅ (Complete - Dec 2025)
- [x] User AI Agent enhancements
- [x] Analytics AI service integration
- [x] Content AI service integration
- [x] User AI API endpoints (/user/ai/*)
- [x] Settings management
- [x] Analysis and suggestions
- [x] Custom queries (Pro/Enterprise)

### Phase 4: Marketplace Integration (Next)
- [ ] Marketplace adapter interface
- [ ] Service AI registration
- [ ] User AI settings for services
- [ ] Content AI service

### Phase 5: Full Features
- [ ] LLM integration
- [ ] Auto-posting service
- [ ] Advanced analytics
- [ ] Predictive features

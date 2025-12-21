"""
AI System - Quick Start Guide
==============================

This guide shows how to use the AI system for both infrastructure management
and user-facing AI features.

## Architecture Overview

The AI system has two layers:

1. **System AI** (`apps.ai.system`) - Infrastructure management
   - Worker auto-scaling
   - Health monitoring
   - Configured via environment variables
   - Admin-only access

2. **User AI** (`apps.ai.user`) - User-facing features
   - Analytics insights
   - Content suggestions
   - Marketplace service integration
   - Configured per-user via database

## System AI Examples

### 1. Initialize System AI Controller

```python
from apps.ai.system import SystemAIController, get_system_ai_config

# Load config from environment
config = get_system_ai_config()

# Create controller
controller = SystemAIController(config)

# Start monitoring
await controller.start()

# Controller will now:
# - Discover all registered workers
# - Monitor their health and performance
# - Make decisions when issues detected
# - Execute approved actions based on approval_mode
```

### 2. Register Custom Worker

```python
from apps.ai.shared.models import WorkerDefinition, WorkerType, WorkerConfig
from apps.ai.system.registry import WorkerRegistry

registry = WorkerRegistry()

# Define your worker
custom_worker = WorkerDefinition(
    name="my_custom_worker",
    worker_type=WorkerType.CUSTOM,
    module_path="apps.my_module.worker",
    description="My custom worker description",
    config=WorkerConfig(
        interval_minutes=15,
        max_runtime_hours=12.0,
        auto_scaling_enabled=True,
        min_instances=1,
        max_instances=3,
    ),
    ai_manageable=True,
    health_endpoint="http://localhost:9092/health",
)

# Register it
await registry.register_worker(custom_worker)
```

### 3. Make System Decision

```python
from apps.ai.shared.models import DecisionType

# Make a decision
decision = await controller.make_decision(
    decision_type=DecisionType.SCALE,
    target_worker="mtproto_worker",
    action="scale_up",
    params={"instances": 2},
    reasoning="High CPU usage detected (>85%)",
    risk_level="low",
)

# If approved automatically, execute it
if decision and decision.approved:
    result = await controller.execute_decision(decision)
    print(f"Result: {result.message}")
```

## User AI Examples

### 4. Create User AI Agent

```python
from apps.ai.user import UserAIAgent, UserAIConfig

# Load user config from database
user_id = 12345
config = await UserAIConfig.from_database(user_id)

# Create agent for user
agent = UserAIAgent(config)

# Check user's status
status = await agent.get_status()
print(f"Tier: {status['tier']}")
print(f"Usage: {status['usage']['requests_today']}/{status['usage']['limits']['daily']}")
```

### 5. Get Analytics Insights

```python
# Analyze a channel
result = await agent.analyze_channel(
    channel_id=67890,
    analysis_type="overview",
    period_days=30,
)

if result['success']:
    print(f"Insights: {result['insights']}")
```

### 6. Get Content Suggestions

```python
# Get content ideas
result = await agent.suggest_content(
    channel_id=67890,
    topic="cryptocurrency",
    count=3,
)

if result['success']:
    for suggestion in result['suggestions']:
        print(f"- {suggestion['title']}")
```

### 7. Use Marketplace Service

```python
from apps.ai.user.marketplace import MarketplaceServiceRegistry

# Get available services
registry = MarketplaceServiceRegistry()
services = registry.search(tier="basic")

# Execute a service
result = await agent.execute_marketplace_service(
    service_id="demo_service_v1",
    parameters={"message": "Hello!"},
)
```

## Configuration

### Environment Variables (System AI)

```bash
# Enable/disable
AI_ENABLED=true
AI_DRY_RUN_MODE=false

# Approval mode: auto, review, approval, disabled
AI_APPROVAL_MODE=review

# Monitoring
AI_MONITORING_INTERVAL_SECONDS=60
AI_AUTO_SCALE_ENABLED=true

# Safety
AI_SAFETY_CHECKS_ENABLED=true
AI_MAX_CONCURRENT_ACTIONS=3

# LLM (Phase 2)
AI_LLM_PROVIDER=openai
AI_LLM_MODEL=gpt-4o-mini
```

### User Tiers (User AI)

| Tier | Requests/Day | Features | Marketplace |
|------|-------------|----------|-------------|
| Free | 10 | Basic analytics | ❌ |
| Basic | 50 | Standard features | ✅ |
| Pro | 200 | Custom queries | ✅ |
| Enterprise | 1000 | Unlimited | ✅ |

## Check AI Controller Status

```python
status = await controller.get_status()
print(f"AI Controller Status: {status}")

# Output:
# {
#     "enabled": True,
#     "is_running": True,
#     "dry_run_mode": False,
#     "stats": {
#         "total_decisions": 42,
#         "successful_actions": 38,
#         "failed_actions": 1,
#         ...
#     },
#     "registry_stats": {
#         "total_workers": 4,
#         "ai_manageable_workers": 4,
#         ...
#     }
# }
```

### 5. List All Workers

```python
# Get all workers
all_workers = await registry.list_workers()

# Filter AI-manageable workers only
ai_workers = await registry.list_workers(ai_manageable_only=True)

# Get specific worker type
mtproto_workers = await registry.list_workers(worker_type=WorkerType.MTPROTO)
```

## Integration with Existing Workers

### MTProto Worker Integration

The MTProto worker is automatically discovered and registered with:
- Health endpoint: http://localhost:9091/health
- Metrics endpoint: http://localhost:9091/metrics
- Auto-scaling: Enabled (1-3 instances)
- AI-manageable: Yes

```python
# AI can monitor and adjust MTProto worker:
# - Adjust collection interval based on load
# - Scale up during high traffic
# - Restart on errors
# - Optimize resource usage
```

### Bot Worker Integration

The Bot worker is automatically registered with:
- Single instance (no auto-scaling)
- Auto-restart on failure: Enabled
- Requires approval for: stop_worker, modify_token

### API Worker Integration

The API worker supports:
- Auto-scaling: 2-8 instances
- Scale based on CPU thresholds (70% up, 30% down)
- AI-manageable: Yes

## Next Steps (Phase 2+)

### Phase 2: Monitoring & Analysis
- Implement monitoring tools
- Add pattern detection
- Build historical analysis
- Create alerting system

### Phase 3: AI Agent Integration
- Integrate LLM for decision making
- Implement reasoning engine
- Add learning feedback loop

### Phase 4: Autonomous Actions
- Implement auto-scaling
- Add self-configuration
- Build auto-healing
- Predictive optimization

## API Integration (Coming Soon)

```python
# REST API endpoints will be available:

GET  /api/ai-workers/status          # Get AI controller status
GET  /api/ai-workers/workers         # List all workers
POST /api/ai-workers/workers/register # Register new worker
GET  /api/ai-workers/decisions       # Get decision history
POST /api/ai-workers/decisions/approve # Approve pending decision
GET  /api/ai-workers/metrics         # Get AI performance metrics
```

## Admin Dashboard (Coming Soon)

The admin panel will include:
- AI Controller dashboard
- Worker registry view
- Decision approval interface
- Real-time monitoring
- Learning statistics

## Safety Features

### Approval Levels
- **AUTO**: Safe actions executed immediately (e.g., restart worker)
- **REVIEW**: Human review recommended (e.g., scale resources)
- **APPROVAL**: Human approval required (e.g., config changes)
- **FORBIDDEN**: AI cannot perform (e.g., delete data)

### Dry Run Mode
```python
controller = AIWorkerController(dry_run_mode=True)
# All actions will be simulated without actual execution
```

### Rollback
```python
# Every action includes rollback information
action.rollback_available  # True/False
action.rollback_instructions  # How to undo

# Automatic rollback if issues detected after execution
```

## Monitoring

The AI controller continuously monitors:
- Worker health status
- CPU and memory usage
- Error rates
- Performance metrics
- System patterns

## Learning (Future)

The AI will learn from:
- Decision outcomes
- Performance patterns
- Error patterns
- Optimization results
- Historical data

And use this to:
- Make better decisions
- Predict issues
- Optimize automatically
- Prevent problems

## Testing

```python
# Run in dry-run mode for testing
controller = AIWorkerController(
    enabled=True,
    dry_run_mode=True,  # No real changes
    safety_checks_enabled=True,
)

await controller.start()

# Make test decisions
decision = await controller.make_decision(
    decision_type=DecisionType.CONFIGURE,
    target_worker="mtproto_worker",
    action="adjust_interval",
    params={"interval_minutes": 15},
)

# Nothing will actually change, but you'll see logs
```

## Troubleshooting

### AI Controller Not Starting
```python
# Check if enabled
status = await controller.get_status()

# Check logs
tail -f logs/ai_worker.log
```

### Worker Not Discovered
```python
# Manually register
await registry.register_worker(worker_definition)

# Verify registration
workers = await registry.list_workers()
print([w.name for w in workers])
```

### Decision Not Auto-Approved
```python
# Check approval level
decision.approval_level  # AUTO, REVIEW, APPROVAL, FORBIDDEN

# Manually approve if needed
decision.approved = True
decision.approved_by = "admin"
decision.approved_at = datetime.utcnow()

# Then execute
await controller.execute_decision(decision)
```

## Support

For questions or issues:
1. Check the architecture document: AI_WORKER_ARCHITECTURE.md
2. Review the code: apps/ai/
3. Contact the development team

---

**Status**: Phase 1 Foundation Complete
**Next**: Phase 2 - Monitoring & Analysis

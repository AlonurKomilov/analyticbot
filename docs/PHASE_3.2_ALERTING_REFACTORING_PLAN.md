# Phase 3.2: AlertingService Refactoring Plan

## Current State Analysis

**File**: `apps/bot/services/alerting_service.py`
**Size**: 328 lines
**Methods**: 15 methods
**Status**: Monolithic service in wrong layer

### Identified Responsibilities

1. **Alert Condition Checking** (Business Logic)
   - `check_alert_conditions()` - Check metrics against conditions
   - `_evaluate_alert_condition()` - Evaluate specific condition
   - `_extract_metric_value()` - Extract metric from data
   - `_get_default_alert_conditions()` - Get alert rules

2. **Alert Event Management** (Business Logic)
   - `_create_alert_event()` - Create alert event
   - `get_active_alerts_for_channel()` - Fetch active alerts
   - `acknowledge_alert()` - Mark alert as acknowledged
   - `get_alert_history()` - Retrieve alert history

3. **Alert Rule Management** (Business Logic)
   - `create_alert_rule()` - Create new alert rule
   - `get_channel_alert_rules()` - Get rules for channel
   - `update_alert_rule()` - Update existing rule
   - `delete_alert_rule()` - Delete rule

4. **Alert Statistics** (Business Logic)
   - `get_alert_statistics()` - Calculate alert metrics

5. **Alert Notification** (External Integration)
   - `send_alert_notification()` - Send notifications (Telegram, email, etc.)

---

## Refactoring Strategy (Clean Architecture)

### 1. Core Services (Framework-Agnostic)

#### **AlertConditionEvaluator**
- **Purpose**: Evaluate metrics against alert rules
- **Responsibilities**:
  - Check alert conditions
  - Evaluate thresholds
  - Generate alert events
- **Location**: `core/services/bot/alerts/alert_condition_evaluator.py`

#### **AlertRuleManager**
- **Purpose**: Manage alert rules (CRUD)
- **Responsibilities**:
  - Create/update/delete rules
  - Fetch rules for channels
  - Validate rule configuration
- **Location**: `core/services/bot/alerts/alert_rule_manager.py`

#### **AlertEventManager**
- **Purpose**: Manage alert events and history
- **Responsibilities**:
  - Create alert events
  - Get active alerts
  - Acknowledge alerts
  - Alert history tracking
  - Calculate statistics
- **Location**: `core/services/bot/alerts/alert_event_manager.py`

### 2. Protocols (Interfaces)

#### **AlertRepository**
```python
class AlertRepository(Protocol):
    async def create_alert_event(self, event: AlertEvent) -> str: ...
    async def get_active_alerts(self, channel_id: str) -> list[AlertEvent]: ...
    async def acknowledge_alert(self, alert_id: str, user_id: str) -> bool: ...
    async def get_alert_history(self, channel_id: str, limit: int) -> list[AlertEvent]: ...
    async def create_rule(self, rule: AlertRule) -> str: ...
    async def get_rules(self, channel_id: str) -> list[AlertRule]: ...
    async def update_rule(self, rule_id: str, updates: dict) -> bool: ...
    async def delete_rule(self, rule_id: str) -> bool: ...
```

#### **AlertNotificationPort**
```python
class AlertNotificationPort(Protocol):
    async def send_alert(self, notification: AlertNotification) -> bool: ...
```

### 3. Adapters (Framework Integration)

#### **TelegramAlertNotifier**
- **Purpose**: Send alert notifications via Telegram
- **Location**: `apps/bot/adapters/alert_adapters.py`
- **Implements**: `AlertNotificationPort`

### 4. Domain Models

Models already exist in `apps/shared/models/alerts.py`:
- ✅ `AlertEvent`
- ✅ `AlertRule`
- ✅ `AlertNotification`

---

## Implementation Plan

### Step 1: Create Protocols ✅
```
core/services/bot/alerts/
├── __init__.py
├── protocols.py          # AlertRepository, AlertNotificationPort
├── models.py             # Domain models (if needed)
```

### Step 2: Implement Core Services ✅
```
core/services/bot/alerts/
├── alert_condition_evaluator.py  # Evaluate metrics
├── alert_rule_manager.py         # CRUD for rules
├── alert_event_manager.py        # Event management
```

### Step 3: Create Adapters ✅
```
apps/bot/adapters/
└── alert_adapters.py     # TelegramAlertNotifier
```

### Step 4: Update DI Container ✅
```python
# In apps/di/bot_container.py
alert_condition_evaluator = providers.Factory(...)
alert_rule_manager = providers.Factory(...)
alert_event_manager = providers.Factory(...)
telegram_alert_notifier = providers.Factory(...)
```

### Step 5: Migrate Handlers ✅
- Update alert handlers to use new services
- Update middleware to inject new services

### Step 6: Archive Legacy Service ✅
- Move to `archive/phase3_alerting_legacy_20251014/`
- Create ARCHIVE_README.md

---

## Benefits

### Before (Monolithic)
```
apps/bot/services/alerting_service.py
└── AlertingService (328 lines, 15 methods)
    ├── Alert condition checking
    ├── Alert event management
    ├── Alert rule management
    ├── Alert statistics
    └── Notification sending
```

### After (Clean Architecture)
```
core/services/bot/alerts/
├── protocols.py (interfaces)
├── alert_condition_evaluator.py (evaluation logic)
├── alert_rule_manager.py (rule CRUD)
└── alert_event_manager.py (event management)

apps/bot/adapters/
└── alert_adapters.py (Telegram integration)
```

---

## Success Criteria

- [ ] 3 core services created (~100-120 lines each)
- [ ] 2 protocols defined (AlertRepository, AlertNotificationPort)
- [ ] 1 adapter created (TelegramAlertNotifier)
- [ ] DI container updated with new providers
- [ ] Handlers migrated to use new services
- [ ] Legacy service archived
- [ ] All tests passing

---

## Estimated Effort

- **Lines to Refactor**: 328 lines
- **Expected Output**: ~500 lines (protocols + services + adapters)
- **Services**: 3 core services + 1 adapter
- **Time**: Similar to Phase 3.1 (proven architecture pattern)

---

**Status**: 📋 Ready to implement
**Next**: Create protocols and begin implementation

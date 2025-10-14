# Legacy Scheduler Service Archive

**Archive Date**: October 14, 2025
**Reason**: Replaced with Clean Architecture implementation
**Phase**: 3.1 - Scheduler Service Refactoring

## What Was Archived

- `scheduler_service.py` (289 lines) - Legacy monolithic scheduler service

## Why It Was Archived

The legacy `SchedulerService` was a God Service with multiple responsibilities:
1. Scheduling posts
2. Sending messages to channels
3. Building inline keyboards
4. Managing post status
5. Recording analytics
6. Error handling
7. Delivery tracking

This violated the Single Responsibility Principle and was tightly coupled to the Telegram framework.

## What Replaced It

### New Clean Architecture (Phase 3.1)

The legacy service was refactored into **5 focused components**:

#### Core Services (Framework-Agnostic)
1. **ScheduleManager** (`core/services/bot/scheduling/schedule_manager.py`)
   - Create and validate scheduled posts
   - Fetch pending posts
   - Business logic only

2. **PostDeliveryService** (`core/services/bot/scheduling/post_delivery_service.py`)
   - Orchestrate message delivery
   - Handle text and media messages
   - Record analytics

3. **DeliveryStatusTracker** (`core/services/bot/scheduling/delivery_status_tracker.py`)
   - Manage post lifecycle
   - Track delivery status
   - Provide statistics

#### Telegram Adapters (Framework Integration)
4. **AiogramMessageSender** (`apps/bot/adapters/scheduling_adapters.py`)
   - Implements MessageSenderPort
   - Sends messages via Telegram
   - Supports 5 media types

5. **AiogramMarkupBuilder** (`apps/bot/adapters/scheduling_adapters.py`)
   - Implements MarkupBuilderPort
   - Builds inline keyboards
   - Framework-specific implementation

### Benefits of New Architecture

✅ **Separation of Concerns** - Each service has one responsibility
✅ **Testability** - Core services are framework-agnostic, easy to test
✅ **Maintainability** - Clear boundaries, focused components
✅ **Flexibility** - Can swap Telegram for another platform
✅ **Type Safety** - Protocol-based interfaces
✅ **Clean Code** - 5 services @ ~200 lines each vs 1 @ 289 lines

## Migration Guide

### Old Code (DEPRECATED)
```python
from apps.bot.services.scheduler_service import SchedulerService

scheduler_service: SchedulerService

# Schedule a post
post_id = await scheduler_service.schedule_post(
    user_id=user_id,
    channel_id=channel_id,
    post_text=text,
    schedule_time=schedule_time
)

# Send a post
result = await scheduler_service.send_post_to_channel(post_data)
```

### New Code (RECOMMENDED)
```python
from core.services.bot.scheduling import (
    ScheduleManager,
    PostDeliveryService,
    DeliveryStatusTracker,
)

# Services injected via DI
schedule_manager: ScheduleManager
post_delivery_service: PostDeliveryService
delivery_status_tracker: DeliveryStatusTracker

# Schedule a post
post_id = await schedule_manager.create_scheduled_post(
    user_id=user_id,
    channel_id=channel_id,
    post_text=text,
    schedule_time=schedule_time
)

# Get pending posts and deliver them
pending_posts = await schedule_manager.get_pending_posts(limit=50)
for post in pending_posts:
    result = await post_delivery_service.deliver_post(post)
    await delivery_status_tracker.update_from_delivery_result(result)
```

## Where It Was Used

The legacy service was used in:
1. ✅ `apps/bot/handlers/admin_handlers.py` - **MIGRATED** to ScheduleManager
2. ✅ `apps/bot/tasks.py` - **MIGRATED** to new services
3. ✅ `apps/bot/middlewares/dependency_middleware.py` - **MIGRATED** to inject new services
4. ✅ `apps/bot/services/__init__.py` - Export removed

All usages have been successfully migrated to the new architecture.

## DI Container Updates

### Old DI (REMOVED)
```python
scheduler_service = providers.Factory(
    _create_scheduler_service,
    schedule_repository=database.schedule_repo,
    bot=bot_client,
)
```

### New DI (ACTIVE)
```python
# Core services
schedule_manager = providers.Factory(
    _create_schedule_manager,
    schedule_repository=database.schedule_repo,
    analytics_repository=database.analytics_repo,
)

post_delivery_service = providers.Factory(
    _create_post_delivery_service,
    message_sender=aiogram_message_sender,
    markup_builder=aiogram_markup_builder,
    schedule_repository=database.schedule_repo,
    analytics_repository=database.analytics_repo,
)

delivery_status_tracker = providers.Factory(
    _create_delivery_status_tracker,
    schedule_repository=database.schedule_repo,
    analytics_repository=database.analytics_repo,
)

# Adapters
aiogram_message_sender = providers.Factory(
    _create_aiogram_message_sender,
    bot=bot_client,
)

aiogram_markup_builder = providers.Factory(
    _create_aiogram_markup_builder,
)
```

## Testing

The new architecture has been validated with:
- ✅ DI container wiring test (`scripts/test_scheduling_di_wiring.py`)
- ✅ All service providers instantiate correctly
- ✅ Protocols and adapters import successfully
- ✅ Handler migration successful
- ✅ Background task migration successful

## Recovery Instructions

If you need to temporarily restore the legacy service:

1. Copy the archived file back:
   ```bash
   cp archive/phase3_scheduler_legacy_20251014/scheduler_service.py \
      apps/bot/services/scheduler_service.py
   ```

2. Re-enable the export in `apps/bot/services/__init__.py`:
   ```python
   from .scheduler_service import SchedulerService
   __all__ = [..., "SchedulerService"]
   ```

3. Revert handler changes to use `scheduler_service` parameter

**Note**: This is not recommended. The new architecture is superior in every way.

## Documentation

For more details on the new architecture, see:
- `docs/PHASE_3.1_COMPLETE.md` - Complete refactoring summary
- `docs/SCHEDULER_REFACTORING_STATUS.md` - Status tracking
- `core/services/bot/scheduling/protocols.py` - Protocol definitions
- `scripts/test_scheduling_di_wiring.py` - Validation script

## Statistics

- **Lines Removed**: 289 (legacy service)
- **Lines Added**: 1,729 (new architecture)
- **Services Created**: 5 (3 core + 2 adapters)
- **Protocols Defined**: 4 interfaces (16 methods)
- **Models Created**: 3 domain models
- **Code Quality**: Improved (testable, maintainable, flexible)

---

**Status**: ✅ Successfully archived and replaced
**Can Be Deleted After**: December 14, 2025 (60-day grace period)

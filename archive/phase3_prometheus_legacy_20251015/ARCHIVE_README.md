# Legacy PrometheusService Archive

**Archive Date:** October 15, 2025
**Phase:** 3.4 - Prometheus Metrics Clean Architecture Migration
**Deprecation Period:** 60 days (until December 14, 2025)

---

## Why This Was Archived

The legacy `prometheus_service.py` (338 lines) was a monolithic service that violated Clean Architecture principles:

### Issues with Legacy Service:
1. **Global Singleton Pattern** - `prometheus_service = PrometheusService()` at module level
2. **Tight Coupling** - Direct dependency on `prometheus_client` library
3. **Mixed Concerns** - Combined metrics collection, exposition, and middleware
4. **Hard to Test** - Required Prometheus library and couldn't use mock backends
5. **No Abstraction** - Couldn't switch to StatsD, CloudWatch, or other backends

---

## What Replaced It

### New Clean Architecture Structure:

**Core Layer** (`core/services/bot/metrics/`):
- ✅ `models.py` - Domain models (HTTPRequestMetric, TelegramAPIMetric, etc.)
- ✅ `protocols.py` - Port definitions (MetricsBackendPort, SystemMetricsPort)
- ✅ `metrics_collector_service.py` - Core metrics orchestration
- ✅ `business_metrics_service.py` - Business-specific metrics
- ✅ `health_check_service.py` - Health monitoring
- ✅ `system_metrics_service.py` - System resource metrics
- ✅ `decorators.py` - @metrics_timer decorator

**Adapter Layer** (`apps/bot/adapters/metrics/`):
- ✅ `prometheus_adapter.py` - Prometheus implementation
- ✅ `system_metrics_adapter.py` - PSUtil implementation
- ✅ `stub_metrics_adapter.py` - Testing stubs

**DI Integration** (`apps/di/`):
- ✅ 9 factory functions
- ✅ 6 service providers
- ✅ 4 DI getter functions

---

## API Migration Guide

### Old API (Deprecated)

```python
# ❌ OLD: Global singleton import
from apps.bot.services.prometheus_service import prometheus_service

# Record HTTP request
prometheus_service.record_http_request(
    method="GET",
    endpoint="/api/channels",
    status_code=200,
    duration=0.123,
)

# Record Telegram update
prometheus_service.record_telegram_update("add_channel")

# Use decorator
from apps.bot.services.prometheus_service import prometheus_timer

@prometheus_timer("celery_task")
async def my_task():
    ...

# Collect system metrics
from apps.bot.services.prometheus_service import collect_system_metrics
await collect_system_metrics()
```

### New API (Recommended)

```python
# ✅ NEW: DI-based access
from apps.di import get_metrics_collector_service, get_system_metrics_service
from core.services.bot.metrics.models import HTTPRequestMetric, TelegramUpdateMetric

# Record HTTP request
metrics_collector = get_metrics_collector_service()
if metrics_collector:
    metric = HTTPRequestMetric(
        method="GET",
        endpoint="/api/channels",
        status_code=200,
        duration=0.123,
    )
    await metrics_collector.record_http_request(metric)

# Record Telegram update
if metrics_collector:
    metric = TelegramUpdateMetric(
        update_type="add_channel",
        status="success",
    )
    await metrics_collector.record_telegram_update(metric)

# Use new decorator
from core.services.bot.metrics.decorators import metrics_timer

@metrics_timer(metric_type="celery_task", metric_name="my_task")
async def my_task():
    ...

# Collect system metrics
system_metrics_service = get_system_metrics_service()
if system_metrics_service:
    await system_metrics_service.collect_and_update_system_metrics()
```

---

## Migration Status

### Files Migrated:
- ✅ `apps/bot/handlers/admin_handlers.py` (2 usages)
- ✅ `apps/bot/services/analytics_service.py` (2 usages)
- ✅ `apps/bot/tasks.py` (2 usages)
- ✅ `apps/celery/tasks/bot_tasks.py` (2 usages)

### Total Changes:
- **Core Services:** 6 new files, 962 lines
- **Adapters:** 3 new files, 458 lines
- **DI Updates:** 2 files updated
- **Usage Migrations:** 4 files updated
- **Legacy Archived:** 1 file, 338 lines

---

## Benefits of New Architecture

### 1. Backend Flexibility ✅
Can easily switch between:
- Prometheus (current)
- StatsD
- CloudWatch
- DataDog
- Custom backends

### 2. Testability ✅
```python
# Easy to test without Prometheus
from apps.bot.adapters.metrics import StubMetricsAdapter
from core.services.bot.metrics import MetricsCollectorService

stub = StubMetricsAdapter()
collector = MetricsCollectorService(metrics_backend=stub)
# Test without any Prometheus dependency
```

### 3. Multiple Backends ✅
Can send metrics to multiple systems simultaneously:
```python
class MultiMetricsBackend:
    def __init__(self, backends: list[MetricsBackendPort]):
        self.backends = backends

    def record_counter(self, name, value, labels):
        for backend in self.backends:
            backend.record_counter(name, value, labels)

# Send to both Prometheus and CloudWatch
multi = MultiMetricsBackend([prometheus_adapter, cloudwatch_adapter])
```

### 4. Type Safety ✅
- Strong typing for all metric data
- Protocol interfaces enforce contracts
- No direct Prometheus types in core

### 5. Clean Architecture ✅
- Core business logic isolated from frameworks
- Easy to add new metric types
- Clear separation of concerns

---

## Deprecation Timeline

- **October 15, 2025** - Archived (this file)
- **November 15, 2025** - Warning period (30 days)
- **December 14, 2025** - Permanent removal

**Action Required:** Update any remaining code to use the new DI-based API.

---

## Rollback Procedure (Emergency Only)

If the new system causes critical issues:

1. **Restore File:**
   ```bash
   cp archive/phase3_prometheus_legacy_20251015/prometheus_service.py \
      apps/bot/services/
   ```

2. **Revert Imports:**
   ```python
   # In affected files
   from apps.bot.services.prometheus_service import prometheus_service
   ```

3. **Report Issue:** Document the problem for investigation

**Note:** Rollback should be temporary only. The new architecture is superior in every way.

---

## Questions?

Contact: Architecture Team
Documentation: `docs/PHASE_3.4_COMPLETE_SUMMARY.md`
Migration Guide: This file

---

**Phase 3.4 Complete** ✅
**Progress:** 80% (4/5 phases done)
**Next:** Phase 3.5 - Final cleanup and review

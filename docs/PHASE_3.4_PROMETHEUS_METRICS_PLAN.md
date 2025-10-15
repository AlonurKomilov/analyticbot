# Phase 3.4: Prometheus Metrics Service - Migration Plan

**Date:** October 15, 2025
**Status:** 🚀 In Progress
**Target:** Migrate PrometheusService to Clean Architecture

---

## Current State Analysis

### File: `apps/bot/services/prometheus_service.py` (338 lines)

**Responsibilities Identified:**
1. ✅ **Metrics Collection** - Counters, Gauges, Histograms (business logic)
2. ✅ **HTTP Request Tracking** - Method, endpoint, status, duration (business logic)
3. ✅ **Telegram API Monitoring** - API calls, updates processed (business logic)
4. ✅ **Database Metrics** - Query tracking, connection pooling (business logic)
5. ✅ **Celery Task Monitoring** - Task execution, workers (business logic)
6. ✅ **Business Metrics** - Channels, users, scheduled posts (business logic)
7. ✅ **System Metrics** - Memory, CPU usage (business logic)
8. ✅ **Health Checks** - Service health status (business logic)
9. ❌ **Prometheus Client** - Direct dependency on `prometheus_client` library (infrastructure)
10. ❌ **PSUtil Integration** - Direct dependency on `psutil` library (infrastructure)

**Dependencies:**
- `prometheus_client` - Metrics library (Counter, Gauge, Histogram)
- `psutil` - System metrics collection (optional)
- Direct instantiation: `prometheus_service = PrometheusService()` (module-level)

**Current Usage:**
- `admin_handlers.py` - Imports `prometheus_service`
- `analytics_service.py` - Imports `prometheus_service`, `prometheus_timer`
- `tasks.py` - Imports `prometheus_timer`, `collect_system_metrics`
- `bot_tasks.py` - Imports `prometheus_timer`, `collect_system_metrics`

---

## Phase 3.4 Architecture Design

### Directory Structure
```
core/services/bot/metrics/
├── __init__.py
├── models.py                    # Domain models
├── protocols.py                 # Port definitions
├── metrics_collector_service.py # Core metrics collection logic
├── business_metrics_service.py  # Business-specific metrics
└── health_check_service.py      # Health monitoring

apps/bot/adapters/metrics/
├── __init__.py
├── prometheus_adapter.py        # Prometheus implementation
├── system_metrics_adapter.py    # PSUtil implementation
└── stub_metrics_adapter.py      # Stub for testing

apps/di/
└── bot_container.py             # Add metrics service providers
```

### Core Layer Design

#### 1. Domain Models (`core/services/bot/metrics/models.py`)
```python
@dataclass
class MetricType(str, Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"

@dataclass
class HTTPRequestMetric:
    """HTTP request metric data"""
    method: str
    endpoint: str
    status_code: int
    duration: float
    timestamp: float = field(default_factory=time.time)

@dataclass
class TelegramAPIMetric:
    """Telegram API call metric"""
    method: str
    status: str
    duration: float
    timestamp: float = field(default_factory=time.time)

@dataclass
class DatabaseQueryMetric:
    """Database query metric"""
    operation: str
    status: str
    duration: float
    timestamp: float = field(default_factory=time.time)

@dataclass
class BusinessMetrics:
    """Business metrics snapshot"""
    channels_count: int
    users_count: int
    scheduled_posts_count: int
    timestamp: float = field(default_factory=time.time)

@dataclass
class SystemMetrics:
    """System resource metrics"""
    memory_percent: float
    cpu_percent: float
    disk_percent: float = 0.0
    timestamp: float = field(default_factory=time.time)

@dataclass
class HealthCheckResult:
    """Health check result"""
    check_name: str
    is_healthy: bool
    message: str = ""
    timestamp: float = field(default_factory=time.time)
```

#### 2. Protocols (`core/services/bot/metrics/protocols.py`)
```python
class MetricsBackendPort(Protocol):
    """Port for metrics backend (Prometheus, StatsD, CloudWatch, etc.)"""

    def record_counter(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record counter metric"""
        ...

    def set_gauge(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Set gauge metric"""
        ...

    def record_histogram(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record histogram metric"""
        ...

    def get_metrics_output(self) -> str:
        """Get formatted metrics output"""
        ...

    def get_content_type(self) -> str:
        """Get metrics content type"""
        ...


class SystemMetricsPort(Protocol):
    """Port for system metrics collection"""

    async def get_memory_usage(self) -> float:
        """Get memory usage percentage"""
        ...

    async def get_cpu_usage(self) -> float:
        """Get CPU usage percentage"""
        ...

    async def get_disk_usage(self) -> float:
        """Get disk usage percentage"""
        ...

    async def is_available(self) -> bool:
        """Check if system metrics are available"""
        ...


class DatabaseMetricsPort(Protocol):
    """Port for database metrics"""

    async def get_active_connections(self) -> int:
        """Get active database connections"""
        ...

    async def get_pool_size(self) -> int:
        """Get connection pool size"""
        ...
```

#### 3. Core Services

**MetricsCollectorService** (`metrics_collector_service.py`):
- Pure orchestration of metrics recording
- Uses MetricsBackendPort for actual recording
- No direct dependency on Prometheus

**BusinessMetricsService** (`business_metrics_service.py`):
- Collects business-specific metrics
- Channels, users, posts tracking
- Uses repository ports for data access

**HealthCheckService** (`health_check_service.py`):
- Service health monitoring
- Aggregates health from multiple sources
- Returns structured health check results

### Adapter Layer Design

#### PrometheusAdapter (`apps/bot/adapters/metrics/prometheus_adapter.py`)
```python
class PrometheusMetricsAdapter:
    """Prometheus implementation of MetricsBackendPort"""

    def __init__(self, registry: CollectorRegistry | None = None):
        self.registry = registry or CollectorRegistry()
        self._counters: dict[str, Counter] = {}
        self._gauges: dict[str, Gauge] = {}
        self._histograms: dict[str, Histogram] = {}

    def record_counter(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        if name not in self._counters:
            label_names = list(labels.keys()) if labels else []
            self._counters[name] = Counter(
                name,
                f"Counter: {name}",
                label_names,
                registry=self.registry,
            )

        if labels:
            self._counters[name].labels(**labels).inc(value)
        else:
            self._counters[name].inc(value)
```

#### SystemMetricsAdapter (`apps/bot/adapters/metrics/system_metrics_adapter.py`)
```python
class PSUtilSystemMetricsAdapter:
    """PSUtil implementation of SystemMetricsPort"""

    async def get_memory_usage(self) -> float:
        try:
            import psutil
            return psutil.virtual_memory().percent
        except ImportError:
            return 0.0

    async def get_cpu_usage(self) -> float:
        try:
            import psutil
            return psutil.cpu_percent(interval=1)
        except ImportError:
            return 0.0
```

### DI Integration

```python
# In apps/di/bot_container.py

def _create_prometheus_metrics_adapter(**kwargs):
    from apps.bot.adapters.metrics import PrometheusMetricsAdapter
    return PrometheusMetricsAdapter()

def _create_system_metrics_adapter(**kwargs):
    from apps.bot.adapters.metrics import PSUtilSystemMetricsAdapter
    return PSUtilSystemMetricsAdapter()

def _create_metrics_collector_service(
    metrics_backend=None,
    **kwargs
):
    from core.services.bot.metrics import MetricsCollectorService
    if not metrics_backend:
        logger.warning("Cannot create metrics collector: missing backend")
        return None
    return MetricsCollectorService(metrics_backend=metrics_backend)

# Providers
prometheus_metrics_adapter = providers.Factory(_create_prometheus_metrics_adapter)
system_metrics_adapter = providers.Factory(_create_system_metrics_adapter)

metrics_collector_service = providers.Factory(
    _create_metrics_collector_service,
    metrics_backend=prometheus_metrics_adapter,
)
```

---

## Migration Steps

### Step 1: Create Core Domain Models ✅
- Extract metric data classes
- Create HTTPRequestMetric, TelegramAPIMetric, etc.
- Framework-agnostic (no Prometheus types)

### Step 2: Define Protocols ✅
- MetricsBackendPort for Prometheus/StatsD/CloudWatch abstraction
- SystemMetricsPort for PSUtil abstraction
- DatabaseMetricsPort for database metrics

### Step 3: Implement Core Services ✅
- MetricsCollectorService: Main orchestrator
- BusinessMetricsService: Business metrics collection
- HealthCheckService: Health monitoring

### Step 4: Create Adapters ✅
- PrometheusMetricsAdapter: Wraps prometheus_client
- PSUtilSystemMetricsAdapter: Wraps psutil
- StubMetricsAdapter: For testing

### Step 5: Update DI Container ✅
- Add metrics adapter providers
- Add metrics service providers
- Wire dependencies

### Step 6: Migrate Usages ✅
- Update admin_handlers.py
- Update analytics_service.py
- Update tasks.py
- Update bot_tasks.py

### Step 7: Create prometheus_timer Replacement ✅
- Create MetricsDecorator in core layer
- Protocol-based timing
- Support async and sync functions

### Step 8: Archive Legacy ✅
- Move prometheus_service.py to archive
- Create ARCHIVE_README.md
- 60-day deprecation notice

### Step 9: Test & Verify ✅
- Run error checker
- Verify DI wiring
- Test metrics collection
- Ensure 0 logical errors

### Step 10: Document ✅
- Create PHASE_3.4_COMPLETE_SUMMARY.md
- Commit all changes
- Update progress tracker

---

## Benefits of This Architecture

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
class MockMetricsBackend:
    def record_counter(self, name, value, labels):
        self.recorded.append((name, value, labels))

collector = MetricsCollectorService(
    metrics_backend=MockMetricsBackend()
)
```

### 3. Multiple Backends ✅
Can send metrics to multiple backends simultaneously:
```python
class MultiMetricsBackend:
    def __init__(self, backends: list[MetricsBackendPort]):
        self.backends = backends

    def record_counter(self, name, value, labels):
        for backend in self.backends:
            backend.record_counter(name, value, labels)
```

### 4. Type Safety ✅
- Strong typing for all metric data
- Protocol interfaces enforce contracts
- No direct Prometheus types in core

### 5. Observability ✅
- Structured metric models
- Easy to add logging
- Clear metric lifecycle

---

## API Migration Example

### Old API (Deprecated)
```python
from apps.bot.services.prometheus_service import prometheus_service

# Record HTTP request
prometheus_service.record_http_request(
    method="GET",
    endpoint="/api/channels",
    status_code=200,
    duration=0.123,
)

# Use decorator
@prometheus_timer("telegram_api")
async def send_message(...):
    ...
```

### New API (Recommended)
```python
from apps.di import get_container
from core.services.bot.metrics.models import HTTPRequestMetric

# DI-based access
container = get_container()
metrics_collector = container.bot.metrics_collector_service()

# Record HTTP request
metric = HTTPRequestMetric(
    method="GET",
    endpoint="/api/channels",
    status_code=200,
    duration=0.123,
)
await metrics_collector.record_http_request(metric)

# Use decorator
from core.services.bot.metrics.decorators import metrics_timer

@metrics_timer(metric_type="telegram_api")
async def send_message(...):
    ...
```

---

## Timeline

- **Day 1 (Today):** Core models, protocols, services
- **Day 2 (Tomorrow):** Adapters, DI, migration, testing

---

## Success Metrics

- ✅ 0 logical errors in all core services
- ✅ 0 type: ignore comments
- ✅ All usages migrated to DI
- ✅ Legacy service archived
- ✅ Full documentation
- ✅ Phase 3 at 80% completion (4/5 sub-phases done)

---

**Status:** Ready to implement
**Next:** Create core/services/bot/metrics/ directory structure

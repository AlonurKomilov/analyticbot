# 🚀 AnalyticBot System Upgrade Plan
**Created:** November 21, 2025
**Status:** Ready for Implementation
**Estimated Timeline:** 8-12 weeks

---

## 📊 Current System Analysis

### ✅ **Strengths Identified**
- **Excellent Architecture**: Clean apps/core/infra separation
- **Production Infrastructure**: Docker, K8s, monitoring configured
- **Rate Limiting**: SlowAPI already implemented
- **CI/CD**: 19 GitHub Actions workflows
- **Monitoring**: Prometheus + Grafana configured
- **Database**: 38 Alembic migrations managed
- **Frontend**: React 18 + TypeScript + Zustand
- **Security**: JWT auth, encryption, RBAC

### ⚠️ **Critical Gaps Found**
1. **Test Coverage**: Only ~53 test files, many with import issues
2. **API Docs**: OpenAPI configured but needs enhancement
3. **Drill-down UI**: Backend ready, frontend partially implemented
4. **Performance**: Claims exist but need validation
5. **Monitoring**: Configured but dashboards need creation

---

## 🎯 Phase-Based Implementation Plan

## **PHASE 1: Testing Infrastructure (Week 1-2) 🔴 CRITICAL**

### **Objective**: Achieve 60%+ test coverage with reliable test suite

### **Tasks:**

#### 1.1 Fix Existing Test Infrastructure
**Priority:** Critical
**Effort:** 3 days
**Status:** 🔴 BLOCKER

**Current Issues:**
- pytest can't collect tests (0 collected)
- Import errors in test files
- No test database configuration

**Actions:**
```bash
# 1. Create test database configuration
touch config/settings_test.py
# Add test database URL override

# 2. Fix import issues in test files
# Review: tests/unit/core/test_analytics_fusion_service.py
# Review: tests/unit/test_mtproto_graceful_shutdown.py
# Review: tests/api/test_analytics_v2_cache.py

# 3. Create pytest fixtures
touch tests/conftest.py
# Add: async database, mock repositories, test client
```

**Files to Create:**
- `tests/conftest.py` - Central fixtures
- `tests/fixtures/database.py` - Test DB management
- `tests/fixtures/repositories.py` - Mock repositories
- `tests/factories/` - Test data factories

**Acceptance Criteria:**
- ✅ pytest --collect-only shows >100 tests
- ✅ All tests can be imported without errors
- ✅ Test database auto-creates and tears down

---

#### 1.2 Integration Tests for Critical Endpoints
**Priority:** Critical
**Effort:** 5 days

**Target Endpoints:**
1. **POST /api/auth/login** - Authentication flow
2. **GET /analytics/posts/dynamics/post-dynamics/{id}** - Post dynamics
3. **GET /analytics/channels** - Channel listing
4. **POST /channels** - Channel creation
5. **GET /health** - Health check
6. **GET /api/statistics/reports/comprehensive-report** - Reports

**Test Structure:**
```python
# tests/integration/test_post_dynamics.py
@pytest.mark.asyncio
async def test_post_dynamics_24h(test_client, test_channel):
    """Test post dynamics returns correct 24h data"""
    response = await test_client.get(
        f"/analytics/posts/dynamics/post-dynamics/{test_channel.id}?period=24h"
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 24  # Hourly buckets
    assert all(k in data[0] for k in ['timestamp', 'views', 'likes'])

@pytest.mark.asyncio
async def test_post_dynamics_drill_down(test_client, test_channel):
    """Test day drill-down returns hourly data"""
    today = datetime.now().date()
    response = await test_client.get(
        f"/analytics/posts/dynamics/post-dynamics/{test_channel.id}",
        params={
            "period": "24h",
            "start_date": str(today),
            "end_date": str(today)
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 24  # All 24 hours, zero-filled
```

**Files to Create:**
- `tests/integration/test_post_dynamics.py`
- `tests/integration/test_authentication.py`
- `tests/integration/test_channels.py`
- `tests/integration/test_analytics.py`
- `tests/integration/test_reports.py`

**Acceptance Criteria:**
- ✅ 30+ integration tests passing
- ✅ Tests cover happy path + error cases
- ✅ Tests run in <30 seconds total
- ✅ Coverage >60% on critical paths

---

#### 1.3 Unit Tests for Services
**Priority:** High
**Effort:** 5 days

**Target Services:**
```
core/services/
├── analytics_fusion/ - 20+ tests
├── predictive_intelligence/ - 15+ tests
├── ai_insights_fusion/ - 15+ tests
├── anomaly_analysis/ - 10+ tests
└── optimization_fusion/ - 10+ tests
```

**Example:**
```python
# tests/unit/services/test_analytics_fusion_service.py
@pytest.mark.asyncio
async def test_get_channel_overview(analytics_service, mock_repo):
    """Test analytics fusion service returns overview"""
    mock_repo.get_channel_metrics.return_value = {
        'views': 1000,
        'subscribers': 500
    }

    result = await analytics_service.get_overview('channel_123')

    assert result['views'] == 1000
    assert result['subscribers'] == 500
    mock_repo.get_channel_metrics.assert_called_once()
```

**Acceptance Criteria:**
- ✅ 70+ unit tests created
- ✅ All services have >80% coverage
- ✅ Mocks used for external dependencies
- ✅ Tests are fast (<5s total)

---

## **PHASE 2: API Documentation Enhancement (Week 3) 🟡 HIGH**

### **Objective**: Professional OpenAPI docs with examples and authentication

### **Tasks:**

#### 2.1 Enhance OpenAPI Schemas
**Priority:** High
**Effort:** 3 days

**Current State:**
- OpenAPI tags configured in main.py
- Pydantic models exist but incomplete

**Actions:**
```python
# apps/api/routers/analytics_post_dynamics_router.py

class PostDynamicsRequest(BaseModel):
    """Request parameters for post dynamics"""
    period: Literal['1h', '6h', '24h', '7d', '30d', '90d', 'all'] = '24h'
    start_date: Optional[date] = Field(None, description="Drill-down: specific day")
    end_date: Optional[date] = Field(None, description="Drill-down: specific day")
    start_time: Optional[datetime] = Field(None, description="Drill-down: specific hour")
    end_time: Optional[datetime] = Field(None, description="Drill-down: specific hour")

    class Config:
        json_schema_extra = {
            "example": {
                "period": "7d",
                "start_date": None,
                "end_date": None
            }
        }

@router.get(
    "/post-dynamics/{channel_id}",
    response_model=List[PostDynamicsPoint],
    summary="Get post view dynamics with drill-down",
    description="""
    ## 📊 Post View Dynamics with 3-Level Drill-Down

    Get time-series analytics for post performance over time.

    ### Drill-Down Levels:
    1. **Overview (90d)** → Daily aggregates → Click day
    2. **Day Detail (24h)** → Hourly breakdown → Click hour
    3. **Hour Detail (60m)** → Minute-by-minute data

    ### Examples:
    - Overview: `GET /post-dynamics/123?period=90d`
    - Day drill: `GET /post-dynamics/123?period=24h&start_date=2025-11-21`
    - Hour drill: `GET /post-dynamics/123?start_time=2025-11-21T10:00&end_time=2025-11-21T11:00`

    ### Response Format:
    Returns array of time-series data points with views, likes, shares, comments.
    """,
    responses={
        200: {
            "description": "Successful response",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "timestamp": "2025-11-21T10:00:00Z",
                            "time": "10:00",
                            "views": 1500,
                            "likes": 120,
                            "shares": 45,
                            "comments": 23,
                            "post_count": 5
                        }
                    ]
                }
            }
        },
        400: {"description": "Invalid parameters"},
        404: {"description": "Channel not found"},
        500: {"description": "Server error"}
    },
    tags=["Analytics - Posts"]
)
```

**Files to Update:**
- All routers in `apps/api/routers/`
- Add response examples to each endpoint
- Add error response schemas

**Acceptance Criteria:**
- ✅ All 40+ routers have detailed docstrings
- ✅ Request/response examples for each endpoint
- ✅ Error responses documented
- ✅ Authentication requirements clear

---

#### 2.2 Interactive API Documentation Page
**Priority:** High
**Effort:** 2 days

**Create:** `apps/api/static/api-docs.html`

```html
<!DOCTYPE html>
<html>
<head>
    <title>AnalyticBot API Documentation</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
        SwaggerUIBundle({
            url: '/openapi.json',
            dom_id: '#swagger-ui',
            presets: [SwaggerUIBundle.presets.apis],
            layout: "BaseLayout",
            deepLinking: true,
            displayRequestDuration: true,
            tryItOutEnabled: true,
            persistAuthorization: true
        });
    </script>
</body>
</html>
```

**Add Authentication UI:**
```python
# apps/api/main.py
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="AnalyticBot API",
        version="7.5.0",
        description=app.description,
        routes=app.routes,
    )

    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT Authorization header using Bearer scheme"
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

**Acceptance Criteria:**
- ✅ /docs shows interactive Swagger UI
- ✅ /redoc shows ReDoc alternative
- ✅ Authentication can be tested in UI
- ✅ All endpoints have "Try it out" button

---

## **PHASE 3: Performance Validation & Optimization (Week 4) 🟡 HIGH**

### **Objective**: Validate <100ms claims and optimize bottlenecks

### **Tasks:**

#### 3.1 Performance Benchmarking
**Priority:** High
**Effort:** 3 days

**Create:** `tests/performance/test_api_benchmarks.py`

```python
import pytest
import time
from locust import HttpUser, task, between

class AnalyticBotUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Login and get auth token"""
        response = self.client.post("/api/auth/login", json={
            "username": "test@example.com",
            "password": "testpass"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def get_post_dynamics(self):
        """Test post dynamics endpoint (most critical)"""
        self.client.get(
            "/analytics/posts/dynamics/post-dynamics/demo_channel?period=24h",
            headers=self.headers
        )

    @task(2)
    def get_channels(self):
        """Test channel listing"""
        self.client.get("/analytics/channels", headers=self.headers)

    @task(1)
    def get_health(self):
        """Test health endpoint"""
        self.client.get("/health")

# Run: locust -f tests/performance/test_api_benchmarks.py --host=http://localhost:10400
```

**Metrics to Measure:**
- Response time (p50, p95, p99)
- Throughput (requests/second)
- Error rate
- Memory usage
- Database query time

**Acceptance Criteria:**
- ✅ p95 response time <200ms for critical endpoints
- ✅ Handles 100+ concurrent users
- ✅ Error rate <1%
- ✅ Memory usage stable under load

---

#### 3.2 Database Query Optimization
**Priority:** High
**Effort:** 4 days

**Actions:**

**1. Add Missing Indexes:**
```sql
-- scripts/performance/add_indexes.sql

-- Post dynamics query optimization
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_posts_channel_date
ON posts(channel_id, date DESC)
WHERE is_deleted = FALSE;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_post_metrics_lookup
ON post_metrics(channel_id, msg_id, snapshot_time DESC);

-- Analytics queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_channel_daily_stats
ON channel_daily_stats(channel_id, date DESC);

-- User queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email
ON users(email) WHERE is_active = TRUE;

-- Partial indexes for hot data (last 30 days)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_posts_recent
ON posts(channel_id, date DESC)
WHERE date > NOW() - INTERVAL '30 days' AND is_deleted = FALSE;
```

**2. Query Analysis:**
```python
# scripts/performance/analyze_queries.py
import asyncio
from apps.di import get_container

async def analyze_slow_queries():
    """Find and report slow queries"""
    container = get_container()
    pool = await container.database.asyncpg_pool()

    async with pool.acquire() as conn:
        slow_queries = await conn.fetch("""
            SELECT
                query,
                calls,
                total_time,
                mean_time,
                max_time
            FROM pg_stat_statements
            WHERE mean_time > 100  -- Queries taking >100ms on average
            ORDER BY total_time DESC
            LIMIT 20
        """)

        for row in slow_queries:
            print(f"Query: {row['query'][:100]}...")
            print(f"  Calls: {row['calls']}")
            print(f"  Avg: {row['mean_time']:.2f}ms")
            print(f"  Max: {row['max_time']:.2f}ms")
            print()

if __name__ == "__main__":
    asyncio.run(analyze_slow_queries())
```

**3. Add Query Monitoring:**
```python
# core/monitoring/query_monitor.py
import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)

def monitor_query(threshold_ms=100):
    """Decorator to log slow queries"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start) * 1000

                if duration_ms > threshold_ms:
                    logger.warning(
                        f"Slow query detected: {func.__name__} took {duration_ms:.2f}ms"
                    )

                return result
            except Exception as e:
                duration_ms = (time.time() - start) * 1000
                logger.error(
                    f"Query failed: {func.__name__} after {duration_ms:.2f}ms - {e}"
                )
                raise
        return wrapper
    return decorator
```

**Acceptance Criteria:**
- ✅ All critical queries have indexes
- ✅ Query times reduced by >50%
- ✅ Slow query logging enabled
- ✅ No N+1 queries detected

---

## **PHASE 4: Monitoring & Observability (Week 5) 🟡 HIGH**

### **Objective**: Create operational dashboards and alerting

### **Tasks:**

#### 4.1 Grafana Dashboard Creation
**Priority:** High
**Effort:** 4 days

**Create:** `infra/monitoring/grafana/dashboards/analyticbot-main.json`

**Dashboards to Create:**

**1. API Performance Dashboard**
- Request rate (req/s)
- Response time (p50, p95, p99)
- Error rate (4xx, 5xx)
- Top 10 slowest endpoints
- Database connection pool usage

**2. Business Metrics Dashboard**
- Active channels
- Total posts analyzed
- API calls per endpoint
- User registrations
- Subscription conversions

**3. Infrastructure Dashboard**
- CPU, Memory, Disk usage
- Database query performance
- Redis hit rate
- Celery queue length
- MTProto service health

**4. Post Dynamics Dashboard**
- Real-time view counts
- Engagement rates
- Top performing posts
- Hour-over-hour growth

**Template:**
```json
{
  "dashboard": {
    "title": "AnalyticBot - API Performance",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [{
          "expr": "rate(http_requests_total[5m])"
        }]
      },
      {
        "title": "Response Time (p95)",
        "targets": [{
          "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
        }]
      }
    ]
  }
}
```

**Acceptance Criteria:**
- ✅ 4 operational dashboards created
- ✅ All metrics have proper labels
- ✅ Dashboards auto-refresh every 30s
- ✅ Alerts configured for critical metrics

---

#### 4.2 Distributed Tracing
**Priority:** Medium
**Effort:** 3 days

**Add OpenTelemetry:**
```python
# core/monitoring/tracing.py
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor

def setup_tracing(app):
    """Configure distributed tracing"""
    provider = TracerProvider()
    processor = BatchSpanProcessor(
        OTLPSpanExporter(endpoint="http://jaeger:4317")
    )
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)

    # Instrument AsyncPG
    AsyncPGInstrumentor().instrument()

    return provider
```

**Usage in Endpoints:**
```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@router.get("/post-dynamics/{channel_id}")
async def get_post_dynamics(channel_id: str):
    with tracer.start_as_current_span("fetch_post_dynamics") as span:
        span.set_attribute("channel_id", channel_id)

        # Your logic here
        data = await fetch_data(channel_id)

        span.set_attribute("data_points", len(data))
        return data
```

**Acceptance Criteria:**
- ✅ All API requests traced
- ✅ Database queries traced
- ✅ Trace IDs in logs
- ✅ Jaeger UI shows traces

---

## **PHASE 5: UI Enhancements (Week 6-7) 🟢 MEDIUM**

### **Objective**: Complete drill-down UI and improve UX

### **Tasks:**

#### 5.1 Complete Drill-Down Implementation
**Priority:** Medium
**Effort:** 5 days

**Current State:**
- Backend fully supports drill-down
- Frontend has partial implementation (variables declared but not used)

**Files to Update:**
```typescript
// apps/frontend/src/shared/components/charts/PostViewDynamics/PostViewDynamicsChart.tsx

// Add drill-down state management
const [drillDownLevel, setDrillDownLevel] = useState<'overview' | 'day' | 'hour'>('overview');
const [drillDownDate, setDrillDownDate] = useState<string | null>(null);
const [drillDownHour, setDrillDownHour] = useState<string | null>(null);

// Handle chart click for drill-down
const handleChartClick = useCallback((data: any) => {
    if (!data?.activePayload?.[0]?.payload) return;

    const point = data.activePayload[0].payload;

    if (drillDownLevel === 'overview') {
        // Level 1 → Level 2: Drill into day
        setDrillDownLevel('day');
        setDrillDownDate(point.timestamp);
        setTimeRange('24h');

        fetchPostDynamics(channelId, '24h', {
            start_date: point.timestamp,
            end_date: point.timestamp
        });
    } else if (drillDownLevel === 'day') {
        // Level 2 → Level 3: Drill into hour
        setDrillDownLevel('hour');
        setDrillDownHour(point.timestamp);

        const hourStart = new Date(point.timestamp);
        const hourEnd = new Date(hourStart.getTime() + 3600000);

        fetchPostDynamics(channelId, '1h', null, {
            start_time: hourStart.toISOString(),
            end_time: hourEnd.toISOString()
        });
    }
}, [drillDownLevel, channelId, fetchPostDynamics]);

// Add breadcrumb navigation
const renderBreadcrumbs = () => (
    <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
        <Chip
            label="90 Days"
            onClick={() => handleBreadcrumbClick('overview')}
            color={drillDownLevel === 'overview' ? 'primary' : 'default'}
        />
        {drillDownDate && (
            <>
                <ChevronRight />
                <Chip
                    label={new Date(drillDownDate).toLocaleDateString()}
                    onClick={() => handleBreadcrumbClick('day')}
                    color={drillDownLevel === 'day' ? 'primary' : 'default'}
                />
            </>
        )}
        {drillDownHour && (
            <>
                <ChevronRight />
                <Chip
                    label={new Date(drillDownHour).toLocaleTimeString()}
                    color="primary"
                />
            </>
        )}
    </Box>
);
```

**Add Visual Indicators:**
```typescript
// Update chart visualization
<ChartVisualization
    data={chartData}
    timeRange={timeRange}
    onChartClick={handleChartClick}
    clickable={drillDownLevel !== 'hour'}  // Can't drill further
    cursorStyle={drillDownLevel !== 'hour' ? 'pointer' : 'default'}
/>
```

**Acceptance Criteria:**
- ✅ Clicking chart drills down to next level
- ✅ Breadcrumbs show navigation path
- ✅ Back button returns to previous level
- ✅ Visual cursor indicates clickable areas
- ✅ Loading state during drill-down

---

#### 5.2 Enhanced Analytics Features
**Priority:** Medium
**Effort:** 5 days

**1. Comparison Mode:**
```typescript
// Add comparison toggle
const [comparisonMode, setComparisonMode] = useState(false);
const [comparisonPeriod, setComparisonPeriod] = useState<'previous_period' | 'previous_year'>('previous_period');

// Fetch comparison data
const fetchComparison = async () => {
    const mainData = await fetchPostDynamics(channelId, period);
    const comparisonData = await fetchPostDynamics(
        channelId,
        period,
        { start_date: calculateComparisonStart() }
    );

    return { mainData, comparisonData };
};

// Render comparison chart
<LineChart>
    <Line dataKey="views" stroke="#8884d8" name="Current Period" />
    {comparisonMode && (
        <Line dataKey="viewsComparison" stroke="#82ca9d" name="Previous Period" strokeDasharray="5 5" />
    )}
</LineChart>
```

**2. Export Functionality:**
```typescript
// Add export buttons
const exportToCSV = () => {
    const csv = chartData.map(row =>
        `${row.timestamp},${row.views},${row.likes},${row.shares},${row.comments}`
    ).join('\n');

    const blob = new Blob([`Timestamp,Views,Likes,Shares,Comments\n${csv}`],
        { type: 'text/csv' }
    );
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `post-dynamics-${channelId}-${new Date().toISOString()}.csv`;
    a.click();
};

const exportToPNG = async () => {
    const chartElement = chartRef.current;
    const canvas = await html2canvas(chartElement);
    const url = canvas.toDataURL('image/png');
    const a = document.createElement('a');
    a.href = url;
    a.download = `post-dynamics-${channelId}-${new Date().toISOString()}.png`;
    a.click();
};
```

**3. Annotations:**
```typescript
// Add viral post markers
const addAnnotations = (data: ChartData[]) => {
    return data.map(point => ({
        ...point,
        isViral: point.views > averageViews * 3,
        annotation: point.views > averageViews * 3 ? '🔥 Viral!' : null
    }));
};
```

**Acceptance Criteria:**
- ✅ Comparison mode shows two periods
- ✅ Export to CSV works
- ✅ Export to PNG works
- ✅ Viral posts marked with icon
- ✅ Mobile responsive

---

## **PHASE 6: Security Hardening (Week 8) 🟠 MEDIUM**

### **Objective**: Enhanced security and vulnerability management

### **Tasks:**

#### 6.1 Enhanced Rate Limiting
**Priority:** Medium
**Effort:** 2 days

**Current:** SlowAPI already implemented
**Enhancement:** Add per-user limits

```python
# apps/api/middleware/rate_limiter_enhanced.py
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

def get_user_identifier(request: Request) -> str:
    """Get user ID for rate limiting, fall back to IP"""
    user = getattr(request.state, 'user', None)
    if user:
        return f"user:{user.id}"
    return f"ip:{get_remote_address(request)}"

limiter = Limiter(
    key_func=get_user_identifier,
    default_limits=["100/minute", "1000/hour"],
    storage_uri="redis://localhost:10200"
)
```

**Add Endpoint-Specific Limits:**
```python
@router.get("/post-dynamics/{channel_id}")
@limiter.limit("30/minute")  # More restrictive for expensive queries
async def get_post_dynamics(...):
    pass
```

**Acceptance Criteria:**
- ✅ Per-user rate limits work
- ✅ Different limits for different endpoints
- ✅ Rate limit headers in response
- ✅ Clear error messages

---

#### 6.2 Security Scanning
**Priority:** Medium
**Effort:** 3 days

**Add to CI/CD:**
```yaml
# .github/workflows/security-scan.yml
name: Security Scan

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  push:
    branches: [main]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Snyk Security Scan
        uses: snyk/actions/python@master
        with:
          args: --severity-threshold=high

      - name: Run Bandit Security Linter
        run: |
          pip install bandit
          bandit -r apps/ core/ infra/ -f json -o bandit-report.json

      - name: Run Safety Check
        run: |
          pip install safety
          safety check --json > safety-report.json

      - name: Upload Reports
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: |
            bandit-report.json
            safety-report.json
```

**Acceptance Criteria:**
- ✅ Daily security scans run
- ✅ Vulnerabilities reported to team
- ✅ High-severity issues block CI
- ✅ Security reports archived

---

## **PHASE 7: Documentation & DevEx (Week 9) 🟢 MEDIUM**

### **Objective**: Improve developer experience and onboarding

### **Tasks:**

#### 7.1 Developer Portal
**Priority:** Medium
**Effort:** 4 days

**Create:** `docs/developer-portal/`

**Structure:**
```
docs/developer-portal/
├── index.md (Getting Started)
├── quickstart.md (5-minute setup)
├── api/
│   ├── authentication.md
│   ├── endpoints.md
│   └── webhooks.md
├── examples/
│   ├── python-client.md
│   ├── javascript-client.md
│   └── curl-examples.md
├── guides/
│   ├── drill-down-analytics.md
│   ├── real-time-updates.md
│   └── custom-dashboards.md
└── troubleshooting.md
```

**Example Content:**
```markdown
# Quick Start Guide

## Installation

\`\`\`bash
pip install analyticbot-client
\`\`\`

## Authentication

\`\`\`python
from analyticbot import Client

client = Client(api_key="your_api_key")
channels = client.channels.list()
\`\`\`

## Get Post Dynamics

\`\`\`python
# Get 7-day overview
dynamics = client.analytics.post_dynamics(
    channel_id="123",
    period="7d"
)

# Drill down to specific day
day_dynamics = client.analytics.post_dynamics(
    channel_id="123",
    period="24h",
    start_date="2025-11-21"
)
\`\`\`
```

**Acceptance Criteria:**
- ✅ Complete getting started guide
- ✅ Code examples in Python, JS, curl
- ✅ Troubleshooting section
- ✅ Migration guides

---

#### 7.2 API Client Libraries
**Priority:** Medium
**Effort:** 3 days

**Create:** `clients/python/analyticbot/`

```python
# clients/python/analyticbot/client.py
import httpx
from typing import Optional, List, Dict, Any

class AnalyticBotClient:
    """Official Python client for AnalyticBot API"""

    def __init__(self, api_key: str, base_url: str = "https://api.analyticbot.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30.0
        )

    async def get_post_dynamics(
        self,
        channel_id: str,
        period: str = "7d",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get post dynamics with optional drill-down"""
        params = {"period": period}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        response = await self.client.get(
            f"{self.base_url}/analytics/posts/dynamics/post-dynamics/{channel_id}",
            params=params
        )
        response.raise_for_status()
        return response.json()

    async def get_channels(self) -> List[Dict[str, Any]]:
        """List all channels"""
        response = await self.client.get(f"{self.base_url}/analytics/channels")
        response.raise_for_status()
        return response.json()
```

**Publish to PyPI:**
```bash
# setup.py
python setup.py sdist bdist_wheel
twine upload dist/*
```

**Acceptance Criteria:**
- ✅ Python client published to PyPI
- ✅ JavaScript client published to npm
- ✅ Full type hints/TypeScript types
- ✅ Unit tests for clients

---

## **PHASE 8: Deployment & Optimization (Week 10-11) 🔵 LOW**

### **Objective**: Production deployment best practices

### **Tasks:**

#### 8.1 Kubernetes Production Setup
**Priority:** Low
**Effort:** 5 days

**Current:** K8s manifests exist
**Enhancement:** Production-ready configuration

**Create:** `infra/k8s/production/`

```yaml
# infra/k8s/production/api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: analyticbot-api
  namespace: production
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: analyticbot-api
  template:
    metadata:
      labels:
        app: analyticbot-api
    spec:
      containers:
      - name: api
        image: analyticbot:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: analyticbot-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: analyticbot-secrets
              key: redis-url
---
apiVersion: v1
kind: Service
metadata:
  name: analyticbot-api
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: analyticbot-api
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: analyticbot-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: analyticbot-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**Acceptance Criteria:**
- ✅ Multi-replica deployment
- ✅ Auto-scaling configured
- ✅ Health checks working
- ✅ Rolling updates tested

---

## **PHASE 9: Mobile & Progressive Web App (Week 12) 🔵 LOW**

### **Objective**: Mobile optimization and PWA features

### **Tasks:**

#### 9.1 PWA Implementation
**Priority:** Low
**Effort:** 3 days

**Add:** `apps/frontend/public/manifest.json`

```json
{
  "name": "AnalyticBot",
  "short_name": "AnalyticBot",
  "description": "Telegram Channel Analytics",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#1976d2",
  "icons": [
    {
      "src": "/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

**Add Service Worker:**
```typescript
// apps/frontend/src/service-worker.ts
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open('analyticbot-v1').then((cache) => {
            return cache.addAll([
                '/',
                '/index.html',
                '/static/css/main.css',
                '/static/js/main.js'
            ]);
        })
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request).then((response) => {
            return response || fetch(event.request);
        })
    );
});
```

**Acceptance Criteria:**
- ✅ Installable as PWA
- ✅ Offline fallback page
- ✅ Push notifications (optional)
- ✅ App icon and splash screen

---

## 📈 Success Metrics

### **Phase 1-3 (Critical)**
- ✅ Test coverage >60%
- ✅ API docs completion 100%
- ✅ p95 response time <200ms
- ✅ All critical queries indexed

### **Phase 4-6 (High)**
- ✅ 4 operational dashboards
- ✅ Drill-down UI complete
- ✅ Daily security scans passing
- ✅ Rate limits per user

### **Phase 7-9 (Medium/Low)**
- ✅ Developer portal live
- ✅ Client libraries published
- ✅ K8s production deployment
- ✅ PWA installable

---

## 🚀 Quick Wins (Can Do Today)

1. **Fix Test Collection** (2 hours)
   - Create `tests/conftest.py`
   - Fix import errors
   - Run pytest successfully

2. **Add OpenAPI Examples** (3 hours)
   - Update 10 most-used endpoints
   - Add request/response examples
   - Test in Swagger UI

3. **Create First Grafana Dashboard** (2 hours)
   - API request rate
   - Response times
   - Error rates

4. **Add Database Indexes** (1 hour)
   - Run scripts/performance/add_indexes.sql
   - Measure query time improvements

5. **Complete Drill-Down UI** (4 hours)
   - Wire up click handlers
   - Add breadcrumbs
   - Test all three levels

---

## 📋 Resource Requirements

### **Team**
- 1 Backend Developer (Full-time, 8 weeks)
- 1 Frontend Developer (Part-time, 4 weeks)
- 1 DevOps Engineer (Part-time, 3 weeks)
- 1 QA Engineer (Part-time, 4 weeks)

### **Tools & Services**
- Locust (load testing) - Free
- Sentry (error tracking) - $26/mo
- Snyk (security scanning) - $0-99/mo
- Grafana Cloud (optional) - $0-49/mo

### **Infrastructure**
- Staging environment - $50/mo
- Load testing server - $20/mo (temporary)
- Additional Redis instance - $10/mo

**Total Cost:** ~$200-300/month

---

## 🎯 Priority Matrix

| Priority | Phase | Effort | Impact | Start |
|----------|-------|--------|--------|-------|
| 🔴 CRITICAL | Testing Infrastructure | High | Very High | Week 1 |
| 🔴 CRITICAL | API Documentation | Medium | High | Week 3 |
| 🟡 HIGH | Performance Validation | High | High | Week 4 |
| 🟡 HIGH | Monitoring Dashboards | Medium | High | Week 5 |
| 🟢 MEDIUM | UI Enhancements | Medium | Medium | Week 6 |
| 🟠 MEDIUM | Security Hardening | Medium | Medium | Week 8 |
| 🟢 MEDIUM | Developer Portal | Medium | Medium | Week 9 |
| 🔵 LOW | K8s Production | High | Low | Week 10 |
| 🔵 LOW | PWA Features | Low | Low | Week 12 |

---

## 📝 Notes

### **Technical Debt to Address**
- Archive folder cleanup (remove legacy code)
- Consolidate duplicate services
- Migration file audit and consolidation
- Remove mock data from production code

### **Future Enhancements** (Post-Plan)
- GraphQL API
- Real-time WebSocket updates
- Machine learning model retraining pipeline
- Multi-language support (i18n completion)
- White-label customization

### **Risk Mitigation**
- Run tests in staging before production
- Feature flags for gradual rollout
- Automated rollback procedures
- Backup before major changes

---

**Last Updated:** November 21, 2025
**Next Review:** December 1, 2025

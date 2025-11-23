# ✅ AnalyticBot - Immediate Action Checklist
**Start Here: Your First 48 Hours**

---

## 🚀 Priority 1: CRITICAL (Do First)

### ⚡ **Quick Win #1: Fix Test Infrastructure** (2-3 hours)
**Why:** Tests are broken (0 collected), blocking all development
**Impact:** 🔴 CRITICAL - Enables all other work

```bash
# Step 1: Create test configuration (15 min)
cd /home/abcdeveloper/projects/analyticbot

cat > tests/conftest.py << 'EOF'
"""
Pytest configuration and fixtures for AnalyticBot tests
"""
import pytest
import asyncio
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from apps.api.main import app
from config.settings import settings

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://analytic:change_me@localhost:10100/analytic_bot_test"

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_client():
    """FastAPI test client"""
    return TestClient(app)

@pytest.fixture
async def async_client():
    """Async test client for real async tests"""
    from httpx import AsyncClient
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def test_db():
    """Test database session"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session

    await engine.dispose()

# Mark all tests as async by default
pytest_plugins = ['pytest_asyncio']
EOF

# Step 2: Create first working test (10 min)
cat > tests/test_health_working.py << 'EOF'
"""
Basic health check test - should always pass
"""
import pytest
from fastapi.testclient import TestClient

def test_health_endpoint(test_client):
    """Test that health endpoint returns 200"""
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["healthy", "ok"]

def test_api_structure(test_client):
    """Test that main API endpoints are accessible"""
    # Just test they don't 404
    endpoints = [
        "/health",
        "/docs",
        "/openapi.json"
    ]

    for endpoint in endpoints:
        response = test_client.get(endpoint, follow_redirects=True)
        assert response.status_code != 404, f"{endpoint} returned 404"
EOF

# Step 3: Run the test (5 min)
pytest tests/test_health_working.py -v

# Step 4: Fix any remaining import errors (30 min - 1 hour)
# Check each failing test file and fix imports
python -m pytest --collect-only tests/ 2>&1 | grep "ERROR" | head -10

# Step 5: Verify (5 min)
pytest tests/ --collect-only | grep "test session starts" -A 5
```

**✅ Success Criteria:**
- pytest collects >5 tests
- At least 1 test passes
- No import errors

---

### ⚡ **Quick Win #2: Add OpenAPI Examples** (2-3 hours)
**Why:** Improve API discoverability and developer experience
**Impact:** 🟡 HIGH - Helps external integrations

```bash
# Step 1: Update post dynamics router (30 min)
# Open: apps/api/routers/analytics_post_dynamics_router.py

# Add this above the route:
from pydantic import BaseModel, Field
from typing import Literal

class PostDynamicsParams(BaseModel):
    """Query parameters for post dynamics"""
    period: Literal['1h', '6h', '12h', '24h', '7d', '30d', '90d', 'all'] = Field(
        default='24h',
        description="Time period for analysis",
        example="7d"
    )
    start_date: Optional[str] = Field(
        None,
        description="Drill-down: Specific day (YYYY-MM-DD)",
        example="2025-11-21"
    )

# Step 2: Update the router decorator (20 min)
@router.get(
    "/post-dynamics/{channel_id}",
    response_model=List[PostDynamicsPoint],
    summary="Get post view dynamics with 3-level drill-down",
    description="""
    ## 📊 Post View Dynamics

    Time-series analytics for post performance with interactive drill-down.

    ### 🎯 Use Cases:
    - Track engagement over time
    - Identify viral posts
    - Optimize posting schedule
    - Compare periods

    ### 🔍 Drill-Down Levels:
    1. **Overview (90d)**: Daily totals → Click to see hourly breakdown
    2. **Day Detail (24h)**: Hourly data → Click to see minute-by-minute
    3. **Hour Detail (60m)**: Minute granularity

    ### 📝 Examples:

    **Get 7-day overview:**
    ```bash
    curl -X GET "http://localhost:10400/analytics/posts/dynamics/post-dynamics/demo_channel?period=7d" \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```

    **Drill into specific day:**
    ```bash
    curl -X GET "http://localhost:10400/analytics/posts/dynamics/post-dynamics/demo_channel?period=24h&start_date=2025-11-21" \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```

    **Drill into specific hour:**
    ```bash
    curl -X GET "http://localhost:10400/analytics/posts/dynamics/post-dynamics/demo_channel?start_time=2025-11-21T10:00:00Z&end_time=2025-11-21T11:00:00Z" \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """,
    responses={
        200: {
            "description": "Successful response with time-series data",
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
                        },
                        {
                            "timestamp": "2025-11-21T11:00:00Z",
                            "time": "11:00",
                            "views": 1750,
                            "likes": 140,
                            "shares": 52,
                            "comments": 31,
                            "post_count": 7
                        }
                    ]
                }
            }
        },
        400: {
            "description": "Invalid parameters (bad channel ID, invalid period)",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid channel ID"}
                }
            }
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authenticated"}
                }
            }
        },
        404: {
            "description": "Channel not found or no data available",
            "content": {
                "application/json": {
                    "example": {"detail": "Channel not found"}
                }
            }
        }
    },
    tags=["Analytics - Posts"]
)

# Step 3: Test in Swagger UI (10 min)
# Open http://localhost:10400/docs
# Find post-dynamics endpoint
# Click "Try it out"
# Verify examples show correctly

# Step 4: Repeat for 5 more critical endpoints (1-2 hours)
# Priority endpoints:
# - /analytics/channels
# - /api/auth/login
# - /health
# - /analytics/historical/overview/{channel_id}
# - /analytics/posts/top-posts/{channel_id}
```

**✅ Success Criteria:**
- 6+ endpoints have detailed docs
- Examples are runnable
- Swagger UI shows all info
- Error responses documented

---

### ⚡ **Quick Win #3: Create First Grafana Dashboard** (2 hours)
**Why:** Visibility into production performance
**Impact:** 🟡 HIGH - Operational awareness

```bash
# Step 1: Access Grafana (5 min)
# Open http://localhost:3000
# Login: admin / admin (change password)

# Step 2: Add Prometheus data source (5 min)
# Settings → Data Sources → Add Prometheus
# URL: http://prometheus:9090
# Save & Test

# Step 3: Create dashboard (30 min)
# Create → Dashboard → Add Panel

# Panel 1: API Request Rate
# Query: rate(http_requests_total[5m])
# Visualization: Time series
# Title: "Requests per Second"

# Panel 2: Response Time (p95)
# Query: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
# Visualization: Time series
# Title: "Response Time p95"

# Panel 3: Error Rate
# Query: rate(http_requests_total{status=~"5.."}[5m])
# Visualization: Time series
# Title: "5xx Errors per Second"
# Alert: > 0.1 for 5 minutes

# Panel 4: Active Channels
# Query: count(channel_metrics)
# Visualization: Stat
# Title: "Active Channels"

# Step 4: Save dashboard (5 min)
# Save → "AnalyticBot - API Performance"
# Add to folder: "Production"
# Set auto-refresh: 30 seconds

# Step 5: Export dashboard JSON (5 min)
# Settings → JSON Model → Copy
# Save to: infra/monitoring/grafana/dashboards/api-performance.json
```

**✅ Success Criteria:**
- Dashboard shows real data
- Auto-refreshes every 30s
- Saved and exportable
- Accessible to team

---

## 🎯 Priority 2: HIGH (Do This Week)

### 📝 **Task #4: Add Database Indexes** (1 hour)
**Why:** Query performance optimization
**Impact:** 🟡 HIGH - Faster response times

```sql
-- Create: scripts/performance/add_critical_indexes.sql

-- Post dynamics optimization
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_posts_channel_date_active
ON posts(channel_id, date DESC)
WHERE is_deleted = FALSE;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_post_metrics_latest
ON post_metrics(channel_id, msg_id, snapshot_time DESC);

-- Analytics queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_channel_daily_recent
ON channel_daily_stats(channel_id, date DESC)
WHERE date > NOW() - INTERVAL '90 days';

-- Run the script:
-- psql -h localhost -p 10100 -U analytic -d analytic_bot -f scripts/performance/add_critical_indexes.sql

-- Verify indexes created:
-- \d posts
-- \d post_metrics
-- \d channel_daily_stats
```

**✅ Success Criteria:**
- 3+ indexes created
- Query times improved
- No errors during creation

---

### 🧪 **Task #5: Write 5 Integration Tests** (3 hours)
**Why:** Ensure critical flows work
**Impact:** 🟡 HIGH - Prevent regressions

```python
# Create: tests/integration/test_post_dynamics_integration.py

import pytest
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_post_dynamics_24h_returns_hourly_data(async_client):
    """Test 24h period returns up to 24 hourly buckets"""
    response = await async_client.get(
        "/analytics/posts/dynamics/post-dynamics/demo_channel",
        params={"period": "24h"}
    )

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) <= 24  # May have fewer if no data

    # Check structure
    if len(data) > 0:
        point = data[0]
        assert "timestamp" in point
        assert "views" in point
        assert "likes" in point
        assert "shares" in point
        assert "comments" in point

@pytest.mark.asyncio
async def test_post_dynamics_7d_returns_daily_data(async_client):
    """Test 7d period returns up to 7 daily buckets"""
    response = await async_client.get(
        "/analytics/posts/dynamics/post-dynamics/demo_channel",
        params={"period": "7d"}
    )

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) <= 7

@pytest.mark.asyncio
async def test_post_dynamics_drill_down_day(async_client):
    """Test drilling into specific day returns 24 hours"""
    today = datetime.now().date()

    response = await async_client.get(
        "/analytics/posts/dynamics/post-dynamics/demo_channel",
        params={
            "period": "24h",
            "start_date": str(today),
            "end_date": str(today)
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Should return all 24 hours (zero-filled if no data)
    assert len(data) == 24

@pytest.mark.asyncio
async def test_post_dynamics_invalid_channel(async_client):
    """Test invalid channel returns appropriate error"""
    response = await async_client.get(
        "/analytics/posts/dynamics/post-dynamics/invalid_channel_999999",
        params={"period": "24h"}
    )

    # Should return empty array or 404
    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

@pytest.mark.asyncio
async def test_post_dynamics_caching(async_client):
    """Test that repeated requests use cache"""
    # First request
    start1 = datetime.now()
    response1 = await async_client.get(
        "/analytics/posts/dynamics/post-dynamics/demo_channel",
        params={"period": "7d"}
    )
    duration1 = (datetime.now() - start1).total_seconds()

    # Second request (should be cached)
    start2 = datetime.now()
    response2 = await async_client.get(
        "/analytics/posts/dynamics/post-dynamics/demo_channel",
        params={"period": "7d"}
    )
    duration2 = (datetime.now() - start2).total_seconds()

    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response1.json() == response2.json()

    # Second request should be faster (cached)
    assert duration2 < duration1 * 0.5  # At least 50% faster

# Run: pytest tests/integration/test_post_dynamics_integration.py -v
```

**✅ Success Criteria:**
- 5 tests written and passing
- Tests cover happy + error paths
- Tests run in <10 seconds

---

## 📊 Priority 3: MEDIUM (Do Next Week)

### 🎨 **Task #6: Complete Drill-Down UI** (4 hours)

See detailed implementation in `/docs/UPGRADE_PLAN.md` Phase 5.1

---

### 🔒 **Task #7: Enhanced Rate Limiting** (2 hours)

See detailed implementation in `/docs/UPGRADE_PLAN.md` Phase 6.1

---

## 📈 Track Your Progress

### Daily Checklist Template

```markdown
## Day 1 Progress: _____

### Completed ✅
- [ ] Fix test infrastructure
- [ ] First test passing
- [ ]

### In Progress 🚧
- [ ]
- [ ]

### Blocked 🚫
- [ ]
- [ ]

### Notes
-
-

### Tomorrow's Plan
1.
2.
3.
```

---

## 🎯 Success Metrics (Week 1)

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Tests Passing | 10+ | ___ | ⬜ |
| Test Coverage | 40% | ___ | ⬜ |
| Docs Updated | 6 endpoints | ___ | ⬜ |
| Dashboards Created | 1 | ___ | ⬜ |
| Indexes Added | 3 | ___ | ⬜ |

---

## 🆘 Troubleshooting Common Issues

### **Issue: pytest not finding tests**
```bash
# Check Python path
export PYTHONPATH=/home/abcdeveloper/projects/analyticbot:$PYTHONPATH

# Try explicit collection
pytest --collect-only -v

# Check for syntax errors
python -m py_compile tests/*.py
```

### **Issue: Database connection fails in tests**
```bash
# Create test database
psql -h localhost -p 10100 -U analytic -c "CREATE DATABASE analytic_bot_test;"

# Update .env with test database
TEST_DATABASE_URL=postgresql+asyncpg://analytic:change_me@localhost:10100/analytic_bot_test
```

### **Issue: Import errors in tests**
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Check import paths
python -c "from apps.api.main import app; print('OK')"
```

---

## 🎉 Quick Wins Summary

**If you complete just these 3 tasks:**
1. ✅ Fix test infrastructure (2-3 hours)
2. ✅ Add API documentation (2-3 hours)
3. ✅ Create Grafana dashboard (2 hours)

**You will have:**
- ✅ Working test suite
- ✅ Professional API docs
- ✅ Production monitoring
- ✅ Solid foundation for everything else

**Total Time:** 6-8 hours (1 focused work day)

---

## 📞 Need Help?

- 📖 **Full Plan:** `/docs/UPGRADE_PLAN.md`
- 🗺️ **Roadmap:** `/docs/IMPLEMENTATION_ROADMAP.md`
- 🐛 **Issues:** Create GitHub issue
- 💬 **Questions:** Team Slack

---

**Remember:** Start small, build momentum, celebrate wins! 🎊

**Let's ship this! 🚀**

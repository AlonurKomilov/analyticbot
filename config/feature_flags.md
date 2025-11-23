# Feature Flags Configuration

## Overview
Feature flags allow safe deployment and rollback of new recommendation system features without code changes.

## Available Flags

### ENABLE_ADVANCED_RECOMMENDATIONS
**Default:** `true`
**Type:** Boolean (`true`/`false`)

Master toggle for all advanced recommendation features. When disabled, the system falls back to the original/legacy query logic.

**When enabled:**
- Uses time-weighted engagement calculations
- Provides content-type specific recommendations
- Includes day-hour combination analysis
- Returns extended API response with new fields

**When disabled:**
- Uses simple average calculations
- No content type analysis
- Basic hourly/daily recommendations only
- Backward-compatible API response

**Impact:**
- Query complexity: Advanced query ~2x slower
- Memory usage: +15% for additional CTEs
- Response size: +30% with new fields

---

### ENABLE_TIME_WEIGHTING
**Default:** `true`
**Type:** Boolean (`true`/`false`)
**Requires:** `ENABLE_ADVANCED_RECOMMENDATIONS=true`

Applies exponential time decay to give more weight to recent posts in recommendations.

**Formula:** `EXP(-0.05 * days_ago)`

**When enabled:**
- Posts from last week: ~70% weight
- Posts from 2 weeks ago: ~50% weight
- Posts from 30 days ago: ~22% weight

**When disabled:**
- All posts weighted equally (1.0)
- Simple average across entire time window

**Use case:** Disable if you want historical patterns to have equal weight as recent patterns.

---

### ENABLE_CONTENT_TYPE_ANALYSIS
**Default:** `true`
**Type:** Boolean (`true`/`false`)
**Requires:** `ENABLE_ADVANCED_RECOMMENDATIONS=true`

Enables content-type specific recommendations (video, image, text, link).

**When enabled:**
- Detects post types using `has_video` and `has_media` columns
- Provides separate recommendations for each content type
- Returns `content_type_recommendations` in API response

**When disabled:**
- No content type detection
- Aggregate recommendations across all post types
- No `content_type_recommendations` field

**Database requirements:**
- Requires `posts.has_video` and `posts.has_media` columns
- Requires migration 004 to be applied

---

## Configuration Methods

### 1. Environment Variables (.env)
```bash
# .env file
ENABLE_ADVANCED_RECOMMENDATIONS=true
ENABLE_TIME_WEIGHTING=true
ENABLE_CONTENT_TYPE_ANALYSIS=true
```

### 2. Docker Compose
```yaml
services:
  api:
    environment:
      - ENABLE_ADVANCED_RECOMMENDATIONS=true
      - ENABLE_TIME_WEIGHTING=true
      - ENABLE_CONTENT_TYPE_ANALYSIS=true
```

### 3. Kubernetes ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: recommendation-feature-flags
data:
  ENABLE_ADVANCED_RECOMMENDATIONS: "true"
  ENABLE_TIME_WEIGHTING: "true"
  ENABLE_CONTENT_TYPE_ANALYSIS: "true"
```

### 4. Runtime Export (Testing)
```bash
export ENABLE_ADVANCED_RECOMMENDATIONS=false
python -m uvicorn apps.api.main:app --reload
```

---

## Deployment Scenarios

### Scenario 1: Full Rollout (Recommended)
```bash
ENABLE_ADVANCED_RECOMMENDATIONS=true
ENABLE_TIME_WEIGHTING=true
ENABLE_CONTENT_TYPE_ANALYSIS=true
```
**Use when:** All features tested and validated in staging.

### Scenario 2: Partial Rollout (Testing Content Types)
```bash
ENABLE_ADVANCED_RECOMMENDATIONS=true
ENABLE_TIME_WEIGHTING=false
ENABLE_CONTENT_TYPE_ANALYSIS=true
```
**Use when:** Testing content-type recommendations without time-weighting complexity.

### Scenario 3: Safe Rollback (Performance Issues)
```bash
ENABLE_ADVANCED_RECOMMENDATIONS=false
```
**Use when:** New features causing performance degradation or errors.

### Scenario 4: Legacy Mode (Emergency)
```bash
ENABLE_ADVANCED_RECOMMENDATIONS=false
ENABLE_TIME_WEIGHTING=false
ENABLE_CONTENT_TYPE_ANALYSIS=false
```
**Use when:** Complete rollback to pre-enhancement behavior needed immediately.

---

## Monitoring & Troubleshooting

### Check Current Flag Status
Flags are logged at query execution:
```
INFO: Using ADVANCED query with new features enabled
INFO: Time weighting: ENABLED
INFO: Content type analysis: ENABLED
```

Or:
```
INFO: Using SIMPLE query (legacy mode)
```

### Performance Comparison
| Configuration | Avg Response Time | Memory Usage | Response Size |
|--------------|-------------------|--------------|---------------|
| All Enabled  | 1.96s             | ~45MB        | ~8KB          |
| All Disabled | 1.12s             | ~32MB        | ~5KB          |

### Common Issues

**Problem:** API returns 500 error after enabling features
**Solution:** Check if migration 004 was applied (`has_video`, `has_media` columns exist)
```bash
psql -d analytic_bot -c "\d posts" | grep has_video
```

**Problem:** Recommendations unchanged after toggling flags
**Solution:** Restart API server to reload environment variables
```bash
docker-compose restart api
# or
systemctl restart analyticbot-api
```

**Problem:** Query timeout with advanced features
**Solution:** Disable time weighting first, then content analysis
```bash
ENABLE_TIME_WEIGHTING=false
ENABLE_CONTENT_TYPE_ANALYSIS=false
```

---

## Testing Flag Combinations

Run comprehensive tests with different flag combinations:

```bash
# Test all enabled
./scripts/test_phase3.sh --all-enabled

# Test all disabled
./scripts/test_phase3.sh --all-disabled

# Test specific combination
ENABLE_ADVANCED_RECOMMENDATIONS=true \
ENABLE_TIME_WEIGHTING=false \
ENABLE_CONTENT_TYPE_ANALYSIS=true \
./scripts/test_phase3.sh
```

---

## Rollback Procedures

### Immediate Rollback (< 1 minute)
1. Set `ENABLE_ADVANCED_RECOMMENDATIONS=false` in environment
2. Restart API service
3. Verify `/health` endpoint responds
4. Test sample recommendation request

### Partial Rollback (< 2 minutes)
1. Keep `ENABLE_ADVANCED_RECOMMENDATIONS=true`
2. Disable specific features:
   - `ENABLE_TIME_WEIGHTING=false` for time-weighting issues
   - `ENABLE_CONTENT_TYPE_ANALYSIS=false` for content-type issues
3. Restart API service
4. Monitor performance metrics

### Code Rollback (if flags insufficient)
1. Git revert to previous commit
2. Rebuild and redeploy
3. Run database rollback: `infra/db/migrations/004_rollback.sql`

---

## Version History

- **v1.0** (2025-01-XX): Initial feature flags implementation
  - Phase 3 of recommendation system enhancement
  - Three-tier flag system (master + two feature-specific)
  - Backward-compatible simple query fallback

---

## Related Documentation

- [Phase 1: Database Schema](../docs/phase1_completion_report.md)
- [Phase 2: Backend Testing](../docs/phase2_completion_report.md)
- [Phase 3: Safety Measures](../docs/phase3_completion_report.md)
- [Migration 004](../infra/db/migrations/004_add_post_content_type_detection.sql)
- [API Documentation](../docs/api_best_times_endpoint.md)

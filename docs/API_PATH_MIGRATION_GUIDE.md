# API Path Migration Guide

## Overview
The API has been refactored from the old `/api/v2/analytics/channels/...` structure to a new domain-separated architecture.

## New Architecture

The new API structure follows clean architecture principles with 6 focused domain routers:

1. **Live Analytics** - `/analytics/live/*` - Real-time streaming data
2. **Alert Management** - `/analytics/alerts/*` - Alert configuration and management
3. **Core Statistics** - `/statistics/core/*` - Historical statistical data
4. **Statistical Reports** - `/statistics/reports/*` - Aggregated statistical reports
5. **Engagement Insights** - `/insights/engagement/*` - Audience engagement analysis
6. **Predictive AI/ML** - `/insights/predictive/*` - ML-powered predictions and recommendations

## Path Migration Mapping

### ✅ Already Updated in Frontend

| Old Path (v2) | New Path | Status | Router |
|--------------|----------|--------|--------|
| `/api/v2/analytics/channels/{id}/best-times` | `/insights/predictive/best-times/{id}` | ✅ Updated | insights_predictive_router.py |
| `/api/v2/analytics/channels/{id}/post-dynamics` | `/analytics/post-dynamics/{id}` | ✅ Updated | analytics_post_dynamics_router.py |
| `/api/v2/analytics/channels/{id}/top-posts` | `/analytics/top-posts/{id}` | ✅ Updated | analytics_post_dynamics_router.py |
| `/api/v2/analytics/channels/{id}/engagement` | `/insights/engagement/channels/{id}/engagement` | ✅ Updated | insights_engagement_router.py |

### ⚠️ Needs Update in Frontend

| Old Path (v2) | New Path | Component | Router |
|--------------|----------|-----------|--------|
| `/api/v2/analytics/channels/{id}/overview` | `/statistics/core/overview/{id}` | client.js, hooks | statistics_core_router.py |
| `/api/v2/analytics/channels/{id}/growth` | `/statistics/core/growth/{id}` | client.js, hooks | statistics_core_router.py |
| `/api/v2/analytics/channels/{id}/reach` | `/statistics/core/reach/{id}` | client.js | statistics_core_router.py |
| `/api/v2/analytics/channels/{id}/real-time` | `/analytics/live/stream/{id}` | client.js | analytics_live_router.py |
| `/api/v2/analytics/channels/{id}/alerts` | `/analytics/alerts/channel/{id}` | client.js, hooks | analytics_alerts_router.py |
| `/api/v2/analytics/channels/{id}/export/*` | `/exports/{format}/*/{id}` | client.js | exports_router.py |
| `/api/v2/analytics/channels/{id}/trends` | `/insights/engagement/trending/{id}` | hooks | insights_engagement_router.py |
| `/api/v2/analytics/channels/{id}/performance` | `/statistics/reports/performance/{id}` | hooks | statistics_reports_router.py |

## Query Parameter Changes

### Date Ranges
- **Old**: `?from=2024-01-01T00:00:00Z&to=2024-01-31T23:59:59Z`
- **New**: `?period=30d` (options: 24h, 7d, 30d, 90d)

### Time Windows
- **Old**: Not standardized
- **New**: `?window=D` (options: H=Hourly, D=Daily, W=Weekly)

## Files Requiring Updates

### High Priority (User-facing features)
1. ✅ `apps/frontend/src/store/appStore.js` - Main analytics fetches (4 functions updated)
2. ⚠️ `apps/frontend/src/api/client.js` - API client methods (~7 endpoints)
3. ⚠️ `apps/frontend/src/hooks/useUnifiedAnalytics.js` - Analytics hook (~6 endpoints)
4. ⚠️ `apps/frontend/src/utils/apiClient.js` - Alternative API client (~4 endpoints)

### Medium Priority (Background features)
5. ⚠️ `apps/frontend/src/utils/offlineStorage.js` - Cache synchronization (1 endpoint)

### Low Priority (Testing)
6. `apps/frontend/src/__mocks__/api/handlers.js` - Mock handlers for tests

## Testing Checklist

After updating paths, test these features:

- [ ] Post Dynamics Chart loads without 404 errors
- [ ] Best Time Recommender displays predictions
- [ ] Top Posts Table populates correctly
- [ ] Engagement Metrics load properly
- [ ] Channel Overview dashboard shows data
- [ ] Real-time analytics stream works
- [ ] Export functionality generates files
- [ ] No console errors about missing endpoints

## Implementation Strategy

1. **Phase 1: Core Analytics** (✅ COMPLETE)
   - Update appStore.js main fetch functions
   - Test post dynamics, best times, top posts, engagement

2. **Phase 2: Dashboard & Overview** (⏳ NEXT)
   - Update client.js getChannelAnalytics method
   - Update useUnifiedAnalytics hook
   - Test channel overview dashboard

3. **Phase 3: Real-time & Exports** (📋 TODO)
   - Update real-time analytics paths
   - Update export functionality
   - Update alert management paths

4. **Phase 4: Cleanup** (📋 TODO)
   - Update mock handlers for tests
   - Update offline storage sync
   - Remove any remaining v2 references

## Notes

- All new endpoints require authentication (JWT token in headers)
- Caching is implemented at the API level with ETag support
- Mock data is only returned when `dataSource='mock'`, never as API fallback
- Period-based queries are preferred over explicit date ranges for better caching

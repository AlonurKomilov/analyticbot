# Legacy Analytics Endpoint Analysis - Detailed Mapping

## Summary of Legacy Patterns Used by Frontend

Based on the comprehensive scan, here are **ALL** the legacy `/analytics/v2/*` and `/api/v2/analytics/*` patterns currently being called by the frontend:

---

## 📊 LEGACY PATTERNS CALLED BY FRONTEND

### 🔴 Pattern 1: `/analytics/v2/*` (Direct v2 calls)
**Found in:** `apps/frontend/src/services/authAwareAPI.js`

| Legacy Frontend Call | Current Backend Router | Status |
|---------------------|------------------------|---------|
| `GET /analytics/v2/post-dynamics/{channelId}` | ✅ `analytics_core_router.py` → `/analytics/core/overview/{channel_id}` | **AVAILABLE** |
| `GET /analytics/v2/top-posts/{channelId}` | ✅ `analytics_core_router.py` → `/analytics/core/channels/{channel_id}/top-posts` | **AVAILABLE** |
| `GET /analytics/v2/best-time/{channelId}` | ❌ **NO CURRENT EQUIVALENT** | **MISSING** |
| `GET /analytics/v2/engagement-metrics/{channelId}` | ❌ **NO CURRENT EQUIVALENT** | **MISSING** |

---

### 🔴 Pattern 2: `/api/v2/analytics/advanced/*` (Advanced analytics)
**Found in:** `apps/frontend/src/utils/apiClient.js`, `apps/frontend/src/providers/DataProvider.js`

| Legacy Frontend Call | Current Backend Router | Status |
|---------------------|------------------------|---------|
| `GET /api/v2/analytics/advanced/dashboard/{channelId}` | ✅ `analytics_core_router.py` → `/analytics/core/dashboard/{channel_id}` | **AVAILABLE** |
| `GET /api/v2/analytics/advanced/metrics/real-time/{channelId}` | ✅ `analytics_realtime_router.py` → `/analytics/realtime/metrics/{channel_id}` | **AVAILABLE** |
| `GET /api/v2/analytics/advanced/alerts/check/{channelId}` | ✅ `analytics_alerts_router.py` → `/analytics/alerts/check/{channel_id}` | **AVAILABLE** |
| `GET /api/v2/analytics/advanced/recommendations/{channelId}` | ✅ `analytics_realtime_router.py` → `/analytics/realtime/recommendations/{channel_id}` | **AVAILABLE** |
| `GET /api/v2/analytics/advanced/performance/score/{channelId}` | ✅ `analytics_realtime_router.py` → `/analytics/realtime/performance/{channel_id}` | **AVAILABLE** |

---

### 🔴 Pattern 3: `/api/v2/analytics/channels/*` (Channel-specific analytics)
**Found in:** `apps/frontend/src/utils/apiClient.js`, `apps/frontend/src/api/client.js`, `apps/frontend/src/store/appStore.js`, `apps/frontend/src/hooks/*.js`

| Legacy Frontend Call | Current Backend Router | Status |
|---------------------|------------------------|---------|
| `GET /api/v2/analytics/channels/{channelId}/overview` | ✅ `analytics_core_router.py` → `/analytics/core/overview/{channel_id}` | **AVAILABLE** |
| `GET /api/v2/analytics/channels/{channelId}/growth` | ✅ `analytics_core_router.py` → `/analytics/core/channels/{channel_id}/growth` | **AVAILABLE** |
| `GET /api/v2/analytics/channels/{channelId}/reach` | ✅ `analytics_realtime_router.py` → `/analytics/realtime/channels/{channel_id}/reach` | **AVAILABLE** |
| `GET /api/v2/analytics/channels/{channelId}/top-posts` | ✅ `analytics_core_router.py` → `/analytics/core/channels/{channel_id}/top-posts` | **AVAILABLE** |
| `GET /api/v2/analytics/channels/{channelId}/trending` | ✅ `analytics_insights_router.py` → `/analytics/insights/channels/{channel_id}/trending` | **AVAILABLE** |
| `GET /api/v2/analytics/channels/{channelId}/post-dynamics` | ✅ `analytics_core_router.py` → `/analytics/core/overview/{channel_id}` | **AVAILABLE** |
| `GET /api/v2/analytics/channels/{channelId}/performance` | ✅ `analytics_realtime_router.py` → `/analytics/realtime/performance/{channel_id}` | **AVAILABLE** |
| `GET /api/v2/analytics/channels/{channelId}/alerts` | ✅ `analytics_alerts_router.py` → `/analytics/alerts/check/{channel_id}` | **AVAILABLE** |
| `GET /api/v2/analytics/channels/{channelId}/real-time` | ✅ `analytics_realtime_router.py` → `/analytics/realtime/live-metrics/{channel_id}` | **AVAILABLE** |
| `GET /api/v2/analytics/channels/{channelId}/export/{type}` | ✅ `exports_v2.py` → `/exports/csv/{type}/{channel_id}` or `/exports/png/{type}/{channel_id}` | **USE EXPORTS ROUTER** |
| `GET /api/v2/analytics/channels/{channelId}/best-times` | ❌ **NO CURRENT EQUIVALENT** | **MISSING** |
| `GET /api/v2/analytics/channels/{channelId}/engagement` | ❌ **NO CURRENT EQUIVALENT** | **MISSING** |
| `GET /api/v2/analytics/channels/{channelId}/trends` | ❌ **NO CURRENT EQUIVALENT** | **MISSING** |

---

### 🔴 Pattern 4: `/api/v2/analytics/*` (Global analytics)
**Found in:** `apps/frontend/src/hooks/useRealTimeAnalytics.js`

| Legacy Frontend Call | Current Backend Router | Status |
|---------------------|------------------------|---------|
| `POST /api/v2/analytics/channel-data` | ✅ `analytics_insights_router.py` → `POST /analytics/insights/channel-data` | **AVAILABLE** |
| `POST /api/v2/analytics/metrics/performance` | ✅ `analytics_insights_router.py` → `POST /analytics/insights/metrics/performance` | **AVAILABLE** |
| `GET /api/v2/analytics/trends/top-posts` | ✅ `analytics_insights_router.py` → `GET /analytics/insights/trends/posts/top` | **AVAILABLE** |

---

## 🎯 ROUTER MAPPING SUMMARY

### ✅ **Analytics Core Router** (`analytics_core_router.py`) - `/analytics/core/*`
**Handles 7 legacy patterns (28%)**
- Overview/Dashboard functionality
- Top posts
- Channel growth
- Post dynamics

### ✅ **Analytics Realtime Router** (`analytics_realtime_router.py`) - `/analytics/realtime/*`
**Handles 6 legacy patterns (24%)**
- Real-time metrics
- Performance scoring
- Recommendations
- Live data monitoring
- Channel reach

### ✅ **Analytics Insights Router** (`analytics_insights_router.py`) - `/analytics/insights/*`
**Handles 4 legacy patterns (16%)**
- Channel data analysis
- Performance metrics
- Trending analysis
- Top posts trends

### ✅ **Analytics Alerts Router** (`analytics_alerts_router.py`) - `/analytics/alerts/*`
**Handles 2 legacy patterns (8%)**
- Alert checking
- Alert management

### ✅ **Exports Router** (`exports_v2.py`) - `/exports/*`
**Handles 1 legacy pattern (4%)**
- Data exports (CSV, PNG)

---

## 🚨 MISSING ENDPOINTS (5 patterns - 20%)

These legacy endpoints are being called by the frontend but **DO NOT exist** in the current backend:

### 🔍 **Should be in Analytics Core Router:**
1. `GET /analytics/v2/best-time/{channelId}` → **SHOULD MAP TO:** `/analytics/core/channels/{channel_id}/best-times`
2. `GET /api/v2/analytics/channels/{channelId}/best-times` → **SHOULD MAP TO:** `/analytics/core/channels/{channel_id}/best-times`
3. `GET /analytics/v2/engagement-metrics/{channelId}` → **SHOULD MAP TO:** `/analytics/core/channels/{channel_id}/engagement`
4. `GET /api/v2/analytics/channels/{channelId}/engagement` → **SHOULD MAP TO:** `/analytics/core/channels/{channel_id}/engagement`

### 🔍 **Should be in Analytics Insights Router:**
5. `GET /api/v2/analytics/channels/{channelId}/trends` → **SHOULD MAP TO:** `/analytics/insights/channels/{channel_id}/trends`

---

## 📁 FRONTEND FILES USING LEGACY PATTERNS

### **Core Service Files (HIGHEST PRIORITY)**
1. `apps/frontend/src/services/authAwareAPI.js` - Main API service using direct `/analytics/v2/*` calls
2. `apps/frontend/src/utils/apiClient.js` - Utility client with extensive `/api/v2/analytics/*` usage
3. `apps/frontend/src/api/client.js` - Unified API client with batch analytics calls

### **State Management (HIGH PRIORITY)**
4. `apps/frontend/src/store/appStore.js` - App store using legacy channel analytics
5. `apps/frontend/src/hooks/useRealTimeAnalytics.js` - Real-time hooks using global analytics
6. `apps/frontend/src/hooks/useUnifiedAnalytics.js` - Unified analytics hooks

### **Data Providers (MEDIUM PRIORITY)**
7. `apps/frontend/src/providers/DataProvider.js` - Data provider with advanced analytics

### **Configuration & Mocks (LOW PRIORITY)**
8. `apps/frontend/src/config/mockConfig.js` - Mock configuration endpoints
9. `apps/frontend/src/__mocks__/api/handlers.js` - Test API handlers
10. `apps/frontend/src/__mocks__/services/mockApiClient.js` - Mock API client

---

## 🛠️ MIGRATION STRATEGY

### **Phase 1: Implement Missing Endpoints (Week 1)**
Add these 3 missing endpoints to the backend:
- `GET /analytics/core/channels/{channel_id}/best-times`
- `GET /analytics/core/channels/{channel_id}/engagement`  
- `GET /analytics/insights/channels/{channel_id}/trends`

### **Phase 2: Update Core Services (Week 2)**
Update these critical files:
- `authAwareAPI.js` - Replace `/analytics/v2/*` with `/analytics/core/*`
- `apiClient.js` - Replace `/api/v2/analytics/*` with domain-specific endpoints
- `client.js` - Update batch calls to use Clean 5-Router Architecture

### **Phase 3: Update State & Hooks (Week 3)**
- Update all store and hook files
- Test frontend functionality
- Verify data consistency

### **Phase 4: Clean Up (Week 4)**
- Update mocks and configuration
- Remove legacy endpoint references
- Update documentation

---

## 🎯 IMMEDIATE ACTION ITEMS

1. **Backend:** Implement 3 missing endpoints in appropriate routers
2. **Frontend:** Start with `authAwareAPI.js` - this affects the most components
3. **Testing:** Set up endpoint monitoring to track migration progress
4. **Documentation:** Update API client documentation with new endpoint structure

This analysis shows that **80% of legacy patterns have current equivalents**, but the frontend needs to be systematically migrated to the Clean 5-Router Architecture to properly utilize the modern backend structure.
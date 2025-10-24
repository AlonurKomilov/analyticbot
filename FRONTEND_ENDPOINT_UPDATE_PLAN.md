# Frontend Endpoint Update Plan - Direct Code Changes

**Goal:** Update ALL frontend code to use new organized API endpoints directly  
**Date:** October 22, 2025  
**Strategy:** Replace old endpoints in code, remove migration helper, clean URLs  

---

## 🎯 Current State Analysis

### Issues Found:
1. ❌ **Old AI endpoints** still in code (`/ai-services`, `/insights/predictive`, etc.)
2. ❌ **Versioned endpoints** (`/api/v1/`, `/api/v2/`) - Should remove version prefixes
3. ❌ **Scattered analytics** endpoints (`/analytics/`, `/insights/`, `/statistics/`)
4. ❌ **Mixed patterns** (some with `/api/`, some without)

### Goal State:
✅ **Clean, organized endpoints** without versions  
✅ **Consistent structure** across all files  
✅ **Match new backend** organization  

---

## 📊 Endpoint Mapping Table

### AI Domain Endpoints

| Current (Old) | New (Organized) | Files Affected | Priority |
|---------------|-----------------|----------------|----------|
| `/ai-services/*` | `/ai/services/*` | aiServicesAPI.ts | HIGH |
| `/insights/predictive/*` | `/analytics/predictive/*` | aiServicesAPI.ts (8 locations) | HIGH |
| `/strategy/*` | `/ai/strategy/*` | - | MEDIUM |
| `/competitive/*` | `/ai/competitive/*` | - | MEDIUM |
| `/optimization/*` | `/ai/optimization/*` | RecentActivity.tsx | MEDIUM |

### Analytics Domain Endpoints

| Current (Old) | New (Organized) | Files Affected | Priority |
|---------------|-----------------|----------------|----------|
| `/api/v2/analytics/*` | `/analytics/*` | client.ts (13 locations) | **CRITICAL** |
| `/api/v1/superadmin/*` | `/admin/super/*` | useUnifiedAnalytics.ts, useAdminAPI.ts | HIGH |
| `/analytics/live/*` | `/analytics/realtime/*` | - | MEDIUM |
| `/analytics/post-dynamics/*` | `/analytics/posts/dynamics/*` | authAwareAPI.ts | MEDIUM |
| `/statistics/core/*` | `/analytics/historical/*` | - | MEDIUM |
| `/insights/engagement/*` | `/analytics/engagement/*` | - | MEDIUM |
| `/insights/orchestration/*` | `/analytics/orchestration/*` | - | MEDIUM |
| `/ml/*` | `/analytics/ml/*` | - | LOW |
| `/trends/*` | `/analytics/trends/*` | - | LOW |

### Admin & Other Endpoints

| Current (Old) | New (Organized) | Files Affected | Priority |
|---------------|-----------------|----------------|----------|
| `/api/v1/superadmin/*` | `/admin/super/*` | useUnifiedAnalytics.ts, useAdminAPI.ts | HIGH |
| `/superadmin/*` | `/admin/super/*` | - | HIGH |
| `/api/content-protection/*` | `/content/protection/*` | TheftDetection.tsx | MEDIUM |
| `/content-protection/*` | `/content/protection/*` | - | MEDIUM |
| `/api/payments` | `/payments` | paymentAPI.ts | MEDIUM |
| `/payment/*` | `/payments/*` | - | MEDIUM |

### Remove Version Prefixes

| Current (Versioned) | New (No Version) | Reason |
|---------------------|------------------|--------|
| `/api/v1/*` | Remove `/api/v1/` prefix | Not using API versioning |
| `/api/v2/analytics/*` | `/analytics/*` | Simplify, no version needed |
| `/api/mobile/v1/*` | `/mobile/*` | Consistent structure |

---

## 📁 Files to Update (by Priority)

### 🔴 **CRITICAL Priority - Core API Client**

#### 1. `apps/frontend/src/api/client.ts` (13 changes)
**Impact:** All API calls go through this file!

**Changes needed:**
```typescript
// REMOVE these imports (migration helper no longer needed)
- import { migrateEndpoint } from './endpointMigration';

// UPDATE timeout configuration
- '/api/v2/': 25000,
+ '/analytics/': 25000,

// UPDATE request method (remove migration)
async request<T>(endpoint: string, ...): Promise<T> {
-  const migratedEndpoint = migrateEndpoint(endpoint);
-  const url = `${this.config.baseURL}${migratedEndpoint}`;
+  const url = `${this.config.baseURL}${endpoint}`;
}

// UPDATE getBatchAnalytics method (lines 462-465)
- this.get(`/api/v2/analytics/channels/${id}/overview?...`),
+ this.get(`/analytics/channels/${id}/overview?...`),

- this.get(`/api/v2/analytics/channels/${id}/growth?...`),
+ this.get(`/analytics/channels/${id}/growth?...`),

- this.get(`/api/v2/analytics/channels/${id}/reach?...`),
+ this.get(`/analytics/channels/${id}/reach?...`),

- this.get(`/api/v2/analytics/channels/${id}/top-posts?...`),
+ this.get(`/analytics/channels/${id}/top-posts?...`),

// UPDATE getRealTimeAnalytics method (line 486)
- return await this.get(`/api/v2/analytics/channels/${id}/real-time`);
+ return await this.get(`/analytics/channels/${id}/realtime`);

// UPDATE getAlerts method (line 498)
- return await this.get(`/api/v2/analytics/channels/${id}/alerts`);
+ return await this.get(`/analytics/alerts/${id}`);

// UPDATE getStorageFiles method (line 510)
- `/api/v1/media/storage-files?limit=${limit}&offset=${offset}`
+ `/media/storage-files?limit=${limit}&offset=${offset}`

// UPDATE exportData method (line 523)
- `/api/v2/analytics/channels/${id}/export/${type}?...`
+ `/analytics/channels/${id}/export/${type}?...`
```

**Estimated time:** 30 minutes  
**Lines to change:** ~15 lines  

---

### 🟠 **HIGH Priority - Service Files**

#### 2. `apps/frontend/src/services/aiServicesAPI.ts` (13 changes)
**Impact:** All AI services

**Changes needed:**
```typescript
// UPDATE base constant (line 12)
- const AI_SERVICES_BASE = '/ai-services';
+ const AI_SERVICES_BASE = '/ai/services';

// UPDATE predictive endpoints (8 locations)
- '/insights/predictive/forecast'
+ '/analytics/predictive/forecast'

- '/insights/predictive/intelligence/contextual'
+ '/analytics/predictive/intelligence/contextual'

- '/insights/predictive/intelligence/temporal'
+ '/analytics/predictive/intelligence/temporal'

- '/insights/predictive/intelligence/cross-channel'
+ '/analytics/predictive/intelligence/cross-channel'

- '/insights/predictive/intelligence/health'
+ '/analytics/predictive/intelligence/health'

// Alert endpoints already correct (analytics/alerts/*)
// NO changes needed for lines 274-391
```

**Estimated time:** 20 minutes  
**Lines to change:** ~9 lines  

---

#### 3. `apps/frontend/src/services/analyticsService.ts` (5 changes)
**Impact:** Analytics data fetching

**Changes needed:**
```typescript
// UPDATE all analytics endpoints (lines 178-224)
- `/analytics/overview/${channelId}`
+ `/analytics/channels/${channelId}/overview`

- `/analytics/post-dynamics/${channelId}`
+ `/analytics/channels/${channelId}/posts/dynamics`

- `/analytics/top-posts/${channelId}`
+ `/analytics/channels/${channelId}/top-posts`

- `/analytics/engagement/${channelId}`
+ `/analytics/channels/${channelId}/engagement`

- `/analytics/best-time/${channelId}`
+ `/analytics/channels/${channelId}/best-times`
```

**Estimated time:** 15 minutes  
**Lines to change:** ~5 lines  

---

#### 4. `apps/frontend/src/services/authAwareAPI.ts` (5 changes)
**Impact:** Authenticated API calls

**Changes needed:**
```typescript
// UPDATE analytics endpoints (lines 129-147)
- `/analytics/overview/${channelId}`
+ `/analytics/channels/${channelId}/overview`

- `/analytics/v2/post-dynamics/${channelId}?period=${period}`
+ `/analytics/channels/${channelId}/posts/dynamics?period=${period}`

- `/analytics/v2/top-posts/${channelId}`
+ `/analytics/channels/${channelId}/top-posts`

- `/analytics/v2/best-time/${channelId}?timeframe=${timeframe}`
+ `/analytics/channels/${channelId}/best-times?timeframe=${timeframe}`

- `/analytics/v2/engagement-metrics/${channelId}?period=${period}`
+ `/analytics/channels/${channelId}/engagement?period=${period}`
```

**Estimated time:** 15 minutes  
**Lines to change:** ~5 lines  

---

#### 5. `apps/frontend/src/services/paymentAPI.ts` (1 change)
**Impact:** Payment processing

**Changes needed:**
```typescript
// UPDATE base URL (line 42)
- constructor(baseURL: string = '/api/payments') {
+ constructor(baseURL: string = '/payments') {
```

**Estimated time:** 2 minutes  
**Lines to change:** 1 line  

---

### 🟡 **MEDIUM Priority - Hooks**

#### 6. `apps/frontend/src/hooks/useUnifiedAnalytics.ts` (10 changes)
**Impact:** Analytics data hooks

**Changes needed:**
```typescript
// UPDATE all API calls (lines 186-221)
- apiClient.get(`/api/v2/analytics/channels/${id}/overview?period=30`)
+ apiClient.get(`/analytics/channels/${id}/overview?period=30`)

- apiClient.get(`/api/v2/analytics/channels/${id}/growth?period=30`)
+ apiClient.get(`/analytics/channels/${id}/growth?period=30`)

- apiClient.get(`/api/v2/analytics/channels/${id}/engagement?period=30`)
+ apiClient.get(`/analytics/channels/${id}/engagement?period=30`)

- apiClient.get(`/api/v2/analytics/channels/${id}/performance?period=30`)
+ apiClient.get(`/analytics/channels/${id}/performance?period=30`)

- apiClient.get(`/api/v2/analytics/channels/${id}/trends?period=7`)
+ apiClient.get(`/analytics/channels/${id}/trends?period=7`)

- apiClient.get(`/api/v2/analytics/channels/${id}/alerts`)
+ apiClient.get(`/analytics/alerts/${id}`)

// UPDATE admin endpoints
- apiClient.get(`/api/v1/superadmin/users`)
+ apiClient.get(`/admin/super/users`)

- apiClient.get(`/api/v1/superadmin/system-status`)
+ apiClient.get(`/admin/super/system-status`)

// UPDATE mobile endpoint
- apiClient.post('/api/mobile/v1/analytics/quick', {...})
+ apiClient.post('/mobile/analytics/quick', {...})
```

**Estimated time:** 20 minutes  
**Lines to change:** ~10 lines  

---

#### 7. `apps/frontend/src/hooks/useRealTimeAnalytics.ts` (5 changes)
**Impact:** Real-time analytics

**Changes needed:**
```typescript
// UPDATE endpoints (lines 102-333)
- apiClient.post('/api/v2/analytics/channel-data', {...})
+ apiClient.post('/analytics/channel-data', {...})

- apiClient.post('/api/mobile/v1/analytics/quick', {...})
+ apiClient.post('/mobile/analytics/quick', {...})

- apiClient.post('/api/v2/analytics/metrics/performance', {...})
+ apiClient.post('/analytics/metrics/performance', {...})

- apiClient.get('/api/v2/analytics/trends/top-posts')
+ apiClient.get('/analytics/trends/top-posts')
```

**Estimated time:** 10 minutes  
**Lines to change:** ~5 lines  

---

#### 8. `apps/frontend/src/hooks/useAdminAPI.ts` (1 change)
**Impact:** Admin operations

**Changes needed:**
```typescript
// UPDATE endpoint (line 82)
- const response = await fetch(`/api/v1/superadmin/${endpoint}`, {...})
+ const response = await fetch(`/admin/super/${endpoint}`, {...})
```

**Estimated time:** 5 minutes  
**Lines to change:** 1 line  

---

#### 9. `apps/frontend/src/hooks/useUserChannels.ts` (3 changes)
**Impact:** Channel management

**Changes needed:**
```typescript
// UPDATE endpoints (lines 76-148)
- (await (dataProvider as any)._makeRequest('/analytics/channels'))
+ (await (dataProvider as any)._makeRequest('/channels'))

- (await (dataProvider as any)._makeRequest('/analytics/channels', {...})
+ (await (dataProvider as any)._makeRequest('/channels', {...})

- (await (dataProvider as any)._makeRequest(`/analytics/channels/${channelId}`))
+ (await (dataProvider as any)._makeRequest(`/channels/${channelId}`))
```

**Estimated time:** 10 minutes  
**Lines to change:** 3 lines  

---

### 🟢 **LOW Priority - Components & Pages**

#### 10. `apps/frontend/src/components/content/TheftDetection.tsx` (3 changes)
**Impact:** Content protection features

**Changes needed:**
```typescript
// UPDATE commented endpoints (lines 100, 120, 171)
- // fetch('/api/content-protection/detection/history')
+ // fetch('/content/protection/detection/history')

- // fetch('/api/content-protection/detection/stats')
+ // fetch('/content/protection/detection/stats')

- // apiClient.post('/api/v1/content-protection/detection/scan', {...})
+ // apiClient.post('/content/protection/detection/scan', {...})
```

**Estimated time:** 5 minutes  
**Lines to change:** 3 lines  

---

#### 11. `apps/frontend/src/components/features/ai-services/ContentOptimizer/RecentActivity.tsx` (1 change)
**Impact:** Content optimization

**Changes needed:**
```typescript
// UPDATE endpoint (line 47)
- // fetch('/api/optimizations/recent')
+ // fetch('/ai/optimization/recent')
```

**Estimated time:** 2 minutes  
**Lines to change:** 1 line  

---

#### 12. `apps/frontend/src/pages/AdminDashboard.tsx` (3 changes)
**Impact:** Admin dashboard

**Changes needed:**
```typescript
// UPDATE endpoints (lines 91-122)
- fetch('/api/analytics/admin/system-stats', {...})
+ fetch('/admin/analytics/system-stats', {...})

- fetch('/api/analytics/admin/all-channels', {...})
+ fetch('/admin/analytics/all-channels', {...})

- fetch(`/api/analytics/admin/channels/${channelId}`, {...})
+ fetch(`/admin/analytics/channels/${channelId}`, {...})
```

**Estimated time:** 10 minutes  
**Lines to change:** 3 lines  

---

#### 13. `apps/frontend/src/utils/offlineStorage.ts` (1 change)
**Impact:** Offline caching

**Changes needed:**
```typescript
// UPDATE endpoint (line 401)
- apiClient.get(`/api/v2/analytics/channels/${channelId}/overview`)
+ apiClient.get(`/analytics/channels/${channelId}/overview`)
```

**Estimated time:** 2 minutes  
**Lines to change:** 1 line  

---

#### 14. `apps/frontend/src/utils/systemHealthCheck.ts` (4 changes)
**Impact:** System health monitoring

**Changes needed:**
```typescript
// UPDATE insights endpoints (lines 328-377)
- fetch(`${API_BASE_URL}/insights/dashboard/overview/demo_channel`, {...})
+ fetch(`${API_BASE_URL}/analytics/dashboard/overview/demo_channel`, {...})

- '/insights/content/'
+ '/analytics/content/'

- '/insights/audience/'
+ '/analytics/audience/'

- '/insights/predictive/best-times/demo_channel'
+ '/analytics/predictive/best-times/demo_channel'
```

**Estimated time:** 10 minutes  
**Lines to change:** 4 lines  

---

### ⚪ **CLEANUP - Remove Migration Helper**

#### 15. Delete `apps/frontend/src/api/endpointMigration.ts`
**Impact:** No longer needed

**Action:**
```bash
rm apps/frontend/src/api/endpointMigration.ts
```

**Estimated time:** 1 minute  

---

## 📋 Implementation Checklist

### Phase 1: Critical Files (Day 1 - 2 hours)
- [ ] **1. Update `api/client.ts`** (30 min)
  - Remove migration helper import
  - Update 13 endpoints
  - Test import/export
  
### Phase 2: High Priority Services (Day 1 - 1.5 hours)
- [ ] **2. Update `services/aiServicesAPI.ts`** (20 min)
- [ ] **3. Update `services/analyticsService.ts`** (15 min)
- [ ] **4. Update `services/authAwareAPI.ts`** (15 min)
- [ ] **5. Update `services/paymentAPI.ts`** (2 min)

### Phase 3: Hooks (Day 1 - 1 hour)
- [ ] **6. Update `hooks/useUnifiedAnalytics.ts`** (20 min)
- [ ] **7. Update `hooks/useRealTimeAnalytics.ts`** (10 min)
- [ ] **8. Update `hooks/useAdminAPI.ts`** (5 min)
- [ ] **9. Update `hooks/useUserChannels.ts`** (10 min)

### Phase 4: Components & Utils (Day 2 - 1 hour)
- [ ] **10. Update `components/content/TheftDetection.tsx`** (5 min)
- [ ] **11. Update `components/.../RecentActivity.tsx`** (2 min)
- [ ] **12. Update `pages/AdminDashboard.tsx`** (10 min)
- [ ] **13. Update `utils/offlineStorage.ts`** (2 min)
- [ ] **14. Update `utils/systemHealthCheck.ts`** (10 min)

### Phase 5: Cleanup (Day 2 - 10 minutes)
- [ ] **15. Delete `api/endpointMigration.ts`** (1 min)
- [ ] **16. Run TypeScript compiler** (5 min)
- [ ] **17. Fix any import errors** (5 min)

### Phase 6: Testing (Day 2 - 2 hours)
- [ ] Run build: `npm run build`
- [ ] Check for TypeScript errors
- [ ] Test in development: `npm run dev`
- [ ] Test each domain:
  - [ ] AI services endpoints
  - [ ] Analytics endpoints
  - [ ] Admin endpoints
  - [ ] Payment endpoints
  - [ ] Content protection endpoints
- [ ] Verify responses match expected format
- [ ] Check browser console for errors

---

## 🎯 Summary Statistics

**Total Files to Update:** 15 files  
**Total Lines to Change:** ~75 lines  
**Total Estimated Time:** 6 hours (including testing)  

**Breakdown by Type:**
- Remove version prefixes (`/api/v1/`, `/api/v2/`): ~35 changes
- Update AI endpoints: ~15 changes
- Update analytics endpoints: ~20 changes
- Update admin endpoints: ~5 changes

---

## ⚠️ Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Breaking changes** | Low | High | Backend has both old/new endpoints active |
| **TypeScript errors** | Medium | Low | Run compiler after each file |
| **Runtime errors** | Low | Medium | Test thoroughly in dev environment |
| **Missing endpoints** | Low | High | Verify each endpoint exists in backend |

---

## 🚀 Execution Order

**Recommended approach:**

1. **Start with `api/client.ts`** - This is the foundation
2. **Update services** - These are heavily used
3. **Update hooks** - These call services
4. **Update components** - These use hooks
5. **Delete migration helper** - No longer needed
6. **Test everything** - Verify all works

---

## ✅ Success Criteria

After completion:
- [ ] No `/api/v1/` or `/api/v2/` in codebase
- [ ] All endpoints match new backend structure
- [ ] No old endpoint names (`/ai-services`, `/insights/predictive`, etc.)
- [ ] TypeScript compiles without errors
- [ ] All features work in development
- [ ] No console errors
- [ ] Migration helper deleted

---

## 🔄 Rollback Plan

If issues occur:
1. **Git revert** to previous commit
2. Or keep migration helper temporarily
3. Fix issues file by file
4. Re-enable migration once stable

---

**Ready to start? Let's begin with Phase 1: Update `api/client.ts`!**

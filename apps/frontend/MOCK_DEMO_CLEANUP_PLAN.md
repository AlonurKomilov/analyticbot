# Mock/Demo Code Cleanup & Organization Plan

## 🎯 **OBJECTIVE**
Ensure all mock/demo code is properly isolated, only loads in demo mode, and maintains clean separation from production code.

---

## 📊 **CURRENT STATE ANALYSIS**

### ✅ **Already Properly Organized in `__mocks__/`**

```
apps/frontend/src/__mocks__/
├── aiServices/              # AI service mock data & logic
│   ├── aiServicesAPIService.js
│   ├── churnPredictor.js
│   ├── contentOptimizer.js
│   ├── predictiveAnalytics.js
│   ├── securityMonitor.js
│   ├── statsService.js
│   └── test-mock-data.js
├── analytics/               # Analytics mock data
│   ├── bestTime.js
│   ├── demoAPI.js
│   ├── engagementMetrics.js
│   ├── postDynamics.js
│   └── topPosts.js
├── api/                     # MSW (Mock Service Worker) handlers
│   ├── handlers.js
│   ├── index.js
│   └── server.js
├── channels/                # Channel mock data
│   └── channelData.js
├── components/              # Demo/Showcase components
│   ├── demo/
│   │   └── AnalyticsAdapterDemo.tsx  ✅
│   └── showcase/
│       └── tables/
│           ├── GenericTableDemo.tsx   ✅
│           └── UsersTableDemo.tsx     ✅
├── providers/               # Mock data providers
│   └── MockDataProvider.js
├── services/                # Mock service implementations
│   ├── ChurnPredictorService.tsx      ✅
│   ├── PredictiveAnalyticsService.tsx ✅
│   └── mockApiClient.js
├── system/                  # System mocks
└── user/                    # User mock data
```

### ⚠️ **Files OUTSIDE `__mocks__/` That Should Be Moved**

#### **Demo Components in Production Folders**
1. `apps/frontend/src/components/showcase/tables/PostsTableDemo.tsx`
   - **Action:** Move to `__mocks__/components/showcase/tables/`
   - **Reason:** Demo component should be in __mocks__

#### **Demo/Mock Utilities**
2. `apps/frontend/src/utils/demoUserUtils.js`
   - **Action:** Move to `__mocks__/utils/`
3. `apps/frontend/src/utils/testDemoFallback.js`
   - **Action:** Move to `__mocks__/utils/`
4. `apps/frontend/src/utils/__tests__/demoUserUtils.test.js`
   - **Action:** Move to `__mocks__/utils/__tests__/`
5. `apps/frontend/src/utils/__tests__/simpleDemoTest.js`
   - **Action:** Move to `__mocks__/utils/__tests__/`

#### **Mock Services**
6. `apps/frontend/src/services/storageMockService.js`
   - **Action:** Move to `__mocks__/services/`

#### **Mock Configuration**
7. `apps/frontend/src/config/mockConfig.js`
   - **Action:** Move to `__mocks__/config/`

---

## 🔍 **PRODUCTION CODE ANALYSIS**

### **Files Importing from `__mocks__/` (Need Review)**

#### ✅ **Properly Gated (Demo Mode Only)**

1. **`services/serviceFactory.js`** ✅ CORRECT
   ```javascript
   // Lines 49, 62, 73, 83, 93 - Dynamic imports in demo mode
   const mockClient = await import('../__mocks__/services/mockApiClient.js');
   ```
   - **Status:** ✅ Only loads when `dataSource === 'mock'`
   - **Action:** Keep as-is

2. **`services/analyticsService.js`** ✅ CORRECT
   ```javascript
   // Demo mode data imports
   import { DEFAULT_DEMO_CHANNEL_ID } from '../__mocks__/constants.js';
   import { mockAnalytics } from '../__mocks__/index.js';
   ```
   - **Status:** ✅ Used only in demo mode branches
   - **Action:** Keep as-is

3. **`test/` files** ✅ CORRECT
   - `test/AnalyticsDashboard.test.tsx`
   - `test/AnalyticsDashboardGolden.test.tsx`
   - `test/setup.js`
   - **Status:** ✅ Test files should use mocks
   - **Action:** Keep as-is

#### ⚠️ **Need Review - Potential Issues**

4. **`services/ContentOptimizerService.tsx`**
   ```typescript
   // Line 32
   import { mockContentOptimizer } from '../__mocks__/aiServices/contentOptimizer';
   ```
   - **Status:** ⚠️ Need to verify demo mode gating
   - **Action:** Audit usage, ensure gated by `dataSource`

5. **`services/SecurityMonitoringService.tsx`**
   ```typescript
   // Line 42
   import { mockSecurityMonitoring } from '../__mocks__/aiServices/securityMonitor';
   ```
   - **Status:** ⚠️ Need to verify demo mode gating
   - **Action:** Audit usage, ensure gated by `dataSource`

6. **`services/aiServicesAPI.js`**
   ```javascript
   // Line 8
   import { aiServicesStatsMock } from '../__mocks__/aiServices/statsService.js';
   ```
   - **Status:** ⚠️ Need to verify not used in real mode
   - **Action:** Audit usage

7. **`components/showcase/TablesShowcase.tsx`**
   ```typescript
   // Lines 24-25
   import UsersTableDemo from '../../__mocks__/components/showcase/tables/UsersTableDemo.jsx';
   import GenericTableDemo from '../../__mocks__/components/showcase/tables/GenericTableDemo.jsx';
   ```
   - **Status:** ⚠️ Showcase component - acceptable but verify demo-only
   - **Action:** Ensure component only shown in demo mode

8. **`components/features/ai-services/SecurityMonitoring/SecurityMonitoringPage.tsx`**
   ```typescript
   // Line 27
   import { mockSecurityThreatData } from '@/__mocks__/aiServices/securityMonitor.js';
   ```
   - **Status:** ⚠️ Production component importing mock data
   - **Action:** Review and ensure demo mode gating

9. **`components/analytics/.../hooks/useRecommenderLogic.js`**
   ```javascript
   import { DEFAULT_DEMO_CHANNEL_ID } from '../../../../__mocks__/constants.js';
   ```
   - **Status:** ⚠️ Hook importing from mocks
   - **Action:** Review usage context

10. **`components/analytics/.../hooks/usePostTableLogic.js`**
    ```javascript
    import { DEFAULT_DEMO_CHANNEL_ID } from '../../../../__mocks__/constants.js';
    ```
    - **Status:** ⚠️ Hook importing from mocks
    - **Action:** Review usage context

---

## 🎯 **ACTION PLAN**

### **Phase 1: Move Demo Files to `__mocks__/`**

#### **Step 1.1: Create Missing Directories**
```bash
mkdir -p apps/frontend/src/__mocks__/utils/__tests__
mkdir -p apps/frontend/src/__mocks__/config
```

#### **Step 1.2: Move Demo Components**
```bash
# Move PostsTableDemo
git mv apps/frontend/src/components/showcase/tables/PostsTableDemo.tsx \
       apps/frontend/src/__mocks__/components/showcase/tables/
```

#### **Step 1.3: Move Demo Utils**
```bash
# Move utils
git mv apps/frontend/src/utils/demoUserUtils.js \
       apps/frontend/src/__mocks__/utils/

git mv apps/frontend/src/utils/testDemoFallback.js \
       apps/frontend/src/__mocks__/utils/

# Move tests
git mv apps/frontend/src/utils/__tests__/demoUserUtils.test.js \
       apps/frontend/src/__mocks__/utils/__tests__/

git mv apps/frontend/src/utils/__tests__/simpleDemoTest.js \
       apps/frontend/src/__mocks__/utils/__tests__/
```

#### **Step 1.4: Move Mock Services**
```bash
git mv apps/frontend/src/services/storageMockService.js \
       apps/frontend/src/__mocks__/services/
```

#### **Step 1.5: Move Mock Config**
```bash
git mv apps/frontend/src/config/mockConfig.js \
       apps/frontend/src/__mocks__/config/
```

### **Phase 2: Update Import Paths**

Update all files that imported moved files:
- Update relative paths to point to new `__mocks__/` locations
- Use TypeScript path aliases where appropriate: `@/__mocks__/...`

### **Phase 3: Audit Production Code for Demo Mode Gating**

For each production file importing from `__mocks__/`:

1. **Verify Demo Mode Check:**
   ```typescript
   const { dataSource } = useUIStore();

   if (dataSource === 'mock') {
     // Use mock data
   } else {
     // Use real API
   }
   ```

2. **Remove Fallbacks to Mock Data:**
   ```typescript
   // ❌ BAD - Falls back to mock on error
   try {
     const data = await realAPI();
   } catch (error) {
     return mockData; // REMOVE THIS
   }

   // ✅ GOOD - Shows error, never falls back to mock
   try {
     const data = await realAPI();
   } catch (error) {
     showError(error);
     return null; // or throw
   }
   ```

3. **Dynamic Imports for Mocks:**
   ```typescript
   // ✅ GOOD - Only loads mock code in demo mode
   if (dataSource === 'mock') {
     const mockModule = await import('@/__mocks__/services/mockService');
     return mockModule.default();
   }
   ```

### **Phase 4: Create Demo Mode Guard Utility**

Create `apps/frontend/src/__mocks__/utils/demoGuard.ts`:

```typescript
/**
 * Demo Mode Guard Utility
 * Ensures mock code only runs in demo mode
 */

import { useUIStore } from '@/stores';

/**
 * Check if application is in demo mode
 */
export const isDemoMode = (): boolean => {
  const { dataSource } = useUIStore.getState();
  return dataSource === 'mock';
};

/**
 * Execute callback only if in demo mode
 */
export const onlyInDemoMode = <T>(
  demoCallback: () => T,
  realCallback?: () => T
): T | undefined => {
  if (isDemoMode()) {
    return demoCallback();
  }
  return realCallback?.();
};

/**
 * Throw error if mock code is accessed in real mode
 */
export const assertDemoMode = (context: string): void => {
  if (!isDemoMode()) {
    throw new Error(
      `🚫 Mock code accessed in real API mode: ${context}. ` +
      `This is a bug - mock code should never run in production mode.`
    );
  }
};

/**
 * React hook to check demo mode
 */
export const useDemoMode = (): boolean => {
  const dataSource = useUIStore((state) => state.dataSource);
  return dataSource === 'mock';
};
```

### **Phase 5: Update Production Services**

#### **Example: ContentOptimizerService**

**Before:**
```typescript
import { mockContentOptimizer } from '../__mocks__/aiServices/contentOptimizer';

export const getOptimizations = async () => {
  if (dataSource === 'mock') {
    return mockContentOptimizer;
  }
  // real API
};
```

**After:**
```typescript
// NO import from __mocks__ at top level

export const getOptimizations = async () => {
  const { dataSource } = useUIStore.getState();

  if (dataSource === 'mock') {
    // Dynamic import - only loaded in demo mode
    const { mockContentOptimizer } = await import(
      '@/__mocks__/aiServices/contentOptimizer'
    );
    return mockContentOptimizer;
  }

  // Real API - no fallback to mock
  try {
    return await realAPI.getOptimizations();
  } catch (error) {
    console.error('Optimization API failed:', error);
    throw error; // Don't fall back to mock!
  }
};
```

### **Phase 6: Update `__mocks__/README.md`**

Document the proper usage:

```markdown
# Mock & Demo Code Directory

## ⚠️ IMPORTANT RULES

1. **Demo Mode Only**: All code in this directory should ONLY run when `dataSource === 'mock'`

2. **No Top-Level Imports**: Production code should use dynamic imports:
   ```typescript
   // ❌ BAD
   import { mockData } from '@/__mocks__/data';

   // ✅ GOOD
   if (dataSource === 'mock') {
     const { mockData } = await import('@/__mocks__/data');
   }
   ```

3. **No Fallbacks**: Real API mode should NEVER fall back to mock data on errors

4. **Use Guards**: Use `isDemoMode()`, `assertDemoMode()` from demoGuard utility

## Directory Structure

- `aiServices/` - AI service mock data
- `analytics/` - Analytics mock data
- `api/` - MSW handlers for testing
- `components/` - Demo/showcase components
- `config/` - Mock configuration
- `services/` - Mock service implementations
- `utils/` - Demo utilities and guards

## Testing

All files in `__mocks__/` are for:
- ✅ Unit/integration tests
- ✅ Demo mode (logged in as demo user)
- ✅ Development/showcase
- ❌ NEVER for production fallbacks
```

---

## 📝 **VALIDATION CHECKLIST**

After implementing changes:

- [ ] All demo files moved to `__mocks__/`
- [ ] No production files have top-level imports from `__mocks__/` (except tests)
- [ ] All mock data access is gated by `dataSource === 'mock'` check
- [ ] Dynamic imports used for mock code
- [ ] No fallbacks from real API to mock data on errors
- [ ] Demo guard utility implemented
- [ ] All import paths updated
- [ ] README.md in `__mocks__/` updated
- [ ] Tests still pass
- [ ] Demo mode still works
- [ ] Real API mode doesn't touch mock code

---

## 🎉 **EXPECTED OUTCOME**

### **Clean Separation:**
```
Production Code (src/)
  ├── services/     → Real API implementations only
  ├── components/   → Real components only
  └── utils/        → Real utilities only

Demo/Test Code (__mocks__/)
  ├── services/     → Mock implementations
  ├── components/   → Demo showcases
  ├── utils/        → Demo utilities
  └── config/       → Mock configuration
```

### **Demo Mode:**
- ✅ User logs in as demo user → `dataSource` = 'mock'
- ✅ All features work with mock data
- ✅ Clear visual indicator (demo badge)

### **Real API Mode:**
- ✅ User logs in with real account → `dataSource` = 'api'
- ✅ Only real APIs called
- ✅ Errors shown, no mock fallbacks
- ✅ Mock code never loaded

---

## 🚀 **IMPLEMENTATION ORDER**

1. ✅ Create this plan document
2. ⏳ Phase 1: Move files to `__mocks__/`
3. ⏳ Phase 2: Update import paths
4. ⏳ Phase 3: Audit and fix demo mode gating
5. ⏳ Phase 4: Create demo guard utility
6. ⏳ Phase 5: Update production services
7. ⏳ Phase 6: Update documentation
8. ⏳ Validate and test

---

**Created:** October 21, 2025
**Status:** 📋 Plan Ready - Awaiting Implementation

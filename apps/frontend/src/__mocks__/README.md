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

4. **Use Guards**: Use the Demo Guard utility for all demo mode checks:
   ```typescript
   import { isDemoMode, useDemoMode, loadMockData } from '@/__mocks__/utils/demoGuard';
   ```

## 📁 Directory Structure

```
__mocks__/
├── aiServices/              # AI service mock data
│   ├── aiServicesAPIService.js
│   ├── churnPredictor.js
│   ├── contentOptimizer.js
│   ├── predictiveAnalytics.js
│   ├── securityMonitor.js
│   └── statsService.js
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
│   │   └── AnalyticsAdapterDemo.tsx
│   └── showcase/
│       └── tables/
│           ├── GenericTableDemo.tsx
│           ├── UsersTableDemo.tsx
│           └── PostsTableDemo.tsx
├── config/                  # Mock configuration
│   └── mockConfig.js
├── providers/               # Mock data providers
│   └── MockDataProvider.js
├── services/                # Mock service implementations
│   ├── ChurnPredictorService.tsx
│   ├── PredictiveAnalyticsService.tsx
│   └── mockApiClient.js
├── system/                  # System mocks
├── user/                    # User mock data
└── utils/                   # ⭐ Demo utilities (NEW)
    ├── demoGuard.ts         # Demo mode guard utility
    ├── demoGuard.examples.tsx
    ├── README.md
    ├── demoUserUtils.js
    └── testDemoFallback.js
```

## 🛡️ Demo Guard Utility (Phase 4)

The **Demo Guard** utility provides centralized, type-safe demo mode checking.

### Quick Start

```typescript
import { 
  isDemoMode,      // Check if in demo mode
  useDemoMode,     // React hook for demo mode
  loadMockData,    // Dynamic import helper
  assertDemoMode   // Throw if not in demo mode
} from '@/__mocks__/utils/demoGuard';
```

### Common Patterns

#### 1. Load Mock Data in Component

```typescript
const MyComponent = () => {
  const [data, setData] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      if (isDemoMode()) {
        const mock = await loadMockData(
          () => import('@/__mocks__/analytics/data')
        );
        setData(mock?.data);
      } else {
        const realData = await fetchRealData();
        setData(realData);
      }
    };
    loadData();
  }, []);

  return <DataDisplay data={data} />;
};
```

#### 2. Show Demo Badge

```typescript
const Header = () => {
  const isDemo = useDemoMode();

  return (
    <Box>
      {isDemo && <Chip label="Demo Mode" color="warning" />}
    </Box>
  );
};
```

#### 3. Protect Mock-Only Functions

```typescript
export const resetDemoData = () => {
  assertDemoMode('resetDemoData');
  // This throws error if called in production
  localStorage.clear();
};
```

### 📚 Full Documentation

See [`utils/README.md`](./utils/README.md) for complete documentation and examples.

## 🎯 Usage Guidelines

### ✅ DO:

- Use `isDemoMode()` or `useDemoMode()` for checks
- Load mock data dynamically with `loadMockData()`
- Protect mock-only functions with `assertDemoMode()`
- Show visual indicators when in demo mode
- Test both demo and real API modes

### ❌ DON'T:

- Import from `__mocks__/` at top level in production code
- Fall back to mock data on API errors
- Check `dataSource` manually (use the guard utility)
- Mix demo and production logic
- Skip error handling in real API mode

## 🧪 Testing

All files in `__mocks__/` are for:
- ✅ Unit/integration tests
- ✅ Demo mode (logged in as demo user)
- ✅ Development/showcase
- ❌ NEVER for production fallbacks

### MSW (Mock Service Worker)

Use MSW handlers in `api/handlers.js` for testing:

```typescript
import { server } from '@/__mocks__/api/server';

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

## 🔧 Integration Examples

### Service with Demo Support

```typescript
import { isDemoMode } from '@/__mocks__/utils/demoGuard';

export const AnalyticsService = {
  async getStats(channelId) {
    if (isDemoMode()) {
      const { getMockStats } = await import('@/__mocks__/analytics/stats');
      return getMockStats(channelId);
    }
    
    const response = await apiClient.get(`/analytics/${channelId}/stats`);
    return response.data;
  }
};
```

### Custom Hook

```typescript
import { useDemoMode } from '@/__mocks__/utils/demoGuard';

export const useAnalytics = (channelId) => {
  const isDemo = useDemoMode();
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      if (isDemo) {
        const mock = await import('@/__mocks__/analytics/data');
        setData(mock.getAnalyticsData(channelId));
      } else {
        const realData = await fetchRealAnalytics(channelId);
        setData(realData);
      }
    };
    fetchData();
  }, [channelId, isDemo]);

  return { data };
};
```

## 📦 Available Mock Data

### Analytics
- Post dynamics and view trends
- Top performing posts
- Best time to post recommendations
- Engagement metrics

### AI Services
- Content optimization results
- Churn prediction data
- Security monitoring alerts
- Predictive analytics forecasts

### Channels
- Demo channel configurations
- Sample channel data

### User
- Demo user profiles
- Subscription tiers

## 🔄 Migration Guide

### Step 1: Replace Manual Checks

**Before:**
```typescript
const { dataSource } = useUIStore();
if (dataSource === 'mock') { ... }
```

**After:**
```typescript
import { useDemoMode } from '@/__mocks__/utils/demoGuard';
const isDemo = useDemoMode();
if (isDemo) { ... }
```

### Step 2: Remove Top-Level Imports

**Before:**
```typescript
import { mockData } from '@/__mocks__/data';
```

**After:**
```typescript
import { loadMockData } from '@/__mocks__/utils/demoGuard';
const mock = await loadMockData(() => import('@/__mocks__/data'));
```

### Step 3: Add Protection

**Before:**
```typescript
export const getMockData = () => mockData;
```

**After:**
```typescript
import { assertDemoMode } from '@/__mocks__/utils/demoGuard';
export const getMockData = () => {
  assertDemoMode('getMockData');
  return mockData;
};
```

## 🚀 Related Documentation

- [Demo Guard Utility](./utils/README.md) - Complete guide and API reference
- [Demo Guard Examples](./utils/demoGuard.examples.tsx) - Real-world usage patterns
- [Mock Components](./components/README.md) - Demo component documentation
- [MOCK_DEMO_CLEANUP_PLAN.md](../../MOCK_DEMO_CLEANUP_PLAN.md) - Cleanup roadmap

---

**Last Updated:** October 21, 2025  
**Version:** 2.0 (Phase 4 Complete)  
**Status:** ✅ Demo Guard Utility Implemented

# Demo Mode Guard Utility

A comprehensive TypeScript utility for managing demo mode checks and ensuring mock code only runs in demo mode.

## 📋 Overview

The Demo Guard utility provides a centralized, type-safe way to:
- Check if the app is in demo mode
- Conditionally execute code based on data source
- Prevent mock code from running in production
- Load mock data dynamically only when needed

## 🎯 Core Functions

### `isDemoMode(): boolean`

Check if application is in demo mode.

```typescript
import { isDemoMode } from '@/__mocks__/utils/demoGuard';

if (isDemoMode()) {
  console.log('Running in demo mode');
}
```

### `useDemoMode(): boolean`

React hook that automatically re-renders when data source changes.

```typescript
import { useDemoMode } from '@/__mocks__/utils/demoGuard';

const MyComponent = () => {
  const isDemo = useDemoMode();
  
  return (
    <Badge color={isDemo ? 'warning' : 'success'}>
      {isDemo ? 'Demo Mode' : 'Live Data'}
    </Badge>
  );
};
```

### `assertDemoMode(context: string): void`

Throws error if called outside demo mode. Use at entry points of mock-only code.

```typescript
import { assertDemoMode } from '@/__mocks__/utils/demoGuard';

export const getMockAnalytics = () => {
  assertDemoMode('getMockAnalytics');
  // This code will only run in demo mode
  return mockAnalyticsData;
};
```

### `onlyInDemoMode<T>(demoCallback, realCallback?): T | undefined`

Execute different callbacks based on data source.

```typescript
import { onlyInDemoMode } from '@/__mocks__/utils/demoGuard';

const data = onlyInDemoMode(
  () => mockData,           // Demo mode
  () => productionData      // Real API mode
);
```

### `onlyInDemoModeAsync<T>(demoCallback, realCallback?): Promise<T | undefined>`

Async version for asynchronous operations.

```typescript
import { onlyInDemoModeAsync } from '@/__mocks__/utils/demoGuard';

const data = await onlyInDemoModeAsync(
  async () => {
    const mock = await import('@/__mocks__/data');
    return mock.default;
  },
  async () => {
    return await fetchRealData();
  }
);
```

### `loadMockData<T>(importFn): Promise<T | null>`

Helper for dynamic mock data imports with proper error handling.

```typescript
import { loadMockData } from '@/__mocks__/utils/demoGuard';

const mockModule = await loadMockData(
  () => import('@/__mocks__/analytics/mockData')
);

if (mockModule) {
  setData(mockModule.topPosts);
}
```

## 🔧 Usage Examples

### Example 1: Service with Demo Mode Support

```typescript
import { isDemoMode } from '@/__mocks__/utils/demoGuard';

export const ContentOptimizerService = () => {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      if (isDemoMode()) {
        // Dynamic import only in demo mode
        const { contentOptimizerStats } = await import(
          '@/__mocks__/aiServices/contentOptimizer'
        );
        setStats(contentOptimizerStats);
      } else {
        // Real API call
        const data = await AIServicesAPI.getStats();
        setStats(data);
      }
    };

    loadData();
  }, []);

  return <StatsDisplay data={stats} />;
};
```

### Example 2: Using the Hook

```typescript
import { useDemoMode } from '@/__mocks__/utils/demoGuard';

export const DashboardHeader = () => {
  const isDemo = useDemoMode();

  return (
    <Box>
      <Typography variant="h4">Analytics Dashboard</Typography>
      {isDemo && (
        <Chip 
          label="Demo Mode" 
          color="warning" 
          icon={<DemoIcon />}
        />
      )}
    </Box>
  );
};
```

### Example 3: With onlyInDemoModeAsync

```typescript
import { onlyInDemoModeAsync } from '@/__mocks__/utils/demoGuard';

export const fetchAnalytics = async (channelId: string) => {
  return await onlyInDemoModeAsync(
    // Demo mode
    async () => {
      const mock = await import('@/__mocks__/analytics/demoAPI');
      return mock.getMockAnalytics(channelId);
    },
    // Real API mode
    async () => {
      const response = await apiClient.get(`/analytics/${channelId}`);
      return response.data;
    }
  );
};
```

### Example 4: Protecting Mock Functions

```typescript
import { assertDemoMode } from '@/__mocks__/utils/demoGuard';

// This function should NEVER be called in production
export const resetDemoData = () => {
  assertDemoMode('resetDemoData');
  
  // Safe - will throw error if called in production
  localStorage.removeItem('demo_state');
  window.location.reload();
};
```

### Example 5: Class Decorator (Advanced)

```typescript
import { demoModeOnly } from '@/__mocks__/utils/demoGuard';

class AnalyticsService {
  @demoModeOnly('AnalyticsService.loadMockData')
  loadMockData() {
    return mockAnalyticsData;
  }
  
  async getData() {
    if (isDemoMode()) {
      return this.loadMockData();
    }
    return await this.fetchRealData();
  }
}
```

## ⚠️ Best Practices

### ✅ DO:

```typescript
// ✅ Use dynamic imports in demo mode
if (isDemoMode()) {
  const { mockData } = await import('@/__mocks__/data');
  return mockData;
}

// ✅ Use hooks in React components
const isDemo = useDemoMode();

// ✅ Use assertDemoMode in mock-only functions
export const getMockData = () => {
  assertDemoMode('getMockData');
  return data;
};

// ✅ Handle both modes explicitly
const result = await onlyInDemoModeAsync(
  async () => mockData,
  async () => realData
);
```

### ❌ DON'T:

```typescript
// ❌ Top-level imports from __mocks__
import { mockData } from '@/__mocks__/data';

// ❌ Fallback to mock on error
try {
  return await realAPI();
} catch (error) {
  return mockData; // NEVER DO THIS
}

// ❌ Manual data source checking
if (localStorage.getItem('useRealAPI') === 'false') {
  // Use the hook or utility instead
}
```

## 🧪 Testing

The utility is designed to work seamlessly in tests:

```typescript
import { isDemoMode } from '@/__mocks__/utils/demoGuard';
import { useUIStore } from '@/stores';

describe('Demo Mode Guard', () => {
  it('detects demo mode correctly', () => {
    // Set demo mode
    useUIStore.setState({ dataSource: 'mock' });
    expect(isDemoMode()).toBe(true);
    
    // Set real API mode
    useUIStore.setState({ dataSource: 'api' });
    expect(isDemoMode()).toBe(false);
  });
});
```

## 🔗 Integration with Existing Code

### Before (Manual Checking):

```typescript
const dataSource = useUIStore((state) => state.dataSource);

if (dataSource === 'mock') {
  // demo logic
}
```

### After (Using Guard):

```typescript
import { useDemoMode } from '@/__mocks__/utils/demoGuard';

const isDemo = useDemoMode();

if (isDemo) {
  // demo logic
}
```

## 📦 Exported Functions

| Function | Type | Description |
|----------|------|-------------|
| `isDemoMode` | `() => boolean` | Check if in demo mode |
| `useDemoMode` | `() => boolean` | React hook for demo mode |
| `assertDemoMode` | `(context: string) => void` | Throw if not in demo mode |
| `onlyInDemoMode` | `<T>(demo, real?) => T \| undefined` | Conditional execution |
| `onlyInDemoModeAsync` | `<T>(demo, real?) => Promise<T \| undefined>` | Async conditional execution |
| `getDataSource` | `() => 'mock' \| 'api'` | Get current data source |
| `isRealApiMode` | `() => boolean` | Check if in real API mode |
| `loadMockData` | `<T>(importFn) => Promise<T \| null>` | Dynamic mock import helper |
| `demoModeOnly` | `(context) => decorator` | Class method decorator |
| `markAsDemoData` | `<T>(data) => DemoModeData<T>` | Type-safe demo data marking |
| `isDemoData` | `<T>(data) => boolean` | Check if data is demo data |

## 🎨 TypeScript Support

Full TypeScript support with generics and type guards:

```typescript
// Type-safe async loading
const data = await loadMockData<AnalyticsData>(
  () => import('@/__mocks__/analytics')
);

// Type narrowing
if (isDemoData(data)) {
  // TypeScript knows data has __demoMode property
}
```

## 📝 Migration Guide

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

### Step 2: Use Dynamic Imports

**Before:**
```typescript
import { mockData } from '@/__mocks__/data';
```

**After:**
```typescript
import { loadMockData } from '@/__mocks__/utils/demoGuard';
const mockModule = await loadMockData(
  () => import('@/__mocks__/data')
);
```

### Step 3: Protect Mock Functions

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

## 🚀 Benefits

1. **Type Safety** - Full TypeScript support with generics
2. **Centralized Logic** - One place to manage demo mode checks
3. **Error Prevention** - Catches mock code in production early
4. **Better DX** - Clear, self-documenting code
5. **Testable** - Easy to mock and test
6. **Maintainable** - Consistent patterns across codebase

---

**Version:** 1.0.0  
**Created:** October 21, 2025  
**Part of:** Mock/Demo Cleanup Phase 4

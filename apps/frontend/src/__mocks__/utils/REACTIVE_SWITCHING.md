# Reactive Demo/Real API Switching

## 🎯 Overview

The Demo Guard utility enables **instant, reactive switching** between demo and real API modes without requiring page refreshes. When a user clicks the demo/real API toggle, all services automatically update to load the appropriate data source.

## ✨ Key Features

### 1. **Instant Mode Switching**
- No page refresh required
- All components update automatically
- Smooth user experience
- Real-time data source changes

### 2. **Reactive Hook Integration**
- `useDemoMode()` hook subscribes to store changes
- React components automatically re-render
- `useEffect` dependencies trigger data reloads
- Clean, declarative code

### 3. **Zero Configuration**
- Works out of the box
- No additional setup needed
- Automatic cleanup
- Memory efficient

## 🔄 How It Works

### Architecture

```
User Click → Store Update → Hook Reacts → useEffect Runs → Data Reloads
     ↓            ↓              ↓             ↓              ↓
[Toggle]  [setDataSource]  [useDemoMode]  [isDemo]    [loadMockData/API]
```

### Data Flow

```typescript
// 1. User clicks toggle button
<GlobalDataSourceSwitch />
  ↓
// 2. Store updates
useUIStore.setState({ dataSource: 'mock' })
  ↓
// 3. Hook detects change
const isDemo = useDemoMode() // Re-renders with true
  ↓
// 4. useEffect runs (isDemo is dependency)
useEffect(() => {
  loadData()
}, [isDemo])
  ↓
// 5. Data loads from appropriate source
if (isDemo) {
  // Load mock
} else {
  // Load real API
}
```

## 📖 Implementation Patterns

### Pattern 1: Service Component

```typescript
import { useDemoMode, loadMockData } from '@/__mocks__/utils/demoGuard';

const MyService = () => {
  const isDemo = useDemoMode(); // Reactive hook
  const [data, setData] = useState(null);

  // This effect runs whenever isDemo changes
  useEffect(() => {
    const loadData = async () => {
      if (isDemo) {
        // Demo mode: Load mock data
        const mock = await loadMockData(
          () => import('@/__mocks__/myData')
        );
        setData(mock?.data);
        console.log('✅ Loaded demo data');
      } else {
        // Real API mode: Fetch from backend
        const response = await apiClient.get('/api/data');
        setData(response.data);
        console.log('✅ Loaded real API data');
      }
    };

    loadData();
  }, [isDemo]); // ← Re-runs when demo mode changes!

  return <DataDisplay data={data} />;
};
```

### Pattern 2: Custom Hook

```typescript
const useAnalytics = (channelId: string) => {
  const isDemo = useDemoMode();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const fetchData = async () => {
      setLoading(true);

      try {
        if (isDemo) {
          const mock = await loadMockData(
            () => import('@/__mocks__/analytics')
          );
          if (!cancelled) setData(mock?.data);
        } else {
          const response = await fetch(`/api/analytics/${channelId}`);
          const realData = await response.json();
          if (!cancelled) setData(realData);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetchData();

    return () => {
      cancelled = true; // Cleanup
    };
  }, [channelId, isDemo]); // Reacts to both changes

  return { data, loading };
};
```

### Pattern 3: Multiple Services Coordination

```typescript
const Dashboard = () => {
  const isDemo = useDemoMode();

  // All these services react to demo mode changes
  const { data: analytics } = useAnalytics();
  const { data: security } = useSecurity();
  const { data: content } = useContent();

  // All services automatically switch when user toggles mode
  return (
    <Box>
      <GlobalDataSourceSwitch /> {/* User clicks here */}
      <AnalyticsPanel data={analytics} />
      <SecurityPanel data={security} />
      <ContentPanel data={content} />
    </Box>
  );
};
```

## 🎬 User Experience Flow

### Scenario: User Switches to Demo Mode

```
1. User on Real API Dashboard
   ├─ Viewing their real channel data
   ├─ Stats: 1,234 posts, 567K views
   └─ [Switch to Demo] button visible

2. User Clicks "Switch to Demo"
   ├─ Button shows "Switching..." (0.3s)
   ├─ Store updates: dataSource = 'mock'
   └─ All components subscribed to isDemo hook re-render

3. Services React Instantly (no refresh!)
   ├─ ContentOptimizerService
   │  ├─ useEffect([isDemo]) triggers
   │  ├─ Loads mock contentOptimizerStats
   │  └─ Updates UI with demo stats
   ├─ SecurityMonitoringService
   │  ├─ useEffect([isDemo]) triggers
   │  ├─ Loads mock security alerts
   │  └─ Updates UI with demo threats
   └─ AnalyticsService
      ├─ useEffect([isDemo]) triggers
      ├─ Loads mock analytics data
      └─ Updates charts with demo data

4. User Sees Demo Data
   ├─ Stats change to: 100 demo posts, 250K demo views
   ├─ Demo badge appears: "🟡 Demo Mode"
   ├─ All data is now from mock sources
   └─ Can explore features risk-free

5. User Switches Back to Real API
   ├─ Clicks "Switch to Real API"
   ├─ Store updates: dataSource = 'api'
   ├─ All services react again
   ├─ Real data fetched from backend
   └─ Returns to their actual channel data
```

**Total Time:** < 1 second (feels instant!)

## 🧪 Testing Reactive Behavior

### Test 1: Hook Re-renders on Mode Change

```typescript
it('should re-render when mode changes', () => {
  const { result } = renderHook(() => useDemoMode());

  expect(result.current).toBe(false); // Real API

  act(() => {
    useUIStore.setState({ dataSource: 'mock' });
  });

  expect(result.current).toBe(true); // Demo mode
});
```

### Test 2: useEffect Triggers on Mode Change

```typescript
it('should trigger useEffect when mode changes', () => {
  const loadData = jest.fn();

  const { rerender } = renderHook(() => {
    const isDemo = useDemoMode();
    useEffect(() => {
      loadData(isDemo);
    }, [isDemo]);
  });

  expect(loadData).toHaveBeenCalledWith(false); // Initial

  act(() => {
    useUIStore.setState({ dataSource: 'mock' });
  });

  expect(loadData).toHaveBeenCalledWith(true); // After switch
});
```

### Test 3: Complete Workflow

```typescript
it('should handle complete user workflow', async () => {
  const events = [];

  // User logs in (real API)
  useUIStore.setState({ dataSource: 'api' });
  events.push('real-api');

  // User switches to demo
  useUIStore.setState({ dataSource: 'mock' });
  events.push('demo');

  // User switches back
  useUIStore.setState({ dataSource: 'api' });
  events.push('real-api');

  expect(events).toEqual(['real-api', 'demo', 'real-api']);
});
```

## ⚡ Performance Considerations

### Optimization 1: Prevent Unnecessary Re-renders

```typescript
// ✅ GOOD: Only subscribes to dataSource
const isDemo = useDemoMode();

// ❌ BAD: Subscribes to entire store
const dataSource = useUIStore();
```

### Optimization 2: Cleanup on Unmount

```typescript
useEffect(() => {
  let cancelled = false;

  const loadData = async () => {
    const data = await fetchData();
    if (!cancelled) setData(data);
  };

  loadData();

  return () => {
    cancelled = true; // ← Important!
  };
}, [isDemo]);
```

### Optimization 3: Debounce Rapid Switches

```typescript
const [isDemo] = useDebounce(useDemoMode(), 100);

useEffect(() => {
  // Only runs if mode stays changed for 100ms
  loadData();
}, [isDemo]);
```

## 🔍 Debugging

### Enable Console Logging

Our updated services include debug logging:

```typescript
console.log('✅ Loaded demo data for ContentOptimizer');
console.log('🔄 Fetching real API data for SecurityMonitoring...');
console.log('✅ Loaded real API data');
```

### Check Store State

```typescript
// In browser console:
useUIStore.getState().dataSource // 'mock' or 'api'
```

### Monitor Hook Updates

```typescript
const isDemo = useDemoMode();

useEffect(() => {
  console.log('Demo mode changed:', isDemo);
}, [isDemo]);
```

## 📊 Comparison: Before vs After

### Before (Phase 3)

```typescript
// Manual checking, not reactive
const ContentOptimizer = () => {
  const dataSource = useUIStore((state) => state.dataSource);

  useEffect(() => {
    loadData();
  }, [dataSource]); // Works but verbose

  const loadData = async () => {
    if (dataSource === 'mock') {
      // Load mock
    }
  };
};
```

### After (Phase 5)

```typescript
// Clean, reactive with Demo Guard
const ContentOptimizer = () => {
  const isDemo = useDemoMode(); // ← Clean hook

  useEffect(() => {
    loadData();
  }, [isDemo]); // ← Clear dependency

  const loadData = async () => {
    if (isDemo) {
      const mock = await loadMockData(...); // ← Utility helper
    }
  };
};
```

**Benefits:**
- ✅ Cleaner code
- ✅ Better type safety
- ✅ Consistent API
- ✅ Easier to test
- ✅ Same reactive behavior

## 🎯 Best Practices

### ✅ DO:

1. **Use `useDemoMode()` in components**
   ```typescript
   const isDemo = useDemoMode();
   ```

2. **Include `isDemo` in useEffect dependencies**
   ```typescript
   useEffect(() => {
     loadData();
   }, [isDemo]);
   ```

3. **Use `loadMockData()` for dynamic imports**
   ```typescript
   const mock = await loadMockData(() => import('...'));
   ```

4. **Add console logging for debugging**
   ```typescript
   console.log('✅ Loaded demo data');
   ```

### ❌ DON'T:

1. **Don't forget cleanup**
   ```typescript
   // ❌ BAD
   useEffect(() => {
     loadData();
   }, [isDemo]);

   // ✅ GOOD
   useEffect(() => {
     let cancelled = false;
     const load = async () => {
       const data = await loadData();
       if (!cancelled) setData(data);
     };
     load();
     return () => { cancelled = true; };
   }, [isDemo]);
   ```

2. **Don't use old patterns**
   ```typescript
   // ❌ BAD
   const dataSource = useUIStore((state) => state.dataSource);

   // ✅ GOOD
   const isDemo = useDemoMode();
   ```

3. **Don't block mode switching**
   ```typescript
   // ❌ BAD - Ignores mode changes
   useEffect(() => {
     loadData();
   }, []); // No dependencies!

   // ✅ GOOD - Reacts to changes
   useEffect(() => {
     loadData();
   }, [isDemo]);
   ```

## 🚀 Migration Checklist

When updating a service to use reactive switching:

- [ ] Import `useDemoMode` and `loadMockData`
- [ ] Replace `useUIStore` with `useDemoMode()`
- [ ] Add `isDemo` to useEffect dependencies
- [ ] Use `loadMockData()` for mock imports
- [ ] Add console logging for debugging
- [ ] Test mode switching manually
- [ ] Verify no errors in console
- [ ] Check data updates instantly

## 📚 Related Documentation

- [Demo Guard API Reference](./README.md)
- [Migration Examples](./demoGuard.examples.tsx)
- [Test Suite](./reactive-switching.test.ts)
- [Mock/Demo Cleanup Plan](../../../MOCK_DEMO_CLEANUP_PLAN.md)

---

**Version:** 1.0.0
**Created:** October 21, 2025
**Part of:** Phase 5 - Reactive Demo/Real API Switching

# Demo Guard Migration Examples

Real-world examples of migrating code to use the Demo Guard utility.

## Example 1: Service with Demo Mode Support

### ❌ BEFORE - Manual checking, top-level imports

```typescript
import { mockStats } from '@/__mocks__/aiServices/stats';
import { useUIStore } from '@/stores';

export const StatsService = () => {
  const dataSource = useUIStore((state) => state.dataSource);
  const [stats, setStats] = useState(mockStats); // Always loads mock!

  useEffect(() => {
    if (dataSource === 'api') {
      fetchRealStats().then(setStats);
    }
  }, [dataSource]);
};
```

### ✅ AFTER - Using Demo Guard

```typescript
import { isDemoMode, loadMockData } from '@/__mocks__/utils/demoGuard';

export const StatsService = () => {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const loadStats = async () => {
      if (isDemoMode()) {
        const mockModule = await loadMockData(
          () => import('@/__mocks__/aiServices/statsService')
        );
        if (mockModule) setStats(mockModule.mockStats);
      } else {
        const data = await fetchRealStats();
        setStats(data);
      }
    };
    loadStats();
  }, []);
};
```

## Example 2: Component with Demo Badge

```typescript
import { useDemoMode } from '@/__mocks__/utils/demoGuard';

export const DashboardHeader = () => {
  const isDemo = useDemoMode();

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      <span style={{
        padding: '4px 8px',
        borderRadius: '4px',
        background: isDemo ? '#ff9800' : '#4caf50',
        color: 'white'
      }}>
        {isDemo ? '🎭 DEMO MODE' : '🔴 LIVE'}
      </span>
    </div>
  );
};
```

## Example 3: Async Data Loading

```typescript
import { onlyInDemoModeAsync } from '@/__mocks__/utils/demoGuard';

export const loadAnalyticsData = async () => {
  return onlyInDemoModeAsync(
    async () => {
      // Only runs in demo mode
      const { getMockAnalytics } = await import('@/__mocks__/analytics/demoAPI');
      return getMockAnalytics();
    },
    async () => {
      // Only runs in real API mode
      return apiClient.getAnalytics();
    }
  );
};
```

## Example 4: Protected Demo-Only Function

```typescript
import { assertDemoMode } from '@/__mocks__/utils/demoGuard';

export const resetDemoData = () => {
  assertDemoMode('resetDemoData');

  // This will throw an error if called in production
  localStorage.removeItem('demo_state');
  localStorage.removeItem('demo_channel_id');
  window.location.reload();
};
```

## Example 5: Reactive Switching in Services

```typescript
import { useDemoMode, loadMockData } from '@/__mocks__/utils/demoGuard';

export const ContentOptimizerService = () => {
  const isDemo = useDemoMode(); // Reactive hook
  const [data, setData] = useState(null);

  // Automatically runs when isDemo changes
  useEffect(() => {
    const loadData = async () => {
      if (isDemo) {
        console.log('✅ Loading demo data...');
        const mock = await loadMockData(
          () => import('@/__mocks__/aiServices/contentOptimizer')
        );
        if (mock) setData(mock.contentOptimizerStats);
      } else {
        console.log('🔄 Fetching real API data...');
        const real = await fetchRealData();
        setData(real);
      }
    };
    loadData();
  }, [isDemo]); // ← Key: isDemo as dependency

  return <div>{/* render data */}</div>;
};
```

## Example 6: Custom Hook Pattern

```typescript
import { useDemoMode, onlyInDemoModeAsync } from '@/__mocks__/utils/demoGuard';

export const useAnalyticsData = (channelId: string) => {
  const isDemo = useDemoMode();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const fetchData = async () => {
      setLoading(true);

      const result = await onlyInDemoModeAsync(
        // Demo mode
        async () => {
          const mock = await import('@/__mocks__/analytics/data');
          return mock.getAnalyticsData(channelId);
        },
        // Real API mode
        async () => {
          const response = await apiClient.get(`/analytics/${channelId}`);
          return response.data;
        }
      );

      if (!cancelled) {
        setData(result);
        setLoading(false);
      }
    };

    fetchData();

    return () => {
      cancelled = true;
    };
  }, [channelId, isDemo]);

  return { data, loading };
};
```

## Migration Checklist

✅ **Replace manual dataSource checks:**
- ❌ `const dataSource = useUIStore((state) => state.dataSource);`
- ✅ `const isDemo = useDemoMode();`

✅ **Remove top-level mock imports:**
- ❌ `import { mockData } from '@/__mocks__/data';`
- ✅ Use `loadMockData(() => import('@/__mocks__/data'))` inside functions

✅ **Use dynamic imports:**
- ❌ Direct mock usage
- ✅ `await loadMockData(() => import('...'))`

✅ **No fallbacks to mock data:**
- ❌ `catch (err) { return mockData; }`
- ✅ `catch (err) { throw err; /* show error */ }`

✅ **Use reactive hooks:**
- Add `isDemo` to useEffect dependencies
- Components re-render automatically on mode change

✅ **Protect demo-only functions:**
- Use `assertDemoMode('functionName')` at start of demo-only functions

## Benefits

- ✅ **Instant mode switching** - No page refresh needed
- ✅ **Type-safe** - Full TypeScript support
- ✅ **Clean separation** - Mock code never loads in production
- ✅ **Reactive** - Automatic updates when mode changes
- ✅ **Safe** - Guards prevent demo code in production

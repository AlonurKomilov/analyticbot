/**
 * Demo Guard Migration Examples
 * 
 * Real-world examples of migrating code to use the Demo Guard utility
 */

import { 
  isDemoMode, 
  useDemoMode, 
  assertDemoMode,
  onlyInDemoModeAsync,
  loadMockData
} from './demoGuard';

// ============================================
// EXAMPLE 1: Service with Demo Mode Support
// ============================================

// ❌ BEFORE - Manual checking, top-level imports
/*
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
*/

// ✅ AFTER - Using Demo Guard
export const StatsService = () => {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const loadStats = async () => {
      if (isDemoMode()) {
        const mockModule = await loadMockData(
          () => import('@/__mocks__/aiServices/stats')
        );
        if (mockModule) setStats(mockModule.mockStats);
      } else {
        const data = await fetchRealStats();
        setStats(data);
      }
    };
    loadStats();
  }, []);

  return stats;
};

// ============================================
// EXAMPLE 2: Component with Demo Badge
// ============================================

// ❌ BEFORE - Verbose manual checking
/*
export const Header = () => {
  const dataSource = useUIStore((state) => state.dataSource);
  const isDemo = dataSource === 'mock';

  return (
    <Box>
      {isDemo && <Chip label="Demo" />}
    </Box>
  );
};
*/

// ✅ AFTER - Clean hook usage
export const Header = () => {
  const isDemo = useDemoMode();

  return (
    <Box>
      {isDemo && <Chip label="Demo" color="warning" />}
    </Box>
  );
};

// ============================================
// EXAMPLE 3: API Client with Fallback
// ============================================

// ❌ BEFORE - Dangerous fallback to mock on error
/*
export const fetchAnalytics = async (channelId) => {
  try {
    return await apiClient.get(`/analytics/${channelId}`);
  } catch (error) {
    // BAD - Falls back to mock on ANY error, even in production!
    return mockAnalyticsData;
  }
};
*/

// ✅ AFTER - Explicit mode handling, no fallback
export const fetchAnalytics = async (channelId: string) => {
  return await onlyInDemoModeAsync(
    // Demo mode - load mock
    async () => {
      const mock = await import('@/__mocks__/analytics/demoAPI');
      return mock.getMockAnalytics(channelId);
    },
    // Real API mode - fetch real data
    async () => {
      const response = await apiClient.get(`/analytics/${channelId}`);
      return response.data;
    }
  );
};

// ============================================
// EXAMPLE 4: Mock-Only Utility Function
// ============================================

// ❌ BEFORE - No protection, could be called in production
/*
export const resetDemoData = () => {
  localStorage.clear();
  window.location.reload();
};
*/

// ✅ AFTER - Protected with assertion
export const resetDemoData = () => {
  assertDemoMode('resetDemoData');
  
  // This will throw an error if called in production
  localStorage.removeItem('demo_state');
  localStorage.removeItem('demo_channel_id');
  window.location.reload();
};

// ============================================
// EXAMPLE 5: Data Provider Pattern
// ============================================

// ❌ BEFORE - Complex conditional logic
/*
export const getDataProvider = async () => {
  const dataSource = localStorage.getItem('useRealAPI') === 'true' ? 'api' : 'mock';
  
  if (dataSource === 'mock') {
    const { MockDataProvider } = await import('@/__mocks__/providers/MockDataProvider');
    return new MockDataProvider();
  } else {
    return productionDataProvider;
  }
};
*/

// ✅ AFTER - Clean and type-safe
export const getDataProvider = async () => {
  if (isDemoMode()) {
    const mockModule = await loadMockData(
      () => import('@/__mocks__/providers/MockDataProvider')
    );
    return mockModule ? new mockModule.MockDataProvider() : null;
  }
  
  return productionDataProvider;
};

// ============================================
// EXAMPLE 6: Service Factory Pattern
// ============================================

// ✅ GOOD - Using Demo Guard in factory
export class ServiceFactory {
  static async createAnalyticsService() {
    return await onlyInDemoModeAsync(
      // Demo mode
      async () => {
        const { MockAnalyticsService } = await import(
          '@/__mocks__/services/MockAnalyticsService'
        );
        return new MockAnalyticsService();
      },
      // Real API mode
      async () => {
        return new RealAnalyticsService();
      }
    );
  }
}

// ============================================
// EXAMPLE 7: React Component with Data Fetch
// ============================================

// ✅ GOOD - Component using Demo Guard
import React, { useState, useEffect } from 'react';

export const AnalyticsChart = ({ channelId }) => {
  const isDemo = useDemoMode();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      setError(null);

      try {
        if (isDemo) {
          // Load mock data dynamically
          const mockModule = await loadMockData(
            () => import('@/__mocks__/analytics/chartData')
          );
          setData(mockModule?.chartData || null);
        } else {
          // Fetch real data
          const response = await fetch(`/api/analytics/${channelId}`);
          if (!response.ok) throw new Error('Failed to fetch');
          const realData = await response.json();
          setData(realData);
        }
      } catch (err) {
        setError(err.message);
        // Don't fall back to mock - show the error!
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [channelId, isDemo]);

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;
  if (!data) return <Alert severity="info">No data available</Alert>;

  return <ChartComponent data={data} />;
};

// ============================================
// EXAMPLE 8: Configuration Helper
// ============================================

// ✅ GOOD - Using guard for configuration
export const getApiConfig = () => {
  if (isDemoMode()) {
    return {
      baseURL: '/mock-api',
      timeout: 100,
      retries: 0,
      enableLogs: true
    };
  }

  return {
    baseURL: process.env.VITE_API_BASE_URL,
    timeout: 5000,
    retries: 3,
    enableLogs: false
  };
};

// ============================================
// EXAMPLE 9: Custom Hook Pattern
// ============================================

// ✅ GOOD - Custom hook using Demo Guard
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

// ============================================
// MIGRATION CHECKLIST
// ============================================

/*
✅ Migration Checklist:

1. Replace manual dataSource checks:
   ❌ const dataSource = useUIStore((state) => state.dataSource);
   ✅ const isDemo = useDemoMode();

2. Remove top-level mock imports:
   ❌ import { mockData } from '@/__mocks__/data';
   ✅ const mock = await loadMockData(() => import('@/__mocks__/data'));

3. Use assertDemoMode for mock-only functions:
   ✅ assertDemoMode('functionName');

4. Replace conditional logic:
   ❌ if (dataSource === 'mock') { ... }
   ✅ if (isDemoMode()) { ... }

5. Use onlyInDemoModeAsync for fetch logic:
   ✅ await onlyInDemoModeAsync(demoFn, realFn);

6. Remove unsafe fallbacks:
   ❌ catch (error) { return mockData; }
   ✅ catch (error) { throw error; }

7. Add demo badges in UI:
   ✅ {useDemoMode() && <Chip label="Demo" />}

8. Test both modes:
   ✅ Test with dataSource='mock'
   ✅ Test with dataSource='api'
*/

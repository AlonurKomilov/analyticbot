/**
 * Demo Mode Guard Utility
 * Ensures mock code only runs in demo mode
 * 
 * This utility provides centralized functions for checking and enforcing
 * demo mode restrictions, preventing mock code from running in production.
 */

import { useUIStore } from '@/stores';

/**
 * Check if application is in demo mode
 * @returns {boolean} True if dataSource is 'mock', false otherwise
 * 
 * @example
 * if (isDemoMode()) {
 *   // Load mock data
 * }
 */
export const isDemoMode = (): boolean => {
  const { dataSource } = useUIStore.getState();
  return dataSource === 'mock';
};

/**
 * Execute callback only if in demo mode
 * Provides a clean way to conditionally execute code based on data source
 * 
 * @param demoCallback - Function to execute in demo mode
 * @param realCallback - Optional function to execute in real API mode
 * @returns Result of the appropriate callback, or undefined
 * 
 * @example
 * const data = onlyInDemoMode(
 *   () => mockData,
 *   () => realApiData
 * );
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
 * Use this at the entry point of mock-only code to fail fast
 * 
 * @param context - Description of where the check is happening (for error message)
 * @throws {Error} If called when not in demo mode
 * 
 * @example
 * export const getMockData = () => {
 *   assertDemoMode('getMockData');
 *   return mockData;
 * };
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
 * Automatically re-renders when data source changes
 * 
 * @returns {boolean} True if in demo mode
 * 
 * @example
 * const MyComponent = () => {
 *   const isDemo = useDemoMode();
 *   
 *   return (
 *     <div>
 *       {isDemo ? <DemoFeature /> : <ProductionFeature />}
 *     </div>
 *   );
 * };
 */
export const useDemoMode = (): boolean => {
  const dataSource = useUIStore((state) => state.dataSource);
  return dataSource === 'mock';
};

/**
 * Async version of onlyInDemoMode for async operations
 * 
 * @param demoCallback - Async function to execute in demo mode
 * @param realCallback - Optional async function to execute in real API mode
 * @returns Promise that resolves to the result of the appropriate callback
 * 
 * @example
 * const data = await onlyInDemoModeAsync(
 *   async () => {
 *     const mock = await import('./mockData');
 *     return mock.data;
 *   },
 *   async () => {
 *     return await fetchRealData();
 *   }
 * );
 */
export const onlyInDemoModeAsync = async <T>(
  demoCallback: () => Promise<T>,
  realCallback?: () => Promise<T>
): Promise<T | undefined> => {
  if (isDemoMode()) {
    return await demoCallback();
  }
  return realCallback ? await realCallback() : undefined;
};

/**
 * Get data source with type safety
 * @returns {'mock' | 'api'} Current data source
 */
export const getDataSource = (): 'mock' | 'api' => {
  const { dataSource } = useUIStore.getState();
  return dataSource;
};

/**
 * Check if using real API
 * Convenience method, opposite of isDemoMode
 * 
 * @returns {boolean} True if dataSource is 'api'
 */
export const isRealApiMode = (): boolean => {
  return !isDemoMode();
};

/**
 * Load mock data dynamically only in demo mode
 * Helper function that encapsulates the dynamic import pattern
 * 
 * @param importFn - Function that returns dynamic import promise
 * @returns Promise resolving to imported module or null if not in demo mode
 * 
 * @example
 * const mockData = await loadMockData(
 *   () => import('@/__mocks__/analytics/mockData')
 * );
 * if (mockData) {
 *   setData(mockData.default);
 * }
 */
export const loadMockData = async <T>(
  importFn: () => Promise<T>
): Promise<T | null> => {
  if (!isDemoMode()) {
    console.warn('Attempted to load mock data in real API mode - ignoring');
    return null;
  }
  
  try {
    return await importFn();
  } catch (error) {
    console.error('Failed to load mock data:', error);
    throw error;
  }
};

/**
 * Demo mode decorator for class methods
 * Ensures method only executes in demo mode
 * 
 * @example
 * class MyService {
 *   @demoModeOnly('MyService.loadMockData')
 *   loadMockData() {
 *     return mockData;
 *   }
 * }
 */
export function demoModeOnly(context: string) {
  return function (
    _target: any,
    _propertyKey: string,
    descriptor: PropertyDescriptor
  ) {
    const originalMethod = descriptor.value;
    
    descriptor.value = function (...args: any[]) {
      assertDemoMode(context);
      return originalMethod.apply(this, args);
    };
    
    return descriptor;
  };
}

/**
 * Type guard for demo mode data
 * Useful for TypeScript type narrowing
 */
export type DemoModeData<T> = T & { __demoMode: true };

/**
 * Mark data as demo mode only (for type checking)
 */
export const markAsDemoData = <T>(data: T): DemoModeData<T> => {
  return { ...data, __demoMode: true as const };
};

/**
 * Check if data is marked as demo data
 */
export const isDemoData = <T>(data: T | DemoModeData<T>): data is DemoModeData<T> => {
  return '__demoMode' in data && (data as any).__demoMode === true;
};

/**
 * Advanced Performance Optimization System
 *
 * This module provides:
 * - Smart component splitting strategies
 * - Dynamic import optimization
 * - Bundle size monitoring
 * - Performance-aware lazy loading
 * - Critical path optimization
 */

import React, { lazy, Suspense, memo, useMemo, useCallback, useRef, ComponentType, ReactNode } from 'react';
import { Box, CircularProgress, Skeleton } from '@mui/material';
import type { LazyExoticComponent } from 'react';

// Performance-aware loading states
export const LOADING_STRATEGIES = {
  SKELETON: 'skeleton',
  SPINNER: 'spinner',
  PROGRESSIVE: 'progressive',
  INLINE: 'inline'
} as const;

type LoadingStrategy = typeof LOADING_STRATEGIES[keyof typeof LOADING_STRATEGIES];

interface SmartLazyOptions {
  name?: string;
  priority?: 'critical' | 'high' | 'normal' | 'low';
  preloadStrategy?: 'idle' | 'immediate' | 'interaction' | 'viewport';
  loadingStrategy?: LoadingStrategy;
  chunkName?: string;
  timeout?: number;
  retryCount?: number;
}

interface PerformanceMetrics {
  loadTime: number;
  timestamp: number;
  attempts: number;
  success: boolean;
  error?: string;
}

interface PerformanceLoadingFallbackProps {
  strategy?: LoadingStrategy;
  height?: number;
  lines?: number;
  variant?: 'text' | 'rectangular' | 'circular';
}

interface PerformanceSuspenseProps {
  children: ReactNode;
  fallback?: ReactNode;
  name?: string;
  onLoad?: (loadTime: number) => void;
  onError?: (error: Error, errorInfo?: React.ErrorInfo) => void;
  timeout?: number;
}

interface LoadTrackerProps {
  children: ReactNode;
  onLoad?: () => void;
}

interface ErrorBoundaryWrapperProps {
  children: ReactNode;
  onError?: (error: Error, errorInfo?: React.ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
}

interface BundleMetrics {
  importCount?: number;
  lineCount?: number;
  dependencies?: string[];
}

interface ChunkInfo {
  name: string;
  size: number;
  loadTime: number;
}

interface LoadingStrategyConfig {
  strategy: 'progressive' | 'batched' | 'parallel';
  batchSize: number;
  delay: number;
}

interface NetworkMetrics {
  networkSpeed?: string;
  deviceMemory?: number;
}

/**
 * Smart Lazy Loading with Performance Optimization
 */
export class SmartLazyLoader {
  loadCache: Map<string, Promise<any>>;
  performanceMetrics: Map<string, PerformanceMetrics>;
  criticalComponents: Set<string>;

  constructor() {
    this.loadCache = new Map();
    this.performanceMetrics = new Map();
    this.criticalComponents = new Set();
  }

  /**
   * Create optimized lazy component with performance tracking
   */
  createLazyComponent<T extends ComponentType<any>>(
    importFn: () => Promise<{ default: T }>,
    options: SmartLazyOptions = {}
  ): LazyExoticComponent<T> & { preload?: () => Promise<{ default: T }>; displayName?: string; priority?: string; chunkName?: string } {
    const {
      name = 'UnnamedComponent',
      priority = 'normal',
      preloadStrategy = 'idle',
      loadingStrategy = LOADING_STRATEGIES.SKELETON,
      chunkName,
      timeout = 10000,
      retryCount = 3
    } = options;

    // Enhanced import function with error handling and retry
    const enhancedImportFn = async (): Promise<{ default: T }> => {
      const startTime = performance.now();
      let attempts = 0;

      while (attempts < retryCount) {
        try {
          const module = await importFn();
          const loadTime = performance.now() - startTime;

          // Track performance metrics
          this.performanceMetrics.set(name, {
            loadTime,
            timestamp: Date.now(),
            attempts: attempts + 1,
            success: true
          });

          return module;
        } catch (error: any) {
          attempts++;
          console.warn(`Failed to load ${name} (attempt ${attempts}/${retryCount}):`, error);

          if (attempts >= retryCount) {
            this.performanceMetrics.set(name, {
              loadTime: performance.now() - startTime,
              timestamp: Date.now(),
              attempts,
              success: false,
              error: error.message
            });
            throw error;
          }

          // Exponential backoff
          await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempts) * 1000));
        }
      }

      throw new Error(`Failed to load ${name} after ${retryCount} attempts`);
    };

    const LazyComponent = lazy(enhancedImportFn);

    // Add preload capability
    const enhancedLazyComponent = LazyComponent as LazyExoticComponent<T> & {
      preload?: () => Promise<{ default: T }>;
      displayName?: string;
      priority?: string;
      chunkName?: string;
    };

    enhancedLazyComponent.preload = () => {
      if (!this.loadCache.has(name)) {
        const promise = enhancedImportFn();
        this.loadCache.set(name, promise);
        return promise;
      }
      return this.loadCache.get(name)!;
    };

    // Add metadata
    enhancedLazyComponent.displayName = name;
    enhancedLazyComponent.priority = priority;
    enhancedLazyComponent.chunkName = chunkName;

    return enhancedLazyComponent;
  }

  /**
   * Preload components based on priority and strategy
   */
  preloadComponents(
    components: Array<LazyExoticComponent<any> & { preload?: () => Promise<any>; displayName?: string }>,
    strategy: 'idle' | 'immediate' | 'interaction' | 'viewport' = 'idle'
  ): void {
    const preloadFn = () => {
      components.forEach(component => {
        if (component.preload && !this.loadCache.has(component.displayName || '')) {
          component.preload().catch(error => {
            console.warn(`Preload failed for ${component.displayName}:`, error);
          });
        }
      });
    };

    switch (strategy) {
      case 'immediate':
        preloadFn();
        break;
      case 'idle':
        if ('requestIdleCallback' in window) {
          requestIdleCallback(preloadFn, { timeout: 5000 });
        } else {
          setTimeout(preloadFn, 100);
        }
        break;
      case 'interaction':
        // Preload on first user interaction
        const interactionEvents = ['mousedown', 'touchstart', 'keydown'];
        const handleInteraction = () => {
          preloadFn();
          interactionEvents.forEach(event => {
            document.removeEventListener(event, handleInteraction);
          });
        };
        interactionEvents.forEach(event => {
          document.addEventListener(event, handleInteraction, { passive: true, once: true });
        });
        break;
      case 'viewport':
        // Preload when near viewport (intersection observer)
        const observer = new IntersectionObserver((entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              preloadFn();
              observer.disconnect();
            }
          });
        }, { rootMargin: '200px' });

        // Observe a trigger element (could be passed as option)
        const triggerElement = document.querySelector('[data-preload-trigger]');
        if (triggerElement) {
          observer.observe(triggerElement);
        }
        break;
    }
  }

  /**
   * Get performance metrics for loaded components
   */
  getPerformanceReport() {
    const report = {
      totalComponents: this.performanceMetrics.size,
      averageLoadTime: 0,
      failures: 0,
      components: {} as Record<string, PerformanceMetrics>
    };

    let totalLoadTime = 0;
    this.performanceMetrics.forEach((metrics, name) => {
      report.components[name] = metrics;
      if (metrics.success) {
        totalLoadTime += metrics.loadTime;
      } else {
        report.failures++;
      }
    });

    report.averageLoadTime = totalLoadTime / (this.performanceMetrics.size - report.failures);
    return report;
  }
}

// Global smart loader instance
export const smartLoader = new SmartLazyLoader();

/**
 * Performance-aware loading components
 */
export const PerformanceLoadingFallback = memo(({
  strategy = LOADING_STRATEGIES.SKELETON,
  height = 200,
  lines = 3,
  variant = 'rectangular'
}: PerformanceLoadingFallbackProps): JSX.Element => {
  const fallbackComponent = useMemo(() => {
    switch (strategy) {
      case LOADING_STRATEGIES.SKELETON:
        return (
          <Box sx={{ p: 2 }}>
            {Array.from({ length: lines }).map((_, index) => {
              return (
                <Skeleton
                  key={index}
                  variant={variant}
                  height={height / lines}
                  sx={{ mb: 1 }}
                  animation="wave"
                />
              );
            })}
          </Box>
        );

      case LOADING_STRATEGIES.SPINNER:
        return (
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              height,
              minHeight: 200
            }}
          >
            <CircularProgress size={40} />
          </Box>
        );

      case LOADING_STRATEGIES.PROGRESSIVE:
        return (
          <Box sx={{ p: 2 }}>
            <Skeleton variant="text" height={40} sx={{ mb: 2 }} />
            <Skeleton variant="rectangular" height={height * 0.6} sx={{ mb: 1 }} />
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Skeleton variant="rectangular" width="30%" height={30} />
              <Skeleton variant="rectangular" width="30%" height={30} />
            </Box>
          </Box>
        );

      case LOADING_STRATEGIES.INLINE:
        return (
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              p: 1,
              opacity: 0.7
            }}
          >
            <CircularProgress size={16} />
            <span>Loading...</span>
          </Box>
        );

      default:
        return <CircularProgress />;
    }
  }, [strategy, height, lines, variant]);

  return fallbackComponent;
});

PerformanceLoadingFallback.displayName = 'PerformanceLoadingFallback';

/**
 * Enhanced Suspense wrapper with performance tracking
 */
export const PerformanceSuspense = memo(({
  children,
  fallback,
  name = 'UnknownSuspense',
  onLoad,
  onError,
  timeout = 10000
}: PerformanceSuspenseProps): JSX.Element => {
  const startTime = useRef(Date.now());

  const handleLoad = useCallback(() => {
    const loadTime = Date.now() - startTime.current;
    smartLoader.performanceMetrics.set(`${name}_suspense`, {
      loadTime,
      timestamp: Date.now(),
      success: true,
      attempts: 1,
      type: 'suspense'
    } as any);
    onLoad?.(loadTime);
  }, [name, onLoad]);

  const handleError = useCallback((error: Error, errorInfo?: React.ErrorInfo) => {
    const loadTime = Date.now() - startTime.current;
    smartLoader.performanceMetrics.set(`${name}_suspense`, {
      loadTime,
      timestamp: Date.now(),
      success: false,
      error: error.message,
      attempts: 1,
      type: 'suspense'
    } as any);
    onError?.(error, errorInfo);
  }, [name, onError]);

  return (
    <Suspense fallback={fallback}>
      <ErrorBoundaryWrapper onError={handleError}>
        <LoadTracker onLoad={handleLoad}>
          {children}
        </LoadTracker>
      </ErrorBoundaryWrapper>
    </Suspense>
  );
});

PerformanceSuspense.displayName = 'PerformanceSuspense';

/**
 * Load tracking wrapper
 */
const LoadTracker = memo(({ children, onLoad }: LoadTrackerProps): JSX.Element => {
  const hasLoaded = useRef(false);

  React.useEffect(() => {
    if (!hasLoaded.current) {
      hasLoaded.current = true;
      onLoad?.();
    }
  }, [onLoad]);

  return <>{children}</>;
});

LoadTracker.displayName = 'LoadTracker';

/**
 * Simple error boundary for Suspense
 */
class ErrorBoundaryWrapper extends React.Component<ErrorBoundaryWrapperProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryWrapperProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(_error: Error): ErrorBoundaryState {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    this.props.onError?.(error, errorInfo);
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        <Box sx={{ p: 2, textAlign: 'center', color: 'error.main' }}>
          Failed to load component
        </Box>
      );
    }

    return this.props.children;
  }
}

/**
 * Bundle size analyzer utilities
 */
export const bundleAnalyzer = {
  /**
   * Estimate component bundle size impact
   */
  estimateComponentSize: (componentName: string, metrics: BundleMetrics = {}): number => {
    // Basic heuristic based on component complexity
    const {
      importCount = 0,
      lineCount = 0,
      dependencies = []
    } = metrics;

    // Rough estimate in KB
    const baseSize = 5; // Base React component overhead
    const importOverhead = importCount * 2; // 2KB per import estimate
    const codeSize = lineCount * 0.1; // 0.1KB per line estimate
    const depSize = dependencies.length * 10; // 10KB per major dependency

    return Math.round(baseSize + importOverhead + codeSize + depSize);
  },

  /**
   * Monitor actual bundle chunk sizes
   */
  monitorChunkSizes: (): ChunkInfo[] => {
    if ('performance' in window && 'getEntriesByType' in performance) {
      const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];
      const chunks = resources.filter(resource =>
        resource.name.includes('.js') && resource.name.includes('chunk')
      );

      return chunks.map(chunk => ({
        name: chunk.name.split('/').pop() || 'unknown',
        size: chunk.transferSize,
        loadTime: chunk.responseEnd - chunk.requestStart
      }));
    }
    return [];
  },

  /**
   * Performance-based chunk loading strategy
   */
  getOptimalLoadingStrategy: (metrics: NetworkMetrics = {}): LoadingStrategyConfig => {
    const { networkSpeed = 'unknown', deviceMemory = 4 } = metrics;

    if (networkSpeed === 'slow-2g' || deviceMemory < 2) {
      return {
        strategy: 'progressive',
        batchSize: 1,
        delay: 1000
      };
    } else if (networkSpeed === '3g' || deviceMemory < 4) {
      return {
        strategy: 'batched',
        batchSize: 2,
        delay: 500
      };
    } else {
      return {
        strategy: 'parallel',
        batchSize: 4,
        delay: 100
      };
    }
  }
};

export default {
  SmartLazyLoader,
  smartLoader,
  PerformanceLoadingFallback,
  PerformanceSuspense,
  bundleAnalyzer,
  LOADING_STRATEGIES
};

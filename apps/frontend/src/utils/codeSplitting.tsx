/**
 * Advanced Code Splitting and Bundle Optimization Utilities
 * Provides intelligent code splitting, preloading strategies, and bundle analysis
 */

import { lazy, Suspense, useState, useEffect, useRef, ComponentType, ReactNode } from 'react';
import type { LazyExoticComponent } from 'react';

interface ChunkStats {
    totalChunks: number;
    totalSize: number;
    averageLoadTime: number;
    slowestChunks: Array<{ name: string; time: number }>;
    failedChunks: string[];
    preloadedChunks: string[];
}

interface SmartLazyOptions {
    preload?: boolean;
    preloadDelay?: number;
    fallback?: ReactNode;
    retryAttempts?: number;
    retryDelay?: number;
    chunkName?: string;
}

interface SmartSuspenseProps {
    children: ReactNode;
    fallback?: ReactNode;
    loadingComponent?: ComponentType;
    errorBoundary?: ComponentType<{ children: ReactNode }>;
    timeout?: number;
}

interface RouteComponentProps {
    [key: string]: any;
}

interface PreloadRoute {
    importFn: () => Promise<any>;
    priority: 'high' | 'normal' | 'low';
}

// Bundle analyzer for runtime analysis
class BundleAnalyzer {
    chunkSizes: Map<string, number>;
    loadTimes: Map<string, number>;
    preloadedChunks: Set<string>;
    failedChunks: Set<string>;
    retryAttempts: Map<string, number>;
    observer: PerformanceObserver | null;

    constructor() {
        this.chunkSizes = new Map();
        this.loadTimes = new Map();
        this.preloadedChunks = new Set();
        this.failedChunks = new Set();
        this.retryAttempts = new Map();
        this.observer = null;

        this.init();
    }

    init(): void {
        // Monitor chunk loading via Performance API
        if ('PerformanceObserver' in window) {
            this.observer = new PerformanceObserver((list) => {
                list.getEntries().forEach((entry) => {
                    if (entry.name.includes('/js/') && entry.name.includes('')) {
                        const chunkName = this.extractChunkName(entry.name);
                        const resourceEntry = entry as PerformanceResourceTiming;
                        this.chunkSizes.set(chunkName, resourceEntry.transferSize || resourceEntry.encodedBodySize);
                        this.loadTimes.set(chunkName, entry.duration);
                    }
                });
            });

            this.observer.observe({ entryTypes: ['resource'] });
        }

        // Monitor failed chunks
        window.addEventListener('error', (event: ErrorEvent) => {
            if (event.filename && event.filename.includes('/js/')) {
                const chunkName = this.extractChunkName(event.filename);
                this.failedChunks.add(chunkName);
                console.error(`❌ Failed to load chunk: ${chunkName}`);
            }
        });
    }

    extractChunkName(url: string): string {
        const match = url.match(/\/js\/([^\/]+)\.js/);
        return match ? match[1] : 'unknown';
    }

    trackChunkLoad(chunkName: string, startTime: number): void {
        const endTime = performance.now();
        const loadTime = endTime - startTime;
        this.loadTimes.set(chunkName, loadTime);

        if (loadTime > 3000) {
            console.warn(`🐌 Slow chunk load: ${chunkName} took ${loadTime.toFixed(2)}ms`);
        }
    }

    getChunkStats(): ChunkStats {
        const stats: ChunkStats = {
            totalChunks: this.chunkSizes.size,
            totalSize: 0,
            averageLoadTime: 0,
            slowestChunks: [],
            failedChunks: Array.from(this.failedChunks),
            preloadedChunks: Array.from(this.preloadedChunks)
        };

        // Calculate total size
        this.chunkSizes.forEach(size => {
            stats.totalSize += size;
        });

        // Calculate average load time
        const loadTimes = Array.from(this.loadTimes.values());
        stats.averageLoadTime = loadTimes.reduce((sum, time) => sum + time, 0) / loadTimes.length;

        // Find slowest chunks
        stats.slowestChunks = Array.from(this.loadTimes.entries())
            .sort(([, a], [, b]) => b - a)
            .slice(0, 5)
            .map(([name, time]) => ({ name, time }));

        return stats;
    }

    generateBundleReport(): ChunkStats {
        const stats = this.getChunkStats();

        console.group('📦 Bundle Analysis Report');
        console.log(`📊 Total Chunks: ${stats.totalChunks}`);
        console.log(`📏 Total Size: ${(stats.totalSize / 1024).toFixed(2)} KB`);
        console.log(`⏱️ Average Load Time: ${stats.averageLoadTime.toFixed(2)}ms`);

        if (stats.slowestChunks.length > 0) {
            console.group('🐌 Slowest Chunks');
            stats.slowestChunks.forEach(({ name, time }) => {
                console.log(`${name}: ${time.toFixed(2)}ms`);
            });
            console.groupEnd();
        }

        if (stats.failedChunks.length > 0) {
            console.group('❌ Failed Chunks');
            stats.failedChunks.forEach(chunk => {
                console.log(chunk);
            });
            console.groupEnd();
        }

        if (stats.preloadedChunks.length > 0) {
            console.group('🚀 Preloaded Chunks');
            stats.preloadedChunks.forEach(chunk => {
                console.log(chunk);
            });
            console.groupEnd();
        }

        console.groupEnd();

        return stats;
    }
}

// Advanced lazy loading with intelligent preloading
export const createSmartLazy = <T extends ComponentType<any>>(
    importFn: () => Promise<{ default: T }>,
    options: SmartLazyOptions = {}
): LazyExoticComponent<T> & { preload?: () => Promise<{ default: T }> } => {
    const {
        preload = false,
        preloadDelay = 2000,
        retryAttempts = 3,
        retryDelay = 1000,
        chunkName
    } = options;

    // Enhanced import function with retry logic
    const enhancedImport = async (): Promise<{ default: T }> => {
        let lastError: any;

        for (let attempt = 1; attempt <= retryAttempts; attempt++) {
            try {
                const startTime = performance.now();
                const module = await importFn();

                // Track successful load
                if (bundleAnalyzer && chunkName) {
                    bundleAnalyzer.trackChunkLoad(chunkName, startTime);
                }

                return module;
            } catch (error) {
                lastError = error;
                console.warn(`⚠️ Chunk load attempt ${attempt} failed:`, error);

                if (attempt < retryAttempts) {
                    await new Promise(resolve => setTimeout(resolve, retryDelay * attempt));
                }
            }
        }

        // All attempts failed
        console.error(`❌ Failed to load chunk after ${retryAttempts} attempts:`, lastError);
        throw lastError;
    };

    const LazyComponent = lazy(enhancedImport);

    // Add preload capability
    const preloadableComponent = LazyComponent as LazyExoticComponent<T> & {
        preload?: () => Promise<{ default: T }>;
    };

    preloadableComponent.preload = enhancedImport;

    // Preload logic
    if (preload) {
        setTimeout(() => {
            enhancedImport().catch(console.error);
            if (bundleAnalyzer && chunkName) {
                bundleAnalyzer.preloadedChunks.add(chunkName);
            }
        }, preloadDelay);
    }

    return preloadableComponent;
};

// Smart Suspense wrapper with loading states
export const SmartSuspense = ({
    children,
    fallback,
    loadingComponent: LoadingComponent,
    errorBoundary: ErrorBoundary,
    timeout = 10000
}: SmartSuspenseProps): React.JSX.Element => {
    const [hasTimedOut, setHasTimedOut] = useState(false);
    const timeoutRef = useRef<NodeJS.Timeout | undefined>(undefined);

    useEffect(() => {
        // Set timeout for loading
        timeoutRef.current = setTimeout(() => {
            setHasTimedOut(true);
            console.warn('⏰ Component loading timeout');
        }, timeout);

        return () => {
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
            }
        };
    }, [timeout]);

    useEffect(() => {
        // Clear timeout when component loads
        return () => {
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
            }
        };
    }, [children]);

    const defaultFallback: React.JSX.Element = LoadingComponent ? (
        <LoadingComponent />
    ) : (
        <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '200px',
            flexDirection: 'column'
        }}>
            <div style={{
                width: '40px',
                height: '40px',
                border: '4px solid #f3f3f3',
                borderTop: '4px solid #3498db',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite'
            }} />
            <p style={{ marginTop: '16px', color: '#666' }}>
                {hasTimedOut ? 'Loading is taking longer than expected...' : 'Loading...'}
            </p>
        </div>
    );

    const suspenseContent: React.JSX.Element = (
        <Suspense fallback={fallback || defaultFallback}>
            {children}
        </Suspense>
    );

    if (ErrorBoundary) {
        return <ErrorBoundary>{suspenseContent}</ErrorBoundary>;
    }

    return suspenseContent;
};

// Route-based code splitting helper
export const createRouteComponent = <P extends RouteComponentProps>(
    importFn: () => Promise<{ default: ComponentType<P> }>,
    routeName: string
): ComponentType<P> => {
    const RouteComponent = createSmartLazy(importFn, {
        chunkName: `route-${routeName}`,
        preload: false,
        retryAttempts: 3
    });

    const RouteWrapper = (props: P) => (
        <SmartSuspense
            loadingComponent={() => (
                <div style={{
                    padding: '2rem',
                    textAlign: 'center',
                    minHeight: '50vh',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexDirection: 'column'
                }}>
                    <div className="loading-spinner" />
                    <p>Loading {routeName}...</p>
                </div>
            )}
        >
            <RouteComponent {...props} />
        </SmartSuspense>
    );

    return RouteWrapper;
};

// Preload manager for critical routes
class PreloadManager {
    preloadQueue: Map<string, PreloadRoute>;
    preloadedRoutes: Set<string>;
    intersectionObserver: IntersectionObserver | null;

    constructor() {
        this.preloadQueue = new Map();
        this.preloadedRoutes = new Set();
        this.intersectionObserver = null;

        this.init();
    }

    init(): void {
        // Create intersection observer for hover-based preloading
        if ('IntersectionObserver' in window) {
            this.intersectionObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const route = (entry.target as HTMLElement).dataset.preloadRoute;
                        if (route && this.preloadQueue.has(route)) {
                            this.preloadRoute(route);
                        }
                    }
                });
            }, { rootMargin: '100px' });
        }
    }

    addRoute(routeName: string, importFn: () => Promise<any>, priority: 'high' | 'normal' | 'low' = 'normal'): void {
        this.preloadQueue.set(routeName, { importFn, priority });
    }

    preloadRoute(routeName: string): void {
        if (this.preloadedRoutes.has(routeName)) return;

        const route = this.preloadQueue.get(routeName);
        if (!route) return;

        console.log(`🚀 Preloading route: ${routeName}`);

        route.importFn()
            .then(() => {
                this.preloadedRoutes.add(routeName);
                console.log(`✅ Route preloaded: ${routeName}`);
            })
            .catch(error => {
                console.error(`❌ Failed to preload route ${routeName}:`, error);
            });
    }

    preloadCriticalRoutes(): void {
        // Preload high-priority routes
        this.preloadQueue.forEach((route, routeName) => {
            if (route.priority === 'high') {
                this.preloadRoute(routeName);
            }
        });
    }

    observeElement(element: HTMLElement | null, routeName: string): void {
        if (this.intersectionObserver && element) {
            element.dataset.preloadRoute = routeName;
            this.intersectionObserver.observe(element);
        }
    }

    cleanup(): void {
        if (this.intersectionObserver) {
            this.intersectionObserver.disconnect();
        }
    }
}

// Global instances
let bundleAnalyzer: BundleAnalyzer | null = null;
let preloadManager: PreloadManager | null = null;

// Initialize bundle analyzer
export const initBundleAnalyzer = (): BundleAnalyzer => {
    if (!bundleAnalyzer && typeof window !== 'undefined') {
        bundleAnalyzer = new BundleAnalyzer();
    }
    return bundleAnalyzer!;
};

// Initialize preload manager
export const initPreloadManager = (): PreloadManager => {
    if (!preloadManager && typeof window !== 'undefined') {
        preloadManager = new PreloadManager();
    }
    return preloadManager!;
};

// Hook for bundle analysis
export const useBundleAnalyzer = () => {
    const analyzer = initBundleAnalyzer();

    return {
        getStats: () => analyzer?.getChunkStats() || {
            totalChunks: 0,
            totalSize: 0,
            averageLoadTime: 0,
            slowestChunks: [],
            failedChunks: [],
            preloadedChunks: []
        },
        generateReport: () => analyzer?.generateBundleReport() || {
            totalChunks: 0,
            totalSize: 0,
            averageLoadTime: 0,
            slowestChunks: [],
            failedChunks: [],
            preloadedChunks: []
        }
    };
};

// Hook for preload management
export const usePreloadManager = () => {
    const manager = initPreloadManager();

    return {
        addRoute: (routeName: string, importFn: () => Promise<any>, priority: 'high' | 'normal' | 'low' = 'normal') =>
            manager?.addRoute(routeName, importFn, priority),
        preloadRoute: (routeName: string) => manager?.preloadRoute(routeName),
        preloadCritical: () => manager?.preloadCriticalRoutes(),
        observeElement: (element: HTMLElement | null, routeName: string) => manager?.observeElement(element, routeName)
    };
};

// Performance-optimized component wrapper
export const withCodeSplitting = <P extends object>(
    importFn: () => Promise<{ default: ComponentType<P> }>,
    options: SmartLazyOptions & { suspenseProps?: Partial<SmartSuspenseProps> } = {}
): ComponentType<P> => {
    const {
        suspenseProps = {},
        preload = false,
        chunkName
    } = options;

    const LazyComponent = createSmartLazy(importFn, {
        preload,
        chunkName,
        retryAttempts: 3
    });

    return (props: P) => (
        <SmartSuspense {...suspenseProps}>
            <LazyComponent {...props} />
        </SmartSuspense>
    );
};

export {
    BundleAnalyzer,
    PreloadManager,
    bundleAnalyzer,
    preloadManager
};

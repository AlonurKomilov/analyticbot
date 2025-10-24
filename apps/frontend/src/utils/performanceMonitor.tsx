/**
 * Performance Monitoring Component
 * Tracks and reports frontend performance metrics
 */

import { useEffect, useRef } from 'react';
import type { ReactNode } from 'react';

interface PerformanceMetrics {
    loadTime: number;
    renderTime: number;
    bundleSize: number;
    chunkLoadTimes: Map<string, number>;
    memoryUsage: number;
    networkRequests: number;
}

interface PerformanceObservers {
    navigation: PerformanceObserver | null;
    resource: PerformanceObserver | null;
    memory: PerformanceObserver | null;
}

interface MetricsReport {
    loadTime: number;
    renderTime: number;
    bundleSize: number;
    chunkLoadTimes: Record<string, number>;
    memoryUsage: number;
    networkRequests: number;
    timestamp: number;
}

interface PerformanceHookOptions {
    autoReport?: boolean;
    reportInterval?: number;
    trackUserInteractions?: boolean;
}

interface PerformanceHookReturn {
    getMetrics: () => MetricsReport;
    getScore: () => number;
    report: () => { metrics: MetricsReport; score: number };
}

interface PerformanceProviderProps {
    children: ReactNode;
    enabled?: boolean;
    autoReport?: boolean;
}

// Performance metrics collection
class PerformanceMonitor {
    metrics: PerformanceMetrics;
    observers: PerformanceObservers;

    constructor() {
        this.metrics = {
            loadTime: 0,
            renderTime: 0,
            bundleSize: 0,
            chunkLoadTimes: new Map(),
            memoryUsage: 0,
            networkRequests: 0
        };

        this.observers = {
            navigation: null,
            resource: null,
            memory: null
        };

        this.init();
    }

    init(): void {
        // Monitor page load performance
        this.monitorPageLoad();

        // Monitor resource loading
        this.monitorResourceLoading();

        // Monitor memory usage (if available)
        this.monitorMemoryUsage();

        // Monitor bundle loading
        this.monitorBundleLoading();
    }

    monitorPageLoad(): void {
        if ('performance' in window) {
            // Use Performance Observer for modern browsers
            if ('PerformanceObserver' in window) {
                const observer = new PerformanceObserver((list) => {
                    list.getEntries().forEach((entry) => {
                        if (entry.entryType === 'navigation') {
                            const navEntry = entry as PerformanceNavigationTiming;
                            this.metrics.loadTime = navEntry.loadEventEnd - navEntry.loadEventStart;
                        }

                        if (entry.entryType === 'measure' && entry.name === 'React') {
                            this.metrics.renderTime = entry.duration;
                        }
                    });
                });

                observer.observe({ entryTypes: ['navigation', 'measure'] });
                this.observers.navigation = observer;
            }

            // Fallback for older browsers
            window.addEventListener('load', () => {
                const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming | undefined;
                if (navigation) {
                    this.metrics.loadTime = navigation.loadEventEnd - navigation.loadEventStart;
                }
            });
        }
    }

    monitorResourceLoading(): void {
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
                list.getEntries().forEach((entry) => {
                    if (entry.name.includes('.js') || entry.name.includes('.css')) {
                        const chunkName = this.extractChunkName(entry.name);
                        if (chunkName) {
                            this.metrics.chunkLoadTimes.set(chunkName, entry.duration);
                        }

                        // Track total bundle size (approximate)
                        const resourceEntry = entry as PerformanceResourceTiming;
                        if (resourceEntry.transferSize) {
                            this.metrics.bundleSize += resourceEntry.transferSize;
                        }
                    }

                    this.metrics.networkRequests++;
                });
            });

            observer.observe({ entryTypes: ['resource'] });
            this.observers.resource = observer;
        }
    }

    monitorMemoryUsage(): void {
        const perfWithMemory = performance as Performance & {
            memory?: {
                usedJSHeapSize: number;
                totalJSHeapSize: number;
                jsHeapSizeLimit: number;
            };
        };

        if ('memory' in performance && perfWithMemory.memory) {
            // Monitor memory usage periodically
            const checkMemory = () => {
                if (perfWithMemory.memory) {
                    this.metrics.memoryUsage = perfWithMemory.memory.usedJSHeapSize / 1024 / 1024; // MB
                }
            };

            checkMemory();
            setInterval(checkMemory, 30000); // Every 30 seconds
        }
    }

    monitorBundleLoading(): void {
        // Track dynamic imports (lazy loaded components)
        const windowWithImport = window as Window & { __import?: (...args: any[]) => Promise<any> };
        const originalImport = windowWithImport.__import || (() => Promise.resolve());

        windowWithImport.__import = async (...args: any[]) => {
            const start = performance.now();

            try {
                const result = await originalImport(...args);
                const end = performance.now();

                const chunkName = this.extractChunkName(args[0]?.toString() || 'unknown');
                this.metrics.chunkLoadTimes.set(`dynamic-${chunkName}`, end - start);

                return result;
            } catch (error) {
                console.error('Dynamic import failed:', error);
                throw error;
            }
        };
    }

    extractChunkName(url: string): string | null {
        // Extract chunk name from URL
        const match = url.match(/\/js\/([^-]+)/);
        return match ? match[1] : null;
    }

    getMetrics(): MetricsReport {
        return {
            ...this.metrics,
            chunkLoadTimes: Object.fromEntries(this.metrics.chunkLoadTimes),
            timestamp: Date.now()
        };
    }

    getPerformanceScore(): number {
        const metrics = this.getMetrics();
        let score = 100;

        // Penalize slow load times
        if (metrics.loadTime > 3000) score -= 20;
        else if (metrics.loadTime > 1500) score -= 10;

        // Penalize large bundle size
        if (metrics.bundleSize > 2000000) score -= 15; // 2MB
        else if (metrics.bundleSize > 1000000) score -= 10; // 1MB

        // Penalize high memory usage
        if (metrics.memoryUsage > 100) score -= 15; // 100MB
        else if (metrics.memoryUsage > 50) score -= 10; // 50MB

        // Penalize too many network requests
        if (metrics.networkRequests > 50) score -= 10;
        else if (metrics.networkRequests > 30) score -= 5;

        return Math.max(0, Math.min(100, score));
    }

    reportMetrics(): { metrics: MetricsReport; score: number } {
        const metrics = this.getMetrics();
        const score = this.getPerformanceScore();

        console.group('🚀 Performance Metrics');
        console.log('📊 Load Time:', `${metrics.loadTime.toFixed(2)}ms`);
        console.log('🎨 Render Time:', `${metrics.renderTime.toFixed(2)}ms`);
        console.log('📦 Bundle Size:', `${(metrics.bundleSize / 1024).toFixed(2)}KB`);
        console.log('🧠 Memory Usage:', `${metrics.memoryUsage.toFixed(2)}MB`);
        console.log('🌐 Network Requests:', metrics.networkRequests);
        console.log('🏆 Performance Score:', `${score}/100`);

        if (Object.keys(metrics.chunkLoadTimes).length > 0) {
            console.group('📦 Chunk Load Times');
            Object.entries(metrics.chunkLoadTimes).forEach(([chunk, time]) => {
                console.log(`${chunk}:`, `${time.toFixed(2)}ms`);
            });
            console.groupEnd();
        }

        console.groupEnd();

        return { metrics, score };
    }

    cleanup(): void {
        // Cleanup observers
        Object.values(this.observers).forEach(observer => {
            if (observer && observer.disconnect) {
                observer.disconnect();
            }
        });
    }
}

// Global performance monitor instance
let performanceMonitor: PerformanceMonitor | null = null;

/**
 * Performance Monitor Hook
 */
export const usePerformanceMonitor = (options: PerformanceHookOptions = {}): PerformanceHookReturn => {
    const {
        autoReport = false,
        reportInterval = 30000, // 30 seconds
        trackUserInteractions = true
    } = options;

    const monitorRef = useRef<PerformanceMonitor | null>(null);

    useEffect(() => {
        // Initialize performance monitor
        if (!performanceMonitor) {
            performanceMonitor = new PerformanceMonitor();
            monitorRef.current = performanceMonitor;
        }

        // Auto-reporting
        let reportIntervalId: NodeJS.Timeout | undefined;
        if (autoReport) {
            reportIntervalId = setInterval(() => {
                performanceMonitor?.reportMetrics();
            }, reportInterval);
        }

        // Track user interactions
        if (trackUserInteractions) {
            const trackInteraction = (event: Event) => {
                console.log(`🖱️ User interaction: ${event.type}`);
            };

            ['click', 'scroll', 'keydown'].forEach(eventType => {
                document.addEventListener(eventType, trackInteraction, { passive: true });
            });

            return () => {
                ['click', 'scroll', 'keydown'].forEach(eventType => {
                    document.removeEventListener(eventType, trackInteraction);
                });

                if (reportIntervalId) {
                    clearInterval(reportIntervalId);
                }
            };
        }

        return () => {
            if (reportIntervalId) {
                clearInterval(reportIntervalId);
            }
        };
    }, [autoReport, reportInterval, trackUserInteractions]);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            if (monitorRef.current) {
                monitorRef.current.cleanup();
            }
        };
    }, []);

    return {
        getMetrics: () => performanceMonitor?.getMetrics() || {
            loadTime: 0,
            renderTime: 0,
            bundleSize: 0,
            chunkLoadTimes: {},
            memoryUsage: 0,
            networkRequests: 0,
            timestamp: Date.now()
        },
        getScore: () => performanceMonitor?.getPerformanceScore() || 0,
        report: () => performanceMonitor?.reportMetrics() || {
            metrics: {
                loadTime: 0,
                renderTime: 0,
                bundleSize: 0,
                chunkLoadTimes: {},
                memoryUsage: 0,
                networkRequests: 0,
                timestamp: Date.now()
            },
            score: 0
        }
    };
};

/**
 * Performance Monitor Component
 */
export const PerformanceMonitorProvider = ({
    children,
    enabled = process.env.NODE_ENV === 'development',
    autoReport = true
}: PerformanceProviderProps): React.JSX.Element => {
    const { report } = usePerformanceMonitor({
        autoReport: enabled && autoReport,
        reportInterval: 60000 // 1 minute in development
    });

    useEffect(() => {
        if (enabled) {
            // Report initial metrics after app load
            setTimeout(() => {
                const result = report();

                // Send metrics to analytics if in production
                const windowWithGtag = window as Window & { gtag?: (...args: any[]) => void };
                if (process.env.NODE_ENV === 'production' && windowWithGtag.gtag) {
                    windowWithGtag.gtag('event', 'performance_metrics', {
                        custom_parameter: {
                            load_time: result.metrics.loadTime,
                            bundle_size: result.metrics.bundleSize,
                            memory_usage: result.metrics.memoryUsage,
                            performance_score: result.score
                        }
                    });
                }
            }, 3000);
        }
    }, [enabled, report]);

    return <>{children}</>;
};

export default PerformanceMonitor;

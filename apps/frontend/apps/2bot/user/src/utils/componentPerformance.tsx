/**
 * Advanced Component Performance Monitoring
 * Tracks React component render performance and optimization opportunities
 */

import React, { useEffect, useRef, useState, useMemo, ComponentType, ReactNode } from 'react';
import { uiLogger } from '@/utils/logger';

interface ComponentMetrics {
    totalRenderTime: number;
    renderCount: number;
    averageRenderTime: number;
    maxRenderTime: number;
    wastedRenders: number;
    lastRenderProps: Record<string, any> | null;
}

interface OptimizationReport {
    slowComponents: Array<{
        name: string;
        averageRenderTime: number;
        renderCount: number;
        maxRenderTime: number;
        wastedRenders: number;
    }>;
    wastedRenders: Array<{
        name: string;
        wastedRenders: number;
    }>;
    heavyComponents: string[];
    totalComponents: number;
}

interface RenderProfilerProps {
    name: string;
    children: ReactNode;
    onRender?: (name: string, duration: number) => void;
    trackProps?: boolean;
}

interface PerformanceDevToolsProps {
    enabled?: boolean;
}

// Component performance tracker
class ComponentPerformanceTracker {
    componentMetrics: Map<string, ComponentMetrics>;
    renderCounts: Map<string, number>;
    wastedRenders: Map<string, number>;
    heavyComponents: Set<string>;
    performanceObserver: PerformanceObserver | null;

    constructor() {
        this.componentMetrics = new Map();
        this.renderCounts = new Map();
        this.wastedRenders = new Map();
        this.heavyComponents = new Set();
        this.performanceObserver = null;

        this.init();
    }

    init(): void {
        // Track long tasks that might indicate heavy component renders
        if ('PerformanceObserver' in window) {
            this.performanceObserver = new PerformanceObserver((list) => {
                list.getEntries().forEach((entry) => {
                    if (entry.entryType === 'longtask' && entry.duration > 50) {
                        uiLogger.warn('Long task detected', { duration: entry.duration.toFixed(2) });
                    }
                });
            });

            this.performanceObserver.observe({ entryTypes: ['longtask'] });
        }
    }

    trackComponentRender(componentName: string, renderTime: number, props: Record<string, any> = {}, _prevProps: Record<string, any> = {}): ComponentMetrics {
        // Initialize component metrics
        if (!this.componentMetrics.has(componentName)) {
            this.componentMetrics.set(componentName, {
                totalRenderTime: 0,
                renderCount: 0,
                averageRenderTime: 0,
                maxRenderTime: 0,
                wastedRenders: 0,
                lastRenderProps: null
            });
        }

        const metrics = this.componentMetrics.get(componentName)!;

        // Update render count
        metrics.renderCount++;
        this.renderCounts.set(componentName, metrics.renderCount);

        // Update render time metrics
        metrics.totalRenderTime += renderTime;
        metrics.averageRenderTime = metrics.totalRenderTime / metrics.renderCount;
        metrics.maxRenderTime = Math.max(metrics.maxRenderTime, renderTime);

        // Check for wasted renders (same props)
        if (metrics.lastRenderProps && this.arePropsEqual(props, metrics.lastRenderProps)) {
            metrics.wastedRenders++;
            this.wastedRenders.set(componentName, metrics.wastedRenders);
            uiLogger.warn('Potentially wasted render', { component: componentName });
        }

        metrics.lastRenderProps = { ...props };

        // Mark as heavy component if consistently slow
        if (metrics.averageRenderTime > 16) { // More than one frame at 60fps
            this.heavyComponents.add(componentName);
        }

        // Log performance warnings
        if (renderTime > 50) {
            uiLogger.warn('Slow render detected', { component: componentName, renderTime: renderTime.toFixed(2) });
        }

        return metrics;
    }

    arePropsEqual(props1: Record<string, any>, props2: Record<string, any>): boolean {
        const keys1 = Object.keys(props1);
        const keys2 = Object.keys(props2);

        if (keys1.length !== keys2.length) return false;

        return keys1.every(key => {
            const val1 = props1[key];
            const val2 = props2[key];

            // Shallow comparison
            if (typeof val1 === 'object' && typeof val2 === 'object') {
                return JSON.stringify(val1) === JSON.stringify(val2);
            }

            return val1 === val2;
        });
    }

    getComponentMetrics(componentName: string): ComponentMetrics | null {
        return this.componentMetrics.get(componentName) || null;
    }

    getAllMetrics(): Record<string, ComponentMetrics> {
        return Object.fromEntries(this.componentMetrics);
    }

    getTopSlowComponents(limit: number = 5): Array<{ name: string } & ComponentMetrics> {
        return Array.from(this.componentMetrics.entries())
            .sort(([, a], [, b]) => b.averageRenderTime - a.averageRenderTime)
            .slice(0, limit)
            .map(([name, metrics]) => ({ name, ...metrics }));
    }

    getTopWastedRenders(limit: number = 5): Array<{ name: string; wastedRenders: number }> {
        return Array.from(this.componentMetrics.entries())
            .filter(([, metrics]) => metrics.wastedRenders > 0)
            .sort(([, a], [, b]) => b.wastedRenders - a.wastedRenders)
            .slice(0, limit)
            .map(([name, metrics]) => ({ name, wastedRenders: metrics.wastedRenders }));
    }

    generateOptimizationReport(): OptimizationReport {
        const slowComponents = this.getTopSlowComponents();
        const wastedRenders = this.getTopWastedRenders();

        const reportData: any = {
            slowComponents: [],
            wastedRenders: [],
            heavyComponents: [],
            totalComponents: this.componentMetrics.size
        };

        if (slowComponents.length > 0) {
            reportData.slowComponents = slowComponents.map(({ name, averageRenderTime, renderCount, maxRenderTime }) => ({
                name,
                avgRenderTime: `${averageRenderTime.toFixed(2)}ms`,
                maxRenderTime: `${maxRenderTime.toFixed(2)}ms`,
                renderCount,
                recommendation: averageRenderTime > 16 ? 'Consider memoization or code splitting' : 'Performance is acceptable'
            }));
        }

        if (wastedRenders.length > 0) {
            reportData.wastedRenders = wastedRenders.map(({ name, wastedRenders }) => ({
                name,
                wastedRenders,
                recommendation: 'Consider using React.memo or useMemo'
            }));
        }

        // Heavy components recommendations
        if (this.heavyComponents.size > 0) {
            reportData.heavyComponents = Array.from(this.heavyComponents).map(componentName => {
                const metrics = this.componentMetrics.get(componentName);
                return {
                    component: componentName,
                    recommendations: [
                        'Consider code splitting with React.lazy()',
                        'Use React.memo() to prevent unnecessary re-renders',
                        'Optimize expensive calculations with useMemo()',
                        'Consider virtualizing large lists',
                        metrics && metrics.wastedRenders > 5 ? 'Check for prop drilling or unnecessary prop changes' : null
                    ].filter(Boolean)
                };
            });
        }

        uiLogger.debug('Component Performance Optimization Report', reportData);

        return {
            slowComponents,
            wastedRenders,
            heavyComponents: Array.from(this.heavyComponents),
            totalComponents: this.componentMetrics.size
        };
    }

    cleanup(): void {
        if (this.performanceObserver) {
            this.performanceObserver.disconnect();
        }
    }
}

// Global tracker instance
let componentTracker: ComponentPerformanceTracker | null = null;

// Performance tracking hook
export const useComponentPerformance = (componentName: string, props: Record<string, any> = {}) => {
    const renderStartTime = useRef(performance.now());
    const prevProps = useRef(props);
    const renderCount = useRef(0);

    // Initialize tracker
    if (!componentTracker) {
        componentTracker = new ComponentPerformanceTracker();
    }

    // Track render start
    useEffect(() => {
        renderStartTime.current = performance.now();
        renderCount.current++;
    });

    // Track render end
    useEffect(() => {
        const renderEndTime = performance.now();
        const renderTime = renderEndTime - renderStartTime.current;

        if (componentTracker) {
            componentTracker.trackComponentRender(
                componentName,
                renderTime,
                props,
                prevProps.current
            );
        }

        prevProps.current = props;
    });

    return {
        getMetrics: () => componentTracker?.getComponentMetrics(componentName) || null,
        renderCount: renderCount.current
    };
};

// Render profiler component
export const RenderProfiler = ({
    name,
    children,
    onRender,
}: RenderProfilerProps): React.JSX.Element => {
    const [_renderTime, setRenderTime] = useState(0);
    const startTime = useRef(performance.now());

    useEffect(() => {
        startTime.current = performance.now();
    });

    useEffect(() => {
        const endTime = performance.now();
        const duration = endTime - startTime.current;
        setRenderTime(duration);

        if (onRender) {
            onRender(name, duration);
        }

        // Track with global tracker
        if (!componentTracker) {
            componentTracker = new ComponentPerformanceTracker();
        }

        componentTracker.trackComponentRender(name, duration);
    });

    return <>{children}</>;
};

// Performance monitoring wrapper
export const withPerformanceMonitoring = <P extends object>(
    WrappedComponent: ComponentType<P>,
    componentName?: string
): ComponentType<P> => {
    const PerformanceMonitoredComponent = (props: P) => {
        const displayName = componentName || WrappedComponent.displayName || WrappedComponent.name || 'Component';
        useComponentPerformance(displayName, props as Record<string, any>);

        // Memoize the component to prevent unnecessary re-renders
        const MemoizedComponent = useMemo(() => {
            return React.memo(WrappedComponent);
        }, []);

        return (
            <RenderProfiler name={displayName}>
                <MemoizedComponent {...props} />
            </RenderProfiler>
        );
    };

    PerformanceMonitoredComponent.displayName = `withPerformanceMonitoring(${componentName || WrappedComponent.displayName || WrappedComponent.name || 'Component'})`;

    return PerformanceMonitoredComponent;
};

// Performance DevTools component
export const PerformanceDevTools = ({ enabled = process.env.NODE_ENV === 'development' }: PerformanceDevToolsProps): React.JSX.Element | null => {
    const [isVisible, setIsVisible] = useState(false);
    const [report, setReport] = useState<OptimizationReport | null>(null);

    useEffect(() => {
        if (!enabled || !componentTracker) return;

        const handleKeyPress = (event: KeyboardEvent) => {
            // Ctrl/Cmd + Shift + P to toggle performance DevTools
            if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'P') {
                event.preventDefault();
                setIsVisible(!isVisible);

                if (!isVisible && componentTracker) {
                    const newReport = componentTracker.generateOptimizationReport();
                    setReport(newReport);
                }
            }
        };

        document.addEventListener('keydown', handleKeyPress);

        return () => {
            document.removeEventListener('keydown', handleKeyPress);
        };
    }, [enabled, isVisible]);

    if (!enabled || !isVisible || !report) return null;

    return (
        <div style={{
            position: 'fixed',
            top: '20px',
            right: '20px',
            width: '400px',
            maxHeight: '600px',
            overflowY: 'auto',
            backgroundColor: '#1e1e1e',
            color: '#ffffff',
            padding: '16px',
            borderRadius: '8px',
            boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
            fontFamily: 'monospace',
            fontSize: '12px',
            zIndex: 10000,
            border: '1px solid #333'
        }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <h3 style={{ margin: 0, color: '#4CAF50' }}>⚡ Performance DevTools</h3>
                <button
                    onClick={() => setIsVisible(false)}
                    style={{
                        background: 'none',
                        border: 'none',
                        color: '#ffffff',
                        cursor: 'pointer',
                        fontSize: '16px'
                    }}
                >
                    ✕
                </button>
            </div>

            <div style={{ marginBottom: '16px' }}>
                <strong>📊 Total Components Tracked: {report.totalComponents}</strong>
            </div>

            {report.slowComponents.length > 0 && (
                <div style={{ marginBottom: '16px' }}>
                    <h4 style={{ color: '#FFA726', margin: '0 0 8px 0' }}>🐌 Slowest Components</h4>
                    {report.slowComponents.map(({ name, averageRenderTime, renderCount }) => (
                        <div key={name} style={{ marginBottom: '4px', paddingLeft: '8px' }}>
                            <strong>{name}</strong>: {averageRenderTime.toFixed(2)}ms avg ({renderCount} renders)
                        </div>
                    ))}
                </div>
            )}

            {report.wastedRenders.length > 0 && (
                <div style={{ marginBottom: '16px' }}>
                    <h4 style={{ color: '#FF7043', margin: '0 0 8px 0' }}>🔄 Wasted Renders</h4>
                    {report.wastedRenders.map(({ name, wastedRenders }) => (
                        <div key={name} style={{ marginBottom: '4px', paddingLeft: '8px' }}>
                            <strong>{name}</strong>: {wastedRenders} wasted renders
                        </div>
                    ))}
                </div>
            )}

            <div style={{ fontSize: '10px', opacity: 0.7, marginTop: '16px' }}>
                Press Ctrl/Cmd + Shift + P to toggle
            </div>
        </div>
    );
};

export { ComponentPerformanceTracker };
export default componentTracker;

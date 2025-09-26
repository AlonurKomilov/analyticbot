/**
 * Advanced Component Performance Monitoring
 * Tracks React component render performance and optimization opportunities
 */

import { useEffect, useRef, useState, useMemo } from 'react';

// Component performance tracker
class ComponentPerformanceTracker {
    constructor() {
        this.componentMetrics = new Map();
        this.renderCounts = new Map();
        this.wastedRenders = new Map();
        this.heavyComponents = new Set();
        this.performanceObserver = null;
        
        this.init();
    }
    
    init() {
        // Track long tasks that might indicate heavy component renders
        if ('PerformanceObserver' in window) {
            this.performanceObserver = new PerformanceObserver((list) => {
                list.getEntries().forEach((entry) => {
                    if (entry.entryType === 'longtask' && entry.duration > 50) {
                        console.warn(`🐌 Long task detected: ${entry.duration.toFixed(2)}ms`);
                    }
                });
            });
            
            this.performanceObserver.observe({ entryTypes: ['longtask'] });
        }
    }
    
    trackComponentRender(componentName, renderTime, props = {}, prevProps = {}) {
        const now = performance.now();
        
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
        
        const metrics = this.componentMetrics.get(componentName);
        
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
            console.warn(`🔄 Potentially wasted render in ${componentName}`);
        }
        
        metrics.lastRenderProps = { ...props };
        
        // Mark as heavy component if consistently slow
        if (metrics.averageRenderTime > 16) { // More than one frame at 60fps
            this.heavyComponents.add(componentName);
        }
        
        // Log performance warnings
        if (renderTime > 50) {
            console.warn(`⚠️ Slow render in ${componentName}: ${renderTime.toFixed(2)}ms`);
        }
        
        return metrics;
    }
    
    arePropsEqual(props1, props2) {
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
    
    getComponentMetrics(componentName) {
        return this.componentMetrics.get(componentName) || null;
    }
    
    getAllMetrics() {
        return Object.fromEntries(this.componentMetrics);
    }
    
    getTopSlowComponents(limit = 5) {
        return Array.from(this.componentMetrics.entries())
            .sort(([, a], [, b]) => b.averageRenderTime - a.averageRenderTime)
            .slice(0, limit)
            .map(([name, metrics]) => ({ name, ...metrics }));
    }
    
    getTopWastedRenders(limit = 5) {
        return Array.from(this.componentMetrics.entries())
            .filter(([, metrics]) => metrics.wastedRenders > 0)
            .sort(([, a], [, b]) => b.wastedRenders - a.wastedRenders)
            .slice(0, limit)
            .map(([name, metrics]) => ({ name, wastedRenders: metrics.wastedRenders }));
    }
    
    generateOptimizationReport() {
        const slowComponents = this.getTopSlowComponents();
        const wastedRenders = this.getTopWastedRenders();
        
        console.group('🔧 Component Performance Optimization Report');
        
        if (slowComponents.length > 0) {
            console.group('🐌 Slowest Components');
            slowComponents.forEach(({ name, averageRenderTime, renderCount, maxRenderTime }) => {
                console.log(`${name}:`, {
                    avgRenderTime: `${averageRenderTime.toFixed(2)}ms`,
                    maxRenderTime: `${maxRenderTime.toFixed(2)}ms`,
                    renderCount,
                    recommendation: averageRenderTime > 16 ? 'Consider memoization or code splitting' : 'Performance is acceptable'
                });
            });
            console.groupEnd();
        }
        
        if (wastedRenders.length > 0) {
            console.group('🔄 Components with Wasted Renders');
            wastedRenders.forEach(({ name, wastedRenders }) => {
                console.log(`${name}: ${wastedRenders} wasted renders - Consider using React.memo or useMemo`);
            });
            console.groupEnd();
        }
        
        // Heavy components recommendations
        if (this.heavyComponents.size > 0) {
            console.group('⚡ Optimization Recommendations');
            this.heavyComponents.forEach(componentName => {
                const metrics = this.componentMetrics.get(componentName);
                console.log(`${componentName}:`, [
                    '• Consider code splitting with React.lazy()',
                    '• Use React.memo() to prevent unnecessary re-renders',
                    '• Optimize expensive calculations with useMemo()',
                    '• Consider virtualizing large lists',
                    metrics?.wastedRenders > 5 ? '• Check for prop drilling or unnecessary prop changes' : null
                ].filter(Boolean));
            });
            console.groupEnd();
        }
        
        console.groupEnd();
        
        return {
            slowComponents,
            wastedRenders,
            heavyComponents: Array.from(this.heavyComponents),
            totalComponents: this.componentMetrics.size
        };
    }
    
    cleanup() {
        if (this.performanceObserver) {
            this.performanceObserver.disconnect();
        }
    }
}

// Global tracker instance
let componentTracker = null;

// Performance tracking hook
export const useComponentPerformance = (componentName, props = {}) => {
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
        
        componentTracker.trackComponentRender(
            componentName,
            renderTime,
            props,
            prevProps.current
        );
        
        prevProps.current = props;
    });
    
    return {
        getMetrics: () => componentTracker.getComponentMetrics(componentName),
        renderCount: renderCount.current
    };
};

// Render profiler component
export const RenderProfiler = ({ 
    name, 
    children, 
    onRender,
    trackProps = true 
}) => {
    const [renderTime, setRenderTime] = useState(0);
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
    
    return children;
};

// Performance monitoring wrapper
export const withPerformanceMonitoring = (WrappedComponent, componentName) => {
    const PerformanceMonitoredComponent = (props) => {
        const { getMetrics } = useComponentPerformance(componentName || WrappedComponent.name, props);
        
        // Memoize the component to prevent unnecessary re-renders
        const MemoizedComponent = useMemo(() => {
            return React.memo(WrappedComponent);
        }, []);
        
        return (
            <RenderProfiler name={componentName || WrappedComponent.name}>
                <MemoizedComponent {...props} />
            </RenderProfiler>
        );
    };
    
    PerformanceMonitoredComponent.displayName = `withPerformanceMonitoring(${componentName || WrappedComponent.name})`;
    
    return PerformanceMonitoredComponent;
};

// Performance DevTools component
export const PerformanceDevTools = ({ enabled = process.env.NODE_ENV === 'development' }) => {
    const [isVisible, setIsVisible] = useState(false);
    const [report, setReport] = useState(null);
    
    useEffect(() => {
        if (!enabled || !componentTracker) return;
        
        const handleKeyPress = (event) => {
            // Ctrl/Cmd + Shift + P to toggle performance DevTools
            if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'P') {
                event.preventDefault();
                setIsVisible(!isVisible);
                
                if (!isVisible) {
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
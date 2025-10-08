/**
 * Core Web Vitals Monitoring
 * Tracks the three main Core Web Vitals metrics that Google uses for ranking
 */

import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

class CoreWebVitalsMonitor {
    constructor() {
        this.vitals = {
            cls: null,      // Cumulative Layout Shift
            fid: null,      // First Input Delay
            fcp: null,      // First Contentful Paint
            lcp: null,      // Largest Contentful Paint
            ttfb: null      // Time to First Byte
        };

        this.callbacks = [];
        this.init();
    }

    init() {
        // Track Cumulative Layout Shift
        getCLS((metric) => {
            this.vitals.cls = metric;
            this.notifyCallbacks('cls', metric);
        });

        // Track First Input Delay
        getFID((metric) => {
            this.vitals.fid = metric;
            this.notifyCallbacks('fid', metric);
        });

        // Track First Contentful Paint
        getFCP((metric) => {
            this.vitals.fcp = metric;
            this.notifyCallbacks('fcp', metric);
        });

        // Track Largest Contentful Paint
        getLCP((metric) => {
            this.vitals.lcp = metric;
            this.notifyCallbacks('lcp', metric);
        });

        // Track Time to First Byte
        getTTFB((metric) => {
            this.vitals.ttfb = metric;
            this.notifyCallbacks('ttfb', metric);
        });
    }

    onVitalUpdate(callback) {
        this.callbacks.push(callback);
    }

    notifyCallbacks(vitalName, metric) {
        this.callbacks.forEach(callback => {
            callback(vitalName, metric);
        });
    }

    getVitals() {
        return { ...this.vitals };
    }

    getVitalsScore() {
        const vitals = this.getVitals();
        let score = 100;

        // CLS scoring (Good: < 0.1, Needs improvement: 0.1-0.25, Poor: > 0.25)
        if (vitals.cls) {
            if (vitals.cls.value > 0.25) score -= 25;
            else if (vitals.cls.value > 0.1) score -= 15;
        }

        // FID scoring (Good: < 100ms, Needs improvement: 100-300ms, Poor: > 300ms)
        if (vitals.fid) {
            if (vitals.fid.value > 300) score -= 25;
            else if (vitals.fid.value > 100) score -= 15;
        }

        // LCP scoring (Good: < 2.5s, Needs improvement: 2.5-4s, Poor: > 4s)
        if (vitals.lcp) {
            if (vitals.lcp.value > 4000) score -= 25;
            else if (vitals.lcp.value > 2500) score -= 15;
        }

        // FCP scoring (Good: < 1.8s, Needs improvement: 1.8-3s, Poor: > 3s)
        if (vitals.fcp) {
            if (vitals.fcp.value > 3000) score -= 15;
            else if (vitals.fcp.value > 1800) score -= 10;
        }

        // TTFB scoring (Good: < 600ms, Needs improvement: 600-1500ms, Poor: > 1500ms)
        if (vitals.ttfb) {
            if (vitals.ttfb.value > 1500) score -= 10;
            else if (vitals.ttfb.value > 600) score -= 5;
        }

        return Math.max(0, Math.min(100, score));
    }

    reportVitals() {
        const vitals = this.getVitals();
        const score = this.getVitalsScore();

        console.group('🎯 Core Web Vitals');

        if (vitals.cls) {
            const clsRating = vitals.cls.value <= 0.1 ? '🟢 Good' :
                             vitals.cls.value <= 0.25 ? '🟡 Needs Improvement' : '🔴 Poor';
            console.log(`📏 CLS (Cumulative Layout Shift): ${vitals.cls.value.toFixed(3)} - ${clsRating}`);
        }

        if (vitals.fid) {
            const fidRating = vitals.fid.value <= 100 ? '🟢 Good' :
                             vitals.fid.value <= 300 ? '🟡 Needs Improvement' : '🔴 Poor';
            console.log(`⚡ FID (First Input Delay): ${vitals.fid.value.toFixed(2)}ms - ${fidRating}`);
        }

        if (vitals.lcp) {
            const lcpRating = vitals.lcp.value <= 2500 ? '🟢 Good' :
                             vitals.lcp.value <= 4000 ? '🟡 Needs Improvement' : '🔴 Poor';
            console.log(`🖼️ LCP (Largest Contentful Paint): ${vitals.lcp.value.toFixed(2)}ms - ${lcpRating}`);
        }

        if (vitals.fcp) {
            const fcpRating = vitals.fcp.value <= 1800 ? '🟢 Good' :
                             vitals.fcp.value <= 3000 ? '🟡 Needs Improvement' : '🔴 Poor';
            console.log(`🎨 FCP (First Contentful Paint): ${vitals.fcp.value.toFixed(2)}ms - ${fcpRating}`);
        }

        if (vitals.ttfb) {
            const ttfbRating = vitals.ttfb.value <= 600 ? '🟢 Good' :
                              vitals.ttfb.value <= 1500 ? '🟡 Needs Improvement' : '🔴 Poor';
            console.log(`🚀 TTFB (Time to First Byte): ${vitals.ttfb.value.toFixed(2)}ms - ${ttfbRating}`);
        }

        console.log(`🏆 Overall Web Vitals Score: ${score}/100`);
        console.groupEnd();

        return { vitals, score };
    }

    sendToAnalytics(vitals) {
        // Send to Google Analytics 4
        if (window.gtag) {
            Object.entries(vitals).forEach(([vital, metric]) => {
                if (metric && metric.value !== undefined) {
                    window.gtag('event', vital.toUpperCase(), {
                        value: Math.round(vital === 'cls' ? metric.value * 1000 : metric.value),
                        metric_id: metric.id,
                        metric_delta: metric.delta,
                        metric_rating: this.getRating(vital, metric.value)
                    });
                }
            });
        }

        // Send to custom analytics endpoint
        if (process.env.NODE_ENV === 'production') {
            fetch('/api/analytics/web-vitals', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    vitals,
                    timestamp: Date.now(),
                    userAgent: navigator.userAgent,
                    url: window.location.href
                })
            }).catch(console.error);
        }
    }

    getRating(vital, value) {
        const thresholds = {
            cls: [0.1, 0.25],
            fid: [100, 300],
            lcp: [2500, 4000],
            fcp: [1800, 3000],
            ttfb: [600, 1500]
        };

        const [good, needsImprovement] = thresholds[vital] || [0, Infinity];

        if (value <= good) return 'good';
        if (value <= needsImprovement) return 'needs-improvement';
        return 'poor';
    }
}

// Global instance
let coreWebVitalsMonitor = null;

export const initCoreWebVitals = () => {
    if (!coreWebVitalsMonitor && typeof window !== 'undefined') {
        coreWebVitalsMonitor = new CoreWebVitalsMonitor();

        // Auto-report vitals after page load
        window.addEventListener('load', () => {
            setTimeout(() => {
                const result = coreWebVitalsMonitor.reportVitals();
                coreWebVitalsMonitor.sendToAnalytics(result.vitals);
            }, 1000);
        });

        // Report vitals when page becomes hidden (user navigates away)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                const vitals = coreWebVitalsMonitor.getVitals();
                coreWebVitalsMonitor.sendToAnalytics(vitals);
            }
        });
    }

    return coreWebVitalsMonitor;
};

export const useCoreWebVitals = () => {
    const monitor = initCoreWebVitals();

    return {
        getVitals: () => monitor?.getVitals() || {},
        getScore: () => monitor?.getVitalsScore() || 0,
        report: () => monitor?.reportVitals() || { vitals: {}, score: 0 },
        onVitalUpdate: (callback) => monitor?.onVitalUpdate(callback)
    };
};

export default CoreWebVitalsMonitor;

/**
 * Specialized Analytics Hooks
 * Common use case patterns built on top of the unified analytics system
 */

import { useUnifiedAnalytics } from './useUnifiedAnalytics';
import { useMemo } from 'react';

/**
 * Dashboard Analytics Hook
 * Optimized for main dashboard with real-time updates
 */
export const useDashboardAnalytics = (channelId, options = {}) => {
    const {
        enableRealTime = true,
        refreshInterval = 30000,
        ...customConfig
    } = options;
    
    const analytics = useUnifiedAnalytics(channelId, 'DASHBOARD', {
        realTime: enableRealTime,
        interval: refreshInterval,
        ...customConfig
    });
    
    // Computed dashboard metrics
    const dashboardData = useMemo(() => {
        const { data } = analytics;
        
        return {
            // Key metrics for dashboard cards
            totalViews: data.overview?.total_views || 0,
            totalPosts: data.overview?.total_posts || 0,
            averageEngagement: data.engagement?.average_rate || 0,
            growthRate: data.growth?.rate_7d || 0,
            
            // Charts data
            viewsChart: data.overview?.views_chart || [],
            growthChart: data.growth?.growth_chart || [],
            engagementChart: data.engagement?.engagement_chart || [],
            
            // Status indicators
            isGrowing: (data.growth?.rate_7d || 0) > 0,
            hasGoodEngagement: (data.engagement?.average_rate || 0) > 3.0,
            
            // Raw data access
            raw: data
        };
    }, [analytics.data]);
    
    return {
        ...analytics,
        dashboardData,
        // Dashboard-specific helpers
        isHealthy: dashboardData.isGrowing && dashboardData.hasGoodEngagement,
        needsAttention: !dashboardData.isGrowing || dashboardData.averageEngagement < 2.0
    };
};

/**
 * Admin Analytics Hook  
 * Optimized for admin dashboard with system metrics
 */
export const useAdminAnalytics = (options = {}) => {
    const analytics = useUnifiedAnalytics('system', 'ADMIN', options);
    
    // Computed admin metrics
    const adminData = useMemo(() => {
        const { data } = analytics;
        
        return {
            // System health
            activeUsers: data.users?.active_count || 0,
            totalUsers: data.users?.total_count || 0,
            systemLoad: data.system?.cpu_usage || 0,
            memoryUsage: data.system?.memory_usage || 0,
            
            // Performance indicators
            apiResponseTime: data.system?.api_response_time || 0,
            errorRate: data.system?.error_rate || 0,
            uptime: data.system?.uptime || 0,
            
            // Status flags
            systemHealthy: (data.system?.status || 'unknown') === 'healthy',
            needsScaling: (data.system?.cpu_usage || 0) > 80,
            
            // Raw data
            raw: data
        };
    }, [analytics.data]);
    
    return {
        ...analytics,
        adminData,
        // Admin-specific helpers
        isSystemHealthy: adminData.systemHealthy && adminData.systemLoad < 80,
        requiresAttention: adminData.needsScaling || adminData.errorRate > 5
    };
};

/**
 * Mobile Analytics Hook
 * Lightweight hook optimized for mobile performance
 */
export const useMobileAnalytics = (channelId, options = {}) => {
    const {
        updateInterval = 60000, // Less frequent updates on mobile
        ...customConfig  
    } = options;
    
    const analytics = useUnifiedAnalytics(channelId, 'MOBILE', {
        interval: updateInterval,
        ...customConfig
    });
    
    // Simplified mobile data
    const mobileData = useMemo(() => {
        const { data } = analytics;
        
        return {
            // Essential metrics only
            views: data.quick?.views || data.overview?.total_views || 0,
            posts: data.quick?.posts || data.overview?.total_posts || 0,
            engagement: data.quick?.engagement || 0,
            
            // Simple trend indicator
            trend: data.quick?.trend || (data.growth?.rate_7d > 0 ? 'up' : 'down'),
            
            // Minimal chart data
            miniChart: data.quick?.mini_chart || [],
            
            // Status
            isOnline: analytics.connectionStatus === 'connected'
        };
    }, [analytics.data, analytics.connectionStatus]);
    
    return {
        ...analytics,
        mobileData,
        // Mobile-specific helpers
        batteryFriendly: true, // Indicates this hook is optimized for battery life
        dataEfficient: true   // Indicates minimal data usage
    };
};

/**
 * Performance Analytics Hook
 * Specialized for performance monitoring and alerts
 */
export const usePerformanceAnalytics = (channelId, options = {}) => {
    const analytics = useUnifiedAnalytics(channelId, 'PERFORMANCE', options);
    
    // Performance-focused metrics
    const performanceData = useMemo(() => {
        const { data } = analytics;
        
        const performanceScore = data.performance?.score || 0;
        const trends = data.trends?.performance_trends || [];
        const alerts = data.alerts?.active || [];
        
        return {
            // Performance scoring
            score: performanceScore,
            grade: performanceScore >= 85 ? 'A' : 
                   performanceScore >= 70 ? 'B' : 
                   performanceScore >= 55 ? 'C' : 'D',
            
            // Performance metrics
            responseTime: data.performance?.avg_response_time || 0,
            errorRate: data.performance?.error_rate || 0,
            throughput: data.performance?.requests_per_second || 0,
            
            // Trending data
            trends,
            trendDirection: trends.length > 1 ? 
                (trends[trends.length - 1].value > trends[trends.length - 2].value ? 'up' : 'down') : 'stable',
            
            // Alerts
            activeAlerts: alerts,
            criticalAlerts: alerts.filter(alert => alert.severity === 'critical'),
            
            // Raw data
            raw: data
        };
    }, [analytics.data]);
    
    return {
        ...analytics,
        performanceData,
        // Performance-specific helpers
        isPerformant: performanceData.score >= 70,
        needsOptimization: performanceData.score < 55,
        hasCriticalIssues: performanceData.criticalAlerts.length > 0
    };
};

/**
 * Real-time Analytics Hook
 * High-frequency updates for live monitoring
 */
export const useRealTimeAnalytics = (channelId, options = {}) => {
    const {
        interval = 10000, // 10 second updates for real-time
        metrics = ['overview', 'engagement'],
        ...customConfig
    } = options;
    
    const analytics = useUnifiedAnalytics(channelId, 'DASHBOARD', {
        realTime: true,
        interval,
        includeMetrics: metrics,
        caching: false, // No caching for real-time data
        ...customConfig
    });
    
    // Real-time specific data processing
    const realTimeData = useMemo(() => {
        const { data, lastUpdated } = analytics;
        
        return {
            // Live metrics
            liveViews: data.overview?.current_views || 0,
            liveEngagement: data.engagement?.current_rate || 0,
            
            // Freshness indicators
            dataAge: lastUpdated ? Date.now() - lastUpdated.getTime() : 0,
            isFresh: lastUpdated ? (Date.now() - lastUpdated.getTime()) < 30000 : false,
            
            // Connection quality
            connectionQuality: analytics.connectionStatus === 'connected' ? 'excellent' :
                              analytics.connectionStatus === 'partial' ? 'good' :
                              analytics.connectionStatus === 'cached' ? 'poor' : 'offline',
            
            // Raw data
            raw: data
        };
    }, [analytics.data, analytics.lastUpdated, analytics.connectionStatus]);
    
    return {
        ...analytics,
        realTimeData,
        // Real-time specific helpers
        isLive: analytics.connectionStatus === 'connected' && realTimeData.isFresh,
        connectionQuality: realTimeData.connectionQuality
    };
};

// All hooks are already exported inline above
// useHighFrequencyAnalytics is an alias for useRealTimeAnalytics
export { useRealTimeAnalytics as useHighFrequencyAnalytics };
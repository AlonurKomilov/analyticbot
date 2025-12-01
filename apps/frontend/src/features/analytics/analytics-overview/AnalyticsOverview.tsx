/**
 * AnalyticsOverview Component
 *
 * Analytics overview dashboard with comprehensive metrics, charts, and real-time data.
 * Integrates multiple data sources and provides rich visualization capabilities.
 */

import React, { useState, useEffect, useRef, useMemo } from 'react';
import { Box, Grid, Alert } from '@mui/material';
import { useAllAnalytics } from '@shared/hooks';
import { useUIStore } from '@store';

// Import extracted components
import DataSourceStatus from './DataSourceStatus';
import OverviewMetrics from './OverviewMetrics';
import DashboardCharts from './DashboardCharts';
import PerformanceScoreWidget from './PerformanceScoreWidget';

// Type assertions for JSX child components
const TypedDataSourceStatus = DataSourceStatus as any;
const TypedOverviewMetrics = OverviewMetrics as any;
const TypedDashboardCharts = DashboardCharts as any;
const TypedPerformanceScoreWidget = PerformanceScoreWidget as any;

interface AnalyticsOverviewProps {
    channelId?: string | null;
    lastUpdated?: Date;
}

interface Metrics {
    totalViews: number;
    growthRate: number;
    engagementRate: number;
    reachScore: number;
    activeUsers: number;
}

const AnalyticsOverview: React.FC<AnalyticsOverviewProps> = ({
    channelId,
    lastUpdated
}) => {
    // Show info message if no channel selected
    if (!channelId) {
        return (
            <Box sx={{ p: 3 }}>
                <Alert severity="info">
                    Please select a channel to view advanced analytics
                </Alert>
            </Box>
        );
    }

    const { dataSource } = useUIStore();
    const analyticsHook = useAllAnalytics(channelId);
    const [refreshing, setRefreshing] = useState(false);

    // Track previous lastUpdated to detect auto-refresh
    const prevLastUpdatedRef = useRef<Date | undefined>(undefined);

    // Extract values safely from hooks
    const isLoading = analyticsHook.isLoading || false;
    const hasError = analyticsHook.hasError || false;
    const actions = analyticsHook.actions || { refetchAll: () => {}, clearAllErrors: () => {} };

    // Determine if using real API
    const isUsingRealAPI = dataSource === 'api';

    // Create computed metrics from actual analytics data
    const metrics: Metrics = useMemo(() => {
        const analytics = analyticsHook.analytics as any;
        const engagement = analyticsHook.engagementMetrics as any;
        
        if (analytics) {
            return {
                totalViews: analytics.totalViews ?? analytics.total_views ?? 0,
                growthRate: analytics.growthRate ?? analytics.growth_rate ?? 0,
                engagementRate: engagement?.engagementRate ?? engagement?.engagement_rate ?? analytics.engagementRate ?? 0,
                reachScore: analytics.reachScore ?? analytics.reach_score ?? 0,
                activeUsers: analytics.activeUsers ?? analytics.active_users ?? analytics.subscriberCount ?? 0,
            };
        }
        
        // Return zeros if no data available
        return {
            totalViews: 0,
            growthRate: 0,
            engagementRate: 0,
            reachScore: 0,
            activeUsers: 0,
        };
    }, [analyticsHook.analytics, analyticsHook.engagementMetrics]);

    // Generate trends from analytics data
    const trends = useMemo(() => {
        const analytics = analyticsHook.analytics as any;
        if (!analytics) return [];
        
        // If analytics has trends data, use it
        if (analytics.trends && Array.isArray(analytics.trends)) {
            return analytics.trends;
        }
        
        // If analytics has daily_stats, transform to trends
        if (analytics.dailyStats || analytics.daily_stats) {
            const dailyData = analytics.dailyStats || analytics.daily_stats;
            if (Array.isArray(dailyData)) {
                return dailyData.map((day: any) => ({
                    date: day.date,
                    views: day.views ?? 0,
                    engagement: day.engagement ?? day.engagementRate ?? 0,
                }));
            }
        }
        
        return [];
    }, [analyticsHook.analytics]);

    // Handle silent auto-refresh when lastUpdated changes
    useEffect(() => {
        if (lastUpdated && prevLastUpdatedRef.current &&
            lastUpdated.getTime() !== prevLastUpdatedRef.current.getTime()) {
            console.log('🔄 AnalyticsOverview: Silent auto-refresh triggered');
            // Refresh data silently (without showing loading state)
            if (actions.refetchAll) {
                try {
                    actions.refetchAll();
                } catch (error: any) {
                    console.error('Silent refresh failed:', error);
                }
            }
        }
        prevLastUpdatedRef.current = lastUpdated;
    }, [lastUpdated, actions]);

    // Refresh handler
    const handleRefresh = async () => {
        setRefreshing(true);
        try {
            if (actions.refetchAll) {
                actions.refetchAll();
            }
        } catch (error) {
            console.error('Failed to refresh dashboard:', error);
        } finally {
            setTimeout(() => setRefreshing(false), 500);
        }
    };

    // Handle loading and error states
    if (isLoading && !refreshing) {
        return (
            <TypedDataSourceStatus
                isLoading={true}
                hasError={false}
                errors={{}}
                onRefresh={handleRefresh}
            />
        );
    }

    if (hasError) {
        return (
            <Box sx={{ p: 3 }}>
                <TypedDataSourceStatus
                    isLoading={false}
                    hasError={true}
                    errors={analyticsHook.errors || {}}
                    onRefresh={handleRefresh}
                    isUsingRealAPI={isUsingRealAPI}
                    dataSource={isUsingRealAPI ? 'Real API' : 'Demo Mode'}
                />
            </Box>
        );
    }

    return (
        <Box sx={{ p: 3 }}>
            {/* Header with Data Source Status */}
            <TypedDataSourceStatus
                isLoading={refreshing}
                hasError={false}
                errors={{}}
                onRefresh={handleRefresh}
                isUsingRealAPI={isUsingRealAPI}
                dataSource={isUsingRealAPI ? 'Real API' : 'Demo Mode'}
            />

            {/* Overview Metrics Grid */}
            <TypedOverviewMetrics metrics={metrics} />

            {/* Advanced Charts */}
            <Grid container spacing={3}>
                {/* Trends Chart */}
                <Grid item xs={12} lg={8}>
                    <TypedDashboardCharts trends={trends} />
                </Grid>

                {/* Performance Score Widget */}
                <TypedPerformanceScoreWidget metrics={metrics} />
            </Grid>
        </Box>
    );
};

export default AnalyticsOverview;

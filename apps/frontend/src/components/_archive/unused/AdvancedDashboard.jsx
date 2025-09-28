import React, { useState, useEffect } from 'react';
import {
    Grid,
    Box,
    Typography,
    Card,
    CardContent,
    Switch,
    FormControlLabel,
    Button,
    ButtonGroup,
    Chip,
    Alert,
    Skeleton,
    AppBar,
    Toolbar,
    IconButton,
    Tooltip,
    useTheme,
    useMediaQuery
} from '@mui/material';
import {
    Dashboard as DashboardIcon,
    Refresh as RefreshIcon,
    Settings as SettingsIcon,
    Fullscreen as FullscreenIcon,
    GetApp as ExportIcon,
    Schedule as ScheduleIcon,
    TrendingUp as TrendingUpIcon,
    Analytics as AnalyticsIcon,
    Speed as SpeedIcon
} from '@mui/icons-material';

// Import Week 7-8 mobile-optimized components
import MetricsCard from './MetricsCard';
import TrendsChart from './TrendsChart';
import { useRealTimeAnalytics, useQuickAnalytics, usePerformanceMetrics } from '../../hooks/useRealTimeAnalytics';

const AdvancedDashboard = ({ 
    userId, 
    compact = false, 
    mobileOptimized = true,
    autoRefresh = true,
    refreshInterval = 30000 
}) => {
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('md'));
    const [realTimeEnabled, setRealTimeEnabled] = useState(autoRefresh);
    const [viewMode, setViewMode] = useState(compact || isMobile ? 'compact' : 'detailed');
    const [selectedMetrics, setSelectedMetrics] = useState(['views', 'engagement', 'growth']);
    const [fullscreen, setFullscreen] = useState(false);
    const [lastRefresh, setLastRefresh] = useState(new Date());

    // Week 7-8 Real-time hooks with mobile optimization
    const {
        data: realTimeData,
        loading: realTimeLoading,
        error: realTimeError,
        isOnline,
        refresh: refreshRealTime
    } = useRealTimeAnalytics(userId, {
        enabled: realTimeEnabled,
        interval: refreshInterval
    });

    const {
        quickData,
        loading: quickLoading,
        refresh: refreshQuick
    } = useQuickAnalytics(userId);

    const {
        performanceData,
        loading: performanceLoading,
        refresh: refreshPerformance
    } = usePerformanceMetrics(userId);

    // Auto-refresh all data
    const handleRefreshAll = async () => {
        setLastRefresh(new Date());
        await Promise.all([
            refreshRealTime(),
            refreshQuick(),
            refreshPerformance()
        ]);
    };

    // Effect for auto-refresh
    useEffect(() => {
        if (realTimeEnabled && autoRefresh) {
            const interval = setInterval(() => {
                handleRefreshAll();
            }, refreshInterval);

            return () => clearInterval(interval);
        }
    }, [realTimeEnabled, autoRefresh, refreshInterval]);

    // Prepare metrics data for MetricsCard
    const metricsData = {
        totalViews: realTimeData?.totalViews || quickData?.views || 0,
        growthRate: performanceData?.growthRate || 0,
        engagementRate: realTimeData?.engagementRate || quickData?.engagement || 0,
        reachScore: performanceData?.reachScore || 0,
        activeUsers: realTimeData?.activeUsers || 0,
        performanceScore: performanceData?.score || 0
    };

    // Prepare trends data for TrendsChart
    const trendsData = realTimeData?.trends || [
        // Demo data if no real data available
        ...Array.from({ length: 7 }, (_, i) => ({
            name: `Day ${i + 1}`,
            date: new Date(Date.now() - (6 - i) * 24 * 60 * 60 * 1000).toLocaleDateString(),
            views: Math.floor(Math.random() * 1000) + 500,
            engagement: Math.floor(Math.random() * 100) + 50,
            reach: Math.floor(Math.random() * 500) + 200,
            growth: (Math.random() - 0.5) * 10
        }))
    ];

    const isLoading = realTimeLoading || quickLoading || performanceLoading;

    if (fullscreen) {
        return (
            <Box sx={{ 
                position: 'fixed', 
                top: 0, 
                left: 0, 
                right: 0, 
                bottom: 0, 
                bgcolor: 'background.default',
                zIndex: 9999,
                overflow: 'auto'
            }}>
                <AppBar position="static" elevation={0}>
                    <Toolbar>
                        <Typography variant="h6" sx={{ flexGrow: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                            <DashboardIcon />
                            Advanced Analytics Dashboard
                        </Typography>
                        <Tooltip title="Exit fullscreen">
                            <IconButton color="inherit" onClick={() => setFullscreen(false)}>
                                <FullscreenIcon />
                            </IconButton>
                        </Tooltip>
                    </Toolbar>
                </AppBar>
                <Box sx={{ p: 3, height: 'calc(100vh - 64px)', overflow: 'auto' }}>
                    <AdvancedDashboard 
                        userId={userId} 
                        compact={false} 
                        mobileOptimized={false}
                        autoRefresh={autoRefresh}
                        refreshInterval={refreshInterval}
                    />
                </Box>
            </Box>
        );
    }

    return (
        <Box sx={{ width: '100%', height: '100%' }}>
            {/* Dashboard Header */}
            <Card sx={{ mb: 3 }}>
                <CardContent>
                    <Box sx={{ 
                        display: 'flex', 
                        justifyContent: 'space-between', 
                        alignItems: 'center',
                        flexWrap: 'wrap',
                        gap: 2
                    }}>
                        <Box>
                            <Typography variant="h5" component="h1" sx={{ 
                                display: 'flex', 
                                alignItems: 'center', 
                                gap: 1,
                                mb: 1
                            }}>
                                <AnalyticsIcon color="primary" />
                                Advanced Analytics Dashboard
                                {mobileOptimized && (
                                    <Chip 
                                        label="Mobile Optimized" 
                                        size="small" 
                                        color="primary" 
                                        variant="outlined" 
                                    />
                                )}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Real-time analytics with mobile-first design • Last updated: {lastRefresh.toLocaleTimeString()}
                            </Typography>
                        </Box>

                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                            {/* Online/Offline Status */}
                            <Chip 
                                label={isOnline ? "Online" : "Offline"} 
                                size="small" 
                                color={isOnline ? "success" : "warning"}
                                sx={{ fontWeight: 600 }}
                            />

                            {/* View Mode Toggle */}
                            <ButtonGroup size="small" variant="outlined">
                                <Button 
                                    variant={viewMode === 'compact' ? 'contained' : 'outlined'}
                                    onClick={() => setViewMode('compact')}
                                    startIcon={<SpeedIcon />}
                                >
                                    Compact
                                </Button>
                                <Button 
                                    variant={viewMode === 'detailed' ? 'contained' : 'outlined'}
                                    onClick={() => setViewMode('detailed')}
                                    startIcon={<AnalyticsIcon />}
                                >
                                    Detailed
                                </Button>
                            </ButtonGroup>

                            {/* Real-time Toggle */}
                            <FormControlLabel
                                control={
                                    <Switch
                                        checked={realTimeEnabled}
                                        onChange={(e) => setRealTimeEnabled(e.target.checked)}
                                        color="primary"
                                    />
                                }
                                label="Real-time"
                                sx={{ ml: 1 }}
                            />

                            {/* Action Buttons */}
                            <Tooltip title="Refresh all data">
                                <IconButton 
                                    color="primary" 
                                    onClick={handleRefreshAll}
                                    disabled={isLoading}
                                >
                                    <RefreshIcon />
                                </IconButton>
                            </Tooltip>

                            <Tooltip title="Fullscreen view">
                                <IconButton color="primary" onClick={() => setFullscreen(true)}>
                                    <FullscreenIcon />
                                </IconButton>
                            </Tooltip>

                            <Tooltip title="Export data">
                                <IconButton color="primary">
                                    <ExportIcon />
                                </IconButton>
                            </Tooltip>
                        </Box>
                    </Box>
                </CardContent>
            </Card>

            {/* Error Handling */}
            {realTimeError && (
                <Alert severity="warning" sx={{ mb: 3 }}>
                    Real-time data connection issue. Showing cached data. {!isOnline && "You're currently offline."}
                </Alert>
            )}

            {/* Main Dashboard Content */}
            <Grid container spacing={3}>
                {/* Metrics Overview - Full Width */}
                <Grid item xs={12}>
                    {isLoading ? (
                        <Skeleton variant="rectangular" height={200} />
                    ) : (
                        <MetricsCard 
                            metrics={metricsData}
                            loading={isLoading}
                            onRefresh={handleRefreshAll}
                            showDetails={viewMode === 'detailed'}
                        />
                    )}
                </Grid>

                {/* Trends Chart */}
                <Grid item xs={12} lg={viewMode === 'detailed' ? 8 : 12}>
                    {isLoading ? (
                        <Skeleton variant="rectangular" height={400} />
                    ) : (
                        <TrendsChart
                            data={trendsData}
                            loading={isLoading}
                            title="Performance Trends"
                            onRefresh={refreshRealTime}
                            onExport={() => console.log('Export trends')}
                            height={viewMode === 'compact' ? 300 : 400}
                        />
                    )}
                </Grid>

                {/* Quick Stats - Only in detailed mode */}
                {viewMode === 'detailed' && (
                    <Grid item xs={12} lg={4}>
                        <Grid container spacing={2}>
                            {/* Real-time Metrics Cards */}
                            <Grid item xs={12}>
                                <Card>
                                    <CardContent>
                                        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <TrendingUpIcon color="success" />
                                            Quick Insights
                                        </Typography>
                                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                                            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                                <Typography variant="body2">Peak Hour:</Typography>
                                                <Typography variant="body2" fontWeight="bold">
                                                    {realTimeData?.peakHour || '14:00-15:00'}
                                                </Typography>
                                            </Box>
                                            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                                <Typography variant="body2">Top Content:</Typography>
                                                <Typography variant="body2" fontWeight="bold">
                                                    {realTimeData?.topContent || 'Analytics Tutorial'}
                                                </Typography>
                                            </Box>
                                            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                                <Typography variant="body2">Conversion Rate:</Typography>
                                                <Typography variant="body2" fontWeight="bold" color="success.main">
                                                    {realTimeData?.conversionRate || '12.5'}%
                                                </Typography>
                                            </Box>
                                            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                                <Typography variant="body2">Bounce Rate:</Typography>
                                                <Typography variant="body2" fontWeight="bold" color="warning.main">
                                                    {realTimeData?.bounceRate || '35.2'}%
                                                </Typography>
                                            </Box>
                                        </Box>
                                    </CardContent>
                                </Card>
                            </Grid>

                            {/* Schedule Summary */}
                            <Grid item xs={12}>
                                <Card>
                                    <CardContent>
                                        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <ScheduleIcon color="primary" />
                                            Upcoming Schedule
                                        </Typography>
                                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                                            <Chip label="2 posts scheduled today" size="small" color="primary" />
                                            <Chip label="5 posts this week" size="small" color="info" />
                                            <Chip label="Next: 2:30 PM" size="small" color="warning" />
                                        </Box>
                                    </CardContent>
                                </Card>
                            </Grid>
                        </Grid>
                    </Grid>
                )}

                {/* Mobile-specific Quick Actions */}
                {(isMobile || mobileOptimized) && (
                    <Grid item xs={12}>
                        <Card>
                            <CardContent>
                                <Typography variant="h6" gutterBottom>
                                    Quick Actions
                                </Typography>
                                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                    <Button 
                                        variant="outlined" 
                                        size="small" 
                                        startIcon={<RefreshIcon />}
                                        onClick={handleRefreshAll}
                                        disabled={isLoading}
                                    >
                                        Refresh
                                    </Button>
                                    <Button 
                                        variant="outlined" 
                                        size="small" 
                                        startIcon={<ExportIcon />}
                                    >
                                        Export
                                    </Button>
                                    <Button 
                                        variant="outlined" 
                                        size="small" 
                                        startIcon={<SettingsIcon />}
                                    >
                                        Settings
                                    </Button>
                                    <Button 
                                        variant="outlined" 
                                        size="small" 
                                        startIcon={<ScheduleIcon />}
                                    >
                                        Schedule
                                    </Button>
                                </Box>
                            </CardContent>
                        </Card>
                    </Grid>
                )}
            </Grid>

            {/* Footer Info */}
            <Box sx={{ mt: 4, textAlign: 'center' }}>
                <Typography variant="caption" color="text.secondary">
                    Advanced Analytics Dashboard v2.0 • Week 7-8 Mobile Preparation • 
                    {realTimeEnabled ? ` Auto-refresh: ${refreshInterval/1000}s` : ' Manual refresh mode'} • 
                    {isOnline ? 'Connected' : 'Offline mode'}
                </Typography>
            </Box>
        </Box>
    );
};

export default AdvancedDashboard;

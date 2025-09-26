import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
    Paper,
    Typography,
    Box,
    CircularProgress,
    Alert,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Chip,
    Grid,
    Card,
    CardContent
} from '@mui/material';
import {
    TrendingUp as TrendingUpIcon,
    Speed as SpeedIcon,
    Visibility as ViewsIcon,
    ShowChart as ChartIcon
} from '@mui/icons-material';

// Import our new hooks and services
import { usePostDynamics, useDataSource } from '../hooks/useDataSource.js';

// Stable Chart Component with Memoization
const StableChart = React.memo(({ data, timeRange }) => {
    // Dynamic import to prevent SSR issues and reduce bundle size
    const [ChartComponents, setChartComponents] = useState(null);
    const [chartError, setChartError] = useState(null);

    useEffect(() => {
        let mounted = true;
        
        const loadChartComponents = async () => {
            try {
                const recharts = await import('recharts');
                if (mounted) {
                    setChartComponents({
                        ResponsiveContainer: recharts.ResponsiveContainer,
                        AreaChart: recharts.AreaChart,
                        Area: recharts.Area,
                        XAxis: recharts.XAxis,
                        YAxis: recharts.YAxis,
                        CartesianGrid: recharts.CartesianGrid,
                        Tooltip: recharts.Tooltip,
                        Legend: recharts.Legend
                    });
                }
            } catch (error) {
                console.error('Failed to load chart components:', error);
                if (mounted) {
                    setChartError(error.message);
                }
            }
        };

        loadChartComponents();
        return () => { mounted = false; };
    }, []);

    if (chartError) {
        return (
            <Alert severity="error" sx={{ mt: 2 }}>
                Failed to load chart: {chartError}
            </Alert>
        );
    }

    if (!ChartComponents) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight={300}>
                <CircularProgress size={30} />
                <Typography variant="body2" sx={{ ml: 2 }}>
                    Loading chart components...
                </Typography>
            </Box>
        );
    }

    if (!data || data.length === 0) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight={300}>
                <Typography variant="body1" color="text.secondary">
                    No data available for the selected time range
                </Typography>
            </Box>
        );
    }

    const { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend } = ChartComponents;

    return (
        <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <defs>
                    <linearGradient id="colorViews" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#8884d8" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorLikes" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#82ca9d" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#82ca9d" stopOpacity={0}/>
                    </linearGradient>
                </defs>
                <XAxis 
                    dataKey="timestamp" 
                    tickFormatter={(value) => {
                        const date = new Date(value);
                        if (timeRange === '24h') {
                            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                        }
                        return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
                    }}
                />
                <YAxis />
                <CartesianGrid strokeDasharray="3 3" />
                <Tooltip 
                    labelFormatter={(value) => new Date(value).toLocaleString()}
                    formatter={(value, name) => [value.toLocaleString(), name]}
                />
                <Legend />
                <Area
                    type="monotone"
                    dataKey="views"
                    stackId="1"
                    stroke="#8884d8"
                    fillOpacity={1}
                    fill="url(#colorViews)"
                    name="Views"
                />
                <Area
                    type="monotone"
                    dataKey="likes"
                    stackId="1"
                    stroke="#82ca9d"
                    fillOpacity={1}
                    fill="url(#colorLikes)"
                    name="Likes"
                />
            </AreaChart>
        </ResponsiveContainer>
    );
});

// Enhanced Post View Dynamics Chart Component
const PostViewDynamicsChart = ({ 
    channelId = 'demo_channel',
    autoRefresh = false, 
    refreshInterval = 'disabled',
    showControls = true 
}) => {
    // State for UI controls
    const [timeRange, setTimeRange] = useState('24h');
    
    // Use our new data source hooks
    const { dataSource, isUsingRealAPI, apiStatus } = useDataSource();
    const { 
        data: rawData, 
        isLoading, 
        error, 
        refetch 
    } = usePostDynamics(channelId, timeRange);

    // Process raw data for chart display
    const processedData = useMemo(() => {
        if (!rawData?.timeline) return [];
        
        return rawData.timeline.map(item => ({
            timestamp: item.timestamp,
            views: item.views || 0,
            likes: item.likes || 0,
            shares: item.shares || 0,
            comments: item.comments || 0
        }));
    }, [rawData]);

    // Calculate summary metrics
    const summaryMetrics = useMemo(() => {
        if (!rawData?.summary) return null;
        
        const summary = rawData.summary;
        return {
            totalViews: summary.totalViews || 0,
            totalReactions: summary.totalReactions || 0,
            avgEngagement: summary.avgEngagement || 0,
            peakHour: summary.peakHour || '18:00',
            growthRate: summary.growthRate || 0
        };
    }, [rawData]);

    // Handle time range changes
    const handleTimeRangeChange = useCallback((event) => {
        const newTimeRange = event.target.value;
        setTimeRange(newTimeRange);
        // The usePostDynamics hook will automatically refetch when timeRange changes
    }, []);

    // Auto-refresh functionality
    useEffect(() => {
        if (!autoRefresh || refreshInterval === 'disabled') return;

        const intervalMs = {
            '30s': 30000,
            '1m': 60000,
            '5m': 300000
        }[refreshInterval] || 30000;

        console.log('PostViewDynamicsChart: Setting up auto-refresh every', intervalMs, 'ms');
        
        const interval = setInterval(() => {
            console.log('PostViewDynamicsChart: Auto-refreshing data');
            refetch(true); // Force refresh
        }, intervalMs);

        return () => clearInterval(interval);
    }, [autoRefresh, refreshInterval, refetch]);

    // Status indicator component
    const StatusIndicator = () => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Chip 
                icon={<ChartIcon />}
                label={isUsingRealAPI ? 'Live API Data' : 'Demo Data'}
                color={isUsingRealAPI ? 'primary' : 'default'}
                size="small"
            />
            {isUsingRealAPI && (
                <Chip 
                    label={apiStatus === 'online' ? 'API Online' : 'API Offline'}
                    color={apiStatus === 'online' ? 'success' : 'error'}
                    size="small"
                />
            )}
        </Box>
    );

    // Metrics cards component
    const MetricsCards = () => {
        if (!summaryMetrics) return null;

        const metrics = [
            {
                title: 'Total Views',
                value: summaryMetrics.totalViews.toLocaleString(),
                icon: <ViewsIcon />,
                color: '#1976d2'
            },
            {
                title: 'Total Reactions',
                value: summaryMetrics.totalReactions.toLocaleString(),
                icon: <TrendingUpIcon />,
                color: '#388e3c'
            },
            {
                title: 'Avg Engagement',
                value: `${summaryMetrics.avgEngagement.toFixed(2)}%`,
                icon: <SpeedIcon />,
                color: '#f57c00'
            },
            {
                title: 'Growth Rate',
                value: `+${summaryMetrics.growthRate.toFixed(1)}%`,
                icon: <TrendingUpIcon />,
                color: '#7b1fa2'
            }
        ];

        return (
            <Grid container spacing={2} sx={{ mb: 3 }}>
                {metrics.map((metric, index) => (
                    <Grid item xs={12} sm={6} md={3} key={index}>
                        <Card elevation={1}>
                            <CardContent sx={{ display: 'flex', alignItems: 'center', p: 2 }}>
                                <Box 
                                    sx={{ 
                                        mr: 2, 
                                        color: metric.color,
                                        display: 'flex',
                                        alignItems: 'center'
                                    }}
                                >
                                    {metric.icon}
                                </Box>
                                <Box>
                                    <Typography variant="body2" color="text.secondary">
                                        {metric.title}
                                    </Typography>
                                    <Typography variant="h6" component="div">
                                        {metric.value}
                                    </Typography>
                                </Box>
                            </CardContent>
                        </Card>
                    </Grid>
                ))}
            </Grid>
        );
    };

    return (
        <Paper elevation={2} sx={{ p: 3 }}>
            {/* Header */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" component="h2">
                    Post View Dynamics
                </Typography>
                
                {showControls && (
                    <FormControl size="small" sx={{ minWidth: 120 }}>
                        <InputLabel>Time Range</InputLabel>
                        <Select
                            value={timeRange}
                            label="Time Range"
                            onChange={handleTimeRangeChange}
                        >
                            <MenuItem value="24h">Last 24 Hours</MenuItem>
                            <MenuItem value="7d">Last 7 Days</MenuItem>
                            <MenuItem value="30d">Last 30 Days</MenuItem>
                        </Select>
                    </FormControl>
                )}
            </Box>

            {/* Status Indicator */}
            <StatusIndicator />

            {/* Error Display */}
            {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
            )}

            {/* Loading State */}
            {isLoading && (
                <Box display="flex" justifyContent="center" alignItems="center" minHeight={300}>
                    <CircularProgress />
                    <Typography variant="body2" sx={{ ml: 2 }}>
                        Loading post dynamics data...
                    </Typography>
                </Box>
            )}

            {/* Metrics Cards */}
            {!isLoading && !error && <MetricsCards />}

            {/* Chart */}
            {!isLoading && !error && (
                <StableChart data={processedData} timeRange={timeRange} />
            )}

            {/* Data Source Info */}
            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="caption" color="text.secondary">
                    Data updated: {rawData?.timestamp ? new Date(rawData.timestamp).toLocaleString() : 'N/A'}
                </Typography>
                
                {summaryMetrics?.peakHour && (
                    <Typography variant="caption" color="text.secondary">
                        Peak activity: {summaryMetrics.peakHour}
                    </Typography>
                )}
            </Box>
        </Paper>
    );
};

export default PostViewDynamicsChart;
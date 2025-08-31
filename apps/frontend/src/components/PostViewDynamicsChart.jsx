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
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    AreaChart,
    Area
} from 'recharts';
import {
    TrendingUp as TrendingUpIcon,
    Speed as SpeedIcon,
    Visibility as ViewsIcon,
    ShowChart as ChartIcon
} from '@mui/icons-material';
import { useAppStore } from '../store/appStore.js';

// Error Boundary Component
class ChartErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        console.error('Chart Error:', error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <Alert severity="error" sx={{ m: 2 }}>
                    Chart ma'lumotlarini ko'rsatishda xatolik yuz berdi. Sahifani yangilang.
                </Alert>
            );
        }

        return this.props.children;
    }
}

const PostViewDynamicsChart = () => {
    const [timeRange, setTimeRange] = useState('24h');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [data, setData] = useState([]);
    const [autoRefresh] = useState(true); // setAutoRefresh removed
    const [refreshInterval, setRefreshInterval] = useState('30s');
    
    // Get store methods and data source
    const { fetchPostDynamics, dataSource } = useAppStore();

    // Analytics data loading function with useCallback to prevent unnecessary re-renders
    const loadDynamics = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            
            // Use store method which respects data source configuration
            const result = await fetchPostDynamics(timeRange);
            setData(result.timeline || result.data || []);
            
        } catch (err) {
            setError(err.message);
            console.error('Analytics malumotlarini olishda xatolik:', err);
        } finally {
            setLoading(false);
        }
    }, [timeRange, fetchPostDynamics]);

    // Generate mock data based on time range
    const generateMockData = (range) => {
        const now = new Date();
        const points = [];
        let intervalMs, count;

        switch (range) {
            case '1h':
                intervalMs = 5 * 60 * 1000; // 5 minutes
                count = 12;
                break;
            case '6h':
                intervalMs = 30 * 60 * 1000; // 30 minutes
                count = 12;
                break;
            case '24h':
                intervalMs = 2 * 60 * 60 * 1000; // 2 hours
                count = 12;
                break;
            case '7d':
                intervalMs = 24 * 60 * 60 * 1000; // 1 day
                count = 7;
                break;
            case '30d':
                intervalMs = 24 * 60 * 60 * 1000; // 1 day
                count = 30;
                break;
            default:
                intervalMs = 60 * 60 * 1000; // 1 hour
                count = 24;
        }

        for (let i = 0; i < count; i++) {
            const timestamp = new Date(now.getTime() - (count - i - 1) * intervalMs);
            const baseViews = Math.floor(Math.random() * 1000) + 500;
            const variation = Math.sin(i * 0.5) * 200; // Add some wave pattern
            
            points.push({
                timestamp: timestamp.toISOString(),
                views: Math.max(0, Math.floor(baseViews + variation + Math.random() * 300)),
                likes: Math.floor((baseViews + variation) * 0.1 + Math.random() * 20),
                shares: Math.floor((baseViews + variation) * 0.05 + Math.random() * 10),
                comments: Math.floor((baseViews + variation) * 0.02 + Math.random() * 5)
            });
        }

        return points;
    };

        // Load data on mount and when timeRange changes
    useEffect(() => {
        loadDynamics();
    }, [loadDynamics]);
    
    // Listen for data source changes
    useEffect(() => {
        const handleDataSourceChange = () => {
            console.log('PostViewDynamicsChart: Data source changed, reloading...');
            loadDynamics();
        };
        
        window.addEventListener('dataSourceChanged', handleDataSourceChange);
        return () => window.removeEventListener('dataSourceChanged', handleDataSourceChange);
    }, [loadDynamics]); // loadDynamics added to dependencies

    // Auto-refresh functionality
    useEffect(() => {
        if (!autoRefresh || refreshInterval === 'disabled') return;

        const intervalMs = refreshInterval === '30s' ? 30000 : 
                          refreshInterval === '1m' ? 60000 : 
                          refreshInterval === '5m' ? 300000 : 30000;

        const interval = setInterval(loadDynamics, intervalMs);
        return () => clearInterval(interval);
    }, [autoRefresh, refreshInterval, loadDynamics]);

    // Chart data transformation
    const chartData = useMemo(() => {
        if (!data || !Array.isArray(data) || data.length === 0) return [];
        
        try {
            return data.map((point, index) => {
                // Ensure point is an object
                if (!point || typeof point !== 'object') {
                    console.warn(`Invalid data point at index ${index}:`, point);
                    return null;
                }
                
                return {
                    time: point.timestamp ? 
                        new Date(point.timestamp).toLocaleTimeString('en-US', { 
                            hour: '2-digit', 
                            minute: '2-digit' 
                        }) : 
                        point.time || `Point ${index + 1}`,
                    views: Number(point.views) || 0,
                    likes: Number(point.likes || point.reactions) || 0,
                    shares: Number(point.shares || point.forwards) || 0,
                    comments: Number(point.comments) || 0,
                    timestamp: point.timestamp || new Date().toISOString()
                };
            }).filter(Boolean); // Remove null entries
        } catch (error) {
            console.error('Error processing chart data:', error);
            return [];
        }
    }, [data]);

    // Summary statistics with error handling
    const summaryStats = useMemo(() => {
        if (!data || !Array.isArray(data) || data.length === 0) return null;

        try {
            const latest = data[data.length - 1] || {};
            const previous = data[data.length - 2] || {};
            
            const safeNumber = (val) => Number(val) || 0;
            const total = data.reduce((sum, item) => sum + safeNumber(item.views), 0);
            const avgViews = Math.round(total / data.length);
            const growth = safeNumber(latest.views) && safeNumber(previous.views) ? 
                ((safeNumber(latest.views) - safeNumber(previous.views)) / safeNumber(previous.views) * 100).toFixed(1) : 0;

            return {
                totalViews: total,
                currentViews: safeNumber(latest.views),
                averageViews: avgViews,
                growthRate: parseFloat(growth),
                peakViews: Math.max(...data.map(d => safeNumber(d.views))),
                dataPoints: data.length
            };
        } catch (error) {
            console.error('Error calculating summary stats:', error);
            return {
                totalViews: 0,
                currentViews: 0,
                averageViews: 0,
                growthRate: 0,
                peakViews: 0,
                dataPoints: 0
            };
        }
    }, [data]);

    // Tooltip formatter
    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
            return (
                <Paper sx={{ p: 2, bgcolor: 'background.paper', border: '1px solid', borderColor: 'divider' }}>
                    <Typography variant="subtitle2" sx={{ mb: 1 }}>
                        {label}
                    </Typography>
                    {payload.map((entry, index) => (
                        <Typography 
                            key={index} 
                            variant="body2" 
                            sx={{ color: entry.color }}
                        >
                            {entry.name}: {entry.value.toLocaleString()}
                        </Typography>
                    ))}
                </Paper>
            );
        }
        return null;
    };

    if (error) {
        return (
            <Paper sx={{ p: 3 }}>
                <Alert severity="error" sx={{ mb: 2 }}>
                    Ma'lumotlarni yuklashda xatolik: {error}
                </Alert>
            </Paper>
        );
    }

    return (
        <Paper sx={{ p: 3 }}>
            {/* Header */}
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <ChartIcon color="primary" />
                    <Typography variant="h6">
                        Post View Dynamics
                    </Typography>
                </Box>
                
                <Box sx={{ display: 'flex', gap: 2 }}>
                    {/* Time Range Selector */}
                    <FormControl size="small" sx={{ minWidth: 120 }}>
                        <InputLabel>Vaqt oralig'i</InputLabel>
                        <Select
                            value={timeRange}
                            label="Vaqt oralig'i"
                            onChange={(e) => setTimeRange(e.target.value)}
                        >
                            <MenuItem value="1h">1 soat</MenuItem>
                            <MenuItem value="6h">6 soat</MenuItem>
                            <MenuItem value="24h">24 soat</MenuItem>
                            <MenuItem value="7d">7 kun</MenuItem>
                            <MenuItem value="30d">30 kun</MenuItem>
                        </Select>
                    </FormControl>

                    {/* Refresh Interval */}
                    <FormControl size="small" sx={{ minWidth: 120 }}>
                        <InputLabel>Yangilash</InputLabel>
                        <Select
                            value={refreshInterval}
                            label="Yangilash"
                            onChange={(e) => setRefreshInterval(e.target.value)}
                        >
                            <MenuItem value="30s">30 soniya</MenuItem>
                            <MenuItem value="1m">1 daqiqa</MenuItem>
                            <MenuItem value="5m">5 daqiqa</MenuItem>
                            <MenuItem value="disabled">O'chirilgan</MenuItem>
                        </Select>
                    </FormControl>
                </Box>
            </Box>

            {/* Summary Stats Cards */}
            {summaryStats && (
                <Grid container spacing={2} sx={{ mb: 3 }}>
                    <Grid item xs={6} sm={3}>
                        <Card variant="outlined">
                            <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                                    <ViewsIcon color="primary" fontSize="small" />
                                    <Typography variant="caption" color="text.secondary">
                                        Jami Ko'rishlar
                                    </Typography>
                                </Box>
                                <Typography variant="h6">
                                    {summaryStats.totalViews.toLocaleString()}
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                    
                    <Grid item xs={6} sm={3}>
                        <Card variant="outlined">
                            <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                                    <SpeedIcon color="secondary" fontSize="small" />
                                    <Typography variant="caption" color="text.secondary">
                                        O'rtacha
                                    </Typography>
                                </Box>
                                <Typography variant="h6">
                                    {summaryStats.averageViews.toLocaleString()}
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>

                    <Grid item xs={6} sm={3}>
                        <Card variant="outlined">
                            <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                                    <TrendingUpIcon color="success" fontSize="small" />
                                    <Typography variant="caption" color="text.secondary">
                                        O'sish %
                                    </Typography>
                                </Box>
                                <Typography variant="h6" sx={{ 
                                    color: summaryStats.growthRate >= 0 ? 'success.main' : 'error.main' 
                                }}>
                                    {summaryStats.growthRate > 0 ? '+' : ''}{summaryStats.growthRate}%
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>

                    <Grid item xs={6} sm={3}>
                        <Card variant="outlined">
                            <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                                    <ChartIcon color="warning" fontSize="small" />
                                    <Typography variant="caption" color="text.secondary">
                                        Eng yuqori
                                    </Typography>
                                </Box>
                                <Typography variant="h6">
                                    {summaryStats.peakViews.toLocaleString()}
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                </Grid>
            )}

            {/* Loading State */}
            {loading && (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
                    <CircularProgress />
                    <Typography variant="body2" sx={{ ml: 2 }}>
                        Ma'lumotlar yuklanmoqda...
                    </Typography>
                </Box>
            )}

            {/* Chart */}
            {!loading && chartData.length > 0 && (
                <Box sx={{ height: 400, mt: 2 }}>
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis 
                                dataKey="time" 
                                tick={{ fontSize: 12 }}
                                interval="preserveStartEnd"
                            />
                            <YAxis 
                                tick={{ fontSize: 12 }}
                                tickFormatter={(value) => value.toLocaleString()}
                            />
                            <Tooltip content={<CustomTooltip />} />
                            <Legend />
                            <Area
                                type="monotone"
                                dataKey="views"
                                stackId="1"
                                stroke="#8884d8"
                                fill="#8884d8"
                                fillOpacity={0.6}
                                name="Ko'rishlar"
                            />
                            <Area
                                type="monotone"
                                dataKey="likes"
                                stackId="1"
                                stroke="#82ca9d"
                                fill="#82ca9d"
                                fillOpacity={0.6}
                                name="Yoqtirishlar"
                            />
                            <Area
                                type="monotone"
                                dataKey="shares"
                                stackId="1"
                                stroke="#ffc658"
                                fill="#ffc658"
                                fillOpacity={0.6}
                                name="Ulashishlar"
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </Box>
            )}

            {/* Empty State */}
            {!loading && chartData.length === 0 && (
                <Box sx={{ 
                    display: 'flex', 
                    flexDirection: 'column', 
                    alignItems: 'center', 
                    justifyContent: 'center', 
                    height: 300,
                    color: 'text.secondary'
                }}>
                    <ChartIcon sx={{ fontSize: 64, mb: 2, opacity: 0.5 }} />
                    <Typography variant="h6" gutterBottom>
                        Ma'lumot topilmadi
                    </Typography>
                    <Typography variant="body2">
                        Tanlangan vaqt oralig'ida post faolligi ma'lumotlari yo'q
                    </Typography>
                </Box>
            )}

            {/* Status indicator */}
            <Box sx={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center', 
                mt: 2, 
                pt: 2, 
                borderTop: '1px solid', 
                borderColor: 'divider' 
            }}>
                <Typography variant="caption" color="text.secondary">
                    So'ngi yangilash: {new Date().toLocaleTimeString()}
                </Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                    {autoRefresh && refreshInterval !== 'disabled' && (
                        <Chip 
                            size="small" 
                            label="🔄 Avtomatik yangilash" 
                            color="primary" 
                            variant="outlined"
                        />
                    )}
                    {summaryStats && summaryStats.growthRate > 10 && (
                        <Chip 
                            size="small" 
                            label="📈 Yuqori o'sish" 
                            color="success" 
                        />
                    )}
                </Box>
            </Box>
        </Paper>
    );
};

export default function PostViewDynamicsChartWrapper() {
    return (
        <ChartErrorBoundary>
            <PostViewDynamicsChart />
        </ChartErrorBoundary>
    );
}

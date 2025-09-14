import React, { useState, useMemo } from 'react';
import {
    Card,
    CardContent,
    Typography,
    Box,
    IconButton,
    Tooltip,
    FormControl,
    Select,
    MenuItem,
    Chip,
    Button,
    ButtonGroup
} from '@mui/material';
import {
    ShowChart as ChartIcon,
    Refresh as RefreshIcon,
    Fullscreen as FullscreenIcon,
    Download as DownloadIcon,
    Timeline as TimelineIcon
} from '@mui/icons-material';
import {
    LineChart,
    Line,
    AreaChart,
    Area,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip as RechartsTooltip,
    ResponsiveContainer,
    Legend,
    Brush
} from 'recharts';

const TrendsChart = ({ 
    data = [], 
    loading = false, 
    title = "Trends Analysis",
    onRefresh,
    onExport,
    height = 400 
}) => {
    const [chartType, setChartType] = useState('line');
    const [timeRange, setTimeRange] = useState('7d');
    const [showBrush, setShowBrush] = useState(false);

    // Process and format data
    const chartData = useMemo(() => {
        if (!data || data.length === 0) {
            // Generate demo data if no data provided
            return Array.from({ length: 30 }, (_, i) => ({
                name: `Day ${i + 1}`,
                date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toLocaleDateString(),
                views: Math.floor(Math.random() * 5000) + 1000,
                engagement: Math.floor(Math.random() * 500) + 100,
                reach: Math.floor(Math.random() * 3000) + 500,
                growth: (Math.random() - 0.5) * 20
            }));
        }

        return data.map((item, index) => ({
            name: item.name || `Point ${index + 1}`,
            date: item.date || new Date().toLocaleDateString(),
            views: item.views || 0,
            engagement: item.engagement || 0,
            reach: item.reach || 0,
            growth: item.growth || 0,
            ...item
        }));
    }, [data]);

    // Filter data based on time range
    const filteredData = useMemo(() => {
        const days = parseInt(timeRange.replace('d', ''));
        return chartData.slice(-days);
    }, [chartData, timeRange]);

    // Custom tooltip component
    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
            return (
                <Card sx={{ p: 2, minWidth: 200 }}>
                    <Typography variant="subtitle2" gutterBottom>
                        {label}
                    </Typography>
                    {payload.map((entry, index) => (
                        <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                            <Box 
                                sx={{ 
                                    width: 12, 
                                    height: 12, 
                                    bgcolor: entry.color, 
                                    borderRadius: '50%' 
                                }} 
                            />
                            <Typography variant="body2">
                                {entry.name}: {typeof entry.value === 'number' ? entry.value.toLocaleString() : entry.value}
                                {entry.name === 'Growth' && '%'}
                            </Typography>
                        </Box>
                    ))}
                </Card>
            );
        }
        return null;
    };

    // Render different chart types
    const renderChart = () => {
        const commonProps = {
            width: '100%',
            height: height - 100,
            data: filteredData,
            margin: { top: 20, right: 30, left: 20, bottom: 20 }
        };

        switch (chartType) {
            case 'area':
                return (
                    <AreaChart {...commonProps}>
                        <defs>
                            <linearGradient id="viewsGradient" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8}/>
                                <stop offset="95%" stopColor="#8884d8" stopOpacity={0.1}/>
                            </linearGradient>
                            <linearGradient id="engagementGradient" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#82ca9d" stopOpacity={0.8}/>
                                <stop offset="95%" stopColor="#82ca9d" stopOpacity={0.1}/>
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                        <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                        <YAxis tick={{ fontSize: 12 }} />
                        <RechartsTooltip content={<CustomTooltip />} />
                        <Legend />
                        <Area 
                            type="monotone" 
                            dataKey="views" 
                            stroke="#8884d8" 
                            fill="url(#viewsGradient)"
                            strokeWidth={2}
                            name="Views"
                        />
                        <Area 
                            type="monotone" 
                            dataKey="engagement" 
                            stroke="#82ca9d" 
                            fill="url(#engagementGradient)"
                            strokeWidth={2}
                            name="Engagement"
                        />
                        {showBrush && <Brush dataKey="name" height={30} stroke="#8884d8" />}
                    </AreaChart>
                );

            case 'bar':
                return (
                    <BarChart {...commonProps}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                        <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                        <YAxis tick={{ fontSize: 12 }} />
                        <RechartsTooltip content={<CustomTooltip />} />
                        <Legend />
                        <Bar dataKey="views" fill="#8884d8" name="Views" radius={[4, 4, 0, 0]} />
                        <Bar dataKey="engagement" fill="#82ca9d" name="Engagement" radius={[4, 4, 0, 0]} />
                        <Bar dataKey="reach" fill="#ffc658" name="Reach" radius={[4, 4, 0, 0]} />
                        {showBrush && <Brush dataKey="name" height={30} stroke="#8884d8" />}
                    </BarChart>
                );

            default: // line
                return (
                    <LineChart {...commonProps}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                        <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                        <YAxis tick={{ fontSize: 12 }} />
                        <RechartsTooltip content={<CustomTooltip />} />
                        <Legend />
                        <Line 
                            type="monotone" 
                            dataKey="views" 
                            stroke="#8884d8" 
                            strokeWidth={3}
                            dot={{ fill: '#8884d8', strokeWidth: 2, r: 4 }}
                            activeDot={{ r: 6, stroke: '#8884d8', strokeWidth: 2 }}
                            name="Views"
                        />
                        <Line 
                            type="monotone" 
                            dataKey="engagement" 
                            stroke="#82ca9d" 
                            strokeWidth={3}
                            dot={{ fill: '#82ca9d', strokeWidth: 2, r: 4 }}
                            activeDot={{ r: 6, stroke: '#82ca9d', strokeWidth: 2 }}
                            name="Engagement"
                        />
                        <Line 
                            type="monotone" 
                            dataKey="reach" 
                            stroke="#ffc658" 
                            strokeWidth={2}
                            dot={{ fill: '#ffc658', strokeWidth: 2, r: 3 }}
                            name="Reach"
                        />
                        {showBrush && <Brush dataKey="name" height={30} stroke="#8884d8" />}
                    </LineChart>
                );
        }
    };

    if (loading) {
        return (
            <Card sx={{ height }}>
                <CardContent>
                    <Typography variant="h6" gutterBottom>
                        Loading trends...
                    </Typography>
                    <Box sx={{ 
                        height: height - 100, 
                        display: 'flex', 
                        alignItems: 'center', 
                        justifyContent: 'center',
                        bgcolor: '#f5f5f5',
                        borderRadius: 1
                    }}>
                        <TimelineIcon sx={{ fontSize: 64, color: 'grey.400' }} />
                    </Box>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card sx={{ height }}>
            <CardContent>
                {/* Header with controls */}
                <Box sx={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center', 
                    mb: 2 
                }}>
                    <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <ChartIcon color="primary" />
                        {title}
                    </Typography>
                    
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {/* Time Range Selector */}
                        <FormControl size="small" sx={{ minWidth: 80 }}>
                            <Select
                                value={timeRange}
                                onChange={(e) => setTimeRange(e.target.value)}
                                displayEmpty
                            >
                                <MenuItem value="7d">7D</MenuItem>
                                <MenuItem value="14d">14D</MenuItem>
                                <MenuItem value="30d">30D</MenuItem>
                            </Select>
                        </FormControl>

                        {/* Chart Type Selector */}
                        <ButtonGroup size="small" variant="outlined">
                            <Button 
                                variant={chartType === 'line' ? 'contained' : 'outlined'}
                                onClick={() => setChartType('line')}
                            >
                                Line
                            </Button>
                            <Button 
                                variant={chartType === 'area' ? 'contained' : 'outlined'}
                                onClick={() => setChartType('area')}
                            >
                                Area
                            </Button>
                            <Button 
                                variant={chartType === 'bar' ? 'contained' : 'outlined'}
                                onClick={() => setChartType('bar')}
                            >
                                Bar
                            </Button>
                        </ButtonGroup>

                        {/* Action buttons */}
                        <Tooltip title="Toggle brush/zoom">
                            <IconButton 
                                size="small" 
                                onClick={() => setShowBrush(!showBrush)}
                                color={showBrush ? "primary" : "default"}
                            >
                                <FullscreenIcon />
                            </IconButton>
                        </Tooltip>

                        {onRefresh && (
                            <Tooltip title="Refresh data">
                                <IconButton size="small" onClick={onRefresh}>
                                    <RefreshIcon />
                                </IconButton>
                            </Tooltip>
                        )}

                        {onExport && (
                            <Tooltip title="Export chart">
                                <IconButton size="small" onClick={onExport}>
                                    <DownloadIcon />
                                </IconButton>
                            </Tooltip>
                        )}
                    </Box>
                </Box>

                {/* Data insights */}
                <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                    {filteredData.length > 0 && (
                        <>
                            <Chip 
                                label={`${filteredData.length} data points`} 
                                size="small" 
                                color="primary" 
                                variant="outlined" 
                            />
                            <Chip 
                                label={`Peak: ${Math.max(...filteredData.map(d => d.views)).toLocaleString()} views`} 
                                size="small" 
                                color="success" 
                                variant="outlined" 
                            />
                            <Chip 
                                label={`Avg engagement: ${(filteredData.reduce((acc, d) => acc + d.engagement, 0) / filteredData.length).toFixed(0)}`} 
                                size="small" 
                                color="info" 
                                variant="outlined" 
                            />
                        </>
                    )}
                </Box>

                {/* Chart */}
                <Box sx={{ width: '100%', height: height - 100 }}>
                    <ResponsiveContainer>
                        {renderChart()}
                    </ResponsiveContainer>
                </Box>
            </CardContent>
        </Card>
    );
};

export default TrendsChart;

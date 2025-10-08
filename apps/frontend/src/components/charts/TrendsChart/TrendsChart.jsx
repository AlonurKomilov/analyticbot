import React, { useState, useMemo } from 'react';
import {
    Card,
    CardContent,
    Typography,
    Box,
    Tooltip
} from '@mui/material';
import { IconButton } from '../../common/TouchTargetCompliance.jsx';
import {
    ShowChart as ChartIcon,
    Refresh as RefreshIcon,
    Fullscreen as FullscreenIcon,
    Download as DownloadIcon,
    Timeline as TimelineIcon
} from '@mui/icons-material';

// Import extracted components
import ChartTypeSelector from './ChartTypeSelector';
import TimeRangeControls from './TimeRangeControls';
import ChartDataInsights from './ChartDataInsights';
import ChartRenderer from './ChartRenderer';

const TrendsChart = React.memo(({
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

    // Event handlers
    const handleChartTypeChange = (newChartType) => {
        setChartType(newChartType);
    };

    const handleTimeRangeChange = (newTimeRange) => {
        setTimeRange(newTimeRange);
    };

    const handleBrushToggle = () => {
        setShowBrush(!showBrush);
    };

    // Loading state
    if (loading) {
        return (
            <Card sx={{ height }}>
                <CardContent>
                    <Box
                        sx={{
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            justifyContent: 'center',
                            height: height - 50
                        }}
                    >
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
                        <TimeRangeControls
                            timeRange={timeRange}
                            onTimeRangeChange={handleTimeRangeChange}
                        />

                        {/* Chart Type Selector */}
                        <ChartTypeSelector
                            chartType={chartType}
                            onChartTypeChange={handleChartTypeChange}
                        />

                        {/* Action buttons */}
                        <Tooltip title="Toggle brush/zoom">
                            <IconButton
                                size="small"
                                onClick={handleBrushToggle}
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
                <ChartDataInsights data={filteredData} />

                {/* Chart */}
                <ChartRenderer
                    chartType={chartType}
                    data={filteredData}
                    showBrush={showBrush}
                    height={height}
                />
            </CardContent>
        </Card>
    );
});

TrendsChart.displayName = 'TrendsChart';

export default TrendsChart;

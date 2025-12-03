import React, { useMemo } from 'react';
import {
    ResponsiveContainer,
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend
} from 'recharts';
import { Box, Typography, useTheme, Theme } from '@mui/material';

// Types
interface ChartDataItem {
    timestamp: string;
    views: number;
    reactions: number;
    shares: number;
    comments: number;
}

interface ProcessedDataItem extends ChartDataItem {
    formattedTime: string;
}

interface CustomTooltipProps {
    active?: boolean;
    payload?: Array<{
        name: string;
        value: number | string;
        color: string;
    }>;
    label?: string;
}

interface ChartConfig {
    strokeColor: string;
    gridColor: string;
    textColor: string;
    tickFormatter: (value: string) => string;
}

interface ChartVisualizationProps {
    data: ChartDataItem[];
    timeRange: string;
    metricFilter?: 'all' | 'views' | 'reactions' | 'forwards' | 'comments';
    onChartClick?: (data: any) => void;
}

/**
 * CustomTooltip - Chart tooltip component with formatted display
 */
const CustomTooltip: React.FC<CustomTooltipProps> = ({ active, payload, label }) => {
    if (!active || !payload || !payload.length) return null;

    // Convert UTC timestamp to local time for display
    const localTime = label ? new Date(label).toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    }) : label;

    return (
        <Box
            sx={{
                bgcolor: 'background.paper',
                p: 1.5,
                border: 1,
                borderColor: 'divider',
                borderRadius: 1,
                boxShadow: 2
            }}
        >
            <Typography variant="body2" fontWeight="medium">
                {localTime}
            </Typography>
            {payload.map((entry, index) => (
                <Typography
                    key={index}
                    variant="body2"
                    sx={{ color: entry.color }}
                >
                    {entry.name}: {typeof entry.value === 'number' ? entry.value.toLocaleString() : entry.value || 0}
                </Typography>
            ))}
        </Box>
    );
};

/**
 * ChartVisualization - Renders the post dynamics chart using Recharts
 *
 * Memoized to prevent unnecessary re-renders in multi-user dashboard scenarios.
 *
 * @param {Object} props - Component props
 * @param {Array} props.data - Chart data array with timestamp and views
 * @param {string} props.timeRange - Current time range for chart formatting (unused, kept for API compatibility)
 */
const ChartVisualization: React.FC<ChartVisualizationProps> = React.memo(({ data, metricFilter = 'all', onChartClick }) => {
    const theme = useTheme<Theme>();

    // Log when component receives click handler
    console.log('🎨 ChartVisualization: onChartClick =', onChartClick ? 'defined' : 'undefined');

    // Deep, saturated colors that stay visible even with dense data
    const colors = {
        views: '#5288C1',       // Telegram Blue - stays visible
        reactions: '#9e3028fa',   // Deep Red - highly visible
        forwards: '#419644ec',    // Deep Green - strong visibility
        comments: '#ca9a09be'     // Amber/Gold - bright and clear
    };

    // Memoized chart configuration based on time range and theme
    const chartConfig: ChartConfig = useMemo(() => {
        const isDark = theme.palette.mode === 'dark';

        // Auto-detect granularity from data timestamps
        let granularity: 'minute' | 'hour' | 'day' = 'day';
        if (data.length >= 2) {
            const firstDate = new Date(data[0].timestamp);
            const secondDate = new Date(data[1].timestamp);
            const diffMs = Math.abs(secondDate.getTime() - firstDate.getTime());
            const diffMinutes = diffMs / (1000 * 60);

            if (diffMinutes <= 1.5) {
                granularity = 'minute'; // ~1 minute apart
            } else if (diffMinutes <= 90) {
                granularity = 'hour'; // ~1 hour apart
            } else {
                granularity = 'day'; // ~1 day apart
            }
        }

        console.log('📊 Chart granularity detected:', granularity, 'from', data.length, 'data points');

        return {
            strokeColor: theme.palette.primary.main,
            gridColor: isDark ? '#333' : '#f0f0f0',
            textColor: theme.palette.text.secondary,
            tickFormatter: (value: string): string => {
                const date = new Date(value);

                // Use detected granularity for formatting
                if (granularity === 'minute') {
                    // Minute view: show time with minutes
                    return date.toLocaleTimeString('en-US', {
                        hour: '2-digit',
                        minute: '2-digit',
                        hour12: true
                    });
                } else if (granularity === 'hour') {
                    // Hour view: show time with hours
                    return date.toLocaleTimeString('en-US', {
                        hour: '2-digit',
                        minute: '2-digit',
                        hour12: true
                    });
                } else {
                    // Day view: show date
                    return date.toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric'
                    });
                }
            }
        };
    }, [theme, data]);

    // Memoized processed data
    const processedData: ProcessedDataItem[] = useMemo(() => {
        if (!data || !Array.isArray(data)) return [];

        return data.map((item: ChartDataItem) => ({
            timestamp: item.timestamp,
            views: Number(item.views) || 0,
            reactions: Number(item.reactions) || 0,
            shares: Number(item.shares) || 0,
            comments: Number(item.comments) || 0,
            // Format timestamp for display
            formattedTime: new Date(item.timestamp).toLocaleString()
        }));
    }, [data]);

    if (!processedData.length) {
        return null;
    }

    return (
        <Box sx={{ width: '100%', height: 400, mt: 2, minHeight: 400, minWidth: 0 }}>
            <ResponsiveContainer width="100%" height={400} minWidth={300}>
                <LineChart
                    data={processedData}
                    margin={{
                        top: 20,
                        right: 30,
                        left: 20,
                        bottom: 20,
                    }}
                    onClick={(data) => {
                        console.log('📊 Chart clicked!', data);
                        if (onChartClick) {
                            console.log('📊 Calling onChartClick handler...');
                            onChartClick(data);
                        } else {
                            console.log('📊 No onChartClick handler defined');
                        }
                    }}
                    style={{ cursor: onChartClick ? 'pointer' : 'default' }}
                >
                    <CartesianGrid
                        strokeDasharray="3 3"
                        stroke={chartConfig.gridColor}
                    />
                    <XAxis
                        dataKey="timestamp"
                        tickFormatter={chartConfig.tickFormatter}
                        stroke={chartConfig.textColor}
                        fontSize={12}
                    />
                    <YAxis
                        stroke={chartConfig.textColor}
                        fontSize={12}
                        tickFormatter={(value: number) => value.toLocaleString()}
                    />
                    <Tooltip
                        content={<CustomTooltip />}
                        labelFormatter={(value: string) => chartConfig.tickFormatter(value)}
                    />
                    <Legend />
                    {(metricFilter === 'all' || metricFilter === 'views') && (
                        <Line
                            type="monotone"
                            dataKey="views"
                            stroke={colors.views}
                            strokeWidth={2.5}
                            dot={{ fill: colors.views, strokeWidth: 2, r: 4 }}
                            activeDot={{ r: 6, strokeWidth: 0 }}
                            name="Views"
                            animationDuration={800}
                            animationEasing="ease-in-out"
                        />
                    )}
                    {(metricFilter === 'all' || metricFilter === 'reactions') && (
                        <Line
                            type="monotone"
                            dataKey="reactions"
                            stroke={colors.reactions}
                            strokeWidth={2.5}
                            dot={{ fill: colors.reactions, strokeWidth: 2, r: 4 }}
                            activeDot={{ r: 6, strokeWidth: 0 }}
                            name="Reactions"
                            animationDuration={800}
                            animationEasing="ease-in-out"
                        />
                    )}
                    {(metricFilter === 'all' || metricFilter === 'forwards') && (
                        <Line
                            type="monotone"
                            dataKey="shares"
                            stroke={colors.forwards}
                            strokeWidth={2.5}
                            dot={{ fill: colors.forwards, strokeWidth: 2, r: 4 }}
                            activeDot={{ r: 6, strokeWidth: 0 }}
                            name="Forwards"
                            animationDuration={800}
                            animationEasing="ease-in-out"
                        />
                    )}
                    {(metricFilter === 'all' || metricFilter === 'comments') && (
                        <Line
                            type="monotone"
                            dataKey="comments"
                            stroke={colors.comments}
                            strokeWidth={2}
                            dot={{ fill: colors.comments, strokeWidth: 2, r: 4 }}
                            activeDot={{ r: 6 }}
                            name="Comments"
                            animationDuration={800}
                            animationEasing="ease-in-out"
                        />
                    )}
                </LineChart>
            </ResponsiveContainer>
        </Box>
    );
});

ChartVisualization.displayName = 'ChartVisualization';

export default ChartVisualization;

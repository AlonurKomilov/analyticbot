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
import { Box, Typography, useTheme } from '@mui/material';

/**
 * CustomTooltip - Chart tooltip component with formatted display
 */
const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload || !payload.length) return null;

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
                {label}
            </Typography>
            {payload.map((entry, index) => (
                <Typography 
                    key={index} 
                    variant="body2" 
                    sx={{ color: entry.color }}
                >
                    {entry.name}: {entry.value?.toLocaleString() || 0}
                </Typography>
            ))}
        </Box>
    );
};

/**
 * ChartVisualization - Memoized Recharts line chart component
 * 
 * Renders post view dynamics data using Recharts with responsive design.
 * Heavily optimized for performance with proper memoization to prevent
 * unnecessary re-renders in multi-user dashboard scenarios.
 * 
 * @param {Object} props - Component props
 * @param {Array} props.data - Chart data array with timestamp and views
 * @param {string} props.timeRange - Current time range for chart formatting
 */
const ChartVisualization = React.memo(({ data, timeRange }) => {
    const theme = useTheme();

    // Memoized chart configuration based on time range and theme
    const chartConfig = useMemo(() => {
        const isDark = theme.palette.mode === 'dark';
        
        return {
            strokeColor: theme.palette.primary.main,
            gridColor: isDark ? '#333' : '#f0f0f0',
            textColor: theme.palette.text.secondary,
            tickFormatter: (value) => {
                const date = new Date(value);
                switch (timeRange) {
                    case '1h':
                    case '6h':
                        return date.toLocaleTimeString('en-US', { 
                            hour: '2-digit', 
                            minute: '2-digit' 
                        });
                    case '24h':
                        return date.toLocaleTimeString('en-US', { 
                            hour: '2-digit', 
                            minute: '2-digit' 
                        });
                    case '7d':
                        return date.toLocaleDateString('en-US', { 
                            month: 'short', 
                            day: 'numeric' 
                        });
                    case '30d':
                        return date.toLocaleDateString('en-US', { 
                            month: 'short', 
                            day: 'numeric' 
                        });
                    default:
                        return date.toLocaleString();
                }
            }
        };
    }, [theme, timeRange]);

    // Memoized processed data
    const processedData = useMemo(() => {
        if (!data || !Array.isArray(data)) return [];
        
        return data.map(item => ({
            timestamp: item.timestamp,
            views: Number(item.views) || 0,
            // Format timestamp for display
            formattedTime: new Date(item.timestamp).toLocaleString()
        }));
    }, [data]);

    if (!processedData.length) {
        return null;
    }

    return (
        <Box sx={{ width: '100%', height: 400, mt: 2 }}>
            <ResponsiveContainer width="100%" height="100%">
                <LineChart
                    data={processedData}
                    margin={{
                        top: 20,
                        right: 30,
                        left: 20,
                        bottom: 20,
                    }}
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
                        tickFormatter={(value) => value.toLocaleString()}
                    />
                    <Tooltip 
                        content={<CustomTooltip />}
                        labelFormatter={(value) => chartConfig.tickFormatter(value)}
                    />
                    <Legend />
                    <Line
                        type="monotone"
                        dataKey="views"
                        stroke={chartConfig.strokeColor}
                        strokeWidth={2}
                        dot={{ fill: chartConfig.strokeColor, strokeWidth: 2, r: 4 }}
                        activeDot={{ r: 6, strokeWidth: 0 }}
                        name="Post Views"
                    />
                </LineChart>
            </ResponsiveContainer>
        </Box>
    );
});

ChartVisualization.displayName = 'ChartVisualization';

export default ChartVisualization;
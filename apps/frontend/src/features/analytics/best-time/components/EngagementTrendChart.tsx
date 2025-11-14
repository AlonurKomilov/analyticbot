/**
 * EngagementTrendChart Component
 *
 * Visualizes hourly engagement patterns over time
 * Shows users when their posts perform best
 */

import React from 'react';
import {
    Box,
    Typography,
    Paper
} from '@mui/material';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Cell
} from 'recharts';

interface EngagementData {
    hour: number;
    engagement: number;
    postCount: number;
}

interface EngagementTrendChartProps {
    data: EngagementData[];
    bestHour?: number;
}

const EngagementTrendChart: React.FC<EngagementTrendChartProps> = ({ data, bestHour }) => {
    if (!data || data.length === 0) {
        return null;
    }

    // Format hour for display
    const formatHour = (hour: number): string => {
        if (hour === 0) return '12 AM';
        if (hour < 12) return `${hour} AM`;
        if (hour === 12) return '12 PM';
        return `${hour - 12} PM`;
    };

    // Custom tooltip
    const CustomTooltip = ({ active, payload }: any) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload;
            return (
                <Paper sx={{ p: 1.5, backgroundColor: 'background.paper', border: '1px solid', borderColor: 'divider' }}>
                    <Typography variant="body2" fontWeight="bold">
                        {formatHour(data.hour)}
                    </Typography>
                    <Typography variant="caption" color="primary">
                        Avg Engagement: {data.engagement.toFixed(2)}
                    </Typography>
                    <Typography variant="caption" display="block" color="text.secondary">
                        Based on {data.postCount} posts
                    </Typography>
                </Paper>
            );
        }
        return null;
    };

    return (
        <Box sx={{ mb: 4 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
                📊 Engagement by Hour
            </Typography>
            <Paper sx={{ p: 2 }}>
                <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                        <XAxis
                            dataKey="hour"
                            tickFormatter={formatHour}
                            tick={{ fontSize: 12 }}
                        />
                        <YAxis
                            label={{ value: 'Avg Engagement', angle: -90, position: 'insideLeft', style: { fontSize: 12 } }}
                            tick={{ fontSize: 12 }}
                        />
                        <Tooltip content={<CustomTooltip />} />
                        <Bar dataKey="engagement" radius={[4, 4, 0, 0]}>
                            {data.map((entry, index) => (
                                <Cell
                                    key={`cell-${index}`}
                                    fill={entry.hour === bestHour ? '#4caf50' : '#1976d2'}
                                />
                            ))}
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1, textAlign: 'center' }}>
                    {bestHour !== undefined && (
                        <>✅ Best performing hour: <strong>{formatHour(bestHour)}</strong> (highlighted in green)</>
                    )}
                </Typography>
            </Paper>
        </Box>
    );
};

export default EngagementTrendChart;

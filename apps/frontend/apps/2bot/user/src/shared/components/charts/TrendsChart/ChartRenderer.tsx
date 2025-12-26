import React from 'react';
import { Box } from '@mui/material';
import {
    ResponsiveContainer,
    LineChart,
    AreaChart,
    BarChart,
    Line,
    Area,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip as RechartsTooltip,
    Legend,
    Brush
} from 'recharts';
import CustomTooltip from './CustomTooltip';

interface ChartData {
    name: string;
    views: number;
    engagement: number;
    reach?: number;
}

interface ChartRendererProps {
    chartType: 'area' | 'bar' | 'line';
    data: ChartData[];
    showBrush: boolean;
    height: number;
}

const ChartRenderer: React.FC<ChartRendererProps> = React.memo(({ chartType, data, showBrush, height }) => {
    const commonProps = {
        width: 800,
        height: height - 100,
        data: data,
        margin: { top: 20, right: 30, left: 20, bottom: 20 }
    };

    const renderChart = () => {
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

    return (
        <Box sx={{ width: '100%', height: height - 100, minHeight: 200, minWidth: 0 }}>
            <ResponsiveContainer width="100%" height={height - 100} minWidth={300}>
                {renderChart()}
            </ResponsiveContainer>
        </Box>
    );
});

ChartRenderer.displayName = 'ChartRenderer';

export default ChartRenderer;

import React, { useMemo } from 'react';
import {
    Box,
    Typography,
    Tooltip
} from '@mui/material';
import { formatHour, getHeatmapColor, generateHourlyPerformance } from '../utils/timeUtils';

interface HourlyPerformance {
    [hour: number]: number;
}

interface Recommendations {
    hourly_performance?: HourlyPerformance;
}

interface HeatmapVisualizationProps {
    recommendations: Recommendations;
}

interface HeatmapDataItem {
    hour: number;
    value: number;
    color: string;
}

const HeatmapVisualization: React.FC<HeatmapVisualizationProps> = ({ recommendations }) => {
    // Generate heatmap data
    const heatmapData = useMemo<HeatmapDataItem[]>(() => {
        const hourlyPerformance = recommendations?.hourly_performance || generateHourlyPerformance();
        const maxValue = Math.max(...Object.values(hourlyPerformance).map(Number));

        return Array.from({ length: 24 }, (_, hour) => ({
            hour,
            value: (hourlyPerformance as any)[hour] || 0,
            color: getHeatmapColor((hourlyPerformance as any)[hour] || 0, maxValue)
        }));
    }, [recommendations]);

    return (
        <Box sx={{ mb: 4 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
                📊 24-Hour Activity Heatmap
            </Typography>
            <Box sx={{ display: 'flex', gap: 0.5, mb: 2, flexWrap: 'wrap' }}>
                {heatmapData.map((item) => (
                    <Tooltip
                        key={item.hour}
                        title={`${formatHour(item.hour)}: ${item.value} engagement`}
                    >
                        <Box
                            sx={{
                                width: 40,
                                height: 40,
                                bgcolor: item.color,
                                borderRadius: 1,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                cursor: 'pointer',
                                border: '1px solid',
                                borderColor: 'divider',
                                '&:hover': {
                                    transform: 'scale(1.05)',
                                    zIndex: 1
                                },
                                transition: 'transform 0.2s'
                            }}
                        >
                            <Typography variant="caption" sx={{ fontSize: '10px', fontWeight: 'bold' }}>
                                {item.hour}
                            </Typography>
                        </Box>
                    </Tooltip>
                ))}
            </Box>

            {/* Heatmap Legend */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, justifyContent: 'center' }}>
                <Typography variant="caption" color="text.secondary">
                    Kam
                </Typography>
                <Box sx={{ display: 'flex', gap: 0.25 }}>
                    {['#e8f5e8', '#a5d6a7', '#66bb6a', '#388e3c', '#2e7d32'].map((color, index) => (
                        <Box
                            key={index}
                            sx={{
                                width: 12,
                                height: 12,
                                bgcolor: color,
                                borderRadius: 0.5
                            }}
                        />
                    ))}
                </Box>
                <Typography variant="caption" color="text.secondary">
                    Ko'p
                </Typography>
            </Box>
        </Box>
    );
};

export default HeatmapVisualization;

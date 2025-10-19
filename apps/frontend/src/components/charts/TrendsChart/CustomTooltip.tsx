import React from 'react';
import { Box, Card, Typography } from '@mui/material';

/**
 * Props for the CustomTooltip component
 */
interface CustomTooltipProps {
    /** Whether the tooltip is active/visible */
    active?: boolean;
    /** Payload data array from Recharts */
    payload?: Array<{
        name: string;
        value: number | string;
        color: string;
    }>;
    /** Label for the tooltip (typically X-axis value) */
    label?: string;
}

const CustomTooltip: React.FC<CustomTooltipProps> = ({ active, payload, label }) => {
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

export default CustomTooltip;

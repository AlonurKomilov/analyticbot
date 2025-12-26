/**
 * CalendarLegend Component
 * Compact legend showing color meanings for historical and prediction data
 */

import React from 'react';
import { Box, Typography } from '@mui/material';

export const CalendarLegend: React.FC = () => {
    return (
        <Box sx={{ mt: 2 }}>
            <Box
                sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    flexWrap: 'wrap',
                    gap: 2,
                    py: 1.5,
                    px: 2,
                    bgcolor: 'background.default',
                    borderRadius: 1
                }}
            >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="caption" color="text.secondary">Historical:</Typography>
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                        <Box sx={{ width: 12, height: 12, bgcolor: '#1b5e20', borderRadius: 0.5 }} title="Excellent" />
                        <Box sx={{ width: 12, height: 12, bgcolor: '#2e7d32', borderRadius: 0.5 }} title="Good" />
                        <Box sx={{ width: 12, height: 12, bgcolor: '#558b2f', borderRadius: 0.5 }} title="Average" />
                        <Box sx={{ width: 12, height: 12, bgcolor: '#424242', borderRadius: 0.5 }} title="Poor" />
                    </Box>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="caption" color="text.secondary">Predictions:</Typography>
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                        <Box sx={{ width: 12, height: 12, bgcolor: '#4caf50', borderRadius: 0.5 }} title="Highly Recommended" />
                        <Box sx={{ width: 12, height: 12, bgcolor: '#8bc34a', borderRadius: 0.5 }} title="Recommended" />
                        <Box sx={{ width: 12, height: 12, bgcolor: '#cddc39', borderRadius: 0.5 }} title="Good Option" />
                        <Box sx={{ width: 12, height: 12, bgcolor: '#ffb74d', borderRadius: 0.5 }} title="Not Recommended" />
                    </Box>
                </Box>
                <Typography variant="caption" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                    💡 Click a future day to schedule a post
                </Typography>
            </Box>
        </Box>
    );
};

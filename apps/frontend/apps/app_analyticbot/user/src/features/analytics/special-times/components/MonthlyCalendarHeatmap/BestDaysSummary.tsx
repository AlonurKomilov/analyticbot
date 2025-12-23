/**
 * BestDaysSummary Component
 * Displays chips showing the best days to post
 */

import React from 'react';
import { Box, Typography, Chip } from '@mui/material';
import { TrendingUp } from '@mui/icons-material';
import type { BestDaySummary } from './types';

interface BestDaysSummaryProps {
    bestDays: BestDaySummary[] | null;
}

export const BestDaysSummary: React.FC<BestDaysSummaryProps> = ({ bestDays }) => {
    if (!bestDays || bestDays.length === 0) {
        return null;
    }

    return (
        <Box sx={{
            display: 'flex',
            justifyContent: 'center',
            gap: 2,
            mb: 3,
            flexWrap: 'wrap'
        }}>
            <Typography variant="body2" color="text.secondary" sx={{ alignSelf: 'center', mr: 1 }}>
                🏆 Best days to post:
            </Typography>
            {bestDays.map((day, idx) => (
                <Chip
                    key={day.name}
                    icon={idx === 0 ? <TrendingUp fontSize="small" /> : undefined}
                    label={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <Typography variant="caption" fontWeight="bold">{day.name}</Typography>
                            <Typography variant="caption" color="text.secondary">
                                ({day.score.toFixed(0)}%)
                            </Typography>
                        </Box>
                    }
                    size="small"
                    sx={{
                        bgcolor: idx === 0 ? 'success.main' : idx === 1 ? 'success.light' : 'grey.300',
                        color: idx < 2 ? 'white' : 'text.primary',
                        fontWeight: idx === 0 ? 'bold' : 'normal'
                    }}
                />
            ))}
        </Box>
    );
};

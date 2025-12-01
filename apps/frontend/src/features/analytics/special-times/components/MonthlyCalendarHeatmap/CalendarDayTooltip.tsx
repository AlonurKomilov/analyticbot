/**
 * CalendarDayTooltip Component
 * Tooltip content for calendar day cells
 */

import React from 'react';
import { Box, Typography } from '@mui/material';
import { DayPerformance, DayStyle } from './types';

interface CalendarDayTooltipProps {
    day: DayPerformance;
    style: DayStyle;
}

export const CalendarDayTooltip: React.FC<CalendarDayTooltipProps> = ({ day, style }) => {
    return (
        <Box sx={{ p: 1, minWidth: 200 }}>
            <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
                {day.isToday ? 'Today' : `Day ${day.date}`}
                {day.isToday && ' 🎯'}
            </Typography>

            <Typography variant="caption" display="block" sx={{ mb: 1 }}>
                Status: {style.label}
            </Typography>

            {day.isPast && day.postCount && day.postCount > 0 ? (
                <>
                    <Typography variant="caption" display="block" sx={{ mb: 1 }}>
                        Historical data: {day.postCount} posts
                    </Typography>
                    {(day.avgViews ?? 0) > 0 && (
                        <Typography variant="caption" display="block" sx={{ mb: 1 }}>
                            Avg views: {(day.avgViews ?? 0).toFixed(1)}
                        </Typography>
                    )}
                    {(day.avgEngagement ?? 0) > 0 && (
                        <Typography variant="caption" display="block" sx={{ mb: 1 }}>
                            Avg engagement: {(day.avgEngagement ?? 0).toFixed(2)}
                        </Typography>
                    )}
                </>
            ) : day.isFuture || day.isToday ? (
                <>
                    <Typography variant="caption" display="block" sx={{ mb: 1 }}>
                        Recommendation score: {day.recommendationScore || 'N/A'}/100
                    </Typography>
                    <Typography variant="caption" display="block" sx={{ mb: 1 }}>
                        Confidence: {day.confidence || 'N/A'}%
                    </Typography>
                    {(day.avgViews ?? 0) > 0 && (
                        <Typography variant="caption" display="block" sx={{ mb: 1 }}>
                            Expected avg views: ~{(day.avgViews ?? 0).toFixed(0)}
                        </Typography>
                    )}
                </>
            ) : (
                <Typography variant="caption" display="block" sx={{ mb: 1 }}>
                    No posts this day
                </Typography>
            )}

            {day.recommendedTimes && day.recommendedTimes.length > 0 && (
                <Box sx={{ mt: 1 }}>
                    <Typography variant="caption" display="block" sx={{ fontWeight: 'bold' }}>
                        Best times to post:
                    </Typography>
                    <Typography variant="caption" display="block">
                        {day.recommendedTimes.join(', ')}
                    </Typography>
                </Box>
            )}

            {(day.isFuture || day.isToday) && (
                <Typography variant="caption" display="block" sx={{ mt: 1, color: 'primary.light' }}>
                    👆 Click to schedule a post
                </Typography>
            )}
        </Box>
    );
};

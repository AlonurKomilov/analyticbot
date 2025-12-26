/**
 * CalendarDayCell Component
 * Individual calendar day cell with styling and interaction
 */

import React from 'react';
import { Box, Tooltip, Typography, useTheme } from '@mui/material';
import { DayPerformance, DayStyle } from './types';
import { CalendarDayTooltip } from './CalendarDayTooltip';

interface CalendarDayCellProps {
    day: DayPerformance;
    style: DayStyle;
    onClick: (event: React.MouseEvent<HTMLElement>, day: DayPerformance) => void;
}

export const CalendarDayCell: React.FC<CalendarDayCellProps> = ({ day, style, onClick }) => {
    const theme = useTheme();

    const handleClick = (e: React.MouseEvent<HTMLElement>) => {
        // Only allow scheduling for today or future days
        if (day.isPast && !day.isToday) return;
        onClick(e, day);
    };

    return (
        <Tooltip
            title={<CalendarDayTooltip day={day} style={style} />}
            arrow
            placement="top"
        >
            <Box
                onClick={handleClick}
                sx={{
                    aspectRatio: '1',
                    minHeight: 80,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    backgroundColor: style.backgroundColor,
                    border: '2px solid',
                    borderColor: style.borderColor,
                    borderRadius: 1,
                    cursor: (day.isFuture || day.isToday) ? 'pointer' : 'default',
                    transition: 'all 0.2s',
                    opacity: style.opacity,
                    position: 'relative',
                    '&:hover': {
                        transform: 'scale(1.05)',
                        boxShadow: `0 0 12px ${style.borderColor}`,
                        zIndex: 2
                    }
                }}
            >
                <Typography
                    variant="body2"
                    sx={{
                        fontWeight: day.isToday ? 'bold' : 'medium',
                        color: style.textColor,
                        fontSize: day.isToday ? '1rem' : '0.875rem'
                    }}
                >
                    {day.date}
                </Typography>

                {/* Status indicator */}
                {React.createElement(style.icon, {
                    sx: {
                        fontSize: 12,
                        color: style.textColor,
                        opacity: 0.7,
                        mt: 0.5
                    }
                })}

                {/* Today indicator */}
                {day.isToday && (
                    <Box
                        sx={{
                            position: 'absolute',
                            top: 4,
                            right: 4,
                            width: 8,
                            height: 8,
                            borderRadius: '50%',
                            backgroundColor: theme.palette.warning.main,
                            border: '1px solid white'
                        }}
                    />
                )}
            </Box>
        </Tooltip>
    );
};

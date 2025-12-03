/**
 * CalendarGrid Component
 * Renders the calendar grid with weekday headers and day cells
 */

import React from 'react';
import { Box, useTheme } from '@mui/material';
import { DayPerformance } from './types';
import { getDayStyle } from './utils';
import { CalendarDayCell } from './CalendarDayCell';

interface CalendarGridProps {
    calendarGrid: (DayPerformance | null)[];
    onDayClick: (event: React.MouseEvent<HTMLElement>, day: DayPerformance) => void;
}

const WEEK_DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

export const CalendarGrid: React.FC<CalendarGridProps> = ({ calendarGrid, onDayClick }) => {
    const theme = useTheme();

    return (
        <>
            {/* Weekday headers */}
            <Box
                sx={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(7, 1fr)',
                    gap: 1,
                    mb: 1
                }}
            >
                {WEEK_DAYS.map(day => (
                    <Box
                        key={day}
                        sx={{
                            textAlign: 'center',
                            fontWeight: 'bold',
                            fontSize: '0.75rem',
                            color: 'text.secondary',
                            py: 0.5
                        }}
                    >
                        {day}
                    </Box>
                ))}
            </Box>

            {/* Calendar grid */}
            <Box
                sx={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(7, 1fr)',
                    gap: 1
                }}
            >
                {calendarGrid.map((day, index) => {
                    if (!day) {
                        return <Box key={`empty-${index}`} sx={{ aspectRatio: '1', minHeight: 80 }} />;
                    }

                    const style = getDayStyle(day, theme);

                    return (
                        <CalendarDayCell
                            key={day.date}
                            day={day}
                            style={style}
                            onClick={onDayClick}
                        />
                    );
                })}
            </Box>
        </>
    );
};

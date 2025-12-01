/**
 * MonthlyCalendarHeatmap Component
 * Main orchestrator - coordinates calendar display with heatmap visualization
 * 
 * Refactored from 579-line monolith to modular component structure:
 * - types.ts: TypeScript interfaces
 * - utils.ts: Utility functions for styling and formatting
 * - CalendarHeader.tsx: Navigation controls
 * - BestDaysSummary.tsx: Top performing days chips
 * - CalendarGrid.tsx: Calendar grid with day cells
 * - CalendarDayCell.tsx: Individual day cell
 * - CalendarDayTooltip.tsx: Day tooltip content
 * - CalendarLegend.tsx: Color legend
 * - TimeSelectionPopover.tsx: Time selection for scheduling
 */

import React, { useMemo, useState } from 'react';
import { Box, Paper, Typography } from '@mui/material';
import { Event } from '@mui/icons-material';

// Import types and utilities
import { DayPerformance, MonthlyCalendarHeatmapProps } from './types';

// Import sub-components
import { CalendarHeader } from './CalendarHeader';
import { BestDaysSummary } from './BestDaysSummary';
import { CalendarGrid } from './CalendarGrid';
import { CalendarLegend } from './CalendarLegend';
import { TimeSelectionPopover } from './TimeSelectionPopover';

const WEEK_DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const DAY_NAMES = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

export const MonthlyCalendarHeatmap: React.FC<MonthlyCalendarHeatmapProps> = ({
    dailyPerformance,
    month = 'Current Month',
    bestTimesByDay = {},
    dayPerformanceScores = {},
    onDateSelect,
    showFuturePredictions = true
}) => {
    const today = new Date();

    // Time selection popover state
    const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
    const [selectedDay, setSelectedDay] = useState<DayPerformance | null>(null);

    // Month navigation state
    const [currentDate, setCurrentDate] = React.useState(() => {
        const now = new Date();
        return month ? new Date(month + ' 1') : new Date(now.getFullYear(), now.getMonth());
    });

    // Calendar calculations
    const year = currentDate.getFullYear();
    const monthNum = currentDate.getMonth();
    const firstDay = new Date(year, monthNum, 1);
    const firstDayOfWeek = firstDay.getDay();
    const daysInMonth = new Date(year, monthNum + 1, 0).getDate();

    // Categorize days - past with historical data, future with predictions
    const categorizedDays = useMemo(() => {
        const result: DayPerformance[] = [];

        for (let day = 1; day <= daysInMonth; day++) {
            const currentDayDate = new Date(year, monthNum, day);
            const isToday = currentDayDate.toDateString() === today.toDateString();
            const isPast = currentDayDate < today && !isToday;
            const isFuture = currentDayDate > today;
            const dayOfWeek = currentDayDate.getDay();

            // Check for historical data
            const historicalData = dailyPerformance.find(d => d.date === day);

            if (historicalData && isPast) {
                // Use historical data for past days
                result.push({
                    ...historicalData,
                    isToday,
                    isPast,
                    isFuture,
                    recommendedTimes: bestTimesByDay[dayOfWeek] || ['10:00', '15:00', '20:00']
                });
            } else if (isFuture || isToday) {
                // For future days, calculate recommendations
                let recommendationScore = 50; // default
                let confidence = 50;
                let avgViews = 0;

                const backendScore = dayPerformanceScores[dayOfWeek];
                if (backendScore) {
                    recommendationScore = backendScore.score;
                    confidence = backendScore.confidence;
                    avgViews = backendScore.avgViews;
                } else {
                    // Fallback calculation
                    const bestDaysData = dailyPerformance.filter(d => d.postCount && d.postCount > 0);
                    const dayOfWeekPerformance = bestDaysData.filter(d => d.dayOfWeek === dayOfWeek);

                    if (dayOfWeekPerformance.length > 0) {
                        avgViews = dayOfWeekPerformance.reduce((sum, d) => sum + (d.avgViews ?? d.avgEngagement ?? 0), 0) / dayOfWeekPerformance.length;
                        const maxValue = Math.max(...bestDaysData.map(d => d.avgViews ?? d.avgEngagement ?? 0));
                        recommendationScore = maxValue > 0 ? (avgViews / maxValue) * 100 : 50;
                        
                        if (dayOfWeekPerformance.length >= 4) confidence = 85;
                        else if (dayOfWeekPerformance.length >= 2) confidence = 70;
                        else confidence = 55;
                    }
                }

                let score: DayPerformance['score'] = 'average';
                if (recommendationScore >= 80) score = 'excellent';
                else if (recommendationScore >= 60) score = 'good';
                else if (recommendationScore >= 40) score = 'average';
                else score = 'poor';

                result.push({
                    date: day,
                    dayOfWeek,
                    score,
                    isToday,
                    isPast,
                    isFuture,
                    avgViews,
                    recommendationScore: Math.round(recommendationScore),
                    confidence: Math.round(confidence),
                    recommendedTimes: bestTimesByDay[dayOfWeek] || (() => {
                        const allTimes = Object.values(bestTimesByDay).flat();
                        return allTimes.length > 0 ?
                            [...new Set(allTimes)].slice(0, 3) :
                            ['10:00', '15:00', '20:00'];
                    })()
                });
            } else {
                result.push({
                    date: day,
                    dayOfWeek,
                    score: 'no-data',
                    isToday,
                    isPast,
                    isFuture,
                    postCount: 0,
                    avgEngagement: 0
                });
            }
        }

        return result;
    }, [dailyPerformance, currentDate, today, showFuturePredictions, bestTimesByDay, dayPerformanceScores, year, monthNum, daysInMonth]);

    // Create calendar grid with empty cells for days before the 1st
    const calendarGrid: (DayPerformance | null)[] = useMemo(() => {
        const grid: (DayPerformance | null)[] = [];

        // Add empty cells for days before the 1st
        for (let i = 0; i < firstDayOfWeek; i++) {
            grid.push(null);
        }

        // Add all days of the month
        for (let day = 1; day <= daysInMonth; day++) {
            const dayData = categorizedDays.find(d => d.date === day);
            grid.push(dayData || {
                date: day,
                dayOfWeek: (firstDayOfWeek + day - 1) % 7,
                avgEngagement: 0,
                postCount: 0,
                score: 'no-data'
            });
        }

        return grid;
    }, [categorizedDays, firstDayOfWeek, daysInMonth]);

    // Best days summary from backend scores
    const bestDaysSummary = useMemo(() => {
        const entries = Object.entries(dayPerformanceScores);
        if (entries.length === 0) return null;
        
        const sorted = entries
            .map(([day, data]) => ({ dayIndex: parseInt(day), ...data }))
            .sort((a, b) => b.score - a.score);
        
        return sorted.slice(0, 3).map(d => ({
            name: DAY_NAMES[d.dayIndex],
            shortName: WEEK_DAYS[d.dayIndex],
            score: d.score,
            avgViews: d.avgViews
        }));
    }, [dayPerformanceScores]);

    // Navigation handlers
    const handleNavigateMonth = (direction: 'prev' | 'next') => {
        setCurrentDate(prev => {
            const newDate = new Date(prev);
            if (direction === 'prev') {
                newDate.setMonth(prev.getMonth() - 1);
            } else {
                newDate.setMonth(prev.getMonth() + 1);
            }
            return newDate;
        });
    };

    const handleGoToToday = () => {
        setCurrentDate(new Date(today.getFullYear(), today.getMonth()));
    };

    // Day click handler
    const handleDayClick = (event: React.MouseEvent<HTMLElement>, day: DayPerformance) => {
        if (day.isPast && !day.isToday) return;
        setAnchorEl(event.currentTarget);
        setSelectedDay(day);
    };

    // Popover handlers
    const handleClosePopover = () => {
        setAnchorEl(null);
        setSelectedDay(null);
    };

    const handleTimeSelect = (time: string) => {
        if (selectedDay && onDateSelect) {
            const selectedDate = new Date(year, monthNum, selectedDay.date);
            onDateSelect(selectedDate, time);
        }
        handleClosePopover();
    };

    const handleCustomTime = () => {
        if (selectedDay && onDateSelect) {
            const selectedDate = new Date(year, monthNum, selectedDay.date);
            onDateSelect(selectedDate);
        }
        handleClosePopover();
    };

    const monthName = currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });

    return (
        <Paper
            elevation={0}
            sx={{
                p: 3,
                mb: 4,
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 2
            }}
        >
            {/* Enhanced Header with Navigation */}
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
                <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Event color="primary" />
                    📅 Monthly Posting Calendar
                </Typography>

                <CalendarHeader
                    onNavigate={handleNavigateMonth}
                    onGoToToday={handleGoToToday}
                />
            </Box>

            <Typography variant="h6" align="center" sx={{ mb: 2, color: 'primary.main' }}>
                {monthName}
            </Typography>

            {/* Best Days Summary */}
            {bestDaysSummary && bestDaysSummary.length > 0 && (
                <BestDaysSummary bestDays={bestDaysSummary} />
            )}

            {/* Calendar Grid */}
            <CalendarGrid
                calendarGrid={calendarGrid}
                onDayClick={handleDayClick}
            />

            {/* Legend */}
            <CalendarLegend />

            {/* Time Selection Popover */}
            <TimeSelectionPopover
                anchorEl={anchorEl}
                selectedDay={selectedDay}
                onClose={handleClosePopover}
                onTimeSelect={handleTimeSelect}
                onCustomTime={handleCustomTime}
            />
        </Paper>
    );
};

export default MonthlyCalendarHeatmap;

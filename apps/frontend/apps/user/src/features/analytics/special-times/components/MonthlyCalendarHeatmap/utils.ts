/**
 * Calendar Utility Functions
 * Shared utilities for calendar calculations and styling
 */

import { Theme } from '@mui/material';
import { TrendingUp, TrendingDown, Remove } from '@mui/icons-material';
import type { DayPerformance, DayStyle } from './types';

/**
 * Get styling for a calendar day based on its performance data
 */
export function getDayStyle(day: DayPerformance, theme: Theme): DayStyle {
    const score = day.score;
    let backgroundColor = '';
    let borderColor = '';
    let textColor = theme.palette.text.primary;
    let opacity = 1;
    let label = '';
    let icon: React.ComponentType<{ sx?: object }> = Remove;

    if (day.isPast) {
        // Historical data - darker, solid colors
        switch (score) {
            case 'excellent':
                backgroundColor = '#1b5e20';
                borderColor = '#2e7d32';
                label = 'Excellent Performance';
                icon = TrendingUp;
                textColor = 'white';
                break;
            case 'good':
                backgroundColor = '#2e7d32';
                borderColor = '#43a047';
                label = 'Good Performance';
                icon = TrendingUp;
                textColor = 'white';
                break;
            case 'average':
                backgroundColor = '#558b2f';
                borderColor = '#7cb342';
                label = 'Average Performance';
                icon = Remove;
                textColor = 'white';
                break;
            case 'poor':
                backgroundColor = '#424242';
                borderColor = '#616161';
                label = 'Poor Performance';
                icon = TrendingDown;
                textColor = '#ccc';
                break;
            default:
                backgroundColor = '#1e1e1e';
                borderColor = '#2a2a2a';
                label = 'No Data';
                textColor = '#666';
        }
    } else {
        // Future predictions - lighter, translucent colors
        switch (score) {
            case 'excellent':
                backgroundColor = '#4caf50';
                borderColor = '#66bb6a';
                label = 'Highly Recommended';
                icon = TrendingUp;
                textColor = 'white';
                break;
            case 'good':
                backgroundColor = '#8bc34a';
                borderColor = '#9ccc65';
                label = 'Recommended';
                icon = TrendingUp;
                textColor = 'white';
                break;
            case 'average':
                backgroundColor = '#cddc39';
                borderColor = '#d4e157';
                label = 'Good Option';
                icon = Remove;
                textColor = '#333';
                break;
            case 'poor':
                backgroundColor = '#ffb74d';
                borderColor = '#ffcc02';
                label = 'Not Recommended';
                icon = TrendingDown;
                textColor = '#333';
                break;
            default:
                backgroundColor = '#f5f5f5';
                borderColor = '#e0e0e0';
                label = 'No Data';
                textColor = '#666';
        }
        if (day.isFuture) {
            opacity = 0.85; // Slightly transparent for predictions
        }
    }

    if (day.isToday) {
        borderColor = theme.palette.primary.main;
    }

    return { backgroundColor, borderColor, textColor, opacity, label, icon };
}

/**
 * Build calendar grid from categorized days
 */
export function buildCalendarGrid(
    categorizedDays: DayPerformance[],
    year: number,
    monthNum: number
): (DayPerformance | null)[] {
    const firstDay = new Date(year, monthNum, 1);
    const firstDayOfWeek = firstDay.getDay();
    const daysInMonth = new Date(year, monthNum + 1, 0).getDate();

    const calendarGrid: (DayPerformance | null)[] = [];

    // Add empty cells for days before the 1st
    for (let i = 0; i < firstDayOfWeek; i++) {
        calendarGrid.push(null);
    }

    // Add all days of the month
    for (let day = 1; day <= daysInMonth; day++) {
        const dayData = categorizedDays.find(d => d.date === day);
        calendarGrid.push(dayData || {
            date: day,
            dayOfWeek: (firstDayOfWeek + day - 1) % 7,
            avgEngagement: 0,
            postCount: 0,
            score: 'no-data'
        });
    }

    return calendarGrid;
}

/**
 * MonthlyCalendarHeatmap Types
 * Type definitions for the calendar heatmap component
 */

export interface DayPerformance {
    date: number; // Day of month (1-31)
    dayOfWeek: number; // 0-6 (Sunday-Saturday)
    month?: number; // 1-12 (for filtering by displayed month)
    year?: number; // Year (for filtering by displayed month)
    avgEngagement?: number; // Optional for future predictions
    avgViews?: number; // Primary metric - average views
    postCount?: number; // Optional for future predictions
    score?: 'excellent' | 'good' | 'average' | 'poor' | 'no-data';
    // New fields for recommendations
    isToday?: boolean;
    isPast?: boolean;
    isFuture?: boolean;
    recommendationScore?: number; // 0-100 score for future days
    confidence?: number; // 0-100 confidence level
    recommendedTimes?: string[]; // Best posting times
}

export interface MonthlyCalendarHeatmapProps {
    dailyPerformance: DayPerformance[];
    month?: string; // e.g., "November 2025"
    bestTimesByDay?: Record<number, string[]>; // weekday (0-6) -> best times
    dayPerformanceScores?: Record<number, { score: number; confidence: number; avgViews: number }>; // Backend day scores
    onDateSelect?: (date: Date, time?: string) => void;
    showFuturePredictions?: boolean;
}

export interface DayStyle {
    backgroundColor: string;
    borderColor: string;
    textColor: string;
    opacity: number;
    label: string;
    icon: React.ComponentType<{ sx?: object }>;
}

export interface BestDaySummary {
    name: string;
    shortName: string;
    score: number;
    avgViews: number;
}

export const WEEK_DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'] as const;
export const DAY_NAMES = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'] as const;

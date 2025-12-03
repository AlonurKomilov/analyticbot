/**
 * Time formatting and calculation utilities for SpecialTimesRecommender
 */

export type ConfidenceColor = 'success' | 'warning' | 'error';
export type InsightType = 'time' | 'content' | 'audience' | 'trend' | 'warning' | 'tip';

export interface AIInsight {
    type: InsightType;
    message: string;
    title?: string;
    description?: string;
    [key: string]: any;
}

// Days of week (matches PostgreSQL EXTRACT(DOW): 0=Sunday, 1=Monday, ..., 6=Saturday)
export const daysOfWeek: string[] = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

// Format hour to readable time string
export const formatHour = (hour: number): string => {
    if (hour === 0) return '12:00 AM';
    if (hour < 12) return `${hour}:00 AM`;
    if (hour === 12) return '12:00 PM';
    return `${hour - 12}:00 PM`;
};

// Get confidence level color based on percentage
export const getConfidenceColor = (confidence: number): ConfidenceColor => {
    if (confidence >= 80) return 'success';
    if (confidence >= 60) return 'warning';
    return 'error';
};

// Get heatmap color based on value intensity
export const getHeatmapColor = (value: number, max: number): string => {
    const intensity = value / max;
    if (intensity > 0.8) return '#2e7d32'; // Dark green
    if (intensity > 0.6) return '#388e3c'; // Green
    if (intensity > 0.4) return '#66bb6a'; // Light green
    if (intensity > 0.2) return '#a5d6a7'; // Very light green
    return '#e8f5e8'; // Almost white green
};

// Generate hourly performance data for heatmap
export const generateHourlyPerformance = (): Record<number, number> => {
    const hourlyPerformance: Record<number, number> = {};
    for (let hour = 0; hour < 24; hour++) {
        // Peak hours: 9-11 AM, 2-4 PM, 7-9 PM
        let basePerformance = 100;
        if ((hour >= 9 && hour <= 11) || (hour >= 14 && hour <= 16) || (hour >= 19 && hour <= 21)) {
            basePerformance = Math.floor(Math.random() * 200) + 300; // 300-500
        } else if (hour >= 6 && hour <= 23) {
            basePerformance = Math.floor(Math.random() * 150) + 150; // 150-300
        } else {
            basePerformance = Math.floor(Math.random() * 100) + 50; // 50-150
        }
        hourlyPerformance[hour] = basePerformance;
    }
    return hourlyPerformance;
};

// Get AI insight icon emoji
export const getAIInsightIcon = (insight: AIInsight): string => {
    const icons: Record<InsightType, string> = {
        time: '⏰',
        content: '📝',
        audience: '👥',
        trend: '📈',
        warning: '⚠️',
        tip: '💡'
    };
    return icons[insight.type] || '🤖';
};

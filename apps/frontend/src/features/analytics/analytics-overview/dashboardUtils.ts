// Dashboard utility functions for AdvancedAnalyticsDashboard components
import type { Theme } from '@mui/material';

export interface Thresholds {
    good: number;
    warning: number;
}

export interface Alert {
    id: string;
    type: 'success' | 'warning' | 'info' | 'error';
    title: string;
    message: string;
    timestamp: string;
}

export interface OverviewData {
    growthRate?: number;
    avgEngagement?: number;
    totalViews?: number;
}

export interface TopPost {
    title: string;
    views: number;
}

export const formatNumber = (num: number | undefined | null): string => {
    if (!num) return '0';
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
};

export const getMetricColor = (
    value: number,
    thresholds: Thresholds = { good: 10, warning: 5 },
    theme: Theme
): string => {
    if (value >= thresholds.good) return theme.palette.success.main;
    if (value >= thresholds.warning) return theme.palette.warning.main;
    return theme.palette.error.main;
};

// Note: generateSmartAlerts removed - alerts now come from backend /analytics/alerts/check API
// See AlertsService.checkAlerts() for real alert generation

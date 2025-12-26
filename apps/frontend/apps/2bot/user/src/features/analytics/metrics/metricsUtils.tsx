import React from 'react';
import {
    TrendingUp as TrendingUpIcon,
    TrendingDown as TrendingDownIcon,
    TrendingFlat as TrendingFlatIcon
} from '@mui/icons-material';

/**
 * Type for metric value format options
 */
export type MetricValueType = 'number' | 'percentage' | 'compact' | 'score';

/**
 * Type for score color options
 */
export type ScoreColor = 'success' | 'warning' | 'error';

/**
 * Metrics utility functions for MetricsCard components
 */

/**
 * Get trend icon based on value
 * @param value - Numeric value indicating trend direction
 * @returns React element with appropriate trend icon
 */
export const getTrendIcon = (value: number): React.ReactElement => {
    if (value > 5) return <TrendingUpIcon color="success" />;
    if (value < -5) return <TrendingDownIcon color="error" />;
    return <TrendingFlatIcon color="warning" />;
};

/**
 * Get score color based on numeric score
 * @param score - Numeric score value (0-100)
 * @returns Color indicator string
 */
export const getScoreColor = (score: number): ScoreColor => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'error';
};

/**
 * Get performance level label based on score
 * @param score - Numeric score value (0-100)
 * @returns Performance level description
 */
export const getPerformanceLevel = (score: number): string => {
    if (score >= 90) return 'Excellent';
    if (score >= 75) return 'Good';
    if (score >= 60) return 'Average';
    if (score >= 40) return 'Below Average';
    return 'Needs Attention';
};

/**
 * Format metric value based on type
 * @param value - Numeric value to format
 * @param type - Format type (number, percentage, compact, score)
 * @returns Formatted string representation
 */
export const formatMetricValue = (value: number, type: MetricValueType = 'number'): string => {
    if (typeof value !== 'number') return '0';

    switch (type) {
        case 'percentage':
            return `${value.toFixed(1)}%`;
        case 'compact':
            if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
            if (value >= 1000) return `${(value / 1000).toFixed(1)}K`;
            return value.toString();
        case 'score':
            return Math.round(value).toString();
        default:
            return value.toLocaleString();
    }
};

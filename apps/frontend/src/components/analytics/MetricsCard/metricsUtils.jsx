import React from 'react';
import {
    TrendingUp as TrendingUpIcon,
    TrendingDown as TrendingDownIcon,
    TrendingFlat as TrendingFlatIcon
} from '@mui/icons-material';

// Metrics utility functions for MetricsCard components

export const getTrendIcon = (value) => {
    if (value > 5) return <TrendingUpIcon color="success" />;
    if (value < -5) return <TrendingDownIcon color="error" />;
    return <TrendingFlatIcon color="warning" />;
};

export const getScoreColor = (score) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'error';
};

export const getPerformanceLevel = (score) => {
    if (score >= 90) return 'Excellent';
    if (score >= 75) return 'Good';
    if (score >= 60) return 'Average';
    if (score >= 40) return 'Below Average';
    return 'Needs Attention';
};

export const formatMetricValue = (value, type = 'number') => {
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

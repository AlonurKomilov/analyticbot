/**
 * PostViewDynamics Types
 * Type definitions for post view dynamics chart
 */

// Re-export from shared controls for consistency
export type { TimeRange, RefreshInterval, MetricFilter } from '@shared/components/controls/TimeRangeControls';

export interface DataPoint {
    timestamp?: string;
    time?: string;
    views?: number;
    reactions?: number;
    likes?: number;  // Legacy support
    shares?: number;
    forwards?: number;
    comments?: number;
    post_count?: number;
    postCount?: number;
    reactions_count?: number;
    replies_count?: number;
    replies?: number;
    threaded_replies_count?: number;
    threaded_replies?: number;
}

export interface ChartDataPoint {
    time: string;
    views: number;
    reactions: number;
    shares: number;
    comments: number;
    timestamp: string;
}

export interface SummaryStats {
    totalViews: number;
    currentViews: number;
    averageViews: number;
    growthRate: number;
    peakViews: number;
    dataPoints: number;
    totalPosts?: number;
    averageViewsTop?: number;
    totalReactions?: number;
    totalComments?: number;
    totalReplies?: number;
    totalForwards?: number;
}

export interface DrillDownState {
    date: string | null;
    hour: string | null;
}

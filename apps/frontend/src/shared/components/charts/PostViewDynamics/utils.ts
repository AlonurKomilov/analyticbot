/**
 * PostViewDynamics Utils
 * Data transformation and calculation utilities
 */

import { DataPoint, ChartDataPoint, SummaryStats } from './types';
import { uiLogger } from '@/utils/logger';

/**
 * Transform raw data points into chart-ready format
 */
export function transformChartData(data: DataPoint[]): ChartDataPoint[] {
    uiLogger.debug('PostDynamics: Transforming chart data', { dataLength: data?.length, isArray: Array.isArray(data) });

    if (!data || !Array.isArray(data) || data.length === 0) {
        uiLogger.debug('PostDynamics: No data to transform, returning empty array');
        return [];
    }

    try {
        uiLogger.debug('PostDynamics: Starting transformation', { itemCount: data.length });
        const transformedData = data.map((point, index) => {
            if (!point || typeof point !== 'object') {
                uiLogger.warn('PostDynamics: Invalid point', { index, point });
                return null;
            }

            // Format time based on data granularity
            let timeLabel: string;
            if (point.timestamp) {
                const date = new Date(point.timestamp);
                // If data spans multiple days, show date; otherwise show time
                const firstTimestamp = data[0]?.timestamp;
                const lastTimestamp = data[data.length - 1]?.timestamp;
                const isMultiDay = data.length > 1 &&
                    firstTimestamp && lastTimestamp &&
                    new Date(firstTimestamp).toDateString() !== new Date(lastTimestamp).toDateString();

                if (isMultiDay) {
                    // Show date for multi-day views
                    timeLabel = date.toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric'
                    });
                } else {
                    // Show time for single-day views
                    timeLabel = date.toLocaleTimeString('en-US', {
                        hour: '2-digit',
                        minute: '2-digit'
                    });
                }
            } else {
                timeLabel = point.time || `Point ${index + 1}`;
            }

            const transformed = {
                time: timeLabel,
                views: Math.max(0, Number(point.views) || 0),
                reactions: Math.max(0, Number(point.reactions || point.likes) || 0),
                shares: Math.max(0, Number(point.shares || point.forwards) || 0),
                comments: Math.max(0, Number(point.comments) || 0),
                timestamp: point.timestamp || new Date().toISOString()
            };

            if (index === 0) {
                uiLogger.debug('PostDynamics: First transformed item', { transformed });
            }

            return transformed;
        }).filter((item): item is ChartDataPoint => item !== null);

        uiLogger.debug('PostDynamics: Transformed chart data', { outputLength: transformedData.length });
        return transformedData;
    } catch (error) {
        uiLogger.error('PostDynamics: Error transforming chart data', { error });
        return [];
    }
}

/**
 * Calculate summary statistics from chart data
 */
export function calculateSummaryStats(chartData: ChartDataPoint[], rawData: DataPoint[]): SummaryStats | null {
    uiLogger.debug('PostDynamics: Calculating summary stats', { chartDataLength: chartData?.length });

    if (!chartData || chartData.length === 0) {
        uiLogger.debug('PostDynamics: No chartData for summary stats');
        return null;
    }

    try {
        const latest = chartData[chartData.length - 1] || {} as ChartDataPoint;
        const previous = chartData[chartData.length - 2] || {} as ChartDataPoint;

        const total = chartData.reduce((sum, item) => sum + (item.views || 0), 0);
        const avgViews = Math.round(total / chartData.length) || 0;
        const currentViews = latest.views || 0;
        const previousViews = previous.views || 0;
        const growth = previousViews > 0 ? ((currentViews - previousViews) / previousViews * 100) : 0;

        // Calculate engagement metrics for top stats
        const postsData = Array.isArray(rawData) ? rawData : [];
        const totalPosts = postsData.reduce((sum: number, point: DataPoint) =>
            sum + (point.post_count || point.postCount || 0), 0
        );
        const totalViewsAll = postsData.reduce((sum: number, post: DataPoint) => sum + (post.views || 0), 0);
        const avgViewsAll = totalPosts > 0 ? Math.round(totalViewsAll / totalPosts) : 0;

        // Calculate totals for reactions, comments, replies, and forwards
        const totalReactions = postsData.reduce((sum: number, post: DataPoint) =>
            sum + (post.likes || post.reactions_count || post.reactions || 0), 0
        );
        const totalComments = postsData.reduce((sum: number, post: DataPoint) =>
            sum + (post.replies_count || post.replies || post.comments || 0), 0
        );
        const totalReplies = postsData.reduce((sum: number, post: DataPoint) =>
            sum + (post.threaded_replies_count || post.threaded_replies || 0), 0
        );
        const totalForwards = postsData.reduce((sum: number, post: DataPoint) =>
            sum + (post.forwards || post.shares || 0), 0
        );

        const stats = {
            totalViews: total,
            currentViews,
            averageViews: avgViews,
            growthRate: Number(growth.toFixed(1)),
            peakViews: Math.max(...chartData.map(d => d.views || 0)),
            dataPoints: chartData.length,
            totalPosts: totalPosts || 0,
            averageViewsTop: avgViewsAll,
            totalReactions: totalReactions || 0,
            totalComments: totalComments || 0,
            totalReplies: totalReplies || 0,
            totalForwards: totalForwards || 0
        };

        uiLogger.debug('PostDynamics: Summary stats calculated', { totalViews: stats.totalViews, currentViews: stats.currentViews });
        return stats;
    } catch (error) {
        uiLogger.error('PostDynamics: Error calculating summary stats', { error });
        return null;
    }
}

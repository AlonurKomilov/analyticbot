/**
 * Mobile Service
 *
 * Mobile-optimized endpoints for app integration.
 * Integrates with backend /mobile/* endpoints.
 *
 * Features:
 * - Mobile dashboard with compressed data
 * - Quick analytics for widgets
 * - Push notification settings
 * - Mobile app preferences
 */

import apiClient from './api/apiClient';

export interface MobileDashboardData {
    channel_id: string;
    timestamp: string;
    metrics: Record<string, number>;
    trends: Array<{ day: number; value: number }>;
    alerts_count: number;
    quick_insights: string[];
}

export interface MobileMetrics {
    views: number;
    growth: number;
    engagement: number;
    score: number;
}

export interface QuickAnalyticsRequest {
    channel_id: string;
    include_real_time?: boolean;
    widget_type?: 'dashboard' | 'widget' | 'notification';
}

export interface QuickAnalyticsResponse {
    channel_id: string;
    metrics: MobileMetrics;
    trend: 'up' | 'down' | 'stable';
    status: 'good' | 'warning' | 'critical';
    cache_time: number;
}

export interface MetricsSummary {
    channel_id: string;
    format: 'compact' | 'widget' | 'notification';
    data: any;
    timestamp: string;
    cache_duration: number;
}

/**
 * Mobile Service Class
 */
class MobileService {
    private baseURL = '/mobile';

    /**
     * Get mobile-optimized dashboard data
     *
     * @param userId - User ID
     * @param channelId - Channel ID
     * @param period - Analysis period in days (1-30)
     * @returns Mobile dashboard data
     */
    async getDashboard(
        userId: number,
        channelId: string,
        period: number = 7
    ): Promise<MobileDashboardData> {
        try {
            const response = await apiClient.get<MobileDashboardData>(
                `${this.baseURL}/dashboard/${userId}`,
                {
                    params: { channel_id: channelId, period }
                }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to get mobile dashboard:', error);
            throw error;
        }
    }

    /**
     * Get quick analytics for widgets/notifications
     *
     * @param request - Quick analytics request
     * @returns Quick analytics response
     */
    async getQuickAnalytics(
        request: QuickAnalyticsRequest
    ): Promise<QuickAnalyticsResponse> {
        try {
            const response = await apiClient.post<QuickAnalyticsResponse>(
                `${this.baseURL}/analytics/quick`,
                request
            );
            return response.data;
        } catch (error) {
            console.error('Failed to get quick analytics:', error);
            throw error;
        }
    }

    /**
     * Get metrics summary in mobile-optimized format
     *
     * @param channelId - Channel ID
     * @param format - Data format (compact, widget, notification)
     * @returns Metrics summary
     */
    async getMetricsSummary(
        channelId: string,
        format: 'compact' | 'widget' | 'notification' = 'compact'
    ): Promise<MetricsSummary> {
        try {
            const response = await apiClient.get<MetricsSummary>(
                `${this.baseURL}/metrics/summary/${channelId}`,
                { params: { format } }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to get metrics summary:', error);
            throw error;
        }
    }

    /**
     * Check if mobile API is healthy
     *
     * @returns Health status
     */
    async checkHealth(): Promise<{
        status: 'healthy' | 'degraded' | 'unhealthy';
        mobile_api: boolean;
        cache_available: boolean;
    }> {
        try {
            const response = await apiClient.get(
                '/health/services',
                { params: { service: 'mobile' } }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to check mobile health:', error);
            return {
                status: 'unhealthy',
                mobile_api: false,
                cache_available: false
            };
        }
    }
}

// Export singleton instance
export const mobileService = new MobileService();
export default mobileService;

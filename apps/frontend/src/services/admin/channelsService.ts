/**
 * Admin Channels Service
 *
 * Channel administration and management for admins.
 * Integrates with backend /admin/channels/* endpoints.
 *
 * Features:
 * - Channel oversight and monitoring
 * - Suspend/unsuspend channels
 * - Force delete channels
 * - View channel analytics
 * - Audit channel activity
 */

import apiClient from '../apiClient';

export interface AdminChannelInfo {
    channel_id: string;
    user_id: number;
    title: string;
    username: string;
    created_at: string;
    status: 'active' | 'suspended' | 'deleted';
    suspension_reason?: string;
    total_posts: number;
    total_views: number;
    last_activity: string;
}

export interface ChannelSuspendRequest {
    reason: string;
    duration_days?: number;
    notify_user?: boolean;
}

export interface ChannelAuditLog {
    action: string;
    admin_id: number;
    admin_email: string;
    timestamp: string;
    details: Record<string, any>;
}

export interface ChannelStatistics {
    total_channels: number;
    active_channels: number;
    suspended_channels: number;
    deleted_channels: number;
    new_today: number;
    new_this_week: number;
    total_views: number;
    total_posts: number;
}

/**
 * Admin Channels Service Class
 */
class AdminChannelsService {
    private baseURL = '/admin/channels';

    /**
     * Get all channels (admin view)
     *
     * @param page - Page number
     * @param limit - Items per page
     * @param status - Filter by status
     * @returns Paginated channel list
     */
    async getAllChannels(
        page: number = 1,
        limit: number = 50,
        status?: 'active' | 'suspended' | 'deleted'
    ): Promise<{
        channels: AdminChannelInfo[];
        total: number;
        page: number;
        pages: number;
    }> {
        try {
            const response = await apiClient.get(
                `${this.baseURL}/list`,
                {
                    params: { page, limit, status }
                }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to get channels:', error);
            throw error;
        }
    }

    /**
     * Get specific channel details (admin view)
     *
     * @param channelId - Channel ID
     * @returns Detailed channel information
     */
    async getChannelDetails(channelId: string | number): Promise<AdminChannelInfo> {
        try {
            const response = await apiClient.get<AdminChannelInfo>(
                `${this.baseURL}/${channelId}`
            );
            return response.data;
        } catch (error) {
            console.error('Failed to get channel details:', error);
            throw error;
        }
    }

    /**
     * Suspend a channel
     *
     * @param channelId - Channel ID to suspend
     * @param request - Suspension details
     * @returns Success message
     */
    async suspendChannel(
        channelId: string | number,
        request: ChannelSuspendRequest
    ): Promise<{ message: string; success: boolean }> {
        try {
            const response = await apiClient.post(
                `${this.baseURL}/${channelId}/suspend`,
                request
            );
            return response.data;
        } catch (error) {
            console.error('Failed to suspend channel:', error);
            throw error;
        }
    }

    /**
     * Unsuspend a channel
     *
     * @param channelId - Channel ID to unsuspend
     * @returns Success message
     */
    async unsuspendChannel(
        channelId: string | number
    ): Promise<{ message: string; success: boolean }> {
        try {
            const response = await apiClient.post(
                `${this.baseURL}/${channelId}/unsuspend`
            );
            return response.data;
        } catch (error) {
            console.error('Failed to unsuspend channel:', error);
            throw error;
        }
    }

    /**
     * Force delete a channel (admin only)
     *
     * @param channelId - Channel ID to delete
     * @param reason - Deletion reason
     * @returns Success message
     */
    async deleteChannel(
        channelId: string | number,
        reason: string
    ): Promise<{ message: string; success: boolean }> {
        try {
            const response = await apiClient.delete(
                `${this.baseURL}/${channelId}`,
                {
                    data: { reason }
                }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to delete channel:', error);
            throw error;
        }
    }

    /**
     * Get channel audit log
     *
     * @param channelId - Channel ID
     * @param limit - Number of entries
     * @returns Audit log entries
     */
    async getChannelAuditLog(
        channelId: string | number,
        limit: number = 100
    ): Promise<ChannelAuditLog[]> {
        try {
            const response = await apiClient.get<ChannelAuditLog[]>(
                `${this.baseURL}/${channelId}/audit`,
                { params: { limit } }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to get audit log:', error);
            throw error;
        }
    }

    /**
     * Get channel statistics (admin overview)
     *
     * @returns Channel statistics
     */
    async getChannelStatistics(): Promise<ChannelStatistics> {
        try {
            const response = await apiClient.get<ChannelStatistics>(
                `${this.baseURL}/statistics`
            );
            return response.data;
        } catch (error) {
            console.error('Failed to get channel statistics:', error);
            throw error;
        }
    }

    /**
     * Search channels by keyword
     *
     * @param query - Search query
     * @param limit - Max results
     * @returns Matching channels
     */
    async searchChannels(
        query: string,
        limit: number = 20
    ): Promise<AdminChannelInfo[]> {
        try {
            const response = await apiClient.get<AdminChannelInfo[]>(
                `${this.baseURL}/search`,
                { params: { q: query, limit } }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to search channels:', error);
            throw error;
        }
    }
}

// Export singleton instance
export const adminChannelsService = new AdminChannelsService();
export default adminChannelsService;

/**
 * Sharing Service
 * 
 * Integrates with backend /sharing/* endpoints for secure analytics sharing.
 * Provides token-based access control with TTL and audit trails.
 * 
 * Backend API: /sharing/create, /sharing/revoke, /sharing/{token}
 */

import apiClient from './apiClient';

export type TTLOption = '1h' | '6h' | '24h' | '3d' | '7d';

export interface CreateShareRequest {
    report_type: string;
    channel_id: string | number;
    ttl?: string;
    format?: 'csv' | 'png';
    period?: number;
}

export interface ShareLinkResponse {
    share_token: string;
    share_url: string;
    expires_at: string;
    access_count: number;
}

export interface SharedReportResponse {
    report_type: string;
    channel_id: string;
    period: number;
    created_at: string;
    expires_at: string;
    access_count: number;
    format: string;
    data: Record<string, any> | null;
}

export interface ShareListItem {
    share_token: string;
    report_type: string;
    channel_id: string;
    created_at: string;
    expires_at: string;
    access_count: number;
    is_expired: boolean;
}

/**
 * Sharing Service Class
 */
class SharingService {
    private baseURL = '/sharing';

    /**
     * Create a shareable link for analytics report
     * 
     * @param reportType - Type of report (engagement, growth, overview, etc.)
     * @param channelId - Channel ID
     * @param ttl - Time-to-live (1h, 6h, 24h, 3d, 7d)
     * @param format - Export format (csv or png)
     * @param period - Period in days
     * @returns Share link with token and expiration
     */
    async createShareLink(
        reportType: string,
        channelId: string | number,
        ttl: TTLOption = '24h',
        format: 'csv' | 'png' = 'csv',
        period: number = 30
    ): Promise<ShareLinkResponse> {
        try {
            const response = await apiClient.post<ShareLinkResponse>(
                `${this.baseURL}/create/${reportType}/${channelId}`,
                null,
                {
                    params: {
                        ttl,
                        format,
                        period
                    }
                }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to create share link:', error);
            throw error;
        }
    }

    /**
     * Access a shared report via token
     * 
     * @param shareToken - Secure share token
     * @returns Shared report data
     */
    async accessSharedReport(shareToken: string): Promise<SharedReportResponse> {
        try {
            const response = await apiClient.get<SharedReportResponse>(
                `${this.baseURL}/${shareToken}`
            );
            return response.data;
        } catch (error) {
            console.error('Failed to access shared report:', error);
            throw error;
        }
    }

    /**
     * Revoke a share link
     * 
     * @param shareToken - Token to revoke
     * @returns Success message
     */
    async revokeShareLink(shareToken: string): Promise<{ message: string }> {
        try {
            const response = await apiClient.delete<{ message: string }>(
                `${this.baseURL}/revoke/${shareToken}`
            );
            return response.data;
        } catch (error) {
            console.error('Failed to revoke share link:', error);
            throw error;
        }
    }

    /**
     * Get list of all share links for a channel
     * 
     * @param channelId - Channel ID
     * @returns List of share links
     */
    async getChannelShareLinks(channelId: string | number): Promise<ShareListItem[]> {
        try {
            const response = await apiClient.get<ShareListItem[]>(
                `${this.baseURL}/channel/${channelId}/links`
            );
            return response.data;
        } catch (error) {
            console.error('Failed to get channel share links:', error);
            throw error;
        }
    }

    /**
     * Get share link statistics
     * 
     * @param shareToken - Share token
     * @returns Access statistics
     */
    async getShareStats(shareToken: string): Promise<{
        access_count: number;
        last_accessed: string | null;
        created_at: string;
        expires_at: string;
    }> {
        try {
            const response = await apiClient.get(
                `${this.baseURL}/${shareToken}/stats`
            );
            return response.data;
        } catch (error) {
            console.error('Failed to get share stats:', error);
            throw error;
        }
    }

    /**
     * Check if a share link is valid
     * 
     * @param shareToken - Share token to validate
     * @returns Validation result
     */
    async validateShareToken(shareToken: string): Promise<{
        valid: boolean;
        expires_at?: string;
        is_expired?: boolean;
    }> {
        try {
            const response = await apiClient.get(
                `${this.baseURL}/validate/${shareToken}`
            );
            return response.data;
        } catch (error) {
            console.error('Failed to validate share token:', error);
            return { valid: false };
        }
    }
}

// Export singleton instance
export const sharingService = new SharingService();
export default sharingService;

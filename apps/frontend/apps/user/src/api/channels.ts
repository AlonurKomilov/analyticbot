/**
 * Channels API Module
 * API functions for channel management
 */

import { apiClient } from './client';

export interface ChannelLookupResult {
    is_valid: boolean;
    telegram_id: number | null;
    username: string | null;
    title: string | null;
    subscriber_count: number | null;
    description: string | null;
    telegram_created_at: string | null;
    is_verified: boolean;
    is_scam: boolean;
    is_admin: boolean | null;
    error_message: string | null;
}

export interface AddChannelRequest {
    name: string;
    username: string;
    description?: string;
    telegram_id?: number;
}

export interface ChannelResponse {
    id: number;
    name: string;
    username: string | null;
    subscriber_count: number;
    is_active: boolean;
    created_at: string;
    last_updated: string | null;
}

/**
 * Channels API functions
 */
export const channelsApi = {
    /**
     * Lookup channel info by username (auto-fetch from Telegram)
     */
    async lookupChannel(username: string): Promise<ChannelLookupResult> {
        const cleanUsername = username.trim().replace(/^@/, '');
        const response = await apiClient.get<ChannelLookupResult>(`/channels/lookup/${encodeURIComponent(cleanUsername)}`);
        return response;
    },

    /**
     * Add an existing Telegram channel for analytics
     */
    async addChannel(data: AddChannelRequest): Promise<ChannelResponse> {
        const response = await apiClient.post<ChannelResponse>('/channels/', data);
        return response;
    },

    /**
     * Get user's channels
     */
    async getChannels(): Promise<ChannelResponse[]> {
        const response = await apiClient.get<ChannelResponse[]>('/channels/');
        return response;
    },

    /**
     * Get single channel
     */
    async getChannel(channelId: number): Promise<ChannelResponse> {
        const response = await apiClient.get<ChannelResponse>(`/channels/${channelId}`);
        return response;
    },

    /**
     * Delete a channel
     */
    async deleteChannel(channelId: number): Promise<void> {
        await apiClient.delete(`/channels/${channelId}`);
    }
};

export default channelsApi;

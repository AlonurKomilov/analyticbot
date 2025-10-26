/**
 * Content Protection Service
 *
 * Security and content protection features.
 * Integrates with backend /content/protection/* endpoints.
 *
 * Features:
 * - Content theft detection
 * - Watermarking (text and images)
 * - Premium emoji formatting
 * - Content scanning
 * - Protection history
 */

import apiClient from '@shared/services/api/apiClient';

export interface TheftDetectionRequest {
    channel_id: string | number;
    content_hash?: string;
    check_platforms?: string[];
}

export interface TheftDetectionResult {
    detected: boolean;
    matches: TheftMatch[];
    confidence: number;
    scan_date: string;
}

export interface TheftMatch {
    platform: string;
    url: string;
    similarity: number;
    detected_at: string;
}

export interface WatermarkRequest {
    text: string;
    watermark_type?: 'invisible' | 'visible';
    position?: 'top' | 'bottom' | 'center';
}

export interface WatermarkResponse {
    watermarked_text: string;
    watermark_id: string;
    expires_at?: string;
}

export interface ImageWatermarkRequest {
    image_url: string;
    watermark_text: string;
    opacity?: number;
    position?: 'topleft' | 'topright' | 'bottomleft' | 'bottomright' | 'center';
}

export interface ProtectionHistory {
    scan_id: string;
    channel_id: string;
    scan_type: 'theft' | 'watermark';
    result: string;
    created_at: string;
}

export interface ProtectionStatistics {
    total_scans: number;
    theft_detected: number;
    watermarks_applied: number;
    last_scan: string;
    protection_level: 'low' | 'medium' | 'high';
}

/**
 * Content Protection Service Class
 */
class ContentProtectionService {
    private baseURL = '/content/protection';

    /**
     * Scan for content theft
     *
     * @param channelId - Channel ID
     * @param contentHash - Optional content hash
     * @param platforms - Platforms to check
     * @returns Theft detection results
     */
    async scanForTheft(
        channelId: string | number,
        contentHash?: string,
        platforms?: string[]
    ): Promise<TheftDetectionResult> {
        try {
            const response = await apiClient.post<TheftDetectionResult>(
                `${this.baseURL}/detection/scan`,
                {
                    channel_id: channelId,
                    content_hash: contentHash,
                    check_platforms: platforms || ['telegram', 'twitter', 'facebook']
                }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to scan for theft:', error);
            throw error;
        }
    }

    /**
     * Get theft detection history
     *
     * @param channelId - Channel ID
     * @param limit - Number of results
     * @returns Detection history
     */
    async getTheftHistory(
        channelId: string | number,
        limit: number = 50
    ): Promise<TheftDetectionResult[]> {
        try {
            const response = await apiClient.get<TheftDetectionResult[]>(
                `${this.baseURL}/detection/history`,
                {
                    params: { channel_id: channelId, limit }
                }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to get theft history:', error);
            throw error;
        }
    }

    /**
     * Get theft detection statistics
     *
     * @param channelId - Channel ID
     * @returns Detection stats
     */
    async getTheftStats(channelId: string | number): Promise<{
        total_scans: number;
        matches_found: number;
        last_scan: string;
    }> {
        try {
            const response = await apiClient.get(
                `${this.baseURL}/detection/stats`,
                { params: { channel_id: channelId } }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to get theft stats:', error);
            throw error;
        }
    }

    /**
     * Apply text watermark
     *
     * @param text - Text to watermark
     * @param watermarkType - Watermark visibility
     * @param position - Watermark position
     * @returns Watermarked text
     */
    async applyTextWatermark(
        text: string,
        watermarkType: 'invisible' | 'visible' = 'invisible',
        position: 'top' | 'bottom' | 'center' = 'bottom'
    ): Promise<WatermarkResponse> {
        try {
            const response = await apiClient.post<WatermarkResponse>(
                `${this.baseURL}/watermark/text`,
                {
                    text,
                    watermark_type: watermarkType,
                    position
                }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to apply text watermark:', error);
            throw error;
        }
    }

    /**
     * Apply image watermark
     *
     * @param imageUrl - Image URL
     * @param watermarkText - Watermark text
     * @param opacity - Watermark opacity (0-1)
     * @param position - Watermark position
     * @returns Watermarked image URL
     */
    async applyImageWatermark(
        imageUrl: string,
        watermarkText: string,
        opacity: number = 0.5,
        position: 'topleft' | 'topright' | 'bottomleft' | 'bottomright' | 'center' = 'bottomright'
    ): Promise<{ watermarked_image_url: string; watermark_id: string }> {
        try {
            const response = await apiClient.post(
                `${this.baseURL}/watermark/image`,
                {
                    image_url: imageUrl,
                    watermark_text: watermarkText,
                    opacity,
                    position
                }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to apply image watermark:', error);
            throw error;
        }
    }

    /**
     * Format text with premium emojis
     *
     * @param text - Text to format
     * @param customEmojiIds - Custom emoji IDs to use
     * @returns Formatted text with premium emojis
     */
    async formatPremiumEmojis(
        text: string,
        customEmojiIds?: string[]
    ): Promise<{
        formatted_text: string;
        entities: any[];
    }> {
        try {
            const response = await apiClient.post(
                `${this.baseURL}/premium/emojis`,
                {
                    text,
                    custom_emoji_ids: customEmojiIds
                }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to format premium emojis:', error);
            throw error;
        }
    }

    /**
     * Get protection history
     *
     * @param channelId - Channel ID
     * @param limit - Number of entries
     * @returns Protection history
     */
    async getProtectionHistory(
        channelId: string | number,
        limit: number = 100
    ): Promise<ProtectionHistory[]> {
        try {
            const response = await apiClient.get<ProtectionHistory[]>(
                `${this.baseURL}/history`,
                {
                    params: { channel_id: channelId, limit }
                }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to get protection history:', error);
            throw error;
        }
    }

    /**
     * Get protection statistics
     *
     * @param channelId - Channel ID
     * @returns Protection stats
     */
    async getProtectionStats(channelId: string | number): Promise<ProtectionStatistics> {
        try {
            const response = await apiClient.get<ProtectionStatistics>(
                `${this.baseURL}/statistics`,
                { params: { channel_id: channelId } }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to get protection statistics:', error);
            throw error;
        }
    }

    /**
     * Verify watermark authenticity
     *
     * @param watermarkId - Watermark ID to verify
     * @returns Verification result
     */
    async verifyWatermark(watermarkId: string): Promise<{
        valid: boolean;
        original_content_id?: string;
        created_at?: string;
    }> {
        try {
            const response = await apiClient.get(
                `${this.baseURL}/watermark/verify/${watermarkId}`
            );
            return response.data;
        } catch (error) {
            console.error('Failed to verify watermark:', error);
            throw error;
        }
    }
}

// Export singleton instance
export const contentProtectionService = new ContentProtectionService();
export default contentProtectionService;

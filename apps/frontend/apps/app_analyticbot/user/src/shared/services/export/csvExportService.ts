/**
 * CSV Export Microservice
 *
 * Single Responsibility: CSV data export only
 * Separated from: chart export, PDF export, batch operations
 */

import { apiClient } from '@/api/client';

export interface CSVExportOptions {
    include_headers?: boolean;
    date_range?: {
        start: string;
        end: string;
    };
    filters?: Record<string, any>;
}

/**
 * CSV Export Service
 * Focused on: CSV file generation and download
 */
class CSVExportService {
    private baseURL = '/exports/csv';

    /**
     * Export overview data as CSV
     */
    async exportOverview(
        channelId: string,
        period: number = 30,
        options: CSVExportOptions = {}
    ): Promise<Blob> {
        try {
            const response = await apiClient.get<Blob>(
                `${this.baseURL}/overview/${channelId}`,
                {
                    params: { period, ...options },
                    responseType: 'blob'
                }
            );
            return response;
        } catch (error) {
            console.error('Failed to export overview CSV:', error);
            throw error;
        }
    }

    /**
     * Export growth data as CSV
     */
    async exportGrowth(
        channelId: string,
        period: number = 30,
        options: CSVExportOptions = {}
    ): Promise<Blob> {
        try {
            const response = await apiClient.get<Blob>(
                `${this.baseURL}/growth/${channelId}`,
                {
                    params: { period, ...options },
                    responseType: 'blob'
                }
            );
            return response;
        } catch (error) {
            console.error('Failed to export growth CSV:', error);
            throw error;
        }
    }

    /**
     * Export top posts as CSV
     */
    async exportTopPosts(
        channelId: string,
        period: number = 30,
        limit: number = 100,
        options: CSVExportOptions = {}
    ): Promise<Blob> {
        try {
            const response = await apiClient.get<Blob>(
                `${this.baseURL}/top-posts/${channelId}`,
                {
                    params: { period, limit, ...options },
                    responseType: 'blob'
                }
            );
            return response;
        } catch (error) {
            console.error('Failed to export top posts CSV:', error);
            throw error;
        }
    }

    /**
     * Export engagement data as CSV
     */
    async exportEngagement(
        channelId: string,
        period: number = 30,
        options: CSVExportOptions = {}
    ): Promise<Blob> {
        try {
            const response = await apiClient.get<Blob>(
                `${this.baseURL}/engagement/${channelId}`,
                {
                    params: { period, ...options },
                    responseType: 'blob'
                }
            );
            return response;
        } catch (error) {
            console.error('Failed to export engagement CSV:', error);
            throw error;
        }
    }

    /**
     * Helper: Download blob as file
     */
    private downloadBlob(blob: Blob, filename: string): void {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }

    /**
     * Export and auto-download
     */
    async exportAndDownload(
        channelId: string,
        type: 'overview' | 'growth' | 'top-posts' | 'engagement',
        period: number = 30
    ): Promise<void> {
        try {
            let blob: Blob;
            let filename: string;

            switch (type) {
                case 'overview':
                    blob = await this.exportOverview(channelId, period);
                    filename = `${channelId}-overview-${period}d.csv`;
                    break;
                case 'growth':
                    blob = await this.exportGrowth(channelId, period);
                    filename = `${channelId}-growth-${period}d.csv`;
                    break;
                case 'top-posts':
                    blob = await this.exportTopPosts(channelId, period);
                    filename = `${channelId}-top-posts-${period}d.csv`;
                    break;
                case 'engagement':
                    blob = await this.exportEngagement(channelId, period);
                    filename = `${channelId}-engagement-${period}d.csv`;
                    break;
            }

            this.downloadBlob(blob, filename);
        } catch (error) {
            console.error('Failed to export and download:', error);
            throw error;
        }
    }
}

export const csvExportService = new CSVExportService();
export default csvExportService;

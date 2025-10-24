/**
 * Chart Export Microservice
 * 
 * Single Responsibility: PNG chart image generation only
 * Separated from: CSV export, PDF export, batch operations
 */

import apiClient from '../apiClient';

export type ChartType = 'line' | 'bar' | 'pie' | 'area' | 'scatter';

export interface ChartExportOptions {
    width?: number;
    height?: number;
    chart_type?: ChartType;
    theme?: 'light' | 'dark';
    title?: string;
}

/**
 * Chart Export Service
 * Focused on: PNG chart image generation
 */
class ChartExportService {
    private baseURL = '/exports/png';

    /**
     * Export chart as PNG image
     */
    async exportChart(
        channelId: string,
        chartType: ChartType,
        period: number = 30,
        options: ChartExportOptions = {}
    ): Promise<Blob> {
        try {
            const response = await apiClient.get<Blob>(
                `${this.baseURL}/chart/${channelId}`,
                {
                    params: {
                        chart_type: chartType,
                        period,
                        width: options.width || 1200,
                        height: options.height || 600,
                        theme: options.theme || 'light',
                        title: options.title
                    },
                    responseType: 'blob'
                }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to export chart PNG:', error);
            throw error;
        }
    }

    /**
     * Export overview chart as PNG
     */
    async exportOverview(
        channelId: string,
        period: number = 30,
        options: ChartExportOptions = {}
    ): Promise<Blob> {
        try {
            const response = await apiClient.get<Blob>(
                `${this.baseURL}/overview/${channelId}`,
                {
                    params: { period, ...options },
                    responseType: 'blob'
                }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to export overview PNG:', error);
            throw error;
        }
    }

    /**
     * Export growth chart as PNG
     */
    async exportGrowthChart(
        channelId: string,
        period: number = 30,
        options: ChartExportOptions = {}
    ): Promise<Blob> {
        try {
            const response = await apiClient.get<Blob>(
                `${this.baseURL}/growth/${channelId}`,
                {
                    params: { period, ...options },
                    responseType: 'blob'
                }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to export growth chart PNG:', error);
            throw error;
        }
    }

    /**
     * Export engagement chart as PNG
     */
    async exportEngagementChart(
        channelId: string,
        period: number = 30,
        options: ChartExportOptions = {}
    ): Promise<Blob> {
        try {
            const response = await apiClient.get<Blob>(
                `${this.baseURL}/engagement/${channelId}`,
                {
                    params: { period, ...options },
                    responseType: 'blob'
                }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to export engagement chart PNG:', error);
            throw error;
        }
    }

    /**
     * Helper: Download chart as image file
     */
    private downloadImage(blob: Blob, filename: string): void {
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
     * Export chart and auto-download
     */
    async exportAndDownload(
        channelId: string,
        chartType: ChartType,
        period: number = 30,
        options: ChartExportOptions = {}
    ): Promise<void> {
        try {
            const blob = await this.exportChart(channelId, chartType, period, options);
            const filename = `${channelId}-${chartType}-chart-${period}d.png`;
            this.downloadImage(blob, filename);
        } catch (error) {
            console.error('Failed to export and download chart:', error);
            throw error;
        }
    }
}

export const chartExportService = new ChartExportService();
export default chartExportService;

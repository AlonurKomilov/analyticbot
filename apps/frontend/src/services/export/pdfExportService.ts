/**
 * PDF Export Microservice
 *
 * Single Responsibility: PDF report generation only
 * Separated from: CSV export, chart export, batch operations
 */

import apiClient from '../apiClient';

export interface PDFExportOptions {
    include_charts?: boolean;
    include_tables?: boolean;
    date_range?: {
        start: string;
        end: string;
    };
    sections?: string[];
}

/**
 * PDF Export Service
 * Focused on: PDF report generation and download
 */
class PDFExportService {
    private baseURL = '/exports/pdf';

    /**
     * Export full analytics report as PDF
     */
    async exportReport(
        channelId: string,
        period: number = 30,
        options: PDFExportOptions = {}
    ): Promise<Blob> {
        try {
            const response = await apiClient.get<Blob>(
                `${this.baseURL}/report/${channelId}`,
                {
                    params: { period, ...options },
                    responseType: 'blob'
                }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to export PDF report:', error);
            throw error;
        }
    }

    /**
     * Export overview report as PDF
     */
    async exportOverview(
        channelId: string,
        period: number = 30,
        options: PDFExportOptions = {}
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
            console.error('Failed to export overview PDF:', error);
            throw error;
        }
    }

    /**
     * Export custom report with selected sections
     */
    async exportCustomReport(
        channelId: string,
        sections: string[],
        period: number = 30,
        options: PDFExportOptions = {}
    ): Promise<Blob> {
        try {
            const response = await apiClient.post<Blob>(
                `${this.baseURL}/custom/${channelId}`,
                {
                    sections,
                    period,
                    ...options
                },
                { responseType: 'blob' }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to export custom PDF report:', error);
            throw error;
        }
    }

    /**
     * Helper: Download PDF file
     */
    private downloadPDF(blob: Blob, filename: string): void {
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
     * Export report and auto-download
     */
    async exportAndDownload(
        channelId: string,
        period: number = 30,
        options: PDFExportOptions = {}
    ): Promise<void> {
        try {
            const blob = await this.exportReport(channelId, period, options);
            const filename = `${channelId}-report-${period}d.pdf`;
            this.downloadPDF(blob, filename);
        } catch (error) {
            console.error('Failed to export and download PDF:', error);
            throw error;
        }
    }
}

export const pdfExportService = new PDFExportService();
export default pdfExportService;

/**
 * Batch Export Microservice
 * 
 * Single Responsibility: Batch export job management only
 * Separated from: individual CSV/PNG/PDF exports
 */

import apiClient from '../apiClient';

export type ExportFormat = 'csv' | 'png' | 'pdf' | 'json';

export interface ExportJob {
    id: string;
    type: string;
    status: 'pending' | 'processing' | 'completed' | 'failed';
    created_at: string;
    completed_at?: string;
    download_url?: string;
    error?: string;
}

/**
 * Batch Export Service
 * Focused on: Asynchronous batch export operations and job tracking
 */
class BatchExportService {
    private baseURL = '/exports/batch';

    /**
     * Export all analytics data for a channel
     */
    async exportAll(
        channelId: string,
        period: number = 30,
        format: ExportFormat = 'csv'
    ): Promise<{ job_id: string }> {
        try {
            const response = await apiClient.post<{ job_id: string }>(
                `${this.baseURL}/all`,
                {
                    channel_id: channelId,
                    period,
                    format
                }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to start batch export:', error);
            throw error;
        }
    }

    /**
     * Get export job status
     */
    async getJobStatus(jobId: string): Promise<ExportJob> {
        try {
            const response = await apiClient.get<ExportJob>(
                `${this.baseURL}/status/${jobId}`
            );
            return response.data;
        } catch (error) {
            console.error('Failed to get export job status:', error);
            throw error;
        }
    }

    /**
     * Download completed export
     */
    async downloadExport(jobId: string): Promise<Blob> {
        try {
            const response = await apiClient.get<Blob>(
                `${this.baseURL}/download/${jobId}`,
                { responseType: 'blob' }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to download export:', error);
            throw error;
        }
    }

    /**
     * Get all user's export jobs
     */
    async getUserJobs(userId: number): Promise<ExportJob[]> {
        try {
            const response = await apiClient.get<{ jobs: ExportJob[] }>(
                `${this.baseURL}/jobs/${userId}`
            );
            return response.data.jobs || [];
        } catch (error) {
            console.error('Failed to get user export jobs:', error);
            throw error;
        }
    }

    /**
     * Cancel pending export job
     */
    async cancelJob(jobId: string): Promise<{ success: boolean }> {
        try {
            const response = await apiClient.delete(
                `${this.baseURL}/job/${jobId}`
            );
            return response.data;
        } catch (error) {
            console.error('Failed to cancel export job:', error);
            throw error;
        }
    }

    /**
     * Poll job status until completed or failed
     */
    async waitForCompletion(
        jobId: string,
        pollInterval: number = 2000,
        maxWaitTime: number = 300000 // 5 minutes
    ): Promise<ExportJob> {
        const startTime = Date.now();
        
        return new Promise((resolve, reject) => {
            const poll = async () => {
                try {
                    const job = await this.getJobStatus(jobId);
                    
                    if (job.status === 'completed') {
                        resolve(job);
                        return;
                    }
                    
                    if (job.status === 'failed') {
                        reject(new Error(job.error || 'Export job failed'));
                        return;
                    }
                    
                    if (Date.now() - startTime > maxWaitTime) {
                        reject(new Error('Export job timeout'));
                        return;
                    }
                    
                    setTimeout(poll, pollInterval);
                } catch (error) {
                    reject(error);
                }
            };
            
            poll();
        });
    }
}

export const batchExportService = new BatchExportService();
export default batchExportService;

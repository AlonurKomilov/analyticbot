/**
 * Storage Mock Service
 * Provides mock data for storage-related features (files, uploads, etc.)
 * Separated from analytics services to maintain clean separation of concerns
 */

class StorageMockService {
    constructor() {
        this.networkDelay = 200; // Simulate network delay
    }

    async simulateDelay() {
        await new Promise(resolve => setTimeout(resolve, this.networkDelay));
    }

    async getStorageFiles(limit = 20, offset = 0) {
        await this.simulateDelay();
        
        const mockFiles = [
            { id: 1, name: 'analytics_report.csv', size: 15234, type: 'csv', created: '2025-09-10T10:30:00Z' },
            { id: 2, name: 'post_dynamics.png', size: 45621, type: 'png', created: '2025-09-09T15:45:00Z' },
            { id: 3, name: 'engagement_chart.pdf', size: 78943, type: 'pdf', created: '2025-09-08T09:15:00Z' },
            { id: 4, name: 'weekly_summary.xlsx', size: 23456, type: 'xlsx', created: '2025-09-07T14:20:00Z' },
            { id: 5, name: 'content_backup.zip', size: 156789, type: 'zip', created: '2025-09-06T11:30:00Z' },
            { id: 6, name: 'user_exports.json', size: 8765, type: 'json', created: '2025-09-05T16:45:00Z' },
            { id: 7, name: 'media_assets.tar.gz', size: 234567, type: 'tar.gz', created: '2025-09-04T12:10:00Z' },
            { id: 8, name: 'database_backup.sql', size: 89012, type: 'sql', created: '2025-09-03T08:30:00Z' }
        ];
        
        const startIndex = offset;
        const endIndex = Math.min(offset + limit, mockFiles.length);
        const paginatedFiles = mockFiles.slice(startIndex, endIndex);
        
        return {
            files: paginatedFiles,
            total: mockFiles.length,
            limit,
            offset,
            hasMore: endIndex < mockFiles.length
        };
    }

    async uploadFile(file) {
        await this.simulateDelay();
        
        return {
            id: Date.now(),
            name: file.name,
            size: file.size,
            type: file.type,
            created: new Date().toISOString(),
            status: 'uploaded'
        };
    }

    async deleteFile(fileId) {
        await this.simulateDelay();
        
        return {
            success: true,
            fileId,
            message: 'File deleted successfully'
        };
    }
}

// Create and export singleton instance
export const storageMockService = new StorageMockService();

// Export class for testing
export { StorageMockService };

export default storageMockService;
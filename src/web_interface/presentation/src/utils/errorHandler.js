/**
 * Enhanced Error Handler for TWA Phase 2.1
 */

class ErrorHandler {
    /**
     * Handle API errors with context
     */
    static handleApiError(error, endpoint, context = {}) {
        console.error(`API Error [${endpoint}]:`, {
            error: error.message,
            context,
            timestamp: new Date().toISOString()
        });

        // Return user-friendly error message
        if (error.response) {
            const { status } = error.response;
            switch (status) {
                case 400:
                    return 'Invalid request. Please check your input.';
                case 401:
                    return 'Authentication failed. Please try again.';
                case 403:
                    return 'Access denied. Check your permissions.';
                case 404:
                    return 'Resource not found.';
                case 413:
                    return 'File too large. Maximum size exceeded.';
                case 429:
                    return 'Too many requests. Please wait and try again.';
                case 500:
                    return 'Server error. Please try again later.';
                default:
                    return `Request failed with status ${status}`;
            }
        }

        // Network or other errors
        if (error.message.includes('timeout')) {
            return 'Request timeout. Please check your connection.';
        }

        if (error.message.includes('network')) {
            return 'Network error. Please check your connection.';
        }

        return error.message || 'An unexpected error occurred.';
    }

    /**
     * Handle general application errors
     */
    static handleError(error, context = {}) {
        console.error('Application Error:', {
            error: error.message,
            stack: error.stack,
            context,
            timestamp: new Date().toISOString()
        });

        // In development, you might want to show more details
        if (import.meta.env?.DEV) {
            console.groupCollapsed('Error Details');
            console.error('Error object:', error);
            console.error('Context:', context);
            console.groupEnd();
        }

        return error.message || 'An error occurred';
    }

    /**
     * Handle file upload errors
     */
    static handleUploadError(error, file = null) {
        console.error('Upload Error:', {
            error: error.message,
            fileName: file?.name,
            fileSize: file?.size,
            fileType: file?.type,
            timestamp: new Date().toISOString()
        });

        // Specific upload error messages
        if (error.message.includes('File too large')) {
            return 'File is too large. Please choose a smaller file.';
        }

        if (error.message.includes('File type not supported')) {
            return 'File type not supported. Please choose a different file format.';
        }

        if (error.message.includes('Upload timeout')) {
            return 'Upload timed out. Please check your connection and try again.';
        }

        return this.handleApiError(error, '/upload', { fileName: file?.name });
    }

    /**
     * Validate file before upload
     */
    static validateFile(file) {
        const maxSize = 50 * 1024 * 1024; // 50MB
        const allowedTypes = [
            'image/jpeg', 'image/png', 'image/gif', 'image/webp',
            'video/mp4', 'video/webm', 'video/mov',
            'application/pdf', 'text/plain'
        ];

        if (!file) {
            throw new Error('No file selected');
        }

        if (file.size > maxSize) {
            throw new Error('File too large. Maximum size is 50MB.');
        }

        if (!allowedTypes.includes(file.type)) {
            throw new Error(`File type not supported: ${file.type}`);
        }

        return true;
    }

    /**
     * Format error for user display
     */
    static formatErrorMessage(error) {
        if (typeof error === 'string') {
            return error;
        }

        if (error.message) {
            return error.message;
        }

        return 'An unexpected error occurred';
    }
}

export { ErrorHandler };

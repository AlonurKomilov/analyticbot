import { ErrorHandler } from './errorHandler.js';

const VITE_API_URL = import.meta.env.VITE_API_URL;
const REQUEST_TIMEOUT = 30000; // 30 seconds
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second

/**
 * Enhanced API client with retry logic, timeout, and comprehensive error handling
 */
class ApiClient {
    constructor() {
        this.baseURL = VITE_API_URL;
        this.defaultHeaders = {
            'Content-Type': 'application/json',
        };
    }

    /**
     * Get authentication headers with TWA data
     */
    getAuthHeaders() {
        const twaInitData = window.Telegram?.WebApp?.initData || '';
        return {
            ...this.defaultHeaders,
            'Authorization': `TWA ${twaInitData}`
        };
    }

    /**
     * Sleep utility for retry delays
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Check if error is retryable
     */
    isRetryableError(error) {
        if (!error.response) return true; // Network errors are retryable
        const status = error.response.status;
        return status === 408 || status === 429 || status >= 500;
    }

    /**
     * Make HTTP request with timeout and retry logic
     */
    async request(endpoint, options = {}, attempt = 1) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

        try {
            const url = `${this.baseURL}${endpoint}`;
            const config = {
                ...options,
                headers: {
                    ...this.getAuthHeaders(),
                    ...options.headers
                },
                signal: controller.signal
            };

            const response = await fetch(url, config);
            clearTimeout(timeoutId);

            const responseData = await response.json();

            if (!response.ok) {
                const error = new Error(responseData.detail || 'API request failed');
                error.response = {
                    status: response.status,
                    statusText: response.statusText,
                    data: responseData
                };
                throw error;
            }

            return responseData;

        } catch (error) {
            clearTimeout(timeoutId);

            // Handle timeout
            if (error.name === 'AbortError') {
                const timeoutError = new Error('Request timeout');
                timeoutError.response = { status: 408 };
                throw timeoutError;
            }

            // Retry logic
            if (this.isRetryableError(error) && attempt < MAX_RETRIES) {
                console.warn(`API request failed (attempt ${attempt}/${MAX_RETRIES}), retrying...`, {
                    endpoint,
                    error: error.message
                });
                
                await this.sleep(RETRY_DELAY * attempt);
                return this.request(endpoint, options, attempt + 1);
            }

            // Final error handling
            throw ErrorHandler.handleApiError(error, endpoint, {
                component: 'ApiClient',
                action: 'request',
                attempt
            });
        }
    }

    /**
     * GET request
     */
    async get(endpoint, params = {}) {
        const searchParams = new URLSearchParams(params);
        const url = searchParams.toString() ? `${endpoint}?${searchParams}` : endpoint;
        return this.request(url, { method: 'GET' });
    }

    /**
     * POST request
     */
    async post(endpoint, data = null) {
        return this.request(endpoint, {
            method: 'POST',
            body: data ? JSON.stringify(data) : null
        });
    }

    /**
     * PUT request
     */
    async put(endpoint, data = null) {
        return this.request(endpoint, {
            method: 'PUT',
            body: data ? JSON.stringify(data) : null
        });
    }

    /**
     * DELETE request
     */
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }

    /**
     * Upload file with progress tracking
     */
    async uploadFile(endpoint, file, onProgress = null) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            const formData = new FormData();
            formData.append('file', file);

            // Progress tracking
            if (onProgress) {
                xhr.upload.addEventListener('progress', (event) => {
                    if (event.lengthComputable) {
                        const progress = (event.loaded / event.total) * 100;
                        onProgress(progress);
                    }
                });
            }

            // Success handler
            xhr.addEventListener('load', () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        resolve(response);
                    } catch {
                        reject(new Error('Invalid JSON response'));
                    }
                } else {
                    const error = new Error(`Upload failed: ${xhr.statusText}`);
                    error.response = {
                        status: xhr.status,
                        statusText: xhr.statusText
                    };
                    reject(ErrorHandler.handleApiError(error, endpoint, {
                        component: 'ApiClient',
                        action: 'uploadFile'
                    }));
                }
            });

            // Error handler
            xhr.addEventListener('error', () => {
                const error = new Error('Upload failed');
                reject(ErrorHandler.handleApiError(error, endpoint, {
                    component: 'ApiClient',
                    action: 'uploadFile'
                }));
            });

            // Timeout handler
            xhr.addEventListener('timeout', () => {
                const error = new Error('Upload timeout');
                error.response = { status: 408 };
                reject(ErrorHandler.handleApiError(error, endpoint, {
                    component: 'ApiClient',
                    action: 'uploadFile'
                }));
            });

            // Set timeout and headers
            xhr.timeout = REQUEST_TIMEOUT;
            
            // Set auth header
            const twaInitData = window.Telegram?.WebApp?.initData || '';
            xhr.setRequestHeader('Authorization', `TWA ${twaInitData}`);

            // Start upload
            xhr.open('POST', `${this.baseURL}${endpoint}`);
            xhr.send(formData);
        });
    }

    /**
     * Enhanced direct upload with channel targeting (NEW for TWA Phase 2.1)
     */
    async uploadFileDirect(file, channelId = null, onProgress = null) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            const formData = new FormData();
            formData.append('file', file);
            
            // Add channel_id if provided
            if (channelId) {
                formData.append('channel_id', channelId.toString());
            }

            // Progress tracking with enhanced metadata
            if (onProgress) {
                xhr.upload.addEventListener('progress', (event) => {
                    if (event.lengthComputable) {
                        const progress = (event.loaded / event.total) * 100;
                        onProgress({
                            progress,
                            loaded: event.loaded,
                            total: event.total,
                            speed: event.loaded / ((Date.now() - startTime) / 1000) // bytes per second
                        });
                    }
                });
            }

            const startTime = Date.now();

            // Success handler with enhanced response
            xhr.addEventListener('load', () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        // Enhanced response with upload metadata
                        resolve({
                            ...response,
                            upload_duration: Date.now() - startTime,
                            upload_speed: file.size / ((Date.now() - startTime) / 1000)
                        });
                    } catch {
                        reject(new Error('Invalid JSON response'));
                    }
                } else {
                    const error = new Error(`Direct upload failed: ${xhr.statusText}`);
                    error.response = {
                        status: xhr.status,
                        statusText: xhr.statusText
                    };
                    reject(ErrorHandler.handleApiError(error, '/api/v1/media/upload-direct', {
                        component: 'ApiClient',
                        action: 'uploadFileDirect',
                        channelId
                    }));
                }
            });

            // Error handler
            xhr.addEventListener('error', () => {
                const error = new Error('Direct upload failed');
                reject(ErrorHandler.handleApiError(error, '/api/v1/media/upload-direct', {
                    component: 'ApiClient',
                    action: 'uploadFileDirect',
                    channelId
                }));
            });

            // Timeout handler
            xhr.addEventListener('timeout', () => {
                const error = new Error('Direct upload timeout');
                error.response = { status: 408 };
                reject(ErrorHandler.handleApiError(error, '/api/v1/media/upload-direct', {
                    component: 'ApiClient',
                    action: 'uploadFileDirect',
                    channelId
                }));
            });

            // Set timeout and headers
            xhr.timeout = REQUEST_TIMEOUT;
            
            // Set auth header
            const twaInitData = window.Telegram?.WebApp?.initData || '';
            xhr.setRequestHeader('Authorization', `TWA ${twaInitData}`);

            // Start upload to enhanced direct endpoint
            xhr.open('POST', `${this.baseURL}/api/v1/media/upload-direct`);
            xhr.send(formData);
        });
    }

    /**
     * Get storage files for media browser (NEW for TWA Phase 2.1)
     */
    async getStorageFiles(limit = 20, offset = 0) {
        return this.get(`/api/v1/media/storage-files?limit=${limit}&offset=${offset}`);
    }
}

// Create singleton instance
export const apiClient = new ApiClient();

// Backward compatibility function
export const apiFetch = async (endpoint, options = {}) => {
    const method = options.method || 'GET';
    const data = options.body ? JSON.parse(options.body) : null;

    switch (method.toUpperCase()) {
        case 'GET':
            return apiClient.get(endpoint);
        case 'POST':
            return apiClient.post(endpoint, data);
        case 'PUT':
            return apiClient.put(endpoint, data);
        case 'DELETE':
            return apiClient.delete(endpoint);
        default:
            throw new Error(`Unsupported method: ${method}`);
    }
};

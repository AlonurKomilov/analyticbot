/**
 * Unified API Client (TypeScript)
 * Consolidates all API client functionality with full type safety
 *
 * Features:
 * - Multiple authentication strategies (JWT, TWA)
 * - Automatic token refresh (proactive + reactive)
 * - Retry logic with exponential backoff
 * - Mock/real data source switching
 * - File upload capabilities
 * - Comprehensive error handling
 * - Type-safe method interface
 */

import type {
  RequestConfig,
  ApiClientConfig,
  AuthStrategy,
  UploadProgress,
  BatchAnalyticsResponse,
  HealthCheckResponse,
  StorageFilesResponse,
  ApiError
} from '@/types';
import { tokenRefreshManager } from '@/utils/tokenRefreshManager';
import { getDeviceFingerprint } from '@/utils/deviceFingerprint';

// Configuration constants
const DEFAULT_CONFIG: ApiClientConfig = {
  baseURL: import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'https://b2qz1m0n-11400.euw.devtunnels.ms',
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT || '30000'),
  maxRetries: 3,
  retryDelay: 1000,
  retryMultiplier: 2
};

// Endpoint-specific timeouts optimized for production
// Note: API responds in 17-173ms locally. DevTunnel adds ~500ms network latency.
// Production deployment will eliminate DevTunnel and be much faster.
const ENDPOINT_TIMEOUTS: Record<string, number> = {
  '/health': 5000,
  '/auth/login': 10000,
  '/auth/register': 10000,
  '/auth/me': 10000,
  '/auth/refresh': 10000,
  '/analytics/channels': 10000, // Reduced from 60s - analytics queries are cached
  '/channels': 5000, // Reduced from 60s - simple database queries
  '/system/schedule': 5000, // Reduced from 90s - database insert is fast
  '/system/send': 10000, // Telegram API + database
  '/schedule/': 5000, // Reduced from 90s - simple SELECT query
  '/analytics/': 15000, // For complex analytics queries
  '/api/user-bot/': 15000, // Reduced from 90s - bot operations with reasonable timeout
  '/api/user-mtproto': 30000, // MTProto setup/verify needs longer timeout (network + Telegram latency)
  'default': 5000 // Reduced from 30s - fail fast for better UX
};

/**
 * Authentication strategies enum
 */
export const AuthStrategies: Record<string, AuthStrategy> = {
  JWT: 'jwt',
  TWA: 'twa',
  NONE: 'none'
} as const;

/**
 * API Error class with response details
 */
export class ApiRequestError extends Error implements ApiError {
  code?: string;
  status?: number;
  details?: Record<string, unknown>;
  response?: {
    status: number;
    statusText: string;
    data?: unknown;
  };

  constructor(message: string, response?: { status: number; statusText: string; data?: unknown }) {
    super(message);
    this.name = 'ApiRequestError';
    this.response = response;
    this.status = response?.status;
  }
}

/**
 * Unified API Client Class
 */
export class UnifiedApiClient {
  private config: ApiClientConfig;
  private authStrategy: AuthStrategy;
  private defaultHeaders: Record<string, string>;

  constructor(config: Partial<ApiClientConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.authStrategy = AuthStrategies.JWT;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    };

    // Debug logging
    if (import.meta.env.DEV) {
      console.log('🔧 Unified API Client Configuration:', {
        baseURL: this.config.baseURL,
        timeout: this.config.timeout,
        maxRetries: this.config.maxRetries,
        authStrategy: this.authStrategy,
      });
    }
  }

  /**
   * Set authentication strategy
   */
  setAuthStrategy(strategy: AuthStrategy): void {
    const validStrategies: AuthStrategy[] = ['jwt', 'twa', 'none'];
    if (!validStrategies.includes(strategy)) {
      throw new Error(`Invalid auth strategy: ${strategy}`);
    }
    this.authStrategy = strategy;
    console.log(`🔐 Auth strategy set to: ${strategy}`);
  }

  /**
   * Get authentication headers based on current strategy
   */
  private getAuthHeaders(): Record<string, string> {
    const headers = { ...this.defaultHeaders };

    // 🔐 Add device fingerprint to all requests
    const deviceId = getDeviceFingerprint();
    headers['X-Device-ID'] = deviceId;

    switch (this.authStrategy) {
      case 'jwt': {
        // Check all possible token storage keys
        const token = localStorage.getItem('access_token') ||
                     localStorage.getItem('auth_token') ||
                     localStorage.getItem('token') ||
                     localStorage.getItem('accessToken') ||
                     sessionStorage.getItem('access_token');
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
          if (import.meta.env.DEV) {
            console.log('🔑 Using JWT token:', token.substring(0, 20) + '...');
          }
        } else {
          if (import.meta.env.DEV) {
            console.warn('⚠️ No JWT token found in storage');
          }
        }
        break;
      }

      case 'twa': {
        const twaInitData = (window as any).Telegram?.WebApp?.initData || '';
        if (twaInitData) {
          headers['Authorization'] = `TWA ${twaInitData}`;
        }
        break;
      }

      case 'none':
        // No authentication headers
        break;
    }

    return headers;
  }

  /**
   * Check if error is retryable
   */
  private isRetryableError(error: ApiRequestError): boolean {
    if (!error.response) return true; // Network errors are retryable
    const status = error.response.status;

    // Don't retry:
    // - 4xx client errors (bad request, validation errors, etc.)
    // - 408 timeouts (already waited long enough)
    // - 500 internal server errors (likely validation/business logic failures)

    // Only retry:
    // - 429 rate limits (with backoff)
    // - 502-504 gateway/proxy errors (temporary infrastructure issues)
    if (status === 429) return true;
    if (status >= 502 && status <= 504) return true;

    return false;
  }

  /**
   * Sleep utility for retry delays
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Get appropriate timeout for endpoint
   */
  private getTimeoutForEndpoint(endpoint: string): number {
    // Check for exact matches first
    for (const [path, timeout] of Object.entries(ENDPOINT_TIMEOUTS)) {
      if (path === 'default') continue;
      if (endpoint.includes(path)) {
        return timeout;
      }
    }
    return ENDPOINT_TIMEOUTS.default;
  }

  /**
   * Core request method with retry logic and automatic token refresh
   */
  async request<T = unknown>(
    endpoint: string,
    options: RequestConfig = {},
    attempt = 1
  ): Promise<T> {
    // ✅ STEP 1: Proactively refresh token if expiring soon (before request)
    // Skip refresh for authentication endpoints (login, register, refresh)
    const isAuthEndpoint = endpoint.includes('/auth/login') ||
                           endpoint.includes('/auth/register') ||
                           endpoint.includes('/auth/refresh');

    if (this.authStrategy === AuthStrategies.JWT && !isAuthEndpoint) {
      try {
        await tokenRefreshManager.refreshIfNeeded();
      } catch (error) {
        console.warn('⚠️ Proactive token refresh failed, continuing with request...');
      }
    }

    const controller = new AbortController();
    const requestTimeout = this.getTimeoutForEndpoint(endpoint);
    const timeoutId = setTimeout(() => {
      if (import.meta.env.DEV) {
        console.warn(`⏱️ Request timeout after ${requestTimeout}ms for ${endpoint}`);
      }
      controller.abort();
    }, requestTimeout);

    try {
      // Construct full URL
      const url = this.config.baseURL ? `${this.config.baseURL}${endpoint}` : endpoint;

      if (import.meta.env.DEV) {
        console.log(`🌐 API Request: ${options.method || 'GET'} ${url} (timeout: ${requestTimeout}ms)`);
      }

      // Prepare request configuration
      const requestConfig: RequestInit = {
        method: options.method || 'GET',
        headers: {
          ...this.getAuthHeaders(),
          ...options.headers
        },
        signal: controller.signal,
      };

      // Add body for non-GET requests
      if (options.body && requestConfig.method !== 'GET') {
        requestConfig.body = typeof options.body === 'string'
          ? options.body
          : JSON.stringify(options.body);
      }

      const response = await fetch(url, requestConfig);
      clearTimeout(timeoutId);

      // Handle response
      let responseData: any;
      const contentType = response.headers.get('content-type');

      if (contentType && contentType.includes('application/json')) {
        try {
          responseData = await response.json();
        } catch (parseError: any) {
          throw new ApiRequestError(
            `Invalid JSON response: ${parseError.message}`,
            {
              status: response.status,
              statusText: response.statusText
            }
          );
        }
      } else {
        const textContent = await response.text();
        if (!response.ok) {
          throw new ApiRequestError(
            `API returned non-JSON response: ${response.status} ${response.statusText}`,
            {
              status: response.status,
              statusText: response.statusText,
              data: textContent.substring(0, 200)
            }
          );
        }
        responseData = { data: textContent };
      }

      if (!response.ok) {
        throw new ApiRequestError(
          responseData.detail || responseData.message || 'API request failed',
          {
            status: response.status,
            statusText: response.statusText,
            data: responseData
          }
        );
      }

      return responseData as T;

    } catch (error: any) {
      clearTimeout(timeoutId);

      // Handle timeout
      if (error.name === 'AbortError') {
        const timeoutError = new ApiRequestError('Request timeout');
        timeoutError.response = { status: 408, statusText: 'Request Timeout' };
        throw timeoutError;
      }

      // Handle connection errors
      if (error.message?.includes('ERR_CONNECTION_REFUSED') ||
          error.message?.includes('Failed to fetch') ||
          error.message?.includes('Network request failed')) {

        if (import.meta.env.DEV) {
          console.warn('API connection failed - consider using demo mode');
        }

        const connectionError = new ApiRequestError('API is currently unavailable');
        connectionError.response = { status: 503, statusText: 'Service Unavailable' };
        throw connectionError;
      }

      // Handle 401 Unauthorized - try token refresh and retry
      if (error instanceof ApiRequestError && error.response?.status === 401 && !options._retry) {
        console.warn('🔄 Got 401 Unauthorized - attempting token refresh...');

        try {
          // ✅ STEP 2: Reactive refresh on 401 (refresh + retry)
          await tokenRefreshManager.handleAuthError(async () => {
            // Mark as retry to prevent infinite loop
            options._retry = true;
            // Retry the request with new token
            return this.request<T>(endpoint, options, attempt);
          });
        } catch (refreshError) {
          // Token refresh failed - logout user
          console.error('❌ Token refresh failed, logging out');
          localStorage.removeItem('authToken');
          localStorage.removeItem('refresh_token');
          sessionStorage.removeItem('authToken');
          sessionStorage.removeItem('refresh_token');
          window.location.href = '/login?reason=session_expired';
          throw error;
        }
      }

      // Retry logic
      if (error instanceof ApiRequestError && this.isRetryableError(error) && attempt < this.config.maxRetries) {
        console.warn(`API request failed (attempt ${attempt}/${this.config.maxRetries}), retrying...`, {
          endpoint,
          error: error.message
        });

        const delay = this.config.retryDelay * Math.pow(this.config.retryMultiplier, attempt - 1);
        await this.sleep(delay);
        return this.request<T>(endpoint, options, attempt + 1);
      }

      // Final error handling
      console.error('API request failed after all retries:', error);
      throw error;
    }
  }

  /**
   * HTTP GET method
   */
  async get<T = unknown>(url: string, config: RequestConfig = {}): Promise<T> {
    return this.request<T>(url, { method: 'GET', ...config });
  }

  /**
   * HTTP POST method
   */
  async post<T = unknown>(url: string, data?: unknown, config: RequestConfig = {}): Promise<T> {
    return this.request<T>(url, {
      method: 'POST',
      body: data,
      ...config
    });
  }

  /**
   * HTTP PUT method
   */
  async put<T = unknown>(url: string, data?: unknown, config: RequestConfig = {}): Promise<T> {
    return this.request<T>(url, {
      method: 'PUT',
      body: data,
      ...config
    });
  }

  /**
   * HTTP PATCH method
   */
  async patch<T = unknown>(url: string, data?: unknown, config: RequestConfig = {}): Promise<T> {
    return this.request<T>(url, {
      method: 'PATCH',
      body: data,
      ...config
    });
  }

  /**
   * HTTP DELETE method
   */
  async delete<T = unknown>(url: string, config: RequestConfig = {}): Promise<T> {
    return this.request<T>(url, { method: 'DELETE', ...config });
  }

  /**
   * File upload method
   */
  async uploadFile<T = unknown>(
    url: string,
    file: File,
    _onProgress?: ((progress: UploadProgress) => void) | null,
    config: RequestConfig = {}
  ): Promise<T> {
    const formData = new FormData();
    formData.append('file', file);

    const uploadConfig: RequestConfig = {
      method: 'POST',
      body: formData,
      headers: {
        // Don't set Content-Type for FormData - browser will set it with boundary
        ...this.getAuthHeaders(),
        ...config.headers
      }
    };

    // Remove Content-Type from headers for file upload
    delete (uploadConfig.headers as Record<string, string>)['Content-Type'];

    // Note: Fetch API doesn't support upload progress like XMLHttpRequest
    // onProgress parameter kept for API compatibility but not currently used
    return this.request<T>(url, uploadConfig);
  }

  /**
   * Direct file upload with channel support
   */
  async uploadFileDirect(
    file: File,
    channelId?: string | null,
    onProgress?: ((progress: UploadProgress) => void) | null
  ): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);

    if (channelId) {
      formData.append('channel_id', channelId.toString());
    }

    const uploadConfig: RequestConfig = {
      method: 'POST',
      body: formData,
      headers: {
        ...this.getAuthHeaders()
      }
    };

    // Remove Content-Type from headers
    delete (uploadConfig.headers as Record<string, string>)['Content-Type'];

    try {
      const result = await this.request('/upload', uploadConfig);

      // Call progress callback with completion if provided
      if (onProgress) {
        onProgress({
          progress: 100,
          loaded: file.size,
          total: file.size,
          speed: file.size
        });
      }

      return result;
    } catch (error: any) {
      if (onProgress) {
        onProgress({
          progress: 0,
          loaded: 0,
          total: file.size,
          error: error.message
        });
      }
      throw error;
    }
  }

  /**
   * Get period date range helper
   */
  private getPeriodDateRange(period: number): { from: string; to: string } {
    const to = new Date();
    const from = new Date();
    from.setDate(to.getDate() - period);

    return {
      from: from.toISOString(),
      to: to.toISOString()
    };
  }

  /**
   * Batch analytics request
   */
  async getBatchAnalytics(channelId: string, period = 30): Promise<BatchAnalyticsResponse> {
    const numericChannelId = channelId === 'demo_channel' ? 1 : parseInt(channelId);
    const { from, to } = this.getPeriodDateRange(period);

    const [overview, growth, reach, topPosts, realTime, alerts] = await Promise.all([
      this.get(`/analytics/historical/overview/${numericChannelId}?from=${from}&to=${to}`),
      this.get(`/analytics/historical/growth/${numericChannelId}?from=${from}&to=${to}`),
      this.get(`/analytics/channels/${numericChannelId}/reach?from=${from}&to=${to}`),
      this.get(`/analytics/historical/top-posts/${numericChannelId}?from=${from}&to=${to}`),
      this.getRealTimeMetrics(numericChannelId),
      this.checkAlerts(numericChannelId)
    ]);

    return {
      overview,
      growth,
      reach,
      topPosts,
      realTime,
      alerts,
      timestamp: new Date().toISOString()
    } as BatchAnalyticsResponse;
  }

  /**
   * Real-time metrics helper
   */
  private async getRealTimeMetrics(channelId: number): Promise<any> {
    try {
      return await this.get(`/analytics/channels/${channelId}/real-time`);
    } catch (error) {
      console.warn('Real-time metrics unavailable:', error);
      return { metrics: [], timestamp: new Date().toISOString() };
    }
  }

  /**
   * Check alerts helper
   */
  private async checkAlerts(channelId: number): Promise<any> {
    try {
      return await this.get(`/analytics/channels/${channelId}/alerts`);
    } catch (error) {
      console.warn('Alerts unavailable:', error);
      return { alerts: [], timestamp: new Date().toISOString() };
    }
  }

  /**
   * Get storage files
   */
  async getStorageFiles(limit = 20, offset = 0): Promise<StorageFilesResponse> {
    return this.get<StorageFilesResponse>(`/media/storage-files?limit=${limit}&offset=${offset}`);
  }

  /**
   * Export analytics to CSV
   */
  async exportToCsv(type: string, channelId: string, period = '7d'): Promise<any> {
    const numericChannelId = channelId === 'demo_channel' ? 1 : parseInt(channelId);
    const periodDays = parseInt(period.replace('d', '')) || 7;
    const { from, to } = this.getPeriodDateRange(periodDays);

    return this.get(
      `/exports/csv/${type}/${numericChannelId}?from=${from}&to=${to}&format=csv`
    );
  }

  /**
   * Health check method
   */
  async healthCheck(): Promise<HealthCheckResponse> {
    return this.get<HealthCheckResponse>('/health');
  }

  /**
   * Check if current user is demo user
   */
  isDemoUser(): boolean {
    return localStorage.getItem('is_demo_user') === 'true' ||
           window.location.search.includes('demo=true') ||
           window.location.hostname.includes('demo');
  }

  /**
   * Initialize client
   */
  async initialize(): Promise<void> {
    console.log('🚀 Unified API Client initialized');
    return Promise.resolve();
  }
}

// Create singleton instance
export const apiClient = new UnifiedApiClient();

// Backward compatibility function
export const apiFetch = async (endpoint: string, options: RequestConfig = {}): Promise<any> => {
  const method = options.method || 'GET';
  const data = options.body;

  switch (method.toUpperCase()) {
    case 'GET':
      return apiClient.get(endpoint, options);
    case 'POST':
      return apiClient.post(endpoint, data, options);
    case 'PUT':
      return apiClient.put(endpoint, data, options);
    case 'DELETE':
      return apiClient.delete(endpoint, options);
    default:
      throw new Error(`Unsupported method: ${method}`);
  }
};

// Default export
export default apiClient;

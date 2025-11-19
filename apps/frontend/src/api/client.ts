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
  baseURL: import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || '',
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
  '/auth/login': 15000, // Increased from 10s - important for initial connection
  '/auth/register': 15000,
  '/auth/me': 15000, // Increased from 10s - used for auth verification
  '/auth/refresh': 20000, // Increased from 10s - critical for maintaining session
  '/auth/telegram': 20000, // Added for Telegram auto-login
  '/analytics/channels': 10000, // Reduced from 60s - analytics queries are cached
  '/channels': 60000, // ✅ Increased from 30s to 60s - CloudFlare tunnel + network latency
  '/system/schedule': 5000, // Reduced from 90s - database insert is fast
  '/system/send': 10000, // Telegram API + database
  '/schedule/': 5000, // Reduced from 90s - simple SELECT query
  '/analytics/': 15000, // For complex analytics queries
  '/api/user-bot/': 15000, // Reduced from 90s - bot operations with reasonable timeout
  '/api/user-mtproto': 30000, // MTProto setup/verify needs longer timeout (network + Telegram latency)
  'default': 10000 // Increased from 5s - better for slower connections
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
        // CRITICAL FIX: Use 'auth_token' as primary key (matches AuthContext and tokenRefreshManager)
        // Check all possible token storage keys for backward compatibility
        const token = localStorage.getItem('auth_token') ||      // ✅ Primary key (matches AuthContext)
                     localStorage.getItem('access_token') ||     // Legacy/alternate key
                     localStorage.getItem('token') ||            // Legacy key
                     localStorage.getItem('accessToken') ||      // Alternate format
                     sessionStorage.getItem('access_token');     // Session storage fallback
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
          if (import.meta.env.DEV) {
            console.log('🔑 Using JWT token from storage:', token.substring(0, 20) + '...');
          }
        } else {
          if (import.meta.env.DEV) {
            console.warn('⚠️ No JWT token found in storage');
            console.warn('📊 Storage keys checked:', {
              auth_token: !!localStorage.getItem('auth_token'),
              access_token: !!localStorage.getItem('access_token'),
              refresh_token: !!localStorage.getItem('refresh_token')
            });
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

    // Retry timeouts for specific slow endpoints
    if (status === 408) {
      // Allow retry for timeout errors (they might succeed on retry)
      return true;
    }

    // Don't retry:
    // - 4xx client errors (bad request, validation errors, etc.)
    // - 500 internal server errors (likely validation/business logic failures)

    // Only retry:
    // - 408 timeouts (might succeed on retry)
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
    // This handles the edge case where token might expire during a long request.
    // By refreshing BEFORE the request, we ensure the token is valid for at least
    // TOKEN_EXPIRY_THRESHOLD more minutes. Even if request takes 60s, token will
    // still be valid when it reaches the backend.
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
    const startTime = performance.now(); // Track request timing
    const timeoutId = setTimeout(() => {
      const elapsed = Math.round(performance.now() - startTime);
      console.warn(`⏱️ [API Client] Request timeout after ${elapsed}ms/${requestTimeout}ms for ${endpoint}`);
      controller.abort();
    }, requestTimeout);

    try {
      // Construct full URL and append query params (if any)
      let url = this.config.baseURL ? `${this.config.baseURL}${endpoint}` : endpoint;
      // Support options.params (query parameters) similar to axios
      if (options.params && typeof options.params === 'object') {
        const searchParams = new URLSearchParams();
        for (const [k, v] of Object.entries(options.params)) {
          if (v === undefined || v === null) continue;
          if (Array.isArray(v)) {
            v.forEach(item => searchParams.append(k, String(item)));
          } else {
            searchParams.append(k, String(v));
          }
        }
        const qs = searchParams.toString();
        if (qs) {
          url = `${url}${url.includes('?') ? '&' : '?'}${qs}`;
        }
      }

      console.log(`🚀 [API Client] Starting ${options.method || 'GET'} ${url} (timeout: ${requestTimeout}ms, attempt: ${attempt})`);
      console.log(`📍 [API Client] Request initiated at ${new Date().toISOString()}`);


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
        // Handle FormData separately - don't stringify it
        if (options.body instanceof FormData) {
          requestConfig.body = options.body;
          // Remove Content-Type header to let browser set it with boundary
          delete (requestConfig.headers as Record<string, string>)['Content-Type'];
        } else {
          requestConfig.body = typeof options.body === 'string'
            ? options.body
            : JSON.stringify(options.body);
        }
      }

      const response = await fetch(url, requestConfig);
      clearTimeout(timeoutId);

      const elapsed = Math.round(performance.now() - startTime);
      console.log(`✅ [API Client] Response received in ${elapsed}ms - Status: ${response.status} ${response.statusText}`);

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
        // Don't trigger auth error handling for timeouts
        console.warn(`⏱️ [API Client] Request timeout for ${endpoint} (${requestTimeout}ms) - NOT triggering token refresh`);
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
      // BUT: Only if it's a real 401 from server, not timeout or connection error
      // AND only if we have a refresh token (don't try to refresh if not logged in)
      // AND NOT if this is a timeout error (those are network issues, not auth issues)
      const hasRefreshToken = localStorage.getItem('refresh_token');
      const isTimeoutError = error.message?.includes('timeout') ||
                             error.message?.includes('Request timeout') ||
                             error.response?.status === 408;  // ✅ Also check status code

      if (error instanceof ApiRequestError &&
          error.response?.status === 401 &&
          !options._retry &&
          hasRefreshToken &&
          !isTimeoutError) {  // Don't try to refresh on timeouts!
        console.warn('🔄 [API Client] Got 401 Unauthorized - attempting token refresh...');        try {
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
          localStorage.removeItem('auth_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('auth_user');
          sessionStorage.removeItem('twa_logged_in');
          sessionStorage.removeItem('auth_token');
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

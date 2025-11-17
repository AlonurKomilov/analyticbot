/**
 * 🔄 Token Refresh Manager - Auto-refresh expired JWT tokens
 *
 * Features:
 * - Proactive token refresh (60s before expiry)
 * - Queue management (prevents duplicate refresh calls)
 * - Automatic retry on 401 responses
 * - Graceful logout on refresh failure
 *
 * Usage:
 * ```typescript
 * // In API client interceptor
 * await tokenRefreshManager.refreshIfNeeded();
 *
 * // On 401 response
 * await tokenRefreshManager.handleAuthError(originalRequest);
 * ```
 */

interface QueueItem {
  resolve: (token: string) => void;
  reject: (error: any) => void;
}

interface TokenPayload {
  sub: string;
  exp: number;
  iat: number;
  email?: string;
}

export class TokenRefreshManager {
  private isRefreshing = false;
  private refreshQueue: QueueItem[] = [];
  private readonly EXPIRY_BUFFER_SECONDS = 60; // Refresh 60s before expiry
  private readonly TOKEN_KEY = 'auth_token';
  private readonly REFRESH_TOKEN_KEY = 'refresh_token';

  /**
   * Parse JWT token payload (without verification - just for expiry check)
   */
  private parseToken(token: string): TokenPayload | null {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );
      return JSON.parse(jsonPayload);
    } catch (error) {
      console.error('Failed to parse token:', error);
      return null;
    }
  }

  /**
   * Check if token is expired or about to expire
   */
  isTokenExpiringSoon(token: string | null): boolean {
    if (!token) return true;

    const payload = this.parseToken(token);
    if (!payload || !payload.exp) return true;

    const expiryTime = payload.exp * 1000; // Convert to milliseconds
    const now = Date.now();
    const timeUntilExpiry = expiryTime - now;

    // Refresh if less than buffer time remaining
    return timeUntilExpiry < this.EXPIRY_BUFFER_SECONDS * 1000;
  }

  /**
   * Get current access token
   */
  getAccessToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  /**
   * Get refresh token
   */
  getRefreshToken(): string | null {
    return localStorage.getItem(this.REFRESH_TOKEN_KEY);
  }

  /**
   * Store new tokens
   */
  private storeTokens(accessToken: string, refreshToken?: string): void {
    localStorage.setItem(this.TOKEN_KEY, accessToken);
    if (refreshToken) {
      localStorage.setItem(this.REFRESH_TOKEN_KEY, refreshToken);
    }
  }

  /**
   * Clear all auth tokens
   */
  private clearTokens(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_TOKEN_KEY);
    localStorage.removeItem('auth_user');
  }

  /**
   * Refresh access token using refresh token
   *
   * Queue management: If already refreshing, queue the request
   * to avoid multiple simultaneous refresh calls
   */
  async refreshToken(): Promise<string> {
    // Check if this is a fresh login (within last 10 seconds) - skip refresh
    const lastLoginTime = localStorage.getItem('last_login_time');
    if (lastLoginTime) {
      const timeSinceLogin = Date.now() - parseInt(lastLoginTime);
      if (timeSinceLogin < 10000) { // 10 seconds
        console.log('⏭️ Recent login detected, skipping token refresh');
        const token = localStorage.getItem(this.TOKEN_KEY);
        if (token) return token;
      }
    }

    const refreshToken = this.getRefreshToken();

    if (!refreshToken) {
      console.warn('⚠️ No refresh token available - cannot refresh access token');
      console.log('📊 Storage state:', {
        hasAccessToken: !!localStorage.getItem('auth_token'),
        hasRefreshToken: !!localStorage.getItem('refresh_token'),
        hasUser: !!localStorage.getItem('auth_user')
      });
      this.clearTokens();
      throw new Error('No refresh token available');
    }

    // If already refreshing, add to queue
    if (this.isRefreshing) {
      console.log('🔄 Token refresh in progress, queuing request...');
      return new Promise<string>((resolve, reject) => {
        this.refreshQueue.push({ resolve, reject });
      });
    }

    this.isRefreshing = true;
    console.log('🔄 Refreshing access token...');

    try {
      const baseURL = import.meta.env.VITE_API_BASE_URL ||
                      import.meta.env.VITE_API_URL ||
                      'https://b2qz1m0n-11400.euw.devtunnels.ms';

      const response = await fetch(`${baseURL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          refresh_token: refreshToken
        })
      });

      if (!response.ok) {
        throw new Error(`Token refresh failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();

      if (!data.access_token) {
        throw new Error('No access token in refresh response');
      }

      const newAccessToken = data.access_token;

      // Store new tokens (refresh token may be rotated)
      this.storeTokens(newAccessToken, data.refresh_token);

      console.log('✅ Token refreshed successfully');

      // Resolve all queued requests with new token
      this.refreshQueue.forEach(item => item.resolve(newAccessToken));
      this.refreshQueue = [];

      return newAccessToken;

    } catch (error: any) {
      console.error('❌ Token refresh failed:', error.message);

      // Reject all queued requests
      this.refreshQueue.forEach(item => item.reject(error));
      this.refreshQueue = [];

      // Clear tokens and redirect to login
      this.clearTokens();

      // Redirect to login page
      if (window.location.pathname !== '/login') {
        window.location.href = '/login?reason=session_expired';
      }

      throw error;

    } finally {
      this.isRefreshing = false;
    }
  }

  /**
   * Proactively check and refresh token if needed
   *
   * Call this before making API requests to ensure token is fresh
   * Returns false if no token exists (user not logged in)
   */
  async refreshIfNeeded(): Promise<boolean> {
    const currentToken = this.getAccessToken();
    const refreshToken = this.getRefreshToken();

    // No token means user is not logged in - this is normal, not an error
    if (!currentToken) {
      return false;
    }

    // No refresh token means we can't refresh - don't attempt
    if (!refreshToken) {
      console.warn('⚠️ Access token exists but no refresh token - cannot refresh');
      return false;
    }

    if (this.isTokenExpiringSoon(currentToken)) {
      try {
        await this.refreshToken();
        return true;
      } catch (error) {
        console.error('Failed to refresh token:', error);
        return false;
      }
    }

    return false;
  }

  /**
   * Handle 401 authentication error
   *
   * Attempt to refresh token and retry the original request
   *
   * @param retryRequest - Function to retry the original request
   * @returns Result of retried request
   */
  async handleAuthError<T>(retryRequest: () => Promise<T>): Promise<T> {
    try {
      console.log('🔄 Got 401, attempting token refresh...');
      await this.refreshToken();

      // Retry original request with new token
      return await retryRequest();
    } catch (error) {
      console.error('❌ Token refresh failed after 401, redirecting to login');
      throw error;
    }
  }

  /**
   * Get time until token expires (in seconds)
   */
  getTimeUntilExpiry(): number | null {
    const token = this.getAccessToken();
    if (!token) return null;

    const payload = this.parseToken(token);
    if (!payload || !payload.exp) return null;

    const expiryTime = payload.exp * 1000;
    const now = Date.now();
    const timeUntilExpiry = expiryTime - now;

    return Math.max(0, Math.floor(timeUntilExpiry / 1000));
  }

  /**
   * Check if user is authenticated (has valid token)
   */
  isAuthenticated(): boolean {
    const token = this.getAccessToken();
    if (!token) return false;

    // Not expired = authenticated
    return !this.isTokenExpiringSoon(token);
  }
}

// Singleton instance
export const tokenRefreshManager = new TokenRefreshManager();

// Auto-refresh timer (optional - proactive background refresh)
if (typeof window !== 'undefined') {
  // Check every 30 seconds if token needs refresh
  setInterval(() => {
    const manager = tokenRefreshManager;
    if (manager.isAuthenticated()) {
      const timeUntilExpiry = manager.getTimeUntilExpiry();
      if (timeUntilExpiry !== null && timeUntilExpiry < 120) {
        // Less than 2 minutes remaining - refresh proactively
        console.log(`⏰ Token expiring in ${timeUntilExpiry}s, refreshing proactively...`);
        manager.refreshIfNeeded().catch(err => {
          console.error('Background token refresh failed:', err);
        });
      }
    }
  }, 30000); // Check every 30 seconds
}

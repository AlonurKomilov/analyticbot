import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { API_CONFIG } from '@config/api';

// CSRF token storage
let csrfToken: string | null = null;

/**
 * Get CSRF token from cookie
 */
function getCsrfTokenFromCookie(): string | null {
  const match = document.cookie.match(/(?:^|; )csrf_token=([^;]*)/);
  return match ? decodeURIComponent(match[1]) : null;
}

/**
 * Fetch CSRF token from server
 */
export async function fetchCsrfToken(): Promise<string> {
  try {
    const response = await axios.get(`${API_CONFIG.BASE_URL}/auth/csrf-token`, {
      withCredentials: true,
    });
    csrfToken = response.data.csrf_token;
    return csrfToken ?? '';
  } catch (error) {
    console.error('Failed to fetch CSRF token:', error);
    // Fallback to cookie if available
    const cookieToken = getCsrfTokenFromCookie();
    if (cookieToken) {
      csrfToken = cookieToken;
      return cookieToken;
    }
    throw error;
  }
}

/**
 * Get current CSRF token (from memory or cookie)
 */
export function getCsrfToken(): string | null {
  if (csrfToken) return csrfToken;
  return getCsrfTokenFromCookie();
}

/**
 * Check if method requires CSRF token
 */
function requiresCsrf(method: string): boolean {
  const safeMethods = ['GET', 'HEAD', 'OPTIONS', 'TRACE'];
  return !safeMethods.includes(method.toUpperCase());
}

// Create axios instance for admin API
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Required for CSRF cookies
});

// Request interceptor - add auth token and CSRF token
apiClient.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('admin_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Add admin header for backend to identify admin requests
    config.headers['X-Admin-Request'] = 'true';

    // Add CSRF token for state-changing requests
    if (config.method && requiresCsrf(config.method)) {
      let token: string | null = getCsrfToken();

      // If no token, try to fetch one
      if (!token) {
        try {
          token = await fetchCsrfToken();
        } catch (e) {
          console.warn('Could not fetch CSRF token:', e);
        }
      }

      if (token) {
        config.headers['X-CSRF-Token'] = token;
      }
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle auth errors and CSRF errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('admin_token');
      csrfToken = null;
      window.location.href = '/login';
    }

    // Handle CSRF errors - refresh token and retry
    if (error.response?.status === 403 && error.config) {
      const errorDetail = (error.response.data as any)?.detail || '';
      if (errorDetail.includes('CSRF')) {
        console.warn('CSRF token expired, refreshing...');
        try {
          await fetchCsrfToken();
          // Retry the request with new token
          const config = error.config;
          config.headers['X-CSRF-Token'] = getCsrfToken() || '';
          return apiClient.request(config);
        } catch (csrfError) {
          console.error('Failed to refresh CSRF token:', csrfError);
        }
      }
    }

    return Promise.reject(error);
  }
);

// Initialize CSRF token on module load (for admin panel)
if (typeof window !== 'undefined') {
  fetchCsrfToken().catch(() => {
    console.debug('Initial CSRF fetch skipped (user may not be logged in)');
  });
}

export default apiClient;

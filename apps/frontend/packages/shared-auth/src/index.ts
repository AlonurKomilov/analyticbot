/**
 * 🔐 Shared Authentication Utilities
 * 
 * Cross-subdomain SSO support for 2Bot platforms:
 * - 2bot.org (user dashboard)
 * - admin.2bot.org (admin panel)
 * - analyticbot.org (public catalog & legacy)
 * - moderator.analyticbot.org (moderator panel)
 * 
 * Uses cookies with dynamic domain detection for cross-subdomain auth
 */

// Cookie configuration
const TOKEN_COOKIE = 'ab_token';
const REFRESH_TOKEN_COOKIE = 'ab_refresh';
const USER_COOKIE = 'ab_user';

// For local development, don't set domain (uses current domain)
const isLocalhost = typeof window !== 'undefined' && 
  (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');

// Dynamic cookie domain detection
function getCookieDomain(): string | null {
  if (typeof window === 'undefined') return null;
  const hostname = window.location.hostname;
  
  // 2bot.org domain
  if (hostname === '2bot.org' || hostname.endsWith('.2bot.org')) {
    return '.2bot.org';
  }
  // analyticbot.org domain
  if (hostname === 'analyticbot.org' || hostname.endsWith('.analyticbot.org')) {
    return '.analyticbot.org';
  }
  return null;
}

/**
 * Set a cookie with proper cross-subdomain configuration
 */
export function setCookie(name: string, value: string, days: number = 30): void {
  const expires = new Date();
  expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
  
  let cookie = `${name}=${encodeURIComponent(value)}; expires=${expires.toUTCString()}; path=/; SameSite=Lax`;
  
  // Only set domain for production (enables cross-subdomain)
  const cookieDomain = getCookieDomain();
  if (!isLocalhost && cookieDomain) {
    cookie += `; domain=${cookieDomain}`;
  }
  
  // Use Secure flag in production
  if (window.location.protocol === 'https:') {
    cookie += '; Secure';
  }
  
  document.cookie = cookie;
}

/**
 * Get a cookie value by name
 */
export function getCookie(name: string): string | null {
  const nameEQ = name + '=';
  const cookies = document.cookie.split(';');
  
  for (let cookie of cookies) {
    cookie = cookie.trim();
    if (cookie.startsWith(nameEQ)) {
      return decodeURIComponent(cookie.substring(nameEQ.length));
    }
  }
  return null;
}

/**
 * Delete a cookie
 */
export function deleteCookie(name: string): void {
  let cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
  
  const cookieDomain = getCookieDomain();
  if (!isLocalhost && cookieDomain) {
    cookie += `; domain=${cookieDomain}`;
  }
  
  document.cookie = cookie;
  
  // Also try without domain for cleanup
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
}

/**
 * Store authentication tokens (cross-subdomain)
 */
export function setAuthTokens(accessToken: string, refreshToken?: string): void {
  setCookie(TOKEN_COOKIE, accessToken, 1); // 1 day for access token
  if (refreshToken) {
    setCookie(REFRESH_TOKEN_COOKIE, refreshToken, 30); // 30 days for refresh
  }
  
  // Also store in localStorage for backward compatibility
  localStorage.setItem('analyticbot_token', accessToken);
  if (refreshToken) {
    localStorage.setItem('analyticbot_refresh_token', refreshToken);
  }
}

/**
 * Get access token (checks cookie first, then localStorage)
 */
export function getAccessToken(): string | null {
  // Cookie has priority (cross-subdomain)
  const cookieToken = getCookie(TOKEN_COOKIE);
  if (cookieToken) return cookieToken;
  
  // Fallback to localStorage
  return localStorage.getItem('analyticbot_token');
}

/**
 * Get refresh token
 */
export function getRefreshToken(): string | null {
  const cookieToken = getCookie(REFRESH_TOKEN_COOKIE);
  if (cookieToken) return cookieToken;
  
  return localStorage.getItem('analyticbot_refresh_token');
}

/**
 * Store user data (cross-subdomain)
 */
export function setUserData(user: any): void {
  const userJson = JSON.stringify(user);
  setCookie(USER_COOKIE, userJson, 30);
  localStorage.setItem('analyticbot_user', userJson);
}

/**
 * Get user data
 */
export function getUserData(): any | null {
  try {
    const cookieData = getCookie(USER_COOKIE);
    if (cookieData) {
      return JSON.parse(cookieData);
    }
    
    const localData = localStorage.getItem('analyticbot_user');
    if (localData) {
      return JSON.parse(localData);
    }
  } catch (e) {
    console.warn('Failed to parse user data:', e);
  }
  return null;
}

/**
 * Clear all auth data (logout)
 */
export function clearAuthData(): void {
  // Clear cookies
  deleteCookie(TOKEN_COOKIE);
  deleteCookie(REFRESH_TOKEN_COOKIE);
  deleteCookie(USER_COOKIE);
  
  // Clear localStorage
  localStorage.removeItem('analyticbot_token');
  localStorage.removeItem('analyticbot_refresh_token');
  localStorage.removeItem('analyticbot_user');
  
  // Clear legacy keys too
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  localStorage.removeItem('refresh_token');
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return !!getAccessToken();
}

/**
 * Generate cross-subdomain navigation URL with token
 * Use this when navigating between subdomains to ensure auth persists
 */
export function getAuthenticatedUrl(targetUrl: string): string {
  const token = getAccessToken();
  if (!token) return targetUrl;
  
  // For same-domain navigation, cookies handle auth
  // For cross-origin, we might need token in URL (less secure, use with caution)
  const url = new URL(targetUrl);
  
  // Check if target is same base domain
  const currentDomain = window.location.hostname;
  const targetDomain = url.hostname;
  
  // If both are *.analyticbot.org, cookies will work
  if (currentDomain.endsWith('analyticbot.org') && targetDomain.endsWith('analyticbot.org')) {
    return targetUrl; // Cookies will handle it
  }
  
  // For truly cross-origin, add token to URL (use with caution)
  url.searchParams.set('auth_token', token);
  return url.toString();
}

/**
 * Handle incoming auth token from URL (for cross-origin navigation)
 */
export function handleUrlAuthToken(): boolean {
  if (typeof window === 'undefined') return false;
  
  const urlParams = new URLSearchParams(window.location.search);
  const token = urlParams.get('auth_token');
  
  if (token) {
    setAuthTokens(token);
    
    // Clean up URL
    urlParams.delete('auth_token');
    const newUrl = `${window.location.pathname}${urlParams.toString() ? '?' + urlParams.toString() : ''}`;
    window.history.replaceState({}, '', newUrl);
    
    return true;
  }
  
  return false;
}

// Platform URLs
export const PLATFORM_URLS = {
  public: 'https://analyticbot.org',
  user: 'https://app.analyticbot.org',
  admin: 'https://admin.analyticbot.org',
  moderator: 'https://moderator.analyticbot.org',
} as const;

// Development URLs
export const DEV_PLATFORM_URLS = {
  public: 'http://localhost:11320',
  user: 'http://localhost:11300',
  admin: 'http://localhost:11310',
  moderator: 'http://localhost:11330',
} as const;

/**
 * Get platform URL based on environment
 */
export function getPlatformUrl(platform: keyof typeof PLATFORM_URLS): string {
  if (isLocalhost) {
    return DEV_PLATFORM_URLS[platform];
  }
  return PLATFORM_URLS[platform];
}

export default {
  setAuthTokens,
  getAccessToken,
  getRefreshToken,
  setUserData,
  getUserData,
  clearAuthData,
  isAuthenticated,
  getAuthenticatedUrl,
  handleUrlAuthToken,
  getPlatformUrl,
  PLATFORM_URLS,
  DEV_PLATFORM_URLS,
};

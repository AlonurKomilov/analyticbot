/**
 * 🍪 Cross-Subdomain Cookie Utilities
 * 
 * Enables Single Sign-On across all AnalyticBot subdomains:
 * - analyticbot.org (public)
 * - app.analyticbot.org (user dashboard)
 * - admin.analyticbot.org (admin panel)
 * - moderator.analyticbot.org (moderator panel)
 */

// Cookie names (prefixed to avoid conflicts)
export const COOKIE_KEYS = {
  TOKEN: 'ab_access_token',
  REFRESH_TOKEN: 'ab_refresh_token',
  USER: 'ab_user_data',
} as const;

// Corresponding localStorage keys for backward compatibility
export const STORAGE_KEYS = {
  TOKEN: 'auth_token',
  REFRESH_TOKEN: 'refresh_token',
  USER: 'auth_user',
} as const;

// Cookie domain for cross-subdomain access
const COOKIE_DOMAIN = '.analyticbot.org';

/**
 * Check if running on localhost
 */
const isLocalDev = (): boolean => {
  if (typeof window === 'undefined') return false;
  const hostname = window.location.hostname;
  return hostname === 'localhost' || hostname === '127.0.0.1' || hostname.startsWith('192.168.');
};

/**
 * Set a cookie with cross-subdomain support
 */
export const setCookie = (name: string, value: string, days: number = 30): void => {
  if (typeof document === 'undefined') return;
  
  const expires = new Date();
  expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
  
  let cookieString = `${name}=${encodeURIComponent(value)}; expires=${expires.toUTCString()}; path=/; SameSite=Lax`;
  
  // Set domain for production (enables cross-subdomain cookies)
  if (!isLocalDev()) {
    cookieString += `; domain=${COOKIE_DOMAIN}`;
  }
  
  // Use Secure flag for HTTPS
  if (typeof window !== 'undefined' && window.location.protocol === 'https:') {
    cookieString += '; Secure';
  }
  
  document.cookie = cookieString;
};

/**
 * Get a cookie by name
 */
export const getCookie = (name: string): string | null => {
  if (typeof document === 'undefined') return null;
  
  const nameEQ = name + '=';
  const cookies = document.cookie.split(';');
  
  for (let cookie of cookies) {
    cookie = cookie.trim();
    if (cookie.startsWith(nameEQ)) {
      try {
        return decodeURIComponent(cookie.substring(nameEQ.length));
      } catch {
        return cookie.substring(nameEQ.length);
      }
    }
  }
  return null;
};

/**
 * Delete a cookie
 */
export const deleteCookie = (name: string): void => {
  if (typeof document === 'undefined') return;
  
  // Delete with domain (production)
  if (!isLocalDev()) {
    document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/; domain=${COOKIE_DOMAIN}`;
  }
  
  // Also delete without domain (for cleanup/localhost)
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
};

/**
 * Store tokens in both cookies (cross-subdomain) and localStorage (backward compatibility)
 */
export const setAuthTokens = (accessToken: string, refreshToken?: string): void => {
  console.log('[SSO] Setting auth tokens:', { 
    hasAccessToken: !!accessToken, 
    hasRefreshToken: !!refreshToken,
    hostname: typeof window !== 'undefined' ? window.location.hostname : 'unknown',
    isLocalDev: isLocalDev(),
    domain: isLocalDev() ? 'none' : COOKIE_DOMAIN
  });
  
  // Set cookies for cross-subdomain SSO
  setCookie(COOKIE_KEYS.TOKEN, accessToken, 1); // 1 day for access token
  if (refreshToken) {
    setCookie(COOKIE_KEYS.REFRESH_TOKEN, refreshToken, 30); // 30 days for refresh token
  }
  
  // Also set localStorage for backward compatibility and same-tab usage
  if (typeof localStorage !== 'undefined') {
    localStorage.setItem(STORAGE_KEYS.TOKEN, accessToken);
    if (refreshToken) {
      localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, refreshToken);
    }
  }
  
  // Verify cookies were set
  setTimeout(() => {
    const verifyToken = getCookie(COOKIE_KEYS.TOKEN);
    console.log('[SSO] Verification - cookie set:', !!verifyToken, 'cookies:', document.cookie.split(';').map(c => c.trim().split('=')[0]));
  }, 100);
};

/**
 * Get access token (cookie first, then localStorage)
 */
export const getAccessToken = (): string | null => {
  // Cookie has priority for cross-subdomain
  const cookieToken = getCookie(COOKIE_KEYS.TOKEN);
  if (cookieToken) {
    console.log('[SSO] getAccessToken: found in cookie');
    return cookieToken;
  }
  
  // Fallback to localStorage
  if (typeof localStorage !== 'undefined') {
    const localToken = localStorage.getItem(STORAGE_KEYS.TOKEN);
    if (localToken) {
      console.log('[SSO] getAccessToken: found in localStorage');
      return localToken;
    }
  }
  
  console.log('[SSO] getAccessToken: no token found anywhere');
  return null;
};

/**
 * Get refresh token
 */
export const getRefreshToken = (): string | null => {
  const cookieToken = getCookie(COOKIE_KEYS.REFRESH_TOKEN);
  if (cookieToken) return cookieToken;
  
  if (typeof localStorage !== 'undefined') {
    return localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
  }
  
  return null;
};

/**
 * Store user data
 */
export const setUserData = (user: any): void => {
  const userJson = JSON.stringify(user);
  
  // Cookie (with size limit consideration - truncate if too large)
  if (userJson.length < 4000) { // Cookies have ~4KB limit
    setCookie(COOKIE_KEYS.USER, userJson, 30);
  }
  
  // localStorage for full data
  if (typeof localStorage !== 'undefined') {
    localStorage.setItem(STORAGE_KEYS.USER, userJson);
  }
};

/**
 * Get user data
 */
export const getUserData = (): any | null => {
  try {
    // Try cookie first
    const cookieData = getCookie(COOKIE_KEYS.USER);
    if (cookieData) {
      return JSON.parse(cookieData);
    }
    
    // Fallback to localStorage
    if (typeof localStorage !== 'undefined') {
      const localData = localStorage.getItem(STORAGE_KEYS.USER);
      if (localData) {
        return JSON.parse(localData);
      }
    }
  } catch (e) {
    console.warn('[SSO] Failed to parse user data:', e);
  }
  return null;
};

/**
 * Clear all auth data (logout)
 */
export const clearAuthData = (): void => {
  // Clear cookies
  deleteCookie(COOKIE_KEYS.TOKEN);
  deleteCookie(COOKIE_KEYS.REFRESH_TOKEN);
  deleteCookie(COOKIE_KEYS.USER);
  
  // Clear localStorage
  if (typeof localStorage !== 'undefined') {
    localStorage.removeItem(STORAGE_KEYS.TOKEN);
    localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.USER);
    
    // Also clear legacy keys
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('analyticbot_token');
    localStorage.removeItem('analyticbot_refresh_token');
    localStorage.removeItem('analyticbot_user');
  }
  
  // Clear sessionStorage
  if (typeof sessionStorage !== 'undefined') {
    sessionStorage.removeItem('twa_login_attempted');
  }
};

/**
 * Sync tokens from one storage to another
 * Call this on app init to ensure cookies and localStorage are in sync
 */
export const syncAuthStorage = (): void => {
  const cookieToken = getCookie(COOKIE_KEYS.TOKEN);
  const localToken = typeof localStorage !== 'undefined' ? localStorage.getItem(STORAGE_KEYS.TOKEN) : null;
  
  console.log('[SSO] syncAuthStorage called:', {
    cookieToken: !!cookieToken,
    localToken: !!localToken,
    hostname: typeof window !== 'undefined' ? window.location.hostname : 'unknown',
    allCookies: typeof document !== 'undefined' ? document.cookie.split(';').map(c => c.trim().split('=')[0]) : []
  });
  
  // If cookie has token but localStorage doesn't, sync to localStorage
  if (cookieToken && !localToken && typeof localStorage !== 'undefined') {
    console.log('[SSO] Syncing cookie token to localStorage');
    localStorage.setItem(STORAGE_KEYS.TOKEN, cookieToken);
    
    const refreshCookie = getCookie(COOKIE_KEYS.REFRESH_TOKEN);
    if (refreshCookie) {
      localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, refreshCookie);
    }
    
    const userCookie = getCookie(COOKIE_KEYS.USER);
    if (userCookie) {
      localStorage.setItem(STORAGE_KEYS.USER, userCookie);
    }
  }
  
  // If localStorage has token but cookie doesn't, sync to cookie
  if (!cookieToken && localToken) {
    console.log('[SSO] Syncing localStorage token to cookie');
    setCookie(COOKIE_KEYS.TOKEN, localToken, 1);
    
    if (typeof localStorage !== 'undefined') {
      const refreshLocal = localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
      if (refreshLocal) {
        setCookie(COOKIE_KEYS.REFRESH_TOKEN, refreshLocal, 30);
      }
      
      const userLocal = localStorage.getItem(STORAGE_KEYS.USER);
      if (userLocal) {
        setCookie(COOKIE_KEYS.USER, userLocal, 30);
      }
    }
  }
  
  if (!cookieToken && !localToken) {
    console.log('[SSO] No tokens found in either storage');
  }
};

/**
 * Check if user is authenticated (has valid token)
 */
export const isAuthenticated = (): boolean => {
  return !!getAccessToken();
};

export default {
  COOKIE_KEYS,
  STORAGE_KEYS,
  setCookie,
  getCookie,
  deleteCookie,
  setAuthTokens,
  getAccessToken,
  getRefreshToken,
  setUserData,
  getUserData,
  clearAuthData,
  syncAuthStorage,
  isAuthenticated,
};

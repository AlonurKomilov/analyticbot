/**
 * 🔒 Authentication Context - JWT User Authentication
 *
 * Provides centralized authentication state management for the React app.
 * Integrates with the backend JWT authentication system.
 */

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { apiClient } from '../api/client.js';

// Type definitions
interface User {
    id: string | number;
    email: string;
    username?: string;
    is_demo?: boolean;
    [key: string]: any;
}

interface LoginResponse {
    success: boolean;
    error?: string;
}

interface RegisterResponse {
    success: boolean;
    error?: string;
}

interface AuthContextValue {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    login: (email: string, password: string, rememberMe?: boolean) => Promise<LoginResponse>;
    logout: () => Promise<void>;
    register: (userData: Record<string, any>) => Promise<any>;
    refreshToken: () => Promise<boolean>;
    isLoading: boolean;
    updateUser: (userData: User) => void;
}

interface AuthProviderProps {
    children: ReactNode;
}

// Authentication context interface
const AuthContext = createContext<AuthContextValue>({
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: true,
    login: async () => ({ success: false }),
    register: async () => ({ success: false }),
    logout: async () => {},
    refreshToken: async () => false,
    updateUser: () => {}
});

// Custom hook to use auth context
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

// Token storage helpers
const TOKEN_KEY = 'auth_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const USER_KEY = 'auth_user';

const getStoredToken = (): string | null => localStorage.getItem(TOKEN_KEY);
const getStoredRefreshToken = (): string | null => localStorage.getItem(REFRESH_TOKEN_KEY);
const getStoredUser = (): User | null => {
    try {
        const user = localStorage.getItem(USER_KEY);
        return user ? JSON.parse(user) : null;
    } catch {
        return null;
    }
};

const setStoredAuth = (token: string, refreshToken: string, user: User): void => {
    console.log('💾 Storing auth tokens:', {
        tokenLength: token?.length,
        refreshTokenLength: refreshToken?.length,
        userId: user?.id
    });
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
};

const clearStoredAuth = (): void => {
    console.warn('🗑️ Clearing all auth tokens - called from:', new Error().stack?.split('\n')[2]);
    // Clear primary keys
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    // Clear backup/legacy keys
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    // Clear TWA session flags
    sessionStorage.removeItem('twa_logged_in');
    localStorage.removeItem('is_twa_session');
    localStorage.removeItem('last_login_time');
};

// Authentication Provider Component
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);

    // Initialize auth state from localStorage
    useEffect(() => {
        const initializeAuth = async () => {
            try {
                // Small delay to allow TWA auto-login to complete first (if in Telegram)
                const isTelegram = !!(window as any).Telegram?.WebApp?.initData;
                if (isTelegram) {
                    console.log('⏳ Waiting for potential TWA auto-login...');
                    await new Promise(resolve => setTimeout(resolve, 300));
                }

                const storedToken = getStoredToken();
                const storedUser = getStoredUser();

                if (storedToken && storedUser) {
                    // For fresh logins (within last 5 seconds), trust the stored data
                    const lastLoginTime = localStorage.getItem('last_login_time');
                    const isFreshLogin = lastLoginTime && (Date.now() - parseInt(lastLoginTime)) < 5000;

                    if (isFreshLogin) {
                        console.log('✅ Fresh login detected - using stored credentials');
                        // Batch state updates to prevent intermediate renders
                        setToken(storedToken);
                        setUser(storedUser);
                        setIsLoading(false);
                        return;
                    }

                    // For recent logins (within last 5 minutes), trust stored data without verification
                    const timeSinceLogin = lastLoginTime ? Date.now() - parseInt(lastLoginTime) : Infinity;
                    if (timeSinceLogin < 5 * 60 * 1000) { // 5 minutes
                        console.log('✅ Recent login - using stored credentials without verification');
                        console.log('👤 Setting user:', storedUser);
                        console.log('🔑 Setting token:', storedToken ? 'present' : 'missing');
                        // Batch state updates to prevent intermediate renders
                        setToken(storedToken);
                        setUser(storedUser);
                        setIsLoading(false);
                        return;
                    }

                    // For older logins, verify token is still valid
                    try {
                        console.log('🔍 Verifying stored token...');
                        const userData = await apiClient.get('/auth/me', { timeout: 5000 });
                        setToken(storedToken);
                        setUser(userData as User);
                        console.log('✅ Token verified successfully');
                    } catch (error: any) {
                        console.warn('⚠️ Token verification failed:', error.message);

                        // Try to refresh token instead of clearing auth
                        try {
                            console.log('🔄 Attempting token refresh...');
                            const refreshSuccess = await refreshTokenFn();
                            if (refreshSuccess) {
                                console.log('✅ Token refreshed successfully');
                                // Token was refreshed, state will be updated by refresh function
                            } else {
                                console.warn('⚠️ Token refresh failed, but keeping user logged in');
                                // Keep the user logged in with existing token
                                // It might work for subsequent requests
                                setToken(storedToken);
                                setUser(storedUser);
                            }
                        } catch (refreshError) {
                            console.error('❌ Token refresh error:', refreshError);
                            // Still keep user logged in - let them try to use the app
                            // If token is truly invalid, API requests will fail and show errors
                            setToken(storedToken);
                            setUser(storedUser);
                        }
                    }
                } else {
                    console.log('ℹ️ No stored credentials found');
                }
            } catch (error) {
                console.error('❌ Auth initialization error:', error);
                // Don't clear auth on error - keep user logged in
                const storedToken = getStoredToken();
                const storedUser = getStoredUser();
                if (storedToken && storedUser) {
                    setToken(storedToken);
                    setUser(storedUser);
                }
            } finally {
                setIsLoading(false);
            }
        };

        initializeAuth();
    }, []);

    // Listen for TWA auto-login completion
    useEffect(() => {
        const handleTWAAuthComplete = () => {
            console.log('🔔 TWA auth complete event received - updating auth state');
            const storedToken = getStoredToken();
            const storedUser = getStoredUser();
            
            if (storedToken && storedUser) {
                console.log('✅ Setting auth state from TWA login');
                setToken(storedToken);
                setUser(storedUser);
                setIsLoading(false);
            }
        };

        window.addEventListener('twa-auth-complete', handleTWAAuthComplete);
        
        return () => {
            window.removeEventListener('twa-auth-complete', handleTWAAuthComplete);
        };
    }, []);

    // Login function (🆕 Phase 3.2: Added remember_me parameter)
    const login = useCallback(async (
        email: string,
        password: string,
        rememberMe: boolean = false
    ): Promise<LoginResponse> => {
        try {
            setIsLoading(true);

            const response = await apiClient.post('/auth/login', {
                email,
                password,
                remember_me: rememberMe  // 🆕 Pass remember_me to backend
            });
            console.log('Login API full response:', response); // Debug log

            // Our apiClient returns data directly (not response.data like axios)
            const data = (response as any).data || response; // Support both formats
            console.log('Login API response data:', data); // Debug log

            const { access_token, refresh_token, user: userData } = data;

            // Validate required fields
            if (!access_token || !userData) {
                console.error('Invalid login response structure:', { access_token: !!access_token, userData: !!userData });
                throw new Error('Invalid login response: missing required fields');
            }

            // Store tokens using the correct keys (must match getStoredToken/User)
            setStoredAuth(access_token, refresh_token, userData);

            // Also store with 'last_login_time' for token refresh skip logic
            localStorage.setItem('last_login_time', Date.now().toString());

            // CRITICAL: Force synchronous write to localStorage
            await new Promise(resolve => setTimeout(resolve, 100));
            
            // Verify tokens were actually stored
            const verifyToken = localStorage.getItem(TOKEN_KEY);
            const verifyRefresh = localStorage.getItem(REFRESH_TOKEN_KEY);
            console.log('🔍 Token storage verification:', {
                tokenStored: !!verifyToken,
                refreshStored: !!verifyRefresh,
                tokenLength: verifyToken?.length || 0,
                refreshLength: verifyRefresh?.length || 0
            });

            if (!verifyToken || !verifyRefresh) {
                console.error('❌ CRITICAL: Tokens not stored properly!');
                throw new Error('Failed to store authentication tokens');
            }

            // Check if this is a demo user based on email or user data
            const isDemoUser = email.includes('demo@') ||
                              email.includes('viewer@') ||
                              email.includes('guest@') ||
                              userData.is_demo === true ||
                              userData.email?.includes('demo') ||
                              window.location.search.includes('demo=true'); // URL param for testing

            if (isDemoUser) {
                localStorage.setItem('is_demo_user', 'true');
                console.info('🎭 Demo user detected - enhanced demo experience enabled');
            } else {
                localStorage.removeItem('is_demo_user');
            }

            // Set data source to API mode when logged in (not demo mode)
            localStorage.setItem('useRealAPI', 'true');
            console.info('✅ Authenticated - using real API data');

            // Update state
            setToken(access_token);
            setUser(userData);

            console.log('Login successful:', userData?.username || userData?.email || 'user');
            return { success: true };
        } catch (error: any) {
            console.error('Login error:', error);
            return {
                success: false,
                error: error.message || 'Network error. Please try again.'
            };
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Register function
    const register = useCallback(async (userData: Record<string, any>): Promise<RegisterResponse> => {
        setIsLoading(true);
        console.log('🔐 AuthContext register called with:', userData);
        try {
            const response = await apiClient.post('/auth/register', userData);
            const data = (response as any).data || response; // Support both formats
            const { access_token, refresh_token, user: userInfo } = data;

            // Store auth data
            setStoredAuth(access_token, refresh_token, userInfo);
            setToken(access_token);
            setUser(userInfo);

            return { success: true };
        } catch (error: any) {
            console.error('Registration error:', error);
            return {
                success: false,
                error: 'Network error. Please try again.'
            };
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Logout function
    const logout = useCallback(async (): Promise<void> => {
        try {
            // Call logout endpoint if we have a token
            if (token) {
                await apiClient.post('/auth/logout');
            }
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            // Clear auth state regardless of API call success
            clearStoredAuth();
            setToken(null);
            setUser(null);

            // Redirect to login page
            window.location.href = '/login';
        }
    }, [token]);

    // Refresh token function
    const refreshTokenFn = useCallback(async (): Promise<boolean> => {
        try {
            const storedRefreshToken = getStoredRefreshToken();
            if (!storedRefreshToken) {
                return false;
            }

            const data = await apiClient.post('/auth/refresh', { refresh_token: storedRefreshToken });
            const newToken = (data as any).access_token;

            // Update stored token
            localStorage.setItem(TOKEN_KEY, newToken);
            setToken(newToken);

            // IMPORTANT: Also restore user from storage after token refresh
            // Without this, user state becomes null and app shows no data
            const storedUser = getStoredUser();
            if (storedUser) {
                setUser(storedUser);
            }

            return true;
        } catch (error) {
            console.error('Token refresh error:', error);
            return false;
        }
    }, []);

    // Update user profile
    const updateUser = useCallback((userData: User): void => {
        setUser(userData);
        localStorage.setItem(USER_KEY, JSON.stringify(userData));
    }, []);

    // Auto-refresh token when it's about to expire
    useEffect(() => {
        if (!token) return;

        // Set up token refresh interval (every 25 minutes for 30-minute tokens)
        const refreshInterval = setInterval(async () => {
            const success = await refreshTokenFn();
            if (!success) {
                logout();
            }
        }, 25 * 60 * 1000); // 25 minutes

        return () => clearInterval(refreshInterval);
    }, [token, refreshTokenFn, logout]);

    const value: AuthContextValue = {
        user,
        token,
        isAuthenticated: !!token && !!user,
        isLoading,
        login,
        register,
        logout,
        refreshToken: refreshTokenFn,
        updateUser
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

export default AuthContext;

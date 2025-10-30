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
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
};

const clearStoredAuth = (): void => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
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
                const storedToken = getStoredToken();
                const storedUser = getStoredUser();

                if (storedToken && storedUser) {
                    // For fresh logins (within last 5 seconds), trust the stored data
                    const lastLoginTime = localStorage.getItem('last_login_time');
                    const isFreshLogin = lastLoginTime && (Date.now() - parseInt(lastLoginTime)) < 5000;

                    if (isFreshLogin) {
                        console.log('✅ Fresh login detected - using stored credentials');
                        setToken(storedToken);
                        setUser(storedUser);
                        setIsLoading(false);
                        return;
                    }

                    // Verify token is still valid by making a test request with shorter timeout
                    try {
                        const userData = await apiClient.get('/auth/me', { timeout: 5000 });
                        setToken(storedToken);
                        setUser(userData as User);
                    } catch (error) {
                        console.warn('Token verification failed, trying refresh...', error);
                        // Token invalid or timeout, try refresh
                        const refreshSuccess = await refreshTokenFn();
                        if (!refreshSuccess) {
                            console.warn('Token refresh failed, clearing auth');
                            clearStoredAuth();
                        }
                    }
                }
            } catch (error) {
                console.error('Auth initialization error:', error);
                clearStoredAuth();
            } finally {
                setIsLoading(false);
            }
        };

        initializeAuth();
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

            // Store tokens securely
            localStorage.setItem('access_token', access_token);
            localStorage.setItem('refresh_token', refresh_token);
            localStorage.setItem('user', JSON.stringify(userData));

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

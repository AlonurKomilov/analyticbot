/**
 * 🔒 Authentication Context - JWT User Authentication
 * 
 * Provides centralized authentication state management for the React app.
 * Integrates with the backend JWT authentication system.
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { apiClient } from '../utils/apiClient.js';

// Authentication context interface
const AuthContext = createContext({
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: true,
    login: async () => false,
    logout: () => {},
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

const getStoredToken = () => localStorage.getItem(TOKEN_KEY);
const getStoredRefreshToken = () => localStorage.getItem(REFRESH_TOKEN_KEY);
const getStoredUser = () => {
    try {
        const user = localStorage.getItem(USER_KEY);
        return user ? JSON.parse(user) : null;
    } catch {
        return null;
    }
};

const setStoredAuth = (token, refreshToken, user) => {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
};

const clearStoredAuth = () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
};

// Authentication Provider Component
export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(null);
    const [isLoading, setIsLoading] = useState(true);

    // Initialize auth state from localStorage
    useEffect(() => {
        const initializeAuth = async () => {
            try {
                const storedToken = getStoredToken();
                const storedUser = getStoredUser();

                if (storedToken && storedUser) {
                    // Verify token is still valid by making a test request
                    try {
                        const userData = await apiClient.get('/auth/me');
                        setToken(storedToken);
                        setUser(userData);
                    } catch (error) {
                        // Token invalid, try refresh
                        const refreshSuccess = await refreshToken();
                        if (!refreshSuccess) {
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

    // Login function
    const login = useCallback(async (email, password) => {
        try {
            setIsLoading(true);
            
            const data = await apiClient.post('/auth/login', { email, password });
            const { access_token, refresh_token, user: userData } = data;
            
            // Store tokens securely
            localStorage.setItem('access_token', access_token);
            localStorage.setItem('refresh_token', refresh_token);
            localStorage.setItem('user', JSON.stringify(userData));
            
            // Update state
            setToken(access_token);
            setUser(userData);
            
            console.log('Login successful:', userData.username);
            return { success: true };
        } catch (error) {
            console.error('Login error:', error);
            return { 
                success: false, 
                error: error.message || 'Network error. Please try again.' 
            };
        } finally {
            setIsLoading(false);
        }
    }, []);    // Register function
    const register = useCallback(async (userData) => {
        setIsLoading(true);
        try {
            const data = await apiClient.post('/auth/register', userData);
            const { access_token, refresh_token, user: userInfo } = data;
            
            // Store auth data
            setStoredAuth(access_token, refresh_token, userInfo);
            setToken(access_token);
            setUser(userInfo);
            
            return { success: true };
        } catch (error) {
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
    const logout = useCallback(async () => {
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
    const refreshToken = useCallback(async () => {
        try {
            const storedRefreshToken = getStoredRefreshToken();
            if (!storedRefreshToken) {
                return false;
            }

            const data = await apiClient.post('/auth/refresh', { refresh_token: storedRefreshToken });
            const newToken = data.access_token;
            
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
    const updateUser = useCallback((userData) => {
        setUser(userData);
        localStorage.setItem(USER_KEY, JSON.stringify(userData));
    }, []);

    // Auto-refresh token when it's about to expire
    useEffect(() => {
        if (!token) return;

        // Set up token refresh interval (every 25 minutes for 30-minute tokens)
        const refreshInterval = setInterval(async () => {
            const success = await refreshToken();
            if (!success) {
                logout();
            }
        }, 25 * 60 * 1000); // 25 minutes

        return () => clearInterval(refreshInterval);
    }, [token, refreshToken, logout]);

    const value = {
        user,
        token,
        isAuthenticated: !!token && !!user,
        isLoading,
        login,
        register,
        logout,
        refreshToken,
        updateUser
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

export default AuthContext;
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient, fetchCsrfToken } from '@api/client';
import { API_ENDPOINTS } from '@config/api';
import { ROUTES } from '@config/routes';

interface User {
  id: string | number;
  email: string;
  username: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string, rememberMe?: boolean) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  // Check auth on mount - now checks both localStorage token and cookie auth
  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Try to verify auth - works with both Bearer token and httpOnly cookies
        const response = await apiClient.get(API_ENDPOINTS.AUTH.ME);
        const userData = response.data.user || response.data;

        // Only allow admin users
        if (userData.role === 'admin' || userData.role === 'owner') {
          setUser(userData);
          // Ensure CSRF token is fetched for admin session
          await fetchCsrfToken().catch(() => {});
        } else {
          // Clear any stored tokens
          localStorage.removeItem('admin_token');
          navigate(ROUTES.LOGIN);
        }
      } catch {
        // Auth failed - clear tokens and stay on current page
        localStorage.removeItem('admin_token');
      }
      setIsLoading(false);
    };
    checkAuth();
  }, [navigate]);

  const login = async (email: string, password: string, rememberMe = false): Promise<void> => {
    const response = await apiClient.post(API_ENDPOINTS.AUTH.LOGIN, { 
      email, 
      password,
      remember_me: rememberMe 
    });
    const { access_token, user: userData } = response.data;

    // Only allow admin users
    if (userData.role !== 'admin' && userData.role !== 'owner') {
      throw new Error('Access denied. Admin privileges required.');
    }

    // Store token in localStorage as backup (httpOnly cookies are now primary)
    // This provides fallback for environments where cookies don't work
    localStorage.setItem('admin_token', access_token);
    
    // Fetch CSRF token for the session
    await fetchCsrfToken().catch(() => {});
    
    setUser(userData);
    navigate(ROUTES.DASHBOARD);
  };

  const logout = async () => {
    try {
      // Call logout endpoint to clear server-side session and cookies
      await apiClient.post(API_ENDPOINTS.AUTH.LOGOUT);
    } catch (error) {
      console.error('Logout request failed:', error);
    }
    
    // Clear local state regardless of server response
    localStorage.removeItem('admin_token');
    setUser(null);
    navigate(ROUTES.LOGIN);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

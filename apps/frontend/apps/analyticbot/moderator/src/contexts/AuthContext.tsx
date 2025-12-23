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

  // Check auth on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await apiClient.get(API_ENDPOINTS.AUTH.ME);
        const userData = response.data.user || response.data;

        // Allow moderator, admin, or owner roles
        if (['moderator', 'admin', 'owner'].includes(userData.role)) {
          setUser(userData);
          await fetchCsrfToken().catch(() => {});
        } else {
          localStorage.removeItem('moderator_token');
          navigate(ROUTES.LOGIN);
        }
      } catch {
        localStorage.removeItem('moderator_token');
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

    // Allow moderator, admin, or owner roles
    if (!['moderator', 'admin', 'owner'].includes(userData.role)) {
      throw new Error('Access denied. Moderator privileges required.');
    }

    localStorage.setItem('moderator_token', access_token);
    await fetchCsrfToken().catch(() => {});

    setUser(userData);
    navigate(ROUTES.DASHBOARD);
  };

  const logout = async () => {
    try {
      await apiClient.post(API_ENDPOINTS.AUTH.LOGOUT);
    } catch (error) {
      console.error('Logout request failed:', error);
    }

    localStorage.removeItem('moderator_token');
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

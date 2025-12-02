import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '@api/client';
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
  login: (email: string, password: string) => Promise<void>;
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
      const token = localStorage.getItem('admin_token');
      if (token) {
        try {
          const response = await apiClient.get(API_ENDPOINTS.AUTH.VERIFY);
          const userData = response.data.user || response.data;
          
          // Only allow admin users
          if (userData.role === 'admin' || userData.role === 'owner') {
            setUser(userData);
          } else {
            localStorage.removeItem('admin_token');
            navigate(ROUTES.LOGIN);
          }
        } catch {
          localStorage.removeItem('admin_token');
        }
      }
      setIsLoading(false);
    };
    checkAuth();
  }, [navigate]);

  const login = async (email: string, password: string): Promise<void> => {
    const response = await apiClient.post(API_ENDPOINTS.AUTH.LOGIN, { email, password });
    const { access_token, user: userData } = response.data;
    
    // Only allow admin users
    if (userData.role !== 'admin' && userData.role !== 'owner') {
      throw new Error('Access denied. Admin privileges required.');
    }
    
    localStorage.setItem('admin_token', access_token);
    setUser(userData);
    navigate(ROUTES.DASHBOARD);
  };

  const logout = () => {
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

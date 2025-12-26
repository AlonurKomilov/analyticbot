import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { ownerApi } from '@api/ownerApi';

interface User {
  id: number;
  email: string;
  username: string;
  role: string;
  created_at: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const checkAuth = useCallback(async () => {
    try {
      const token = localStorage.getItem('owner_token');
      if (!token) {
        setUser(null);
        setIsLoading(false);
        return;
      }

      const response = await ownerApi.getMe();
      if (response.data?.user) {
        // Verify owner role
        if (response.data.user.role === 'owner') {
          setUser(response.data.user);
        } else {
          localStorage.removeItem('owner_token');
          setUser(null);
        }
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem('owner_token');
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const login = async (username: string, password: string) => {
    setIsLoading(true);
    try {
      const response = await ownerApi.login(username, password);
      if (response.data?.access_token) {
        localStorage.setItem('owner_token', response.data.access_token);
        
        // The API returns admin_user, not user
        const adminUser = response.data.admin_user;
        if (adminUser?.role === 'owner') {
          setUser({
            id: adminUser.id,
            email: adminUser.email || '',
            username: adminUser.username,
            role: adminUser.role,
            created_at: adminUser.created_at || new Date().toISOString(),
          });
        } else {
          localStorage.removeItem('owner_token');
          throw new Error('Access denied. Owner privileges required.');
        }
      } else {
        throw new Error('Invalid response from server');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await ownerApi.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('owner_token');
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        checkAuth,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

/**
 * Authentication Store (TypeScript)
 * Manages user authentication state and operations
 * Pure domain logic for auth - separated from god store
 */

import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { apiClient } from '@/api/client';
import offlineStorage from '@/utils/offlineStorage';
import type { User, UserPreferences } from '@/types';

interface Plan {
  name: string;
  max_channels: number;
  features?: string[];
}

interface AuthState {
  // State
  user: User | null;
  plan: Plan | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  loadUser: () => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  register: (data: {
    email: string;
    password: string;
    firstName?: string;
    lastName?: string;
  }) => Promise<void>;
  setUser: (user: User | null) => void;
  updateUser: (data: Partial<User>) => Promise<void>;
  updatePreferences: (preferences: Partial<UserPreferences>) => Promise<void>;
  setPlan: (plan: Plan | null) => void;
  logout: () => void;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  subscribeWithSelector((set, get) => ({
    // Initial state
    user: null,
    plan: null,
    isAuthenticated: false,
    isLoading: false,
    error: null,

    // Load current user from API
    loadUser: async () => {
      set({ isLoading: true, error: null });

      try {
        const userData = await apiClient.get<User>('/auth/me');
        console.log('✅ User loaded from API:', userData);

        set({
          user: userData,
          isAuthenticated: true,
          isLoading: false
        });
      } catch (error) {
        console.error('❌ Failed to load user:', error);
        const errorMessage = error instanceof Error ? error.message : 'Authentication failed';

        set({
          user: null,
          isAuthenticated: false,
          isLoading: false,
          error: errorMessage
        });
      }
    },

    // Login user
    login: async (email: string, password: string) => {
      set({ isLoading: true, error: null });

      try {
        const response = await apiClient.post<{ access_token: string; user: User }>(
          '/auth/login',
          { email, password }
        );

        if (response.access_token) {
          localStorage.setItem('access_token', response.access_token);
        }

        set({
          user: response.user,
          isAuthenticated: true,
          isLoading: false
        });
      } catch (error) {
        console.error('❌ Login failed:', error);
        const errorMessage = error instanceof Error ? error.message : 'Login failed';
        set({
          error: errorMessage,
          isLoading: false
        });
      }
    },

    // Register new user
    register: async (data) => {
      set({ isLoading: true, error: null });

      try {
        const response = await apiClient.post<{ access_token: string; user: User }>(
          '/auth/register',
          data
        );

        if (response.access_token) {
          localStorage.setItem('access_token', response.access_token);
        }

        set({
          user: response.user,
          isAuthenticated: true,
          isLoading: false
        });
      } catch (error) {
        console.error('❌ Registration failed:', error);
        const errorMessage = error instanceof Error ? error.message : 'Registration failed';
        set({
          error: errorMessage,
          isLoading: false
        });
      }
    },

    // Set user directly
    setUser: (user) => {
      set({
        user,
        isAuthenticated: !!user
      });
    },

    // Update user profile
    updateUser: async (data: Partial<User>) => {
      set({ isLoading: true, error: null });

      try {
        const updatedUser = await apiClient.patch<User>('/auth/me', data);
        set({
          user: updatedUser,
          isLoading: false
        });
      } catch (error) {
        console.error('❌ Failed to update user:', error);
        const errorMessage = error instanceof Error ? error.message : 'Update failed';
        set({
          error: errorMessage,
          isLoading: false
        });
      }
    },

    // Update user preferences
    updatePreferences: async (preferences: Partial<UserPreferences>) => {
      const { user } = get();
      if (!user) return;

      set({ isLoading: true, error: null });

      try {
        const updatedUser = await apiClient.patch<User>('/auth/me/preferences', preferences);
        set({
          user: updatedUser,
          isLoading: false
        });
      } catch (error) {
        console.error('❌ Failed to update preferences:', error);
        const errorMessage = error instanceof Error ? error.message : 'Update failed';
        set({
          error: errorMessage,
          isLoading: false
        });
      }
    },

    // Set plan
    setPlan: (plan) => {
      set({ plan });
    },

    // Logout user
    logout: async () => {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('authToken');

      // Clear all cached channel data to prevent data leaking between users
      try {
        await offlineStorage.clearCache();
        console.log('✅ Cleared offline cache on logout');
      } catch (error) {
        console.warn('Failed to clear offline cache:', error);
      }

      set({
        user: null,
        plan: null,
        isAuthenticated: false,
        error: null
      });

      console.log('✅ User logged out');
    },

    // Clear error
    clearError: () => {
      set({ error: null });
    }
  }))
);

export default useAuthStore;

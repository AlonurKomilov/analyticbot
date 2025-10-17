/**
 * Authentication Store
 * Manages user authentication state and operations
 * Pure domain logic for auth - separated from god store
 */

import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { apiClient } from '@/api/client.js';

interface User {
  id?: string | number;
  username: string;
  first_name?: string;
  last_name?: string;
  email?: string;
  role?: string;
}

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
  setUser: (user: User | null) => void;
  setPlan: (plan: Plan | null) => void;
  logout: () => void;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  subscribeWithSelector((set) => ({
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
        const userData = await apiClient.get('/auth/me');
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

    // Set user directly
    setUser: (user) => {
      set({
        user,
        isAuthenticated: !!user
      });
    },

    // Set plan
    setPlan: (plan) => {
      set({ plan });
    },

    // Logout user
    logout: () => {
      set({
        user: null,
        plan: null,
        isAuthenticated: false,
        error: null
      });

      // Clear auth token if exists
      localStorage.removeItem('authToken');

      console.log('✅ User logged out');
    },

    // Clear error
    clearError: () => {
      set({ error: null });
    }
  }))
);

export default useAuthStore;

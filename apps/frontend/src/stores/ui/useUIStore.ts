/**
 * UI Store (TypeScript)
 * Manages global UI state (data source, loading states, errors, notifications)
 * Pure domain logic for UI state - separated from god store
 */

import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import type { DataSource } from '@/types';

interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
}

interface UIState {
  // State
  dataSource: DataSource;
  isSidebarOpen: boolean;
  isMobileMenuOpen: boolean;
  activeModal: string | null;
  notifications: Notification[];
  theme: 'light' | 'dark' | 'system';
  isGlobalLoading: boolean;

  // Actions
  setDataSource: (source: DataSource) => void;
  toggleSidebar: () => void;
  setSidebarOpen: (isOpen: boolean) => void;
  toggleMobileMenu: () => void;
  setMobileMenuOpen: (isOpen: boolean) => void;
  openModal: (modalId: string) => void;
  closeModal: () => void;
  addNotification: (notification: Omit<Notification, 'id'>) => void;
  removeNotification: (id: string) => void;
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  setGlobalLoading: (isLoading: boolean) => void;
}

export const useUIStore = create<UIState>()(
  subscribeWithSelector((set, get) => ({
    // Initial state
    dataSource: (localStorage.getItem('dataSource') || 'api') as DataSource,
    isSidebarOpen: true,
    isMobileMenuOpen: false,
    activeModal: null,
    notifications: [],
    theme: (localStorage.getItem('theme') || 'system') as 'light' | 'dark' | 'system',
    isGlobalLoading: false,

    // Set data source
    setDataSource: (source: DataSource) => {
      const previousSource = get().dataSource;

      set({ dataSource: source });
      localStorage.setItem('dataSource', source);

      console.log(`📡 Data source changed: ${previousSource} → ${source}`);

      // Dispatch event if source actually changed
      if (previousSource !== source) {
        setTimeout(() => {
          window.dispatchEvent(new CustomEvent('dataSourceChanged', {
            detail: { source, previousSource }
          }));
        }, 100);
      }
    },

    // Toggle sidebar
    toggleSidebar: () => {
      set(state => ({ isSidebarOpen: !state.isSidebarOpen }));
    },

    // Set sidebar open state
    setSidebarOpen: (isOpen: boolean) => {
      set({ isSidebarOpen: isOpen });
    },

    // Toggle mobile menu
    toggleMobileMenu: () => {
      set(state => ({ isMobileMenuOpen: !state.isMobileMenuOpen }));
    },

    // Set mobile menu open state
    setMobileMenuOpen: (isOpen: boolean) => {
      set({ isMobileMenuOpen: isOpen });
    },

    // Open modal
    openModal: (modalId: string) => {
      set({ activeModal: modalId });
    },

    // Close modal
    closeModal: () => {
      set({ activeModal: null });
    },

    // Add notification
    addNotification: (notification) => {
      const id = `notification-${Date.now()}-${Math.random()}`;
      const newNotification: Notification = { id, ...notification };

      set(state => ({
        notifications: [...state.notifications, newNotification]
      }));

      // Auto-remove notification after duration
      if (notification.duration) {
        setTimeout(() => {
          get().removeNotification(id);
        }, notification.duration);
      }
    },

    // Remove notification
    removeNotification: (id: string) => {
      set(state => ({
        notifications: state.notifications.filter(n => n.id !== id)
      }));
    },

    // Set theme
    setTheme: (theme: 'light' | 'dark' | 'system') => {
      set({ theme });
      localStorage.setItem('theme', theme);
    },

    // Set global loading
    setGlobalLoading: (isLoading: boolean) => {
      set({ isGlobalLoading: isLoading });
    }
  }))
);

export default useUIStore;

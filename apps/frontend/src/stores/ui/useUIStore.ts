/**
 * UI Store
 * Manages global UI state (data source, loading states, errors)
 * Pure domain logic for UI state - separated from god store
 */

import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';

type DataSource = 'api' | 'mock';

interface LoadingState {
  isLoading: boolean;
  error: string | null;
  lastUpdated: number | null;
}

interface UIState {
  // State
  dataSource: DataSource;
  globalLoading: LoadingState;

  // Actions
  setDataSource: (source: DataSource) => void;
  isUsingRealAPI: () => boolean;
  setGlobalLoading: (isLoading: boolean) => void;
  setGlobalError: (error: string | null) => void;
  clearGlobalError: () => void;
}

const createLoadingState = (): LoadingState => ({
  isLoading: false,
  error: null,
  lastUpdated: null
});

export const useUIStore = create<UIState>()(
  subscribeWithSelector((set, get) => ({
    // Initial state - read from localStorage
    dataSource: (localStorage.getItem('useRealAPI') === 'true' ? 'api' : 'mock') as DataSource,
    globalLoading: createLoadingState(),

    // Set data source (API or Mock)
    setDataSource: (source: DataSource) => {
      const previousSource = get().dataSource;

      set({ dataSource: source });
      localStorage.setItem('useRealAPI', source === 'api' ? 'true' : 'false');

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

    // Check if using real API
    isUsingRealAPI: () => {
      return get().dataSource === 'api';
    },

    // Set global loading state
    setGlobalLoading: (isLoading: boolean) => {
      set(state => ({
        globalLoading: {
          ...state.globalLoading,
          isLoading,
          lastUpdated: isLoading ? state.globalLoading.lastUpdated : Date.now()
        }
      }));
    },

    // Set global error
    setGlobalError: (error: string | null) => {
      set(state => ({
        globalLoading: {
          ...state.globalLoading,
          error,
          isLoading: false
        }
      }));
    },

    // Clear global error
    clearGlobalError: () => {
      set(state => ({
        globalLoading: {
          ...state.globalLoading,
          error: null
        }
      }));
    }
  }))
);

export default useUIStore;

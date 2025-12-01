/**
 * Navigation Search Hook
 */
import { useCallback } from 'react';
import { useUserPreferences } from './useUserPreferences';
import { SearchHistoryItem } from './types';

export const useNavigationSearchInternal = () => {
  const { preferences, updatePreferences } = useUserPreferences();

  const addSearchHistory = useCallback(
    (query: string) => {
      if (!query.trim()) return;

      updatePreferences((prev) => {
        const history = prev.searchHistory || [];
        const filtered = history.filter((h) => h.query !== query);
        const updated: SearchHistoryItem[] = [
          { query, timestamp: Date.now() },
          ...filtered,
        ].slice(0, 20); // Keep last 20 searches
        return { searchHistory: updated };
      });
    },
    [updatePreferences]
  );

  const clearSearchHistory = useCallback(() => {
    updatePreferences({ searchHistory: [] });
  }, [updatePreferences]);

  return {
    searchHistory: preferences.searchHistory || [],
    addSearchHistory,
    clearSearchHistory,
  };
};

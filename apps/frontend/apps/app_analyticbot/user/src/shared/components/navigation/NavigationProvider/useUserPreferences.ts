/**
 * User Preferences Hook
 */
import { useState, useCallback } from 'react';
import { UserPreferences, DEFAULT_PREFERENCES } from './types';

export const useUserPreferences = () => {
  const [preferences, setPreferences] = useState<UserPreferences>(() => {
    try {
      const saved = localStorage.getItem('navigationPreferences');
      return saved ? JSON.parse(saved) : DEFAULT_PREFERENCES;
    } catch {
      return DEFAULT_PREFERENCES;
    }
  });

  const updatePreferences = useCallback(
    (
      updates:
        | Partial<UserPreferences>
        | ((prev: UserPreferences) => Partial<UserPreferences>)
    ) => {
      setPreferences((prev) => {
        const updateValues =
          typeof updates === 'function' ? updates(prev) : updates;
        const updated = { ...prev, ...updateValues };
        try {
          localStorage.setItem('navigationPreferences', JSON.stringify(updated));
        } catch (error) {
          console.warn('Failed to save navigation preferences:', error);
        }
        return updated;
      });
    },
    []
  );

  return {
    preferences,
    updatePreferences,
  };
};

/**
 * Navigation History Hook (Bookmarks and Recent Pages)
 */
import { useCallback, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useUserPreferences } from './useUserPreferences';
import { Bookmark, RecentPage } from './types';

export const useNavigationHistoryInternal = () => {
  const location = useLocation();
  const { preferences, updatePreferences } = useUserPreferences();

  const addBookmark = useCallback(
    (bookmark: Bookmark) => {
      updatePreferences((prev) => {
        const bookmarks = prev.bookmarks || [];
        const exists = bookmarks.find((b) => b.path === bookmark.path);

        if (!exists) {
          const updated = [bookmark, ...bookmarks].slice(0, 20); // Max 20 bookmarks
          return { bookmarks: updated };
        }
        return {};
      });
    },
    [updatePreferences]
  );

  const removeBookmark = useCallback(
    (path: string) => {
      updatePreferences((prev) => {
        const bookmarks = prev.bookmarks || [];
        const updated = bookmarks.filter((b) => b.path !== path);
        return { bookmarks: updated };
      });
    },
    [updatePreferences]
  );

  const isBookmarked = useCallback(
    (path: string): boolean => {
      const bookmarks = preferences.bookmarks || [];
      return bookmarks.some((b) => b.path === path);
    },
    [preferences]
  );

  // Track current page
  useEffect(() => {
    const pathSegments = location.pathname.split('/').filter(Boolean);
    const title =
      pathSegments.length > 0
        ? pathSegments[pathSegments.length - 1]
            .split('-')
            .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ')
        : 'Dashboard';

    const page: RecentPage = {
      path: location.pathname,
      title,
      timestamp: Date.now(),
    };

    updatePreferences((prev) => {
      const recent = prev.recentPages || [];
      const filtered = recent.filter((p) => p.path !== page.path);
      const updated = [page, ...filtered].slice(0, 10);
      return { recentPages: updated };
    });
  }, [location.pathname, updatePreferences]);

  return {
    recentPages: preferences.recentPages || [],
    bookmarks: preferences.bookmarks || [],
    addBookmark,
    removeBookmark,
    isBookmarked,
  };
};

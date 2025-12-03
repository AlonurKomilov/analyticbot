/**
 * Navigation Analytics Hook
 */
import { useState, useCallback } from 'react';
import { PageView } from './types';

export const useNavigationAnalytics = () => {
  const [pageViews, setPageViews] = useState<PageView[]>([]);
  const [sessionStart] = useState(Date.now());

  const trackPageView = useCallback((path: string, title: string) => {
    const view: PageView = {
      id: Date.now(),
      path,
      title,
      timestamp: Date.now(),
      duration: 0,
    };

    setPageViews((prev) => {
      // Update duration of previous page
      const updated = [...prev];
      if (updated.length > 0) {
        const lastView = updated[updated.length - 1];
        lastView.duration = Date.now() - lastView.timestamp;
      }

      return [...updated, view].slice(-50); // Keep last 50 views
    });

    // Analytics tracking (could integrate with Google Analytics, etc.)
    if (
      process.env.NODE_ENV === 'development' &&
      process.env.VITE_DEBUG_NAVIGATION === 'true'
    ) {
      console.debug('[Navigation]', {
        path,
        title,
        sessionTime: Date.now() - sessionStart,
      });
    }
  }, []);

  return {
    pageViews,
    trackPageView,
    sessionStart,
  };
};

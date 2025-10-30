/**
 * useScheduledPosts Hook
 * Handles fetching scheduled posts data with loading/error states
 */

import { useState, useEffect, useCallback } from 'react';
import { usePostStore } from '@/store';
import { UseScheduledPostsReturn } from '../types';

export const useScheduledPosts = (): UseScheduledPostsReturn => {
  const { scheduledPosts, fetchScheduledPosts } = usePostStore();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadPosts = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      await fetchScheduledPosts();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load scheduled posts';
      setError(errorMessage);
      console.error('Error loading scheduled posts:', err);
    } finally {
      setIsLoading(false);
    }
  }, [fetchScheduledPosts]);

  // Fetch posts on mount
  useEffect(() => {
    loadPosts();
  }, [loadPosts]);

  return {
    posts: scheduledPosts || [],
    isLoading,
    error,
    refetch: loadPosts
  };
};

/**
 * usePostActions Hook
 * Handles post manipulation actions (delete, cancel) with confirmation
 */

import { useState, useCallback } from 'react';
import { usePostStore } from '@/store';
import { UsePostActionsReturn } from '../types';

export const usePostActions = (): UsePostActionsReturn => {
  const { cancelScheduledPost, deletePost } = usePostStore();
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = useCallback(async (id: string | number) => {
    // Confirm before deleting
    const confirmed = window.confirm(
      'Are you sure you want to cancel this scheduled post?'
    );

    if (!confirmed) {
      return;
    }

    setIsDeleting(true);

    try {
      // Try cancelScheduledPost first, fallback to deletePost
      if (cancelScheduledPost) {
        await cancelScheduledPost(String(id));
      } else if (deletePost) {
        await deletePost(String(id));
      }

      console.log('✅ Post deleted successfully:', id);
    } catch (err) {
      console.error('❌ Failed to delete post:', err);
      alert('Failed to delete post. Please try again.');
    } finally {
      setIsDeleting(false);
    }
  }, [cancelScheduledPost, deletePost]);

  return {
    handleDelete,
    isDeleting
  };
};

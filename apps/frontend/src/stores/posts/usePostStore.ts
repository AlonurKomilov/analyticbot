/**
 * Posts Store
 * Manages scheduled posts state and operations
 * Pure domain logic for posts - separated from god store
 */

import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { apiClient } from '@/api/client.js';
import { ErrorHandler } from '@/utils/errorHandler.js';

interface Post {
  id: string | number;
  content: string;
  scheduled_time?: string;
  channel_id?: string | number;
  status?: 'scheduled' | 'published' | 'failed';
  media_id?: string;
  created_at?: string;
}

interface PostState {
  // State
  scheduledPosts: Post[];
  isLoading: boolean;
  error: string | null;

  // Actions
  loadPosts: (channelId?: string | number) => Promise<void>;
  schedulePost: (postData: Partial<Post>) => Promise<any>;
  deletePost: (postId: string | number) => Promise<void>;
  updatePost: (postId: string | number, postData: Partial<Post>) => Promise<void>;
  clearError: () => void;
}

export const usePostStore = create<PostState>()(
  subscribeWithSelector((set) => ({
    // Initial state
    scheduledPosts: [],
    isLoading: false,
    error: null,

    // Load all scheduled posts
    loadPosts: async () => {
      set({ isLoading: true, error: null });

      try {
        const posts = await apiClient.get('/posts/scheduled');
        set({
          scheduledPosts: posts || [],
          isLoading: false
        });
        console.log('✅ Scheduled posts loaded:', posts?.length || 0);
      } catch (error) {
        console.error('❌ Failed to load posts:', error);
        const errorMessage = error instanceof Error ? error.message : 'Failed to load posts';
        set({
          scheduledPosts: [],
          error: errorMessage,
          isLoading: false
        });
      }
    },

    // Schedule a new post
    schedulePost: async (postData: Partial<Post>): Promise<boolean> => {
      set({ isLoading: true, error: null });

      try {
        console.log('� Scheduling post:', postData);

        const newPost = await apiClient.post('/posts/schedule', postData as any);

        // Add to local state
        set(state => ({
          scheduledPosts: [...state.scheduledPosts, newPost],
          isLoading: false
        }));

        console.log('✅ Post scheduled successfully:', newPost);
        return true;

      } catch (error) {
        console.error('❌ Schedule post error:', error);
        ErrorHandler.handleError(error, {
          component: 'PostStore',
          action: 'schedulePost',
          postData
        });

        const errorMessage = error instanceof Error ? error.message : 'Failed to schedule post';
        set({
          error: errorMessage,
          isLoading: false
        });
        return false;
      }
    },

    // Delete a scheduled post
    deletePost: async (postId: string | number) => {
      set({ isLoading: true, error: null });

      try {
        console.log('🗑️ Deleting post:', postId);
        await apiClient.delete(`/posts/${postId}`);

        // Remove from local state
        set(state => ({
          scheduledPosts: state.scheduledPosts.filter(post => post.id !== postId),
          isLoading: false
        }));

        console.log('✅ Post deleted successfully');
      } catch (error) {
        console.error('❌ Delete post error:', error);
        ErrorHandler.handleError(error, {
          component: 'PostStore',
          action: 'deletePost',
          postId
        });

        const errorMessage = error instanceof Error ? error.message : 'Failed to delete post';
        set({
          error: errorMessage,
          isLoading: false
        });
      }
    },

    // Update a post
    updatePost: async (postId: string | number, postData: Partial<Post>) => {
      set({ isLoading: true, error: null });

      try {
        console.log('✏️ Updating post:', postId, postData);

        const updatedPost = await apiClient.put(`/posts/${postId}`, postData as any);

        // Update in local state
        set(state => ({
          scheduledPosts: state.scheduledPosts.map(post =>
            post.id === postId ? { ...post, ...updatedPost } : post
          ),
          isLoading: false
        }));

        console.log('✅ Post updated successfully');
      } catch (error) {
        console.error('❌ Update post error:', error);
        ErrorHandler.handleError(error, {
          component: 'PostStore',
          action: 'updatePost',
          postId,
          postData
        });

        const errorMessage = error instanceof Error ? error.message : 'Failed to update post';
        set({
          error: errorMessage,
          isLoading: false
        });
      }
    },

    // Set posts directly
    setPosts: (posts: Post[]) => {
      set({ scheduledPosts: posts });
    },

    // Clear error
    clearError: () => {
      set({ error: null });
    }
  }))
);

export default usePostStore;

/**
 * Posts Store (TypeScript)
 * Manages scheduled posts state and operations
 * Pure domain logic for posts - separated from god store
 */

import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { apiClient } from '@/api/client';
import { ErrorHandler } from '@/utils/errorHandler';
import type { Post, ScheduledPost, CreatePostRequest } from '@/types';

interface PostState {
  // State
  posts: Post[];
  scheduledPosts: ScheduledPost[];
  selectedPost: Post | null;
  isLoading: boolean;
  isScheduling: boolean;
  error: string | null;

  // Actions
  fetchPosts: (channelId?: string) => Promise<void>;
  fetchScheduledPosts: (channelId?: string) => Promise<void>;
  createPost: (postData: CreatePostRequest) => Promise<void>;
  schedulePost: (postData: CreatePostRequest & { scheduledTime: string }) => Promise<void>;
  updatePost: (postId: string, data: Partial<Post>) => Promise<void>;
  deletePost: (postId: string) => Promise<void>;
  cancelScheduledPost: (postId: string) => Promise<void>;
  selectPost: (post: Post | null) => void;
  clearError: () => void;
}

export const usePostStore = create<PostState>()(
  subscribeWithSelector((set) => ({
    // Initial state
    posts: [],
    scheduledPosts: [],
    selectedPost: null,
    isLoading: false,
    isScheduling: false,
    error: null,

    // Fetch all posts
    fetchPosts: async (channelId?: string) => {
      set({ isLoading: true, error: null });

      try {
        const endpoint = channelId ? `/posts?channel_id=${channelId}` : '/posts';
        const posts = await apiClient.get<Post[]>(endpoint);
        set({
          posts: posts || [],
          isLoading: false
        });
        console.log('✅ Posts loaded:', posts?.length || 0);
      } catch (error) {
        console.error('❌ Failed to load posts:', error);
        const errorMessage = error instanceof Error ? error.message : 'Failed to load posts';
        set({
          posts: [],
          error: errorMessage,
          isLoading: false
        });
      }
    },

    // Fetch scheduled posts
    fetchScheduledPosts: async (channelId?: string) => {
      set({ isLoading: true, error: null });

      try {
        const endpoint = channelId
          ? `/posts/scheduled?channel_id=${channelId}`
          : '/posts/scheduled';
        const scheduledPosts = await apiClient.get<ScheduledPost[]>(endpoint);
        set({
          scheduledPosts: scheduledPosts || [],
          isLoading: false
        });
        console.log('✅ Scheduled posts loaded:', scheduledPosts?.length || 0);
      } catch (error) {
        console.error('❌ Failed to load scheduled posts:', error);
        const errorMessage = error instanceof Error ? error.message : 'Failed to load scheduled posts';
        set({
          scheduledPosts: [],
          error: errorMessage,
          isLoading: false
        });
      }
    },

    // Create a new post
    createPost: async (postData: CreatePostRequest) => {
      set({ isLoading: true, error: null });

      try {
        console.log('📝 Creating post:', postData);
        const newPost = await apiClient.post<Post>('/posts', postData);

        set(state => ({
          posts: [...state.posts, newPost],
          isLoading: false
        }));

        console.log('✅ Post created successfully:', newPost);
      } catch (error) {
        console.error('❌ Create post error:', error);
        ErrorHandler.handleError(error, {
          component: 'PostStore',
          action: 'createPost',
          postData
        });

        const errorMessage = error instanceof Error ? error.message : 'Failed to create post';
        set({
          error: errorMessage,
          isLoading: false
        });
        throw error;
      }
    },

    // Schedule a new post
    schedulePost: async (postData) => {
      set({ isScheduling: true, error: null });

      try {
        console.log('📅 Scheduling post:', postData);

        const scheduledPost = await apiClient.post<ScheduledPost>('/posts/schedule', postData);

        set(state => ({
          scheduledPosts: [...state.scheduledPosts, scheduledPost],
          isScheduling: false
        }));

        console.log('✅ Post scheduled successfully:', scheduledPost);
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
          isScheduling: false
        });
        throw error;
      }
    },

    // Update a post
    updatePost: async (postId: string, data: Partial<Post>) => {
      set({ isLoading: true, error: null });

      try {
        console.log('✏️ Updating post:', postId, data);
        const updatedPost = await apiClient.patch<Post>(`/posts/${postId}`, data);

        set(state => ({
          posts: state.posts.map(post =>
            post.id === postId ? updatedPost : post
          ),
          selectedPost: state.selectedPost?.id === postId
            ? updatedPost
            : state.selectedPost,
          isLoading: false
        }));

        console.log('✅ Post updated successfully');
      } catch (error) {
        console.error('❌ Update post error:', error);
        ErrorHandler.handleError(error, {
          component: 'PostStore',
          action: 'updatePost',
          postId,
          data
        });

        const errorMessage = error instanceof Error ? error.message : 'Failed to update post';
        set({
          error: errorMessage,
          isLoading: false
        });
        throw error;
      }
    },

    // Delete a post
    deletePost: async (postId: string) => {
      set({ isLoading: true, error: null });

      try {
        console.log('🗑️ Deleting post:', postId);
        await apiClient.delete(`/posts/${postId}`);

        set(state => ({
          posts: state.posts.filter(post => post.id !== postId),
          selectedPost: state.selectedPost?.id === postId
            ? null
            : state.selectedPost,
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
        throw error;
      }
    },

    // Cancel scheduled post
    cancelScheduledPost: async (postId: string) => {
      set({ isLoading: true, error: null });

      try {
        console.log('⏹️ Canceling scheduled post:', postId);
        await apiClient.delete(`/posts/scheduled/${postId}`);

        set(state => ({
          scheduledPosts: state.scheduledPosts.filter(post => post.id !== postId),
          isLoading: false
        }));

        console.log('✅ Scheduled post canceled successfully');
      } catch (error) {
        console.error('❌ Cancel scheduled post error:', error);
        const errorMessage = error instanceof Error ? error.message : 'Failed to cancel scheduled post';
        set({
          error: errorMessage,
          isLoading: false
        });
        throw error;
      }
    },

    // Select post
    selectPost: (post: Post | null) => {
      set({ selectedPost: post });
    },

    // Clear error
    clearError: () => {
      set({ error: null });
    }
  }))
);

export default usePostStore;

/**
 * Posts Store (TypeScript)
 * Manages scheduled posts state and operations
 * Pure domain logic for posts - separated from god store
 */

import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { apiClient } from '@/api/client';
import { ErrorHandler } from '@/utils/errorHandler';
import { storeLogger } from '@/utils/logger';
import type { Post, ScheduledPost, CreatePostRequest } from '@/types';

// Internal type for PostCreator component data
interface PostCreatorData {
  text: string;
  selectedChannel: string;
  scheduleTime: string | null;
  inline_buttons?: any[][];
  media?: {
    type: string;
    url: string;
    telegram_file_id?: string;
  };
}

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
  sendNowPost: (postData: PostCreatorData) => Promise<void>;
  schedulePost: (postData: PostCreatorData) => Promise<void>;
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

    // Fetch all posts - NOTE: Backend doesn't have a general /posts endpoint
    // Posts only exist as either scheduled (future) or in analytics (past, sent via bot)
    fetchPosts: async () => {
      set({ isLoading: true, error: null });

      try {
        // For now, return empty array since there's no /posts endpoint
        // Posts are tracked in analytics after being sent through the bot
        storeLogger.debug('No general /posts endpoint - posts are tracked in scheduled or analytics');
        set({
          posts: [],
          isLoading: false
        });
      } catch (error) {
        storeLogger.error('Failed to load posts', { error });
        const errorMessage = error instanceof Error ? error.message : 'Failed to load posts';
        set({
          posts: [],
          error: errorMessage,
          isLoading: false
        });
      }
    },

        // Fetch scheduled posts
    fetchScheduledPosts: async () => {
      set({ isLoading: true, error: null });

      try {
        // Get user ID from JWT token (check multiple possible keys)
        const token = localStorage.getItem('access_token') ||
                     localStorage.getItem('jwt_token') ||
                     localStorage.getItem('auth_token');

        if (!token) {
          throw new Error('No authentication token found');
        }

        const payload = JSON.parse(atob(token.split('.')[1]));
        const userId = payload.sub;

        const endpoint = `/schedule/user/${userId}`;
        const scheduledPosts = await apiClient.get<ScheduledPost[]>(endpoint);
        set({
          scheduledPosts: scheduledPosts || [],
          isLoading: false
        });
        storeLogger.debug('Scheduled posts loaded', { count: scheduledPosts?.length || 0 });
      } catch (error) {
        storeLogger.error('Failed to load scheduled posts', { error });
        const errorMessage = error instanceof Error ? error.message : 'Failed to load scheduled posts';
        set({
          scheduledPosts: [],
          isLoading: false,
          error: errorMessage
        });
      }
    },

    // Create a new post
    createPost: async (postData: CreatePostRequest) => {
      set({ isLoading: true, error: null });

      try {
        storeLogger.debug('Creating post', { postData });
        const newPost = await apiClient.post<Post>('/posts', postData);

        set(state => ({
          posts: [...state.posts, newPost],
          isLoading: false
        }));

        storeLogger.info('Post created successfully', { postId: newPost.id });
      } catch (error) {
        storeLogger.error('Create post error', { error, postData });
        ErrorHandler.handleError(error as Error, {
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

    // Send post immediately (no scheduling)
    sendNowPost: async (postData) => {
      set({ isScheduling: true, error: null });

      try {
        storeLogger.debug('Sending post immediately', { postData });

        // Get user ID from JWT token (check multiple keys)
        const token = localStorage.getItem('access_token') ||
                     localStorage.getItem('jwt_token') ||
                     localStorage.getItem('auth_token');

        if (!token) {
          throw new Error('No authentication token found');
        }

        // Decode JWT to get user_id
        const payload = JSON.parse(atob(token.split('.')[1]));
        const userId = payload.sub || payload.user_id || payload.id;

        if (!userId) {
          throw new Error('User ID not found in token');
        }

        // Transform frontend data to backend API format for immediate send
        // Frontend sends: { text, selectedChannel, inline_buttons, media }
        // Backend /send expects: { user_id, channel_id, message, media_type, media_url, telegram_file_id }
        const backendPayload = {
          user_id: parseInt(userId),
          channel_id: parseInt(postData.selectedChannel),
          message: postData.text,
          media_type: postData.media?.type || 'text',
          media_url: postData.media?.url || null,
          telegram_file_id: postData.media?.telegram_file_id || null,  // For Telegram storage files
        };

        storeLogger.debug('Transformed payload for backend /send', { backendPayload });

        const sentPost = await apiClient.post<ScheduledPost>('/system/send', backendPayload);

        set(state => ({
          scheduledPosts: [...state.scheduledPosts, sentPost],
          isScheduling: false
        }));

        storeLogger.info('Post sent immediately', { postId: sentPost.id });
      } catch (error) {
        storeLogger.error('Send post error', { error, postData });
        ErrorHandler.handleError(error as Error, {
          component: 'PostStore',
          action: 'sendNowPost',
          postData
        });

        const errorMessage = error instanceof Error ? error.message : 'Failed to send post';
        set({ error: errorMessage, isScheduling: false });
        throw error;
      }
    },

    // Schedule a new post
    schedulePost: async (postData) => {
      set({ isScheduling: true, error: null });

      try {
        storeLogger.debug('Scheduling post', { postData });

        // Get user ID from JWT token (check multiple keys)
        const token = localStorage.getItem('access_token') ||
                     localStorage.getItem('jwt_token') ||
                     localStorage.getItem('auth_token');

        if (!token) {
          throw new Error('No authentication token found');
        }

        // Decode JWT to get user_id
        const payload = JSON.parse(atob(token.split('.')[1]));
        const userId = payload.sub || payload.user_id || payload.id;

        if (!userId) {
          throw new Error('User ID not found in token');
        }

        // Transform frontend data to backend API format
        // Frontend sends: { text, selectedChannel, scheduleTime, inline_buttons, media }
        // Backend expects: { user_id, channel_id, message, scheduled_time, media_type, media_url }
        const backendPayload = {
          user_id: parseInt(userId),
          channel_id: parseInt(postData.selectedChannel),
          message: postData.text,
          scheduled_time: postData.scheduleTime,
          media_type: postData.media?.type || 'text',
          media_url: postData.media?.url || null,
        };

        storeLogger.debug('Transformed payload for backend schedule', { backendPayload });

        const scheduledPost = await apiClient.post<ScheduledPost>('/system/schedule', backendPayload);

        set(state => ({
          scheduledPosts: [...state.scheduledPosts, scheduledPost],
          isScheduling: false
        }));

        storeLogger.info('Post scheduled successfully', { postId: scheduledPost.id });
      } catch (error) {
        storeLogger.error('Schedule post error', { error, postData });
        ErrorHandler.handleError(error as Error, {
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
        storeLogger.debug('Updating post', { postId, data });
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

        storeLogger.info('Post updated successfully', { postId });
      } catch (error) {
        storeLogger.error('Update post error', { error, postId, data });
        ErrorHandler.handleError(error as Error, {
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
        storeLogger.debug('Deleting post', { postId });
        await apiClient.delete(`/posts/${postId}`);

        set(state => ({
          posts: state.posts.filter(post => post.id !== postId),
          selectedPost: state.selectedPost?.id === postId
            ? null
            : state.selectedPost,
          isLoading: false
        }));

        storeLogger.info('Post deleted successfully', { postId });
      } catch (error) {
        storeLogger.error('Delete post error', { error, postId });
        ErrorHandler.handleError(error as Error, {
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
        storeLogger.debug('Canceling scheduled post', { postId });
        await apiClient.delete(`/posts/scheduled/${postId}`);

        set(state => ({
          scheduledPosts: state.scheduledPosts.filter(post => post.id !== postId),
          isLoading: false
        }));

        storeLogger.info('Scheduled post canceled successfully', { postId });
      } catch (error) {
        storeLogger.error('Cancel scheduled post error', { error, postId });
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

/**
 * Channels Store
 * Manages Telegram channels state and operations
 * Pure domain logic for channels - separated from god store
 */

import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { apiClient } from '@/api/client.js';
import { ErrorHandler } from '@/utils/errorHandler.js';

interface Channel {
  id: string | number;
  username: string;
  title?: string;
  description?: string;
  members_count?: number;
  photo_url?: string;
  is_active?: boolean;
}

interface ValidationResult {
  success: boolean;
  data?: any;
  error?: string;
}

interface ChannelsState {
  // State
  channels: Channel[];
  isLoading: boolean;
  error: string | null;
  validating: boolean;
  validationError: string | null;

  // Actions
  loadChannels: () => Promise<void>;
  addChannel: (username: string) => Promise<boolean>;
  deleteChannel: (channelId: string | number) => Promise<void>;
  validateChannel: (username: string) => Promise<ValidationResult>;
  setChannels: (channels: Channel[]) => void;
  clearError: () => void;
}

export const useChannelStore = create<ChannelsState>()(
  subscribeWithSelector((set, get) => ({
    // Initial state
    channels: [],
    isLoading: false,
    error: null,
    validating: false,
    validationError: null,

    // Load all channels
    loadChannels: async () => {
      set({ isLoading: true, error: null });

      try {
        const channels = await apiClient.get('/analytics/channels');
        set({
          channels: channels || [],
          isLoading: false
        });
        console.log('✅ Channels loaded:', channels?.length || 0);
      } catch (error) {
        console.error('❌ Failed to load channels:', error);
        const errorMessage = error instanceof Error ? error.message : 'Failed to load channels';
        set({
          channels: [],
          error: errorMessage,
          isLoading: false
        });
      }
    },

    // Validate Telegram channel
    validateChannel: async (username: string): Promise<ValidationResult> => {
      set({ validating: true, validationError: null });

      try {
        // Ensure username starts with @
        const channelUsername = username.startsWith('@') ? username : `@${username}`;
        console.log('🔍 Validating Telegram channel:', channelUsername);

        const validationResult = await apiClient.post('/analytics/channels/validate', {
          username: channelUsername
        } as any);

        set({ validating: false });

        if (validationResult.is_valid) {
          console.log('✅ Channel validated:', validationResult.title);
          return {
            success: true,
            data: validationResult
          };
        } else {
          console.warn('❌ Channel validation failed:', validationResult.error_message);
          return {
            success: false,
            error: validationResult.error_message || 'Channel not found'
          };
        }
      } catch (error) {
        console.error('❌ Channel validation error:', error);
        ErrorHandler.handleError(error, {
          component: 'ChannelStore',
          action: 'validateChannel',
          username
        });

        const errorMessage = error instanceof Error ? error.message : 'Validation failed';
        set({
          validating: false,
          validationError: errorMessage
        });

        return {
          success: false,
          error: errorMessage
        };
      }
    },

    // Add new channel
    addChannel: async (channelUsername: string): Promise<boolean> => {
      set({ isLoading: true, error: null });

      try {
        // Clean username
        const cleanUsername = channelUsername.replace('@', '');
        const usernameWithAt = `@${cleanUsername}`;
        console.log('📺 Adding channel:', usernameWithAt);

        // Step 1: Validate with Telegram API first
        const validation = await get().validateChannel(usernameWithAt);

        if (!validation.success) {
          set({
            isLoading: false,
            error: validation.error || 'Channel validation failed'
          });
          return false;
        }

        // Step 2: Add to database
        console.log('💾 Saving channel to database...');
        const result = await apiClient.post('/analytics/channels', {
          username: usernameWithAt,
          title: validation.data?.title,
          description: validation.data?.description,
          members_count: validation.data?.members_count
        } as any);

        // Step 3: Reload channels list
        await get().loadChannels();

        console.log('✅ Channel added successfully:', result);
        set({ isLoading: false });
        return true;

      } catch (error) {
        console.error('❌ Add channel error:', error);
        ErrorHandler.handleError(error, {
          component: 'ChannelStore',
          action: 'addChannel',
          username: channelUsername
        });

        const errorMessage = error instanceof Error ? error.message : 'Failed to add channel';
        set({
          error: errorMessage,
          isLoading: false
        });
        return false;
      }
    },

    // Delete channel
    deleteChannel: async (channelId: string | number) => {
      set({ isLoading: true, error: null });

      try {
        console.log('🗑️ Deleting channel:', channelId);
        await apiClient.delete(`/analytics/channels/${channelId}`);

        // Remove from local state
        set(state => ({
          channels: state.channels.filter(ch => ch.id !== channelId),
          isLoading: false
        }));

        console.log('✅ Channel deleted successfully');
      } catch (error) {
        console.error('❌ Delete channel error:', error);
        ErrorHandler.handleError(error, {
          component: 'ChannelStore',
          action: 'deleteChannel',
          channelId
        });

        const errorMessage = error instanceof Error ? error.message : 'Failed to delete channel';
        set({
          error: errorMessage,
          isLoading: false
        });
      }
    },

    // Set channels directly
    setChannels: (channels: Channel[]) => {
      set({ channels });
    },

    // Clear error
    clearError: () => {
      set({ error: null, validationError: null });
    }
  }))
);

export default useChannelStore;

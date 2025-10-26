/**
 * Channels Store (TypeScript)
 * Manages Telegram channels state and operations
 * Pure domain logic for channels - separated from god store
 */

import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { apiClient } from '@/api/client';
import { ErrorHandler } from '@/utils/errorHandler';
import type { Channel, ValidationResult, ChannelValidationResponse } from '@/types';

interface ChannelState {
  // State
  channels: Channel[];
  selectedChannel: Channel | null;
  isLoading: boolean;
  isValidating: boolean;
  error: string | null;
  validationError: string | null;

  // Actions
  fetchChannels: () => Promise<void>;
  addChannel: (channelData: {
    name: string;
    username: string;
    description?: string;
  }) => Promise<void>;
  updateChannel: (channelId: string, data: Partial<Channel>) => Promise<void>;
  deleteChannel: (channelId: string) => Promise<void>;
  selectChannel: (channel: Channel | null) => void;
  validateChannel: (username: string) => Promise<ValidationResult>;
  clearError: () => void;
  clearValidationError: () => void;
}

export const useChannelStore = create<ChannelState>()(
  subscribeWithSelector((set, get) => ({
    // Initial state
    channels: [],
    selectedChannel: null,
    isLoading: false,
    isValidating: false,
    error: null,
    validationError: null,

    // Fetch all channels
    fetchChannels: async () => {
      set({ isLoading: true, error: null });

      try {
        const channels = await apiClient.get<Channel[]>('/analytics/channels');
        set({
          channels: channels || [],
          isLoading: false
        });
        console.log('✅ Channels loaded:', channels?.length || 0);
      } catch (error) {
        console.error('❌ Failed to load channels:', error);
        
        // Provide helpful error message
        let errorMessage = 'Failed to load channels';
        if (error instanceof Error) {
          if (error.message.includes('timeout')) {
            errorMessage = 'API request timed out - please check your connection or try again';
          } else if (error.message.includes('Network') || error.message.includes('Failed to fetch')) {
            errorMessage = 'Cannot connect to API - please check if the backend is running';
          } else {
            errorMessage = error.message;
          }
        }
        
        set({
          channels: [],
          error: errorMessage,
          isLoading: false
        });
      }
    },

    // Validate Telegram channel
    validateChannel: async (username: string): Promise<ValidationResult> => {
      set({ isValidating: true, validationError: null });

      try {
        // Ensure username starts with @
        const channelUsername = username.startsWith('@') ? username : `@${username}`;
        console.log('🔍 Validating Telegram channel:', channelUsername);

        // Use shorter timeout (5s) since validation is optional
        const validationResult = await apiClient.post<ChannelValidationResponse>(
          '/analytics/channels/validate',
          { username: channelUsername },
          { timeout: 5000 } // 5 second timeout for optional validation
        );

        set({ isValidating: false });

        if (validationResult.valid) {
          console.log('✅ Channel validated:', validationResult.channelData?.title);
          return {
            valid: true
          };
        } else {
          console.warn('❌ Channel validation failed:', validationResult.error);
          return {
            valid: false,
            errors: [validationResult.error || 'Channel not found']
          };
        }
      } catch (error) {
        console.error('❌ Channel validation error:', error);
        ErrorHandler.handleError(error as Error, {
          component: 'ChannelStore',
          action: 'validateChannel',
          username
        });

        const errorMessage = error instanceof Error ? error.message : 'Validation failed';
        set({
          isValidating: false,
          validationError: errorMessage
        });

        return {
          valid: false,
          errors: [errorMessage]
        };
      }
    },

    // Add new channel
    addChannel: async (channelData) => {
      set({ isLoading: true, error: null });

      try {
        // Clean username
        const cleanUsername = channelData.username.replace('@', '');
        const usernameWithAt = `@${cleanUsername}`;
        console.log('📺 Adding channel:', usernameWithAt);

        // Step 1: Optional validation with Telegram API
        // If validation fails or times out, we still continue with channel creation
        try {
          console.log('🔍 Attempting Telegram validation (optional)...');
          const validation = await get().validateChannel(usernameWithAt);

          if (validation.valid) {
            console.log('✅ Telegram validation successful');
          } else {
            console.warn('⚠️ Telegram validation failed, continuing anyway:', validation.errors);
          }
        } catch (validationError) {
          // Log but don't block channel creation
          console.warn('⚠️ Telegram validation unavailable, continuing anyway:', validationError);
        }

        // Step 2: Add to database
        console.log('💾 Saving channel to database...');
        const newChannel = await apiClient.post<Channel>('/channels', {
          name: channelData.name,
          username: usernameWithAt,
          description: channelData.description
        });

        // Step 3: Add to local state
        set(state => ({
          channels: [...state.channels, newChannel],
          isLoading: false
        }));

        console.log('✅ Channel added successfully:', newChannel);
      } catch (error) {
        console.error('❌ Add channel error:', error);
        ErrorHandler.handleError(error as Error, {
          component: 'ChannelStore',
          action: 'addChannel',
          username: channelData.username
        });

        const errorMessage = error instanceof Error ? error.message : 'Failed to add channel';
        set({
          error: errorMessage,
          isLoading: false
        });
        throw error;
      }
    },

    // Update channel
    updateChannel: async (channelId: string, data: Partial<Channel>) => {
      set({ isLoading: true, error: null });

      try {
        const updatedChannel = await apiClient.patch<Channel>(
          `/analytics/channels/${channelId}`,
          data
        );

        set(state => ({
          channels: state.channels.map(ch =>
            ch.id === channelId ? updatedChannel : ch
          ),
          selectedChannel: state.selectedChannel?.id === channelId
            ? updatedChannel
            : state.selectedChannel,
          isLoading: false
        }));

        console.log('✅ Channel updated successfully');
      } catch (error) {
        console.error('❌ Update channel error:', error);
        const errorMessage = error instanceof Error ? error.message : 'Failed to update channel';
        set({
          error: errorMessage,
          isLoading: false
        });
        throw error;
      }
    },

    // Delete channel
    deleteChannel: async (channelId: string) => {
      set({ isLoading: true, error: null });

      try {
        console.log('🗑️ Deleting channel:', channelId);
        await apiClient.delete(`/channels/${channelId}`);

        // Remove from local state
        set(state => ({
          channels: state.channels.filter(ch => ch.id !== channelId),
          selectedChannel: state.selectedChannel?.id === channelId
            ? null
            : state.selectedChannel,
          isLoading: false
        }));

        console.log('✅ Channel deleted successfully');
      } catch (error) {
        console.error('❌ Delete channel error:', error);
        ErrorHandler.handleError(error as Error, {
          component: 'ChannelStore',
          action: 'deleteChannel',
          channelId
        });

        const errorMessage = error instanceof Error ? error.message : 'Failed to delete channel';
        set({
          error: errorMessage,
          isLoading: false
        });
        throw error;
      }
    },

    // Select channel
    selectChannel: (channel: Channel | null) => {
      set({ selectedChannel: channel });
    },

    // Clear error
    clearError: () => {
      set({ error: null });
    },

    // Clear validation error
    clearValidationError: () => {
      set({ validationError: null });
    }
  }))
);

export default useChannelStore;

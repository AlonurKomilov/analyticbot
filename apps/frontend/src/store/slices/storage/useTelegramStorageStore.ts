/**
 * Telegram Storage Store
 *
 * Manages user-owned Telegram channels for file storage and media management.
 * Enables file hosting by uploading files to user's private channels.
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { apiClient } from '@/api/client';

// ============================================================================
// Types
// ============================================================================

export interface StorageChannel {
  id: number;
  user_id: number;
  channel_id: number;
  channel_title: string;
  channel_username: string | null;
  is_active: boolean;
  is_bot_admin: boolean;
  created_at: string;
  last_validated_at: string | null;
}

export interface TelegramMedia {
  id: number;
  user_id: number;
  storage_channel_id: number;
  telegram_file_id: string;
  telegram_message_id: number;
  file_type: 'photo' | 'video' | 'document' | 'audio';
  file_name: string;
  file_size: number;
  file_size_formatted: string;
  mime_type: string | null;
  width: number | null;
  height: number | null;
  duration: number | null;
  caption: string | null;
  preview_url: string | null;
  uploaded_at: string;
}

export interface ChannelValidationResult {
  is_valid: boolean;
  channel_id: number;
  channel_title: string;
  channel_username: string | null;
  member_count: number;
  bot_is_admin: boolean;
  message: string;
}

export interface FileUploadResult {
  success: boolean;
  media: TelegramMedia;
  message: string;
}

export interface FilesListResult {
  files: TelegramMedia[];
  total: number;
  limit: number;
  offset: number;
}

interface TelegramStorageState {
  // State
  channels: StorageChannel[];
  currentChannel: StorageChannel | null;
  files: TelegramMedia[];
  totalFiles: number;

  // Loading states
  isLoadingChannels: boolean;
  isLoadingFiles: boolean;
  isValidating: boolean;
  isUploading: boolean;

  // Error states
  error: string | null;

  // Actions - Channels
  fetchChannels: (onlyActive?: boolean) => Promise<void>;
  validateChannel: (channelId: number, channelUsername?: string) => Promise<ChannelValidationResult>;
  connectChannel: (channelId: number, channelUsername?: string) => Promise<StorageChannel>;
  disconnectChannel: (channelId: number) => Promise<void>;
  setCurrentChannel: (channel: StorageChannel | null) => void;

  // Actions - Files
  uploadFile: (file: File, caption?: string, storageChannelId?: number) => Promise<TelegramMedia>;
  fetchFiles: (filters?: { fileType?: string; limit?: number; offset?: number }) => Promise<void>;
  getFileUrl: (mediaId: number) => Promise<string>;
  deleteFile: (mediaId: number, deleteFromTelegram?: boolean) => Promise<void>;
  forwardFile: (mediaId: number, targetChannelId: number) => Promise<number>;

  // Utility
  clearError: () => void;
  reset: () => void;
}

// ============================================================================
// Initial State
// ============================================================================

const initialState = {
  channels: [],
  currentChannel: null,
  files: [],
  totalFiles: 0,
  isLoadingChannels: false,
  isLoadingFiles: false,
  isValidating: false,
  isUploading: false,
  error: null,
};

// ============================================================================
// Store
// ============================================================================

export const useTelegramStorageStore = create<TelegramStorageState>()(
  devtools(
    (set) => ({
      ...initialState,

      // ========================================================================
      // Channel Management
      // ========================================================================

      fetchChannels: async (onlyActive = true) => {
        set({ isLoadingChannels: true, error: null });
        try {
          const response = await apiClient.get<StorageChannel[]>(
            '/api/storage/channels',
            { params: { only_active: onlyActive } }
          );

          // Ensure channels is always an array
          const channels = Array.isArray(response) ? response : [];

          set({
            channels,
            currentChannel: channels.length > 0 ? channels[0] : null,
            isLoadingChannels: false
          });
        } catch (error: any) {
          console.error('Failed to fetch storage channels:', error);
          set({
            channels: [], // Reset to empty array on error
            currentChannel: null,
            error: error.response?.data?.detail || 'Failed to load storage channels',
            isLoadingChannels: false
          });
        }
      },

      validateChannel: async (channelId: number, channelUsername?: string) => {
        set({ isValidating: true, error: null });
        try {
          const result = await apiClient.post<ChannelValidationResult>(
            '/api/storage/channels/validate',
            { channel_id: channelId, channel_username: channelUsername }
          );

          set({ isValidating: false });
          return result;
        } catch (error: any) {
          console.error('Channel validation failed:', error);
          const errorMessage = error.response?.data?.detail || 'Channel validation failed';
          set({ error: errorMessage, isValidating: false });
          throw new Error(errorMessage);
        }
      },

      connectChannel: async (channelId: number, channelUsername?: string) => {
        set({ isLoadingChannels: true, error: null });
        try {
          const newChannel = await apiClient.post<StorageChannel>(
            '/api/storage/channels/connect',
            { channel_id: channelId, channel_username: channelUsername }
          );

          set((state) => ({
            channels: [newChannel, ...state.channels],
            currentChannel: newChannel,
            isLoadingChannels: false,
          }));

          return newChannel;
        } catch (error: any) {
          console.error('Failed to connect channel:', error);
          const errorMessage = error.response?.data?.detail || 'Failed to connect channel';
          set({ error: errorMessage, isLoadingChannels: false });
          throw new Error(errorMessage);
        }
      },

      disconnectChannel: async (channelId: number) => {
        set({ isLoadingChannels: true, error: null });
        try {
          await apiClient.delete(`/api/storage/channels/${channelId}`);

          set((state) => {
            const updatedChannels = state.channels.filter((ch) => ch.id !== channelId);
            return {
              channels: updatedChannels,
              currentChannel: state.currentChannel?.id === channelId
                ? (updatedChannels[0] || null)
                : state.currentChannel,
              isLoadingChannels: false,
            };
          });
        } catch (error: any) {
          console.error('Failed to disconnect channel:', error);
          set({
            error: error.response?.data?.detail || 'Failed to disconnect channel',
            isLoadingChannels: false
          });
          throw error;
        }
      },

      setCurrentChannel: (channel: StorageChannel | null) => {
        set({ currentChannel: channel });
      },

      // ========================================================================
      // File Management
      // ========================================================================

      uploadFile: async (file: File, caption?: string, storageChannelId?: number) => {
        set({ isUploading: true, error: null });
        try {
          const formData = new FormData();
          formData.append('file', file);
          if (caption) formData.append('caption', caption);
          if (storageChannelId) formData.append('storage_channel_id', storageChannelId.toString());

          const uploadResult = await apiClient.post<FileUploadResult>(
            '/api/storage/upload',
            formData
          );

          const newMedia = uploadResult.media;

          set((state) => ({
            files: [newMedia, ...state.files],
            totalFiles: state.totalFiles + 1,
            isUploading: false,
          }));

          return newMedia;
        } catch (error: any) {
          console.error('File upload failed:', error);
          const errorMessage = error.response?.data?.detail || 'Failed to upload file';
          set({ error: errorMessage, isUploading: false });
          throw new Error(errorMessage);
        }
      },

      fetchFiles: async (filters = {}) => {
        set({ isLoadingFiles: true, error: null });
        try {
          const result = await apiClient.get<FilesListResult>(
            '/api/storage/files',
            { params: filters }
          );

          // Ensure files is always an array
          const files = Array.isArray(result?.files) ? result.files : [];
          const total = typeof result?.total === 'number' ? result.total : 0;

          set({
            files,
            totalFiles: total,
            isLoadingFiles: false
          });
        } catch (error: any) {
          console.error('Failed to fetch files:', error);
          set({
            files: [], // Reset to empty array on error
            totalFiles: 0,
            error: error.response?.data?.detail || 'Failed to load files',
            isLoadingFiles: false
          });
        }
      },

      getFileUrl: async (mediaId: number) => {
        try {
          const result = await apiClient.get<{ url: string }>(
            `/api/storage/files/${mediaId}/url`
          );
          return result.url;
        } catch (error: any) {
          console.error('Failed to get file URL:', error);
          throw new Error(error.response?.data?.detail || 'Failed to get file URL');
        }
      },

      deleteFile: async (mediaId: number, deleteFromTelegram = true) => {
        set({ error: null });
        try {
          await apiClient.delete(
            `/api/storage/files/${mediaId}`,
            { params: { delete_from_telegram: deleteFromTelegram } }
          );

          set((state) => ({
            files: state.files.filter((file) => file.id !== mediaId),
            totalFiles: Math.max(0, state.totalFiles - 1),
          }));
        } catch (error: any) {
          console.error('Failed to delete file:', error);
          const errorMessage = error.response?.data?.detail || 'Failed to delete file';
          set({ error: errorMessage });
          throw new Error(errorMessage);
        }
      },

      forwardFile: async (mediaId: number, targetChannelId: number) => {
        set({ error: null });
        try {
          const result = await apiClient.post<{ success: boolean; message_id: number }>(
            `/api/storage/files/${mediaId}/forward`,
            null,
            { params: { target_channel_id: targetChannelId } }
          );

          return result.message_id;
        } catch (error: any) {
          console.error('Failed to forward file:', error);
          const errorMessage = error.response?.data?.detail || 'Failed to forward file';
          set({ error: errorMessage });
          throw new Error(errorMessage);
        }
      },

      // ========================================================================
      // Utility
      // ========================================================================

      clearError: () => set({ error: null }),

      reset: () => set(initialState),
    }),
    { name: 'TelegramStorageStore' }
  )
);

// ============================================================================
// Selectors
// ============================================================================

export const selectHasStorageChannels = (state: TelegramStorageState) =>
  state.channels.length > 0;

export const selectDefaultChannel = (state: TelegramStorageState) =>
  state.channels.find((ch) => ch.is_active) || state.channels[0] || null;

export const selectFilesByType = (fileType: string) => (state: TelegramStorageState) =>
  state.files.filter((file) => file.file_type === fileType);

export const selectTotalStorageUsed = (state: TelegramStorageState) =>
  state.files.reduce((total, file) => total + file.file_size, 0);

export const selectTotalStorageUsedFormatted = (state: TelegramStorageState) => {
  const bytes = selectTotalStorageUsed(state);
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
};

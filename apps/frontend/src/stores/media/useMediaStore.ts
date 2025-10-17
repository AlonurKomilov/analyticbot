/**
 * Media Store
 * Manages media upload state and operations
 * Pure domain logic for media - separated from god store
 */

import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { apiClient } from '@/api/client.js';
import { ErrorHandler } from '@/utils/errorHandler.js';

export interface PendingMedia {
  file_id: string | null;
  file_type: string | null;
  previewUrl: string | null;
  uploadProgress: number;
  fileName?: string;
  fileSize?: number;
}

interface MediaState {
  // State
  pendingMedia: PendingMedia;
  isUploading: boolean;
  error: string | null;

  // Actions
  uploadMedia: (file: File) => Promise<any>;
  uploadMediaDirect: (file: File, channelId?: string | number) => Promise<any>;
  clearPendingMedia: () => void;
  setUploadProgress: (progress: number) => void;
  clearError: () => void;
}

export const useMediaStore = create<MediaState>()(
  subscribeWithSelector((set, get) => ({
    // Initial state
    pendingMedia: {
      file_id: null,
      file_type: null,
      previewUrl: null,
      uploadProgress: 0
    },
    isUploading: false,
    error: null,

    // Upload media file
    uploadMedia: async (file: File) => {
      set({ isUploading: true, error: null });

      try {
        // Create preview URL
        const previewUrl = URL.createObjectURL(file);

        set({
          pendingMedia: {
            file_id: null,
            file_type: file.type,
            previewUrl,
            uploadProgress: 0,
            fileName: file.name,
            fileSize: file.size
          }
        });

        console.log('📤 Uploading media:', file.name, file.type);

        const response = await (apiClient.uploadFile as any)('/upload-media', file, (progress: number) => {
          set(state => ({
            pendingMedia: {
              ...state.pendingMedia,
              uploadProgress: progress
            }
          }));
        });

        set(state => ({
          pendingMedia: {
            ...state.pendingMedia,
            file_id: response.file_id,
            file_type: response.file_type,
            uploadProgress: 100
          },
          isUploading: false
        }));

        console.log('✅ Media uploaded successfully:', response.file_id);
        return response;

      } catch (error) {
        console.error('❌ Media upload error:', error);
        ErrorHandler.handleError(error, {
          component: 'MediaStore',
          action: 'uploadMedia',
          fileType: file.type,
          fileSize: file.size
        });

        const errorMessage = error instanceof Error ? error.message : 'Failed to upload media';
        set({
          error: errorMessage,
          isUploading: false
        });

        get().clearPendingMedia();
        throw error;
      }
    },

    // Direct media upload for TWA
    uploadMediaDirect: async (file: File, channelId?: string | number) => {
      set({ isUploading: true, error: null });

      try {
        // Create preview URL
        const previewUrl = URL.createObjectURL(file);

        set({
          pendingMedia: {
            file_id: null,
            file_type: file.type,
            previewUrl,
            uploadProgress: 0,
            fileName: file.name,
            fileSize: file.size
          }
        });

        console.log('📤 Direct media upload:', file.name, channelId);

        const formData = new FormData();
        formData.append('file', file);
        if (channelId) {
          formData.append('channel_id', String(channelId));
        }

        const response = await apiClient.post('/media/upload-direct', formData as any, {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          onUploadProgress: (progressEvent: any) => {
            if (progressEvent.total) {
              const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
              set(state => ({
                pendingMedia: {
                  ...state.pendingMedia,
                  uploadProgress: progress
                }
              }));
            }
          }
        });

        set(state => ({
          pendingMedia: {
            ...state.pendingMedia,
            file_id: response.file_id || response.id,
            file_type: response.file_type || file.type,
            uploadProgress: 100
          },
          isUploading: false
        }));

        console.log('✅ Direct media uploaded successfully');
        return response;

      } catch (error) {
        console.error('❌ Direct media upload error:', error);
        ErrorHandler.handleError(error, {
          component: 'MediaStore',
          action: 'uploadMediaDirect',
          fileType: file.type,
          fileSize: file.size,
          channelId
        });

        const errorMessage = error instanceof Error ? error.message : 'Failed to upload media';
        set({
          error: errorMessage,
          isUploading: false
        });

        get().clearPendingMedia();
        throw error;
      }
    },

    // Clear pending media
    clearPendingMedia: () => {
      const currentMedia = get().pendingMedia;

      // Revoke object URL to free memory
      if (currentMedia.previewUrl) {
        URL.revokeObjectURL(currentMedia.previewUrl);
      }

      set({
        pendingMedia: {
          file_id: null,
          file_type: null,
          previewUrl: null,
          uploadProgress: 0
        }
      });
    },

    // Set upload progress
    setUploadProgress: (progress: number) => {
      set(state => ({
        pendingMedia: {
          ...state.pendingMedia,
          uploadProgress: progress
        }
      }));
    },

    // Clear error
    clearError: () => {
      set({ error: null });
    }
  }))
);

export default useMediaStore;

/**
 * Media Store (TypeScript)
 * Manages media upload state and operations
 * Pure domain logic for media - separated from god store
 */

import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { apiClient } from '@/api/client';
import { ErrorHandler } from '@/utils/errorHandler';
import type { MediaFile, PendingMedia, UploadProgress } from '@/types';

interface MediaState {
  // State
  mediaFiles: MediaFile[];
  pendingMedia: PendingMedia | null;
  uploadProgress: UploadProgress | null;
  isUploading: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchMediaFiles: (channelId?: string) => Promise<void>;
  uploadMedia: (file: File, metadata?: {
    channelId?: string;
    caption?: string;
  }) => Promise<MediaFile>;
  deleteMedia: (mediaId: string) => Promise<void>;
  setPendingMedia: (media: PendingMedia | null) => void;
  clearPendingMedia: () => void;
  setUploadProgress: (progress: UploadProgress) => void;
  clearUploadProgress: () => void;
  clearError: () => void;
}

export const useMediaStore = create<MediaState>()(
  subscribeWithSelector((set, get) => ({
    // Initial state
    mediaFiles: [],
    pendingMedia: null as PendingMedia | null,
    uploadProgress: null,
    isUploading: false,
    isLoading: false,
    error: null,

    // Fetch media files
    fetchMediaFiles: async (channelId?: string) => {
      set({ isLoading: true, error: null });

      try {
        const endpoint = channelId ? `/media?channel_id=${channelId}` : '/media';
        const mediaFiles = await apiClient.get<MediaFile[]>(endpoint);

        set({
          mediaFiles: mediaFiles || [],
          isLoading: false
        });

        console.log('✅ Media files loaded:', mediaFiles?.length || 0);
      } catch (error) {
        console.error('❌ Failed to load media files:', error);
        const errorMessage = error instanceof Error ? error.message : 'Failed to load media files';
        set({
          mediaFiles: [],
          error: errorMessage,
          isLoading: false
        });
      }
    },

    // Upload media file
    uploadMedia: async (file: File, metadata = {}) => {
      set({ isUploading: true, error: null });

      try {
        // Create preview URL
        const preview = URL.createObjectURL(file);

        set({
          pendingMedia: {
            id: `pending-${Date.now()}`,
            file,
            preview,
            status: 'pending',
            type: file.type.startsWith('image/') ? 'image' :
                  file.type.startsWith('video/') ? 'video' : 'document'
          },
          uploadProgress: {
            progress: 0,
            loaded: 0,
            total: file.size
          }
        });

        console.log('📤 Uploading media:', file.name, file.type);

        // Create FormData
        const formData = new FormData();
        formData.append('file', file);
        if (metadata.channelId) {
          formData.append('channel_id', metadata.channelId);
        }
        if (metadata.caption) {
          formData.append('caption', metadata.caption);
        }

        const uploadedFile = await apiClient.post<MediaFile>('/media/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          onUploadProgress: (progressEvent: any) => {
            if (progressEvent.total) {
              const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
              set({
                uploadProgress: {
                  progress,
                  loaded: progressEvent.loaded,
                  total: progressEvent.total
                }
              });
            }
          }
        });

        set(state => ({
          mediaFiles: [...state.mediaFiles, uploadedFile],
          isUploading: false,
          uploadProgress: null
        }));

        // Clear pending media after successful upload
        get().clearPendingMedia();

        console.log('✅ Media uploaded successfully:', uploadedFile.id);
        return uploadedFile;

      } catch (error) {
        console.error('❌ Media upload error:', error);
        ErrorHandler.handleError(error as Error, {
          component: 'MediaStore',
          action: 'uploadMedia',
          fileType: file.type,
          fileSize: file.size
        });

        const errorMessage = error instanceof Error ? error.message : 'Failed to upload media';
        set({
          error: errorMessage,
          isUploading: false,
          uploadProgress: null
        });

        get().clearPendingMedia();
        throw error;
      }
    },

    // Delete media file
    deleteMedia: async (mediaId: string) => {
      set({ isLoading: true, error: null });

      try {
        console.log('�️ Deleting media:', mediaId);
        await apiClient.delete(`/media/${mediaId}`);

        set(state => ({
          mediaFiles: state.mediaFiles.filter(file => file.id !== mediaId),
          isLoading: false
        }));

        console.log('✅ Media deleted successfully');
      } catch (error) {
        console.error('❌ Delete media error:', error);
        const errorMessage = error instanceof Error ? error.message : 'Failed to delete media';
        set({
          error: errorMessage,
          isLoading: false
        });
        throw error;
      }
    },

    // Set pending media
    setPendingMedia: (media: PendingMedia | null) => {
      set({ pendingMedia: media });
    },

    // Clear pending media
    clearPendingMedia: () => {
      const currentMedia = get().pendingMedia;

      // Revoke object URL to free memory
      if (currentMedia?.preview) {
        URL.revokeObjectURL(currentMedia.preview);
      }

      set({
        pendingMedia: null
      });
    },

    // Set upload progress
    setUploadProgress: (progress: UploadProgress) => {
      set({ uploadProgress: progress });
    },

    // Clear upload progress
    clearUploadProgress: () => {
      set({ uploadProgress: null });
    },

    // Clear error
    clearError: () => {
      set({ error: null });
    }
  }))
);

export default useMediaStore;

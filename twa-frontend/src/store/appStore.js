import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { apiClient } from '../utils/apiClient.js';
import { ErrorHandler } from '../utils/errorHandler.js';

// Loading states interface
const createLoadingState = () => ({
    isLoading: false,
    error: null,
    lastUpdated: null
});

export const useAppStore = create(
    subscribeWithSelector((set, get) => ({
        // Data state
        user: null,
        plan: null,
        channels: [],
        scheduledPosts: [],
        
        // UI state
        ui: {
            global: createLoadingState(),
            fetchData: createLoadingState(),
            addChannel: createLoadingState(),
            schedulePost: createLoadingState(),
            deletePost: createLoadingState(),
            deleteChannel: createLoadingState(),
            uploadMedia: createLoadingState(),
            // NEW: Analytics operations
            fetchPostDynamics: createLoadingState(),
            fetchTopPosts: createLoadingState(),
            fetchBestTime: createLoadingState(),
            fetchEngagementMetrics: createLoadingState()
        },
        
        // NEW: Analytics data state
        analytics: {
            postDynamics: null,
            topPosts: [],
            bestTimeRecommendations: null,
            engagementMetrics: null,
            lastAnalyticsUpdate: null
        },
        
        // Media state
        pendingMedia: {
            file_id: null,
            file_type: null,
            previewUrl: null,
            uploadProgress: 0
        },

        
        // Helper functions for UI state management
        setLoading: (operation, isLoading) => set(state => ({
            ui: {
                ...state.ui,
                [operation]: {
                    ...state.ui[operation],
                    isLoading,
                    ...(isLoading ? {} : { lastUpdated: Date.now() })
                }
            }
        })),
        
        setError: (operation, error) => set(state => ({
            ui: {
                ...state.ui,
                [operation]: {
                    ...state.ui[operation],
                    error,
                    isLoading: false
                }
            }
        })),
        
        clearError: (operation) => set(state => ({
            ui: {
                ...state.ui,
                [operation]: {
                    ...state.ui[operation],
                    error: null
                }
            }
        })),

        // Boshlang'ich ma'lumotlarni backend'dan yuklash
        fetchData: async () => {
            const operation = 'fetchData';
            try {
                get().setLoading(operation, true);
                get().clearError(operation);
                
                const data = await apiClient.get('/initial-data');
                
                set({
                    channels: data.channels || [],
                    scheduledPosts: data.scheduled_posts || [],
                    plan: data.plan,
                    user: data.user,
                });
                
                get().setLoading(operation, false);
            } catch (error) {
                ErrorHandler.handleError(error, {
                    component: 'AppStore',
                    action: 'fetchData'
                });
                get().setError(operation, error.message);
            }
        },

        // Yangi kanal qo'shish
        addChannel: async (channelUsername) => {
            const operation = 'addChannel';
            try {
                get().setLoading(operation, true);
                get().clearError(operation);
                
                const newChannel = await apiClient.post('/channels', {
                    channel_username: channelUsername
                });
                
                set((state) => ({
                    channels: [...state.channels, newChannel]
                }));
                
                get().setLoading(operation, false);
                return newChannel;
            } catch (error) {
                ErrorHandler.handleError(error, {
                    component: 'AppStore',
                    action: 'addChannel',
                    channelUsername
                });
                get().setError(operation, error.message);
                throw error;
            }
        },

        // Media yuklash
        uploadMedia: async (file) => {
            const operation = 'uploadMedia';
            try {
                get().setLoading(operation, true);
                get().clearError(operation);
                
                // Create preview URL
                const previewUrl = URL.createObjectURL(file);
                
                set(state => ({
                    pendingMedia: {
                        ...state.pendingMedia,
                        previewUrl,
                        uploadProgress: 0
                    }
                }));
                
                const response = await apiClient.uploadFile('/upload-media', file, (progress) => {
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
                    }
                }));
                
                get().setLoading(operation, false);
                return response;
            } catch (error) {
                ErrorHandler.handleError(error, {
                    component: 'AppStore',
                    action: 'uploadMedia',
                    fileType: file.type,
                    fileSize: file.size
                });
                get().setError(operation, error.message);
                get().clearPendingMedia();
                throw error;
            }
        },

        // NEW: Enhanced direct media upload for TWA Phase 2.1
        uploadMediaDirect: async (file, channelId = null) => {
            const operation = 'uploadMediaDirect';
            try {
                get().setLoading(operation, true);
                get().clearError(operation);
                
                // Create preview URL
                const previewUrl = URL.createObjectURL(file);
                
                set(state => ({
                    pendingMedia: {
                        ...state.pendingMedia,
                        previewUrl,
                        uploadProgress: 0,
                        uploadSpeed: 0,
                        uploadType: channelId ? 'direct_channel' : 'storage'
                    }
                }));
                
                const response = await apiClient.uploadFileDirect(file, channelId, (progressData) => {
                    set(state => ({
                        pendingMedia: {
                            ...state.pendingMedia,
                            uploadProgress: progressData.progress,
                            uploadSpeed: progressData.speed,
                            bytesLoaded: progressData.loaded,
                            bytesTotal: progressData.total
                        }
                    }));
                });
                
                set(state => ({
                    pendingMedia: {
                        ...state.pendingMedia,
                        file_id: response.file_id,
                        file_type: response.media_type,
                        uploadProgress: 100,
                        metadata: response.metadata,
                        message_id: response.message_id,
                        upload_duration: response.upload_duration,
                        upload_speed: response.upload_speed
                    }
                }));
                
                get().setLoading(operation, false);
                return response;
            } catch (error) {
                ErrorHandler.handleError(error, {
                    component: 'AppStore',
                    action: 'uploadMediaDirect',
                    fileType: file.type,
                    fileSize: file.size,
                    channelId
                });
                get().setError(operation, error.message);
                get().clearPendingMedia();
                throw error;
            }
        },

        // NEW: Get storage files for media browser
        getStorageFiles: async (limit = 20, offset = 0) => {
            const operation = 'getStorageFiles';
            try {
                get().setLoading(operation, true);
                get().clearError(operation);
                
                const response = await apiClient.getStorageFiles(limit, offset);
                
                set(() => ({
                    storageFiles: {
                        files: response.files || [],
                        total: response.total || 0,
                        limit: response.limit || 20,
                        offset: response.offset || 0
                    }
                }));
                
                get().setLoading(operation, false);
                return response;
            } catch (error) {
                ErrorHandler.handleError(error, {
                    component: 'AppStore',
                    action: 'getStorageFiles',
                    limit,
                    offset
                });
                get().setError(operation, error.message);
                throw error;
            }
        },
        
        // Media tozalash
        clearPendingMedia: () => set(state => {
            if (state.pendingMedia.previewUrl) {
                URL.revokeObjectURL(state.pendingMedia.previewUrl);
            }
            return {
                pendingMedia: {
                    file_id: null,
                    file_type: null,
                    previewUrl: null,
                    uploadProgress: 0
                }
            };
        }),

        // Postni rejalashtirish
        schedulePost: async (postData) => {
            const operation = 'schedulePost';
            try {
                get().setLoading(operation, true);
                get().clearError(operation);
                
                const newPost = await apiClient.post('/schedule-post', postData);
                
                set(state => ({
                    scheduledPosts: [...state.scheduledPosts, newPost]
                        .sort((a, b) => new Date(a.schedule_time) - new Date(b.schedule_time))
                }));
                
                // Clear pending media after successful scheduling
                get().clearPendingMedia();
                
                get().setLoading(operation, false);
                return newPost;
            } catch (error) {
                ErrorHandler.handleError(error, {
                    component: 'AppStore',
                    action: 'schedulePost',
                    postData: JSON.stringify(postData)
                });
                get().setError(operation, error.message);
                throw error;
            }
        },

        // Rejalashtirilgan postni o'chirish
        deletePost: async (postId) => {
            const operation = 'deletePost';
            try {
                get().setLoading(operation, true);
                get().clearError(operation);
                
                await apiClient.delete(`/posts/${postId}`);
                
                set(state => ({
                    scheduledPosts: state.scheduledPosts.filter(post => post.id !== postId)
                }));
                
                get().setLoading(operation, false);
            } catch (error) {
                ErrorHandler.handleError(error, {
                    component: 'AppStore',
                    action: 'deletePost',
                    postId
                });
                get().setError(operation, error.message);
                throw error;
            }
        },

        // ANALYTICS METHODS - NEW for Phase 2.1 Week 2

        // Post dynamics ma'lumotlarini olish
        fetchPostDynamics: async (period = '24h') => {
            const operation = 'fetchPostDynamics';
            try {
                get().setLoading(operation, true);
                get().clearError(operation);
                
                const response = await apiClient.get(`/analytics/post-dynamics?period=${period}`);
                
                set(state => ({
                    analytics: {
                        ...state.analytics,
                        postDynamics: response,
                        lastAnalyticsUpdate: Date.now()
                    }
                }));
                
                get().setLoading(operation, false);
                return response;
            } catch (error) {
                ErrorHandler.handleError(error, {
                    component: 'AppStore',
                    action: 'fetchPostDynamics',
                    period
                });
                get().setError(operation, error.message);
                throw error;
            }
        },

        // Top posts ma'lumotlarini olish
        fetchTopPosts: async (period = 'today', sortBy = 'views') => {
            const operation = 'fetchTopPosts';
            try {
                get().setLoading(operation, true);
                get().clearError(operation);
                
                const response = await apiClient.get(`/analytics/top-posts?period=${period}&sort=${sortBy}`);
                
                set(state => ({
                    analytics: {
                        ...state.analytics,
                        topPosts: response.posts || [],
                        lastAnalyticsUpdate: Date.now()
                    }
                }));
                
                get().setLoading(operation, false);
                return response;
            } catch (error) {
                ErrorHandler.handleError(error, {
                    component: 'AppStore',
                    action: 'fetchTopPosts',
                    period,
                    sortBy
                });
                get().setError(operation, error.message);
                throw error;
            }
        },

        // Best time recommendations olish
        fetchBestTime: async (timeframe = 'week', contentType = 'all') => {
            const operation = 'fetchBestTime';
            try {
                get().setLoading(operation, true);
                get().clearError(operation);
                
                const response = await apiClient.get(`/analytics/best-posting-time?timeframe=${timeframe}&content_type=${contentType}`);
                
                set(state => ({
                    analytics: {
                        ...state.analytics,
                        bestTimeRecommendations: response,
                        lastAnalyticsUpdate: Date.now()
                    }
                }));
                
                get().setLoading(operation, false);
                return response;
            } catch (error) {
                ErrorHandler.handleError(error, {
                    component: 'AppStore',
                    action: 'fetchBestTime',
                    timeframe,
                    contentType
                });
                get().setError(operation, error.message);
                throw error;
            }
        },

        // Engagement metrics olish
        fetchEngagementMetrics: async (period = '7d') => {
            const operation = 'fetchEngagementMetrics';
            try {
                get().setLoading(operation, true);
                get().clearError(operation);
                
                const response = await apiClient.get(`/analytics/engagement?period=${period}`);
                
                set(state => ({
                    analytics: {
                        ...state.analytics,
                        engagementMetrics: response,
                        lastAnalyticsUpdate: Date.now()
                    }
                }));
                
                get().setLoading(operation, false);
                return response;
            } catch (error) {
                ErrorHandler.handleError(error, {
                    component: 'AppStore',
                    action: 'fetchEngagementMetrics',
                    period
                });
                get().setError(operation, error.message);
                throw error;
            }
        },

        // Analytics data'ni tozalash
        clearAnalyticsData: () => set(() => ({
            analytics: {
                postDynamics: null,
                topPosts: [],
                bestTimeRecommendations: null,
                engagementMetrics: null,
                lastAnalyticsUpdate: null
            }
        })),

        // Kanalni o'chirish
        deleteChannel: async (channelId) => {
            const operation = 'deleteChannel';
            try {
                get().setLoading(operation, true);
                get().clearError(operation);
                
                await apiClient.delete(`/channels/${channelId}`);
                
                set(state => ({
                    channels: state.channels.filter(channel => channel.id !== channelId)
                }));
                
                get().setLoading(operation, false);
            } catch (error) {
                ErrorHandler.handleError(error, {
                    component: 'AppStore',
                    action: 'deleteChannel',
                    channelId
                });
                get().setError(operation, error.message);
                throw error;
            }
        },

        // Selectors for easier access to loading states
        isLoading: (operation) => get().ui[operation]?.isLoading || false,
        getError: (operation) => get().ui[operation]?.error || null,
        isGlobalLoading: () => Object.values(get().ui).some(state => state.isLoading),
    }))
);

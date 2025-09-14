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
        // Data source configuration
        dataSource: localStorage.getItem('useRealAPI') === 'true' ? 'api' : 'mock',
        
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

        // Data source control methods
        setDataSource: (source) => {
            const previousSource = get().dataSource;
            set({ dataSource: source });
            localStorage.setItem('useRealAPI', source === 'api' ? 'true' : 'false');
            
            // If data source actually changed, dispatch event
            if (previousSource !== source) {
                setTimeout(() => {
                    window.dispatchEvent(new CustomEvent('dataSourceChanged', { 
                        detail: { source, previousSource } 
                    }));
                }, 100);
            }
        },
        
        // Check if using real API
        isUsingRealAPI: () => get().dataSource === 'api',
        
        // Boshlang'ich ma'lumotlarni backend'dan loading (with throttling)
        fetchData: async (forceSource = null) => {
            const operation = 'fetchData';
            const currentSource = forceSource || get().dataSource;
            const now = Date.now();
            
            // Throttle requests to prevent rapid successive calls
            const lastFetchKey = `lastFetch_${operation}`;
            const lastFetchTime = get()[lastFetchKey] || 0;
            const minInterval = 3000; // Minimum 3 seconds between fetchData requests
            
            if (now - lastFetchTime < minInterval && !forceSource) {
                console.log(`FetchData: Throttling request (last fetch ${now - lastFetchTime}ms ago)`);
                return;
            }
            
            // Update last fetch time immediately to prevent concurrent calls
            set(state => ({ ...state, [lastFetchKey]: now }));
            
            try {
                get().setLoading(operation, true);
                get().clearError(operation);
                
                let data;
                
                if (currentSource === 'api') {
                    try {
                        // Try real API first - correct endpoint
                        data = await apiClient.get('/initial-data');
                        console.log('✅ Successfully loaded data from real API');
                    } catch (apiError) {
                        console.log('⚠️ Real API unavailable');
                        console.log('API Error details:', apiError.message);
                        
                        // Store the error for user dialog instead of auto-switching
                        get().setError(operation, {
                            type: 'API_CONNECTION_FAILED',
                            message: apiError.message,
                            originalError: apiError,
                            timestamp: Date.now()
                        });
                        
                        // Don't auto-switch - let the UI handle this
                        throw apiError;
                    }
                } else {
                    // Use mock data directly
                    console.log('📊 Loading professional demo data');
                    const { mockService } = await import('../services/mockService.js');
                    data = await mockService.getInitialData();
                }
                
                set({
                    channels: data.channels || [],
                    scheduledPosts: data.scheduled_posts || [],
                    plan: data.plan,
                    user: data.user,
                });
                
                get().setLoading(operation, false);
            } catch (error) {
                // Fallback to basic demo data if everything fails
                console.warn('Error loading data:', error);
                set({
                    channels: [],
                    scheduledPosts: [],
                    plan: { name: "Demo", max_channels: 10 },
                    user: { username: "demo_user", first_name: "Demo" },
                });
                get().setLoading(operation, false);
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

        // Media loading
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

        // NEW: Get storage files for media browser (with fallback)
        getStorageFiles: async (limit = 20, offset = 0) => {
            const operation = 'getStorageFiles';
            const currentSource = get().dataSource;
            
            try {
                get().setLoading(operation, true);
                get().clearError(operation);
                
                let response;
                
                if (currentSource === 'api') {
                    try {
                        response = await apiClient.getStorageFiles(limit, offset);
                        console.log('✅ Storage files loaded from real API');
                    } catch (apiError) {
                        console.log('⚠️ API unavailable for storage files, using demo data');
                        console.log('Storage API Error:', apiError.message);
                        
                        // Fallback to mock storage files
                        const { mockService } = await import('../services/mockService.js');
                        response = await mockService.getStorageFiles(limit, offset);
                    }
                } else {
                    // Load from mock data
                    console.log('📊 Loading storage files demo data');
                    const { mockService } = await import('../services/mockService.js');
                    response = await mockService.getStorageFiles(limit, offset);
                }
                
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

        // Post dynamics datani getting with data source support (with throttling)
        fetchPostDynamics: async (period = '24h', channelId = 'demo_channel') => {
            const operation = 'fetchPostDynamics';
            const currentSource = get().dataSource;
            const now = Date.now();
            
            // Throttle requests to prevent rapid successive calls
            const lastFetchKey = `lastFetch_${operation}_${period}`;
            const lastFetchTime = get()[lastFetchKey] || 0;
            const minInterval = 2000; // Minimum 2 seconds between requests
            
            if (now - lastFetchTime < minInterval) {
                console.log(`PostDynamics: Throttling request (last fetch ${now - lastFetchTime}ms ago)`);
                return get().analytics?.postDynamics || [];
            }
            
            // Update last fetch time immediately to prevent concurrent calls
            set(state => ({ ...state, [lastFetchKey]: now }));
            
            try {
                get().setLoading(operation, true);
                get().clearError(operation);
                
                let response;
                
                if (currentSource === 'api') {
                    try {
                        // Use proper analytics v2 API with date range
                        const getPeriodDateRange = (periodDays) => {
                            const to = new Date();
                            const from = new Date();
                            from.setDate(from.getDate() - parseInt(periodDays.replace('h', '')) / 24);
                            return { from: from.toISOString(), to: to.toISOString() };
                        };
                        
                        const { from, to } = getPeriodDateRange(period);
                        response = await apiClient.get(`/api/v2/analytics/channels/${channelId}/post-dynamics?from=${from}&to=${to}`);
                        console.log('✅ Post dynamics loaded from real API');
                    } catch (apiError) {
                        console.log('⚠️ API unavailable for post dynamics, using demo data');
                        console.log('Analytics API Error:', apiError.message);
                        const { mockService } = await import('../services/mockService.js');
                        response = await mockService.getPostDynamics(channelId);
                    }
                } else {
                    // Load from mock data
                    console.log('📊 Loading post dynamics demo data');
                    const { mockService } = await import('../services/mockService.js');
                    response = await mockService.getPostDynamics(channelId);
                }
                
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
                    period,
                    dataSource: currentSource
                });
                get().setError(operation, error.message);
                throw error;
            }
        },

        // Top posts datani getting with data source support
        fetchTopPosts: async (channelId = 'demo_channel', period = 'today', sortBy = 'views') => {
            const operation = 'fetchTopPosts';
            const currentSource = get().dataSource;
            
            try {
                get().setLoading(operation, true);
                get().clearError(operation);
                
                let response;
                
                if (currentSource === 'api') {
                    try {
                        // Use proper analytics v2 API with date range
                        const getPeriodDateRange = (periodDays) => {
                            const periodMap = { 'today': 1, 'week': 7, 'month': 30 };
                            const days = periodMap[period] || 7;
                            const to = new Date();
                            const from = new Date();
                            from.setDate(from.getDate() - days);
                            return { from: from.toISOString(), to: to.toISOString() };
                        };
                        
                        const { from, to } = getPeriodDateRange(period);
                        response = await apiClient.get(`/api/v2/analytics/channels/${channelId}/top-posts?from=${from}&to=${to}&sort=${sortBy}`);
                        console.log('✅ Top posts loaded from real API');
                    } catch (apiError) {
                        console.log('⚠️ API unavailable for top posts, using demo data');
                        const { mockService } = await import('../services/mockService.js');
                        response = await mockService.getTopPosts(channelId, period, sortBy);
                    }
                } else {
                    // Load from mock data
                    console.log('📊 Loading top posts demo data');
                    const { mockService } = await import('../services/mockService.js');
                    response = await mockService.getTopPosts(channelId, period, sortBy);
                }
                
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
                    sortBy,
                    dataSource: currentSource
                });
                get().setError(operation, error.message);
                throw error;
            }
        },

        // Best time recommendations getting with data source support
        fetchBestTime: async (channelId = 'demo_channel', timeframe = 'week', contentType = 'all') => {
            const operation = 'fetchBestTime';
            const currentSource = get().dataSource;
            
            try {
                get().setLoading(operation, true);
                get().clearError(operation);
                
                let response;
                
                if (currentSource === 'api') {
                    try {
                        // Use proper analytics v2 API
                        response = await apiClient.get(`/api/v2/analytics/channels/${channelId}/best-times?timeframe=${timeframe}&content_type=${contentType}`);
                        console.log('✅ Best time recommendations loaded from real API');
                    } catch (apiError) {
                        console.log('⚠️ API unavailable for best time, using demo data');
                        const { mockService } = await import('../services/mockService.js');
                        response = await mockService.getBestTime(channelId);
                    }
                } else {
                    // Load from mock data
                    console.log('📊 Loading best time demo data');
                    const { mockService } = await import('../services/mockService.js');
                    response = await mockService.getBestTime(channelId);
                }
                
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
                    contentType,
                    dataSource: currentSource
                });
                get().setError(operation, error.message);
                throw error;
            }
        },

        // Engagement metrics getting with data source support
        fetchEngagementMetrics: async (period = '7d') => {
            const operation = 'fetchEngagementMetrics';
            const currentSource = get().dataSource;
            
            try {
                get().setLoading(operation, true);
                get().clearError(operation);
                
                let response;
                
                if (currentSource === 'api') {
                    try {
                        // Use proper analytics v2 API with date range
                        const getPeriodDateRange = (periodStr) => {
                            const days = parseInt(periodStr.replace('d', '')) || 7;
                            const to = new Date();
                            const from = new Date();
                            from.setDate(from.getDate() - days);
                            return { from: from.toISOString(), to: to.toISOString() };
                        };
                        
                        const { from, to } = getPeriodDateRange(period);
                        response = await apiClient.get(`/api/v2/analytics/channels/${channelId}/engagement?from=${from}&to=${to}`);
                        console.log('✅ Engagement metrics loaded from real API');
                    } catch (apiError) {
                        console.log('⚠️ API unavailable for engagement metrics, using demo data');
                        const { mockService } = await import('../services/mockService.js');
                        response = await mockService.getEngagementMetrics(channelId);
                    }
                } else {
                    // Load from mock data
                    console.log('📊 Loading engagement metrics demo data');
                    const { mockService } = await import('../services/mockService.js');
                    response = await mockService.getEngagementMetrics(channelId);
                }
                
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
                    period,
                    dataSource: currentSource
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

        // User-controlled data source switching methods
        switchToMockWithUserConsent: async () => {
            console.log('🔄 User approved switch to mock data');
            const previousSource = get().dataSource;
            
            // Switch to mock data source
            get().setDataSource('mock');
            
            // Clear any API errors since we're switching to mock
            get().clearError('fetchData');
            
            try {
                // Reload data with mock source
                await get().fetchData('mock');
                console.log('✅ Successfully switched to mock data');
                return true;
            } catch (error) {
                console.error('❌ Failed to load mock data:', error);
                // Revert to previous source if mock fails
                get().setDataSource(previousSource);
                throw error;
            }
        },

        retryApiConnection: async () => {
            console.log('🔄 User requested API retry');
            
            // Clear previous errors
            get().clearError('fetchData');
            
            try {
                // Force retry with API source
                await get().fetchData('api');
                console.log('✅ API connection retry successful');
                return true;
            } catch (error) {
                console.error('❌ API connection retry failed:', error);
                throw error;
            }
        },

        // Selectors for easier access to loading states
        isLoading: (operation) => get().ui[operation]?.isLoading || false,
        getError: (operation) => get().ui[operation]?.error || null,
        isGlobalLoading: () => Object.values(get().ui).some(state => state.isLoading),
    }))
);

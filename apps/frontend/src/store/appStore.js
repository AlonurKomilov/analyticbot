/**
 * ⚠️ DEPRECATED - DO NOT USE IN NEW CODE ⚠️
 *
 * This file has been deprecated as of October 17, 2025.
 * All components have been migrated to domain-specific stores.
 *
 * Migration completed: Phase 2.3 & 2.4 (37 files migrated)
 *
 * NEW STORE ARCHITECTURE:
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 * Instead of:  import { useAppStore } from './store/appStore'
 *
 * Use domain stores from: '@/stores'
 *
 * 📦 Available Stores:
 *   • useAuthStore       - User authentication & profile
 *   • useChannelStore    - Channel CRUD operations
 *   • usePostStore       - Post scheduling & management
 *   • useAnalyticsStore  - Analytics data fetching
 *   • useMediaStore      - Media upload management
 *   • useUIStore         - Global UI state
 *
 * 📚 Documentation:
 *   • See: DOMAIN_STORE_MIGRATION_COMPLETE.md
 *   • See: docs/STORE_MIGRATION_GUIDE.md
 *
 * This file is kept for reference only and will be removed
 * in the next major version. Archived backup available at:
 * archive/deprecated_store_phase2/appStore.js.backup
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 */

import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { apiClient } from '../api/client.js';
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
                        // Get current user info from /auth/me endpoint
                        const userData = await apiClient.get('/auth/me');
                        console.log('✅ Successfully loaded user data from API:', userData);

                        // Store user data in the app state
                        data = {
                            user: userData,
                            channels: [],
                            analytics: null
                        };
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
                    // Use unified analytics service
                    console.log('📊 Loading professional demo data');
                    const { analyticsService } = await import('../services/analyticsService.js');
                    data = await analyticsService.getAnalyticsOverview();
                }

                set({
                    channels: data.channels || [],
                    scheduledPosts: data.scheduled_posts || [],
                    plan: data.plan,
                    user: data.user,
                });

                get().setLoading(operation, false);
            } catch (error) {
                // Fallback to empty state if everything fails
                console.warn('Error loading data:', error);
                set({
                    channels: [],
                    scheduledPosts: [],
                    plan: { name: "Free", max_channels: 3 },
                    user: { username: "user", first_name: "User" },
                });
                get().setLoading(operation, false);
            }
        },

        // Validate Telegram channel
        validateChannel: async (username) => {
            const operation = 'validateChannel';
            try {
                get().setLoading(operation, true);
                get().clearError(operation);

                // Ensure username starts with @
                const channelUsername = username.startsWith('@') ? username : `@${username}`;

                console.log('🔍 Validating Telegram channel:', channelUsername);

                const validationResult = await apiClient.post('/analytics/channels/validate', {
                    username: channelUsername
                });

                get().setLoading(operation, false);

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
                    component: 'AppStore',
                    action: 'validateChannel',
                    username
                });
                get().setError(operation, error.message);
                get().setLoading(operation, false);
                return {
                    success: false,
                    error: error.message || 'Validation failed'
                };
            }
        },

        // Yangi kanal qo'shish (with Telegram validation)
        addChannel: async (channelUsername) => {
            const operation = 'addChannel';
            try {
                get().setLoading(operation, true);
                get().clearError(operation);

                // Clean username
                const cleanUsername = channelUsername.replace('@', '');
                const usernameWithAt = `@${cleanUsername}`;

                console.log('📺 Adding channel:', usernameWithAt);

                // Step 1: Validate with Telegram API first
                const validation = await get().validateChannel(usernameWithAt);

                if (!validation.success) {
                    throw new Error(validation.error || 'Channel validation failed');
                }

                console.log('✅ Channel validated, creating in database...');

                // Step 2: Create channel with real Telegram data
                const newChannel = await apiClient.post('/channels', {
                    name: validation.data.title || cleanUsername,
                    telegram_id: validation.data.telegram_id,
                    description: validation.data.description || `Channel ${validation.data.title || cleanUsername}`
                });

                console.log('✅ Channel created successfully:', newChannel);

                set((state) => ({
                    channels: [...state.channels, newChannel]
                }));

                get().setLoading(operation, false);
                return newChannel;
            } catch (error) {
                console.error('❌ Add channel error:', error);
                ErrorHandler.handleError(error, {
                    component: 'AppStore',
                    action: 'addChannel',
                    channelUsername
                });
                get().setError(operation, error.message);
                get().setLoading(operation, false);
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
                    // Real API mode - NEVER fallback to mock data
                    response = await apiClient.getStorageFiles(limit, offset);
                    console.log('✅ Storage files loaded from real API');
                    // If API fails, error will be thrown and caught below - NO fallback to demo
                } else {
                    // Load from mock data
                    console.log('📊 Loading storage files demo data');
                    const { storageMockService } = await import('../services/storageMockService.js');
                    response = await storageMockService.getStorageFiles(limit, offset);
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

                await apiClient.delete(`/schedule/${postId}`);

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
                    // Real API mode - NEVER fallback to mock/demo data
                    // Note: analytics/post-dynamics endpoint uses period parameter (24h, 7d, etc.)
                    // not from/to dates
                    response = await apiClient.get(`/analytics/post-dynamics/${channelId}?period=${period}`);
                    console.log('✅ Post dynamics loaded from real API');
                    // If API fails, error will be thrown and caught below - NO fallback to demo
                } else{
                    // Demo mode - use mock data from analytics service
                    console.log('📊 Loading post dynamics demo data');
                    const { analyticsService } = await import('../services/analyticsService.js');
                    response = await analyticsService.getPostDynamics(channelId);
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
                    // Real API mode - NEVER fallback to mock/demo data
                    const getPeriodDateRange = (periodDays) => {
                        const periodMap = { 'today': 1, 'week': 7, 'month': 30 };
                        const days = periodMap[period] || 7;
                        const to = new Date();
                        const from = new Date();
                        from.setDate(from.getDate() - days);
                        return { from: from.toISOString(), to: to.toISOString() };
                    };

                    response = await apiClient.get(`/analytics/top-posts/${channelId}?period=${period}&sort=${sortBy}`);
                    console.log('✅ Top posts loaded from real API');
                    // If API fails, error will be thrown and caught below - NO fallback to demo
                } else {
                    // Demo mode - use mock data from analytics service
                    console.log('📊 Loading top posts demo data');
                    const { analyticsService } = await import('../services/analyticsService.js');
                    response = await analyticsService.getTopPosts(channelId, period, sortBy);
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
                let normalizedData;

                if (currentSource === 'api') {
                    // Real API mode - NEVER fallback to mock/demo data
                    // Convert demo_channel string to numeric ID for API
                    const numericChannelId = channelId === 'demo_channel' ? 1 : parseInt(channelId) || 1;
                    response = await apiClient.get(`/insights/predictive/best-times/${numericChannelId}?timeframe=${timeframe}&content_type=${contentType}`);
                    console.log('✅ Best time recommendations loaded from real API');

                    // Normalize real API response: {success, channel_id, data, ...} -> consistent format
                    normalizedData = {
                        success: response.success,
                        best_times: response.data?.best_times || response.data?.optimal_times || [],
                        recommendations: response.data?.recommendations || response.data,
                        optimal_times: response.data?.optimal_times || [],
                        analysis_type: response.analysis_type,
                        generated_at: response.generated_at
                    };
                } else {
                    // Demo mode - use backend demo endpoint
                    console.log('📊 Loading best time demo data from backend demo endpoint');
                    response = await apiClient.get(`/demo/analytics/best-times?channel_id=1&timezone=UTC`);

                    // Normalize demo API response: {success, recommendations, optimal_times, ...} -> consistent format
                    normalizedData = {
                        success: response.success,
                        best_times: response.optimal_times || [],
                        recommendations: response.recommendations,
                        optimal_times: response.optimal_times || [],
                        demo_info: response.demo_info
                    };
                }

                set(state => ({
                    analytics: {
                        ...state.analytics,
                        bestTimeRecommendations: normalizedData,
                        lastAnalyticsUpdate: Date.now()
                    }
                }));

                get().setLoading(operation, false);
                return normalizedData;
            } catch (error) {
                // Don't fallback to demo - respect user's data source choice
                console.error('❌ Failed to load best time recommendations:', error.message);

                ErrorHandler.handleError(error, {
                    component: 'AppStore',
                    action: 'fetchBestTime',
                    timeframe,
                    contentType,
                    dataSource: currentSource
                });

                get().setLoading(operation, false);
                get().setError(operation, error.message);

                // Return null so component can show "No Data" message
                return null;
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
                    // Real API mode - NEVER fallback to mock/demo data
                    const getPeriodDateRange = (periodStr) => {
                        const days = parseInt(periodStr.replace('d', '')) || 7;
                        const to = new Date();
                        const from = new Date();
                        from.setDate(from.getDate() - days);
                        return { from: from.toISOString(), to: to.toISOString() };
                    };

                    response = await apiClient.get(`/insights/engagement/channels/${channelId}/engagement?period=${period}`);
                    console.log('✅ Engagement metrics loaded from real API');
                    // If API fails, error will be thrown and caught below - NO fallback to demo
                } else {
                    // Demo mode - use mock data from analytics service
                    console.log('📊 Loading engagement metrics demo data');
                    const { analyticsService } = await import('../services/analyticsService.js');
                    response = await analyticsService.getEngagementMetrics(channelId);
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

        // No longer allow switching to mock - redirect to demo login instead
        switchToMockWithUserConsent: async () => {
            console.log('❌ Frontend mock switching disabled - redirecting to demo login');

            // Redirect to demo login instead of switching to frontend mock
            const demoLoginUrl = `/login?demo=true&redirect=${encodeURIComponent(window.location.pathname)}`;
            window.location.href = demoLoginUrl;

            return false; // No switch occurred
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

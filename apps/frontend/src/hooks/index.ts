import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { useMediaStore, useUIStore } from '@store';

/**
 * ⚠️ MIGRATION IN PROGRESS - Phase 3 Task 1.4
 * Hooks have been reorganized into feature-specific and shared directories.
 * This file now re-exports hooks from their new locations for backward compatibility.
 * 
 * New structure:
 * - features/admin/hooks/ - Admin-specific hooks
 * - features/analytics/hooks/ - Analytics hooks
 * - features/ai-services/hooks/ - AI service hooks
 * - features/protection/hooks/ - Content protection hooks
 * - features/alerts/hooks/ - Alert system hooks
 * - shared/hooks/ - Shared utility hooks
 */

// ============================================================================
// FEATURE-SPECIFIC HOOKS (re-exported for backward compatibility)
// ============================================================================

// Admin hooks
export { useAdminAPI, useAdminDashboard } from '@features/admin/hooks';
export type {
    UseAdminAPIReturn,
    UseAdminDashboardReturn,
    AdminStats,
    AdminUser,
    AuditLog
} from '@features/admin/hooks';

// Analytics hooks
export { 
    useUnifiedAnalytics, 
    ANALYTICS_PRESETS,
    useDashboardAnalytics,
    useAdminAnalytics,
    useMobileAnalytics,
    usePerformanceAnalytics,
    useHighFrequencyAnalytics,
    useRealTimeAnalytics,
    useRealTimeAnalyticsHook,
    useQuickAnalytics,
    usePerformanceMetrics
} from '@features/analytics/hooks';
export type {
    UseUnifiedAnalyticsReturn,
    AnalyticsPresetType,
    AnalyticsConfig,
    ConnectionStatus,
    AnalyticsData,
    DashboardData,
    AdminData,
    MobileData,
    PerformanceData,
    RealTimeData,
    UseRealTimeAnalyticsReturn,
    UseQuickAnalyticsReturn,
    UsePerformanceMetricsReturn,
    RealTimeAnalyticsOptions
} from '@features/analytics/hooks';

// AI Services hooks
export { useContentOptimizer } from '@features/ai-services/hooks';
export { usePredictiveAnalytics } from '@features/ai-services/hooks';
export type {
    UsePredictiveAnalyticsReturn,
    UsePredictiveAnalyticsOptions
} from '@features/ai-services/hooks';
export { useSecurityMonitoring } from '@features/ai-services/hooks';

// Protection hooks
export { useContentProtection } from '@features/protection/hooks';

// Alerts hooks
export { useAlerts } from '@features/alerts/hooks';
export type {
    UseAlertsReturn,
    UseAlertsOptions
} from '@features/alerts/hooks';

// ============================================================================
// SHARED HOOKS (re-exported for backward compatibility)
// ============================================================================

export {
    useDataSource,
    useAnalytics,
    useTopPosts,
    useEngagementMetrics,
    useRecommendations,
    useAllAnalytics,
    useAuthenticatedDataProvider,
    useAuthenticatedAnalytics,
    useAuthenticatedTopPosts,
    useAuthenticatedEngagementMetrics,
    useAuthenticatedRecommendations,
    useAuthenticatedDataSourceStatus,
    useAuthenticatedDataSource,
    useUserChannels,
    useSelectedChannel,
    useChannelAccess,
    useEnhancedResponsive,
    useSwipeGesture,
    useMobileDrawer,
    useTouchFriendlyButton,
    useResponsiveGrid,
    useMobileSpacing,
    useAdaptiveTypography,
    useOrientationChange,
    useApiFailureDialog
} from '@shared/hooks';
export type {
    UseDataSourceReturn,
    UseAnalyticsReturn,
    DataProvider,
    UseUserChannelsReturn,
    UseSelectedChannelReturn,
    UseChannelAccessReturn,
    Channel,
    DeviceType,
    ResponsiveConfig,
    SwipeGestureOptions,
    UseApiFailureDialogReturn,
    APIError
} from '@shared/hooks';

// ============================================================================
// INLINE UTILITY HOOKS (keeping here for simplicity)
// ============================================================================

/**
 * Loading state return type
 */
export interface UseLoadingStateReturn {
    loading: boolean;
    debouncedLoading: boolean;
    error: string | null;
    clearError: () => void;
}

/**
 * Custom hook for managing loading states with debouncing
 */
export const useLoadingState = (_operation?: string, delay: number = 300): UseLoadingStateReturn => {
    const [debouncedLoading, setDebouncedLoading] = useState<boolean>(false);
    const { isGlobalLoading } = useUIStore();
    const timeoutRef = useRef<NodeJS.Timeout | undefined>(undefined);

    const loading = isGlobalLoading;
    const error = null; // Error handling moved to individual stores

    useEffect(() => {
        if (timeoutRef.current) {
            clearTimeout(timeoutRef.current);
        }

        if (loading) {
            setDebouncedLoading(true);
        } else {
            timeoutRef.current = setTimeout(() => {
                setDebouncedLoading(false);
            }, delay);
        }

        return () => {
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
            }
        };
    }, [loading, delay]);

    const clearOperationError = useCallback(() => {
        // Error clearing moved to individual stores
        // This is a no-op for now
    }, []);

    return {
        loading,
        debouncedLoading,
        error,
        clearError: clearOperationError
    };
};

/**
 * Form state return type
 */
export interface UseFormStateReturn<T> {
    state: T;
    errors: Record<string, string | undefined>;
    touched: Record<string, boolean>;
    updateField: (field: keyof T, value: any) => void;
    validateForm: () => boolean;
    resetForm: () => void;
    isValid: boolean;
}

/**
 * Custom hook for form handling with validation
 */
export const useFormState = <T extends Record<string, any>>(
    initialState: T,
    validator?: (state: T) => Record<string, string | undefined>
): UseFormStateReturn<T> => {
    const [state, setState] = useState<T>(initialState);
    const [errors, setErrors] = useState<Record<string, string | undefined>>({});
    const [touched, setTouched] = useState<Record<string, boolean>>({});

    const updateField = useCallback((field: keyof T, value: any): void => {
        setState(prev => {
            const newState = { ...prev, [field]: value };
            
            // Run validation with new state if validator exists
            if (validator) {
                const fieldErrors = validator(newState);
                setErrors(prevErrors => ({ ...prevErrors, [field as string]: fieldErrors[field as string] }));
            }
            
            return newState;
        });
        setTouched(prev => ({ ...prev, [field as string]: true }));
    }, [validator]);

    const validateForm = useCallback((): boolean => {
        if (!validator) return true;

        const formErrors = validator(state);
        setErrors(formErrors);

        return Object.keys(formErrors).length === 0;
    }, [state, validator]);

    const resetForm = useCallback((): void => {
        setState(initialState);
        setErrors({});
        setTouched({});
    }, [initialState]);

    return {
        state,
        errors,
        touched,
        updateField,
        validateForm,
        resetForm,
        isValid: Object.keys(errors).length === 0
    };
};

/**
 * Optimized list return type
 */
export interface UseOptimizedListReturn<T> {
    items: T[];
    itemsMap: Record<string, T>;
    sortedItems: T[];
    getItem: (key: string) => T | undefined;
    count: number;
}

/**
 * Custom hook for optimized list operations
 */
export const useOptimizedList = <T>(
    items: T[],
    keyExtractor: (item: T) => string
): UseOptimizedListReturn<T> => {
    const itemsMap = useMemo(() => {
        return items.reduce((map, item) => {
            map[keyExtractor(item)] = item;
            return map;
        }, {} as Record<string, T>);
    }, [items, keyExtractor]);

    const getItem = useCallback((key: string): T | undefined => itemsMap[key], [itemsMap]);

    const sortedItems = useMemo(() => {
        return [...items].sort((a, b) => {
            const aKey = keyExtractor(a);
            const bKey = keyExtractor(b);
            return aKey.localeCompare(bKey);
        });
    }, [items, keyExtractor]);

    return {
        items,
        itemsMap,
        sortedItems,
        getItem,
        count: items.length
    };
};

/**
 * Media upload return type
 */
export interface UseMediaUploadReturn {
    handleUpload: (file: File, channelId?: string | null) => Promise<any>;
    handleUploadWithProgress: (file: File, channelId?: string | null, onProgress?: ((progress: number) => void) | null) => Promise<any>;
    uploadProgress: number;
    pendingMedia: any;
    clearPendingMedia: () => void;
    loading: boolean;
    error: string | null;
    uploadSpeed: number;
    uploadType: string;
    metadata: Record<string, any>;
}

/**
 * Custom hook for managing media uploads (Enhanced for TWA Phase 2.1)
 */
export const useMediaUpload = (): UseMediaUploadReturn => {
    const { uploadMedia, pendingMedia, clearPendingMedia } = useMediaStore();
    const [uploadProgress, setUploadProgress] = useState<number>(0);
    const loading = useMediaStore(state => state.isUploading);
    const error = useMediaStore(state => state.error);

    // Enhanced upload handler with direct upload support
    const handleUpload = useCallback(async (file: File, channelId: string | null = null): Promise<any> => {
        if (!file) return;

        // Validate file
        const maxSize = 50 * 1024 * 1024; // 50MB
        const allowedTypes = [
            'image/jpeg', 'image/png', 'image/gif', 'image/webp',
            'video/mp4', 'video/webm', 'video/mov',
            'application/pdf', 'text/plain'
        ];

        if (file.size > maxSize) {
            throw new Error('File size must be less than 50MB');
        }

        if (!allowedTypes.includes(file.type)) {
            throw new Error('File type not supported');
        }

        setUploadProgress(0);

        // Upload with optional channel ID in metadata
        return uploadMedia(file, channelId ? { channelId } : {});
    }, [uploadMedia]);

    // Enhanced upload with progress tracking
    const handleUploadWithProgress = useCallback(async (
        file: File,
        channelId: string | null = null,
        onProgress: ((progress: number) => void) | null = null
    ): Promise<any> => {
        if (!file) return;

        try {
            const result = await handleUpload(file, channelId);

            // Update progress state if callback provided and media exists
            if (onProgress && pendingMedia?.uploadProgress !== undefined) {
                setUploadProgress(pendingMedia.uploadProgress);
                onProgress(pendingMedia.uploadProgress);
            }

            return result;
        } catch (error) {
            setUploadProgress(0);
            throw error;
        }
    }, [handleUpload, pendingMedia?.uploadProgress]);

    useEffect(() => {
        setUploadProgress(pendingMedia?.uploadProgress || 0);
    }, [pendingMedia?.uploadProgress]);

    return {
        handleUpload,
        handleUploadWithProgress,
        uploadProgress,
        pendingMedia,
        clearPendingMedia,
        loading,
        error,
        // Enhanced metadata (with null safety)
        uploadSpeed: 0, // Not available in current PendingMedia type
        uploadType: 'storage', // Default type
        metadata: {} // Not available in current PendingMedia type
    };
};/**
 * Telegram WebApp type
 */
export interface TelegramWebApp {
    ready: () => void;
    expand: () => void;
    showAlert: (message: string) => void;
    showConfirm: (message: string, callback: (result: boolean) => void) => void;
    HapticFeedback?: {
        impactOccurred: (style: 'light' | 'medium' | 'heavy') => void;
        notificationOccurred: (type: 'error' | 'success' | 'warning') => void;
    };
    initDataUnsafe?: {
        user?: any;
    };
    colorScheme?: 'light' | 'dark';
}

/**
 * Telegram WebApp return type
 */
export interface UseTelegramWebAppReturn {
    webApp: TelegramWebApp | null;
    isReady: boolean;
    showAlert: (message: string) => void;
    showConfirm: (message: string) => Promise<boolean>;
    hapticFeedback: (type?: 'light' | 'medium' | 'heavy' | 'success' | 'error') => void;
    user: any;
    theme: 'light' | 'dark';
}

/**
 * Custom hook for Telegram Web App integration
 */
export const useTelegramWebApp = (): UseTelegramWebAppReturn => {
    const [webApp, setWebApp] = useState<TelegramWebApp | null>(null);
    const [isReady, setIsReady] = useState<boolean>(false);

    useEffect(() => {
        const tg = (window as any).Telegram?.WebApp as TelegramWebApp | undefined;

        if (tg) {
            // Initialize Telegram Web App
            tg.ready();
            tg.expand();

            // Set theme
            if (tg.colorScheme === 'dark') {
                document.body.setAttribute('data-theme', 'dark');
            }

            setWebApp(tg);
            setIsReady(true);
        } else {
            console.warn('Telegram Web App not available');
        }
    }, []);

    const showAlert = useCallback((message: string): void => {
        if (webApp) {
            webApp.showAlert(message);
        } else {
            alert(message);
        }
    }, [webApp]);

    const showConfirm = useCallback((message: string): Promise<boolean> => {
        return new Promise((resolve) => {
            if (webApp) {
                webApp.showConfirm(message, resolve);
            } else {
                resolve(confirm(message));
            }
        });
    }, [webApp]);

    const hapticFeedback = useCallback((type: 'light' | 'medium' | 'heavy' | 'success' | 'error' = 'medium'): void => {
        if (webApp?.HapticFeedback) {
            switch (type) {
                case 'light':
                    webApp.HapticFeedback.impactOccurred('light');
                    break;
                case 'medium':
                    webApp.HapticFeedback.impactOccurred('medium');
                    break;
                case 'heavy':
                    webApp.HapticFeedback.impactOccurred('heavy');
                    break;
                case 'success':
                    webApp.HapticFeedback.notificationOccurred('success');
                    break;
                case 'error':
                    webApp.HapticFeedback.notificationOccurred('error');
                    break;
                default:
                    webApp.HapticFeedback.impactOccurred('medium');
            }
        }
    }, [webApp]);

    return {
        webApp,
        isReady,
        showAlert,
        showConfirm,
        hapticFeedback,
        user: webApp?.initDataUnsafe?.user,
        theme: webApp?.colorScheme || 'light'
    };
};

/**
 * Shared Hooks
 * Reusable React hooks - General purpose utilities
 */

// Data source hooks
export { useDataSource, useAnalytics, useTopPosts, useEngagementMetrics, useRecommendations, useAllAnalytics } from './useDataSource';
export type {
    UseDataSourceReturn,
    UseAnalyticsReturn,
    DataProvider
} from './useDataSource';

export {
    useAuthenticatedDataProvider,
    useAuthenticatedAnalytics,
    useAuthenticatedTopPosts,
    useAuthenticatedEngagementMetrics,
    useAuthenticatedRecommendations,
    useAuthenticatedDataSourceStatus,
    useAuthenticatedDataSource
} from './useAuthenticatedDataSource';

// Channel hooks
export { useUserChannels, useSelectedChannel, useChannelAccess } from './useUserChannels';
export type {
    UseUserChannelsReturn,
    UseSelectedChannelReturn,
    UseChannelAccessReturn,
    Channel
} from './useUserChannels';

// Responsive & mobile hooks
export {
    useEnhancedResponsive,
    useSwipeGesture,
    useMobileDrawer,
    useTouchFriendlyButton,
    useResponsiveGrid,
    useMobileSpacing,
    useAdaptiveTypography,
    useOrientationChange
} from './useMobileResponsive';
export type {
    DeviceType,
    ResponsiveConfig,
    SwipeGestureOptions
} from './useMobileResponsive';

// API & error handling hooks
export { useApiFailureDialog } from './useApiFailureDialog';
export type {
    UseApiFailureDialogReturn,
    APIError
} from './useApiFailureDialog';

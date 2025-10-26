// Analytics hooks - Re-exported from feature
export { useUnifiedAnalytics, ANALYTICS_PRESETS } from './useUnifiedAnalytics';
export type {
    UseUnifiedAnalyticsReturn,
    AnalyticsPresetType,
    AnalyticsConfig,
    ConnectionStatus,
    AnalyticsData
} from './useUnifiedAnalytics';

export {
    useDashboardAnalytics,
    useAdminAnalytics,
    useMobileAnalytics,
    usePerformanceAnalytics,
    useHighFrequencyAnalytics,
    useRealTimeAnalytics
} from './useSpecializedAnalytics';
export type {
    DashboardData,
    AdminData,
    MobileData,
    PerformanceData,
    RealTimeData
} from './useSpecializedAnalytics';

export { useRealTimeAnalytics as useRealTimeAnalyticsHook, useQuickAnalytics, usePerformanceMetrics } from './useRealTimeAnalytics';
export type {
    UseRealTimeAnalyticsReturn,
    UseQuickAnalyticsReturn,
    UsePerformanceMetricsReturn,
    RealTimeAnalyticsOptions
} from './useRealTimeAnalytics';

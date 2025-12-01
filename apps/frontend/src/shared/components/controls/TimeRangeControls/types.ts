/**
 * TimeRangeControls Types
 * Unified type definitions for time range controls
 */

export type TimeRange = '1h' | '6h' | '12h' | '24h' | '7d' | '14d' | '30d' | '90d' | 'all';
export type RefreshInterval = '30s' | '1m' | '5m' | '10m' | 'disabled';
export type MetricFilter = 'all' | 'views' | 'reactions' | 'forwards' | 'comments';

/**
 * Full-featured TimeRangeControls props
 * Used for advanced analytics dashboards with refresh and metric filtering
 */
export interface AdvancedTimeRangeControlsProps {
    /** Current time range value */
    timeRange?: TimeRange;
    /** Current refresh interval value */
    refreshInterval?: RefreshInterval;
    /** Current metric filter value */
    metricFilter?: MetricFilter;
    /** Time range change handler */
    onTimeRangeChange: (value: TimeRange) => void;
    /** Refresh interval change handler */
    onRefreshIntervalChange?: (value: RefreshInterval) => void;
    /** Metric filter change handler */
    onMetricFilterChange?: (value: MetricFilter) => void;
    /** If true, hides the refresh interval selector */
    hideRefreshControl?: boolean;
    /** If true, hides the metric filter selector */
    hideMetricFilter?: boolean;
}

/**
 * Simple TimeRangeControls props
 * Used for basic time range selection (TrendsChart style)
 */
export interface SimpleTimeRangeControlsProps {
    /** Current time range value */
    timeRange: string;
    /** Callback when time range changes */
    onTimeRangeChange: (value: string) => void;
    /** Available time range options */
    options?: Array<{ value: string; label: string }>;
}

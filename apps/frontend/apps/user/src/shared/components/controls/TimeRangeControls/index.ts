/**
 * TimeRangeControls - Unified time range controls module
 *
 * Provides both simple and advanced time range controls:
 * - SimpleTimeRangeControls: Basic dropdown for time range selection
 * - AdvancedTimeRangeControls: Full-featured with refresh interval and metric filtering
 *
 * @example
 * ```tsx
 * // Simple usage
 * import { SimpleTimeRangeControls } from '@shared/components/controls';
 * <SimpleTimeRangeControls timeRange="7d" onTimeRangeChange={handleChange} />
 *
 * // Advanced usage
 * import { AdvancedTimeRangeControls } from '@shared/components/controls';
 * <AdvancedTimeRangeControls
 *   timeRange="24h"
 *   onTimeRangeChange={handleTimeChange}
 *   onRefreshIntervalChange={handleRefresh}
 * />
 * ```
 */

export { default as SimpleTimeRangeControls } from './SimpleTimeRangeControls';
export { default as AdvancedTimeRangeControls } from './AdvancedTimeRangeControls';
export * from './types';

// Default export for backward compatibility
export { default } from './AdvancedTimeRangeControls';

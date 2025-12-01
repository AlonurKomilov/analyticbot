/**
 * TimeRangeControls - Re-export from shared controls
 * 
 * This module re-exports the AdvancedTimeRangeControls for backward compatibility.
 * 
 * @deprecated Import from '@shared/components/controls' instead
 */

import { AdvancedTimeRangeControls } from '@shared/components/controls';
export type { TimeRange, RefreshInterval, MetricFilter } from '@shared/components/controls';

export default AdvancedTimeRangeControls;

import React from 'react';
import { FormControl, Select, MenuItem, SelectChangeEvent } from '@mui/material';

interface TimeRangeControlsProps {
  /** Current selected time range value */
  timeRange: string;
  /** Callback fired when time range selection changes */
  onTimeRangeChange: (value: string) => void;
}

/**
 * TimeRangeControls - Dropdown selector for choosing time range periods
 *
 * @component
 * @example
 * ```tsx
 * <TimeRangeControls
 *   timeRange="7d"
 *   onTimeRangeChange={(range) => console.log(range)}
 * />
 * ```
 */
const TimeRangeControls: React.FC<TimeRangeControlsProps> = React.memo(({
  timeRange,
  onTimeRangeChange
}) => {
    const handleChange = (e: SelectChangeEvent<string>) => {
        onTimeRangeChange(e.target.value);
    };

    return (
        <FormControl size="small" sx={{ minWidth: 80 }}>
            <Select
                value={timeRange}
                onChange={handleChange}
                displayEmpty
            >
                <MenuItem value="7d">7D</MenuItem>
                <MenuItem value="14d">14D</MenuItem>
                <MenuItem value="30d">30D</MenuItem>
            </Select>
        </FormControl>
    );
});

TimeRangeControls.displayName = 'TimeRangeControls';

export default TimeRangeControls;

/**
 * SimpleTimeRangeControls - Basic time range dropdown
 *
 * Used for simple time range selection with customizable options.
 *
 * @example
 * ```tsx
 * <SimpleTimeRangeControls
 *   timeRange="7d"
 *   onTimeRangeChange={(range) => setTimeRange(range)}
 * />
 * ```
 */

import React from 'react';
import { FormControl, Select, MenuItem, SelectChangeEvent } from '@mui/material';
import type { SimpleTimeRangeControlsProps } from './types';

const DEFAULT_OPTIONS = [
    { value: '7d', label: '7D' },
    { value: '14d', label: '14D' },
    { value: '30d', label: '30D' }
];

const SimpleTimeRangeControls: React.FC<SimpleTimeRangeControlsProps> = React.memo(({
    timeRange,
    onTimeRangeChange,
    options = DEFAULT_OPTIONS
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
                {options.map(option => (
                    <MenuItem key={option.value} value={option.value}>
                        {option.label}
                    </MenuItem>
                ))}
            </Select>
        </FormControl>
    );
});

SimpleTimeRangeControls.displayName = 'SimpleTimeRangeControls';

export default SimpleTimeRangeControls;

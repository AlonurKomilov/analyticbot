import React from 'react';
import { FormControl, Select, MenuItem } from '@mui/material';

const TimeRangeControls = React.memo(({ timeRange, onTimeRangeChange }) => {
    return (
        <FormControl size="small" sx={{ minWidth: 80 }}>
            <Select
                value={timeRange}
                onChange={(e) => onTimeRangeChange(e.target.value)}
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
import React from 'react';
import {
    Box,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Typography,
    SelectChangeEvent
} from '@mui/material';
import { Psychology as AIIcon } from '@mui/icons-material';

/**
 * Time frame options
 */
export type TimeFrame = 'hour' | '6hours' | '24hours' | '7days' | '30days' | '90days' | 'alltime';

/**
 * Content type options
 */
export type ContentType = 'all' | 'text' | 'image' | 'video' | 'poll';

/**
 * Props for TimeFrameFilters component
 */
interface TimeFrameFiltersProps {
    /** Selected time frame */
    timeFrame: TimeFrame;
    /** Callback to update time frame */
    setTimeFrame: (timeFrame: TimeFrame) => void;
    /** Selected content type */
    contentType: ContentType;
    /** Callback to update content type */
    setContentType: (contentType: ContentType) => void;
}

/**
 * TimeFrameFilters Component
 * Filter controls for AI posting time recommendations
 */
const TimeFrameFilters: React.FC<TimeFrameFiltersProps> = ({
    timeFrame,
    setTimeFrame
}) => {
    const handleTimeFrameChange = (event: SelectChangeEvent) => {
        setTimeFrame(event.target.value as TimeFrame);
    };

    return (
        <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <AIIcon color="primary" />
                <Typography variant="h5" component="h1">
                    📊 Performance Time Recommendations
                </Typography>
            </Box>

            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <FormControl size="small" sx={{ minWidth: 200 }}>
                    <InputLabel id="timeframe-label">Analysis Period</InputLabel>
                    <Select
                        labelId="timeframe-label"
                        value={timeFrame}
                        label="Analysis Period"
                        onChange={handleTimeFrameChange}
                    >
                        <MenuItem value="hour">Last Hour</MenuItem>
                        <MenuItem value="6hours">Last 6 Hours</MenuItem>
                        <MenuItem value="24hours">Last 24 Hours</MenuItem>
                        <MenuItem value="7days">Last 7 Days</MenuItem>
                        <MenuItem value="30days">Last 30 Days</MenuItem>
                        <MenuItem value="90days">Last 90 Days</MenuItem>
                        <MenuItem value="alltime">All Time</MenuItem>
                    </Select>
                </FormControl>
            </Box>
        </Box>
    );
};

export default TimeFrameFilters;

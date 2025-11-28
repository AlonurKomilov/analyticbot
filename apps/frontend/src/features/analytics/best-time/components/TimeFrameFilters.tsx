import React from 'react';
import {
    Box,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Typography,
    SelectChangeEvent,
    Chip
} from '@mui/material';
import { Psychology as AIIcon } from '@mui/icons-material';

/**
 * Time frame options (standardized format)
 */
export type TimeFrame = '1h' | '6h' | '24h' | '7d' | '30d' | '90d' | '180d' | '1y' | 'all';

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
                    📊 Special Times Recommender
                </Typography>
            </Box>

            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
                <FormControl size="small" sx={{ minWidth: 200 }}>
                    <InputLabel id="timeframe-label">Analysis Period</InputLabel>
                    <Select
                        labelId="timeframe-label"
                        value={timeFrame}
                        label="Analysis Period"
                        onChange={handleTimeFrameChange}
                    >
                        <MenuItem value="1h">Last Hour</MenuItem>
                        <MenuItem value="6h">Last 6 Hours</MenuItem>
                        <MenuItem value="24h">Last 24 Hours</MenuItem>
                        <MenuItem value="7d">Last 7 Days</MenuItem>
                        <MenuItem value="30d">Last 30 Days</MenuItem>
                        <MenuItem value="90d">Last 90 Days</MenuItem>
                        <MenuItem value="180d">Last 6 Months</MenuItem>
                        <MenuItem value="1y">Last Year</MenuItem>
                        <MenuItem value="all">All Time</MenuItem>
                    </Select>
                </FormControl>
                {timeFrame === 'all' && (
                    <Chip
                        label="Analyzing complete history (up to 10k posts)"
                        color="primary"
                        size="small"
                        sx={{ fontWeight: 500 }}
                    />
                )}
                {timeFrame === '1y' && (
                    <Chip
                        label="Last 365 days"
                        color="info"
                        size="small"
                    />
                )}
            </Box>
        </Box>
    );
};

export default TimeFrameFilters;

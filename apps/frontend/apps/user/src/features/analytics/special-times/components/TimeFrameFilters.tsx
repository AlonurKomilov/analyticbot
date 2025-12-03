import React from 'react';
import {
    Box,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    SelectChangeEvent,
    Chip
} from '@mui/material';

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
    /** Total posts analyzed */
    totalPostsAnalyzed?: number;
    /** Content type breakdown */
    contentTypeBreakdown?: {
        text?: number;
        video?: number;
        image?: number;
        link?: number;
    };
}

/**
 * TimeFrameFilters Component
 * Filter controls for AI posting time recommendations
 */
const TimeFrameFilters: React.FC<TimeFrameFiltersProps> = ({
    timeFrame,
    setTimeFrame,
    totalPostsAnalyzed,
    contentTypeBreakdown
}) => {
    const handleTimeFrameChange = (event: SelectChangeEvent) => {
        setTimeFrame(event.target.value as TimeFrame);
    };

    return (
        <Box sx={{ mb: 3 }}>
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
                {totalPostsAnalyzed !== undefined && totalPostsAnalyzed > 0 && (
                    <Chip
                        label={`${totalPostsAnalyzed.toLocaleString()} posts analyzed${
                            contentTypeBreakdown
                                ? ` (Text: ${contentTypeBreakdown.text || 0}, Video: ${contentTypeBreakdown.video || 0}, Image: ${contentTypeBreakdown.image || 0}, Link: ${contentTypeBreakdown.link || 0})`
                                : ''
                        }`}
                        color="primary"
                        size="small"
                        sx={{ fontWeight: 500 }}
                    />
                )}
            </Box>
        </Box>
    );
};

export default TimeFrameFilters;

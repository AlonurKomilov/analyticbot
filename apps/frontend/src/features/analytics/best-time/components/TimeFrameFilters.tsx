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
export type TimeFrame = 'week' | 'month' | 'year';

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
    setTimeFrame,
    contentType,
    setContentType
}) => {
    const handleTimeFrameChange = (event: SelectChangeEvent) => {
        setTimeFrame(event.target.value as TimeFrame);
    };

    const handleContentTypeChange = (event: SelectChangeEvent) => {
        setContentType(event.target.value as ContentType);
    };

    return (
        <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <AIIcon color="primary" />
                <Typography variant="h5" component="h1">
                    🤖 AI Posting Time Recommendations
                </Typography>
            </Box>

            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <FormControl size="small" sx={{ minWidth: 120 }}>
                    <InputLabel id="timeframe-label">Vaqt oralig'i</InputLabel>
                    <Select
                        labelId="timeframe-label"
                        value={timeFrame}
                        label="Vaqt oralig'i"
                        onChange={handleTimeFrameChange}
                    >
                        <MenuItem value="week">Hafta</MenuItem>
                        <MenuItem value="month">Oy</MenuItem>
                        <MenuItem value="year">Yil</MenuItem>
                    </Select>
                </FormControl>

                <FormControl size="small" sx={{ minWidth: 120 }}>
                    <InputLabel id="content-type-label">Kontent turi</InputLabel>
                    <Select
                        labelId="content-type-label"
                        value={contentType}
                        label="Kontent turi"
                        onChange={handleContentTypeChange}
                    >
                        <MenuItem value="all">Barcha</MenuItem>
                        <MenuItem value="text">Matn</MenuItem>
                        <MenuItem value="image">Rasm</MenuItem>
                        <MenuItem value="video">Video</MenuItem>
                        <MenuItem value="poll">So'rov</MenuItem>
                    </Select>
                </FormControl>
            </Box>
        </Box>
    );
};

export default TimeFrameFilters;

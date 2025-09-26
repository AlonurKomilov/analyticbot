import React from 'react';
import {
    Box,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Typography
} from '@mui/material';
import { Psychology as AIIcon } from '@mui/icons-material';

const TimeFrameFilters = ({ timeFrame, setTimeFrame, contentType, setContentType }) => {
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
                        onChange={(e) => setTimeFrame(e.target.value)}
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
                        onChange={(e) => setContentType(e.target.value)}
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
import React from 'react';
import {
    Box,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Typography
} from '@mui/material';

const PostTableFilters = ({ timeFilter, setTimeFilter, sortBy, setSortBy }) => {
    return (
        <Box 
            sx={{ 
                display: 'flex', 
                gap: 2, 
                mb: 3, 
                alignItems: 'center',
                flexWrap: 'wrap'
            }}
        >
            <Typography variant="h6" component="h2" sx={{ mr: 2 }}>
                📊 Top Posts
            </Typography>
            
            <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel id="time-filter-label">Time Period</InputLabel>
                <Select
                    labelId="time-filter-label"
                    id="time-filter"
                    value={timeFilter}
                    label="Time Period"
                    onChange={(e) => setTimeFilter(e.target.value)}
                >
                    <MenuItem value="today">Today</MenuItem>
                    <MenuItem value="yesterday">Yesterday</MenuItem>
                    <MenuItem value="week">This Week</MenuItem>
                    <MenuItem value="month">This Month</MenuItem>
                </Select>
            </FormControl>
            
            <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel id="sort-by-label">Sort By</InputLabel>
                <Select
                    labelId="sort-by-label"
                    id="sort-by"
                    value={sortBy}
                    label="Sort By"
                    onChange={(e) => setSortBy(e.target.value)}
                >
                    <MenuItem value="views">Views</MenuItem>
                    <MenuItem value="likes">Likes</MenuItem>
                    <MenuItem value="shares">Shares</MenuItem>
                    <MenuItem value="comments">Comments</MenuItem>
                    <MenuItem value="engagement">Engagement Rate</MenuItem>
                </Select>
            </FormControl>
        </Box>
    );
};

export default PostTableFilters;
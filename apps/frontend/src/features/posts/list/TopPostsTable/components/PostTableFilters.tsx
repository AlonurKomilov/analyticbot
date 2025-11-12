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

/**
 * Time filter options - aligned with Post Dynamics
 */
export type TimeFilter = '1h' | '6h' | '24h' | '7d' | '30d' | '90d' | 'all';

/**
 * Sort by options
 */
export type SortBy = 'views' | 'likes' | 'shares' | 'comments' | 'engagement';

/**
 * Props for PostTableFilters component
 */
interface PostTableFiltersProps {
    /** Selected time filter */
    timeFilter: TimeFilter;
    /** Callback to update time filter */
    setTimeFilter: (filter: TimeFilter) => void;
    /** Selected sort option */
    sortBy: SortBy;
    /** Callback to update sort option */
    setSortBy: (sort: SortBy) => void;
}

/**
 * PostTableFilters Component
 * Filter controls for top posts table
 */
const PostTableFilters: React.FC<PostTableFiltersProps> = ({
    timeFilter,
    setTimeFilter,
    sortBy,
    setSortBy
}) => {
    const handleTimeFilterChange = (event: SelectChangeEvent) => {
        setTimeFilter(event.target.value as TimeFilter);
    };

    const handleSortByChange = (event: SelectChangeEvent) => {
        setSortBy(event.target.value as SortBy);
    };

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
                    onChange={handleTimeFilterChange}
                >
                    <MenuItem value="1h">Last Hour</MenuItem>
                    <MenuItem value="6h">Last 6 Hours</MenuItem>
                    <MenuItem value="24h">Last 24 Hours</MenuItem>
                    <MenuItem value="7d">Last 7 Days</MenuItem>
                    <MenuItem value="30d">Last 30 Days</MenuItem>
                    <MenuItem value="90d">Last 90 Days</MenuItem>
                    <MenuItem value="all">All Time</MenuItem>
                </Select>
            </FormControl>

            <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel id="sort-by-label">Sort By</InputLabel>
                <Select
                    labelId="sort-by-label"
                    id="sort-by"
                    value={sortBy}
                    label="Sort By"
                    onChange={handleSortByChange}
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

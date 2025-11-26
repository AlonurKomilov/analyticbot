import React from 'react';
import {
    Box,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    SelectChangeEvent
} from '@mui/material';

/**
 * Time filter options - aligned with Post Dynamics
 */
export type TimeFilter = '1h' | '6h' | '24h' | '7d' | '30d' | '90d' | 'all';

/**
 * Sort by options
 */
export type SortBy = 'views' | 'reactions' | 'shares' | 'comments' | 'engagement';

/**
 * Limit options for top N posts
 */
export type LimitOption = 10 | 25 | 50;

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
    /** Selected limit for top N posts */
    limit: LimitOption;
    /** Callback to update limit */
    setLimit: (limit: LimitOption) => void;
}

/**
 * PostTableFilters Component
 * Filter controls for top posts table
 */
const PostTableFilters: React.FC<PostTableFiltersProps> = ({
    timeFilter,
    setTimeFilter,
    sortBy,
    setSortBy,
    limit,
    setLimit
}) => {
    const handleTimeFilterChange = (event: SelectChangeEvent) => {
        setTimeFilter(event.target.value as TimeFilter);
    };

    const handleSortByChange = (event: SelectChangeEvent) => {
        setSortBy(event.target.value as SortBy);
    };

    const handleLimitChange = (event: SelectChangeEvent) => {
        setLimit(parseInt(event.target.value) as LimitOption);
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
                    <MenuItem value="reactions">Reactions</MenuItem>
                    <MenuItem value="shares">Shares</MenuItem>
                    <MenuItem value="comments">Comments</MenuItem>
                    <MenuItem value="engagement">Engagement Rate</MenuItem>
                </Select>
            </FormControl>

            <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel id="limit-label">Top</InputLabel>
                <Select
                    labelId="limit-label"
                    id="limit"
                    value={limit.toString()}
                    label="Top"
                    onChange={handleLimitChange}
                >
                    <MenuItem value="10">10 Posts</MenuItem>
                    <MenuItem value="25">25 Posts</MenuItem>
                    <MenuItem value="50">50 Posts</MenuItem>
                </Select>
            </FormControl>
        </Box>
    );
};

export default PostTableFilters;

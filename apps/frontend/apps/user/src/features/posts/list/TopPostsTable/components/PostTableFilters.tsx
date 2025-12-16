import React from 'react';
import { useTranslation } from 'react-i18next';
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
    const { t } = useTranslation('filters');
    
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
                <InputLabel id="time-filter-label">{t('filters.timePeriod')}</InputLabel>
                <Select
                    labelId="time-filter-label"
                    id="time-filter"
                    value={timeFilter}
                    label={t('filters.timePeriod')}
                    onChange={handleTimeFilterChange}
                >
                    <MenuItem value="1h">{t('timePeriods.lastHour')}</MenuItem>
                    <MenuItem value="6h">{t('timePeriods.last6Hours')}</MenuItem>
                    <MenuItem value="24h">{t('timePeriods.last24Hours')}</MenuItem>
                    <MenuItem value="7d">{t('timePeriods.last7Days')}</MenuItem>
                    <MenuItem value="30d">{t('timePeriods.last30Days')}</MenuItem>
                    <MenuItem value="90d">{t('timePeriods.last90Days')}</MenuItem>
                    <MenuItem value="all">{t('timePeriods.allTime')}</MenuItem>
                </Select>
            </FormControl>

            <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel id="sort-by-label">{t('common.sortBy')}</InputLabel>
                <Select
                    labelId="sort-by-label"
                    id="sort-by"
                    value={sortBy}
                    label={t('common.sortBy')}
                    onChange={handleSortByChange}
                >
                    <MenuItem value="views">{t('common.views')}</MenuItem>
                    <MenuItem value="reactions">{t('common.reactions')}</MenuItem>
                    <MenuItem value="shares">{t('common.shares')}</MenuItem>
                    <MenuItem value="comments">{t('common.comments')}</MenuItem>
                    <MenuItem value="engagement">{t('posts.engagementRate')}</MenuItem>
                </Select>
            </FormControl>

            <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel id="limit-label">{t('posts.top')}</InputLabel>
                <Select
                    labelId="limit-label"
                    id="limit"
                    value={limit.toString()}
                    label={t('posts.top')}
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

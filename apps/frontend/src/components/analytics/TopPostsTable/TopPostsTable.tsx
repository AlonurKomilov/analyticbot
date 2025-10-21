import React, { useState } from 'react';
import { Paper, Box, Alert } from '@mui/material';
import { EnhancedDataTable } from '../../common/EnhancedDataTable';
import PostTableFilters from './components/PostTableFilters';
import PostSummaryStats from './components/PostSummaryStats';
import { usePostTableLogic } from './hooks/usePostTableLogic';
import { createTopPostsColumns, topPostsTableConfig } from './TopPostsTableConfig';

const TopPostsTable: React.FC = () => {
    const {
        timeFilter,
        sortBy,
        loading,
        error,
        posts,
        summaryStats,
        setTimeFilter,
        setSortBy
    } = usePostTableLogic();

    // Menu state for actions
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
    const [selectedPostId, setSelectedPostId] = useState<string | number | null>(null);

    const handleMenuClick = (event: React.MouseEvent<HTMLElement>, postId: string | number) => {
        setAnchorEl(event.currentTarget);
        setSelectedPostId(postId);
    };

    const handleMenuClose = () => {
        setAnchorEl(null);
        setSelectedPostId(null);
    };

    // Create columns with current menu state
    const columns = createTopPostsColumns(anchorEl, selectedPostId, handleMenuClick, handleMenuClose);

    return (
        <Paper sx={{ p: 3, borderRadius: 2 }}>
            {/* Filters */}
            <PostTableFilters
                timeFilter={timeFilter as any}
                setTimeFilter={setTimeFilter as any}
                sortBy={sortBy as any}
                setSortBy={setSortBy as any}
            />

            {/* Error State */}
            {error && (
                <Alert
                    severity="error"
                    sx={{ mb: 2 }}
                    aria-live="polite"
                >
                    {error}
                </Alert>
            )}

            {/* Summary Statistics */}
            <PostSummaryStats summaryStats={summaryStats as any} />

            {/* Enhanced Data Table */}
            <Box sx={{ mt: 3 }}>
                <EnhancedDataTable
                    data={posts}
                    columns={columns as any}
                    loading={loading}
                    error={error}
                    {...topPostsTableConfig as any}
                    emptyStateMessage="No posts found. Try adjusting your filters or check back later."
                    aria-label="Top performing posts with engagement metrics"
                />
            </Box>
        </Paper>
    );
};

export default TopPostsTable;

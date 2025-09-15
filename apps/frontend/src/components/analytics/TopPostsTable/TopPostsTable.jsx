import React, { useState } from 'react';
import { Paper, Typography, Box, Alert } from '@mui/material';
import { EnhancedDataTable } from '../../common/EnhancedDataTable';
import PostTableFilters from './components/PostTableFilters.jsx';
import PostSummaryStats from './components/PostSummaryStats.jsx';
import { usePostTableLogic } from './hooks/usePostTableLogic.js';
import { createTopPostsColumns, topPostsTableConfig } from './TopPostsTableConfig.jsx';

const TopPostsTable = () => {
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
    const [anchorEl, setAnchorEl] = useState(null);
    const [selectedPostId, setSelectedPostId] = useState(null);

    const handleMenuClick = (event, postId) => {
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
                timeFilter={timeFilter}
                setTimeFilter={setTimeFilter}
                sortBy={sortBy}
                setSortBy={setSortBy}
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
            <PostSummaryStats summaryStats={summaryStats} />

            {/* Enhanced Data Table */}
            <Box sx={{ mt: 3 }}>
                <EnhancedDataTable
                    data={posts}
                    columns={columns}
                    loading={loading}
                    error={error}
                    title={topPostsTableConfig.title}
                    defaultSortField={topPostsTableConfig.defaultSortField}
                    defaultSortDirection={topPostsTableConfig.defaultSortDirection}
                    defaultPageSize={topPostsTableConfig.defaultPageSize}
                    pageSizeOptions={topPostsTableConfig.pageSizeOptions}
                    enableSearch={topPostsTableConfig.enableSearch}
                    searchFields={topPostsTableConfig.searchFields}
                    enableExport={topPostsTableConfig.enableExport}
                    enableBulkActions={topPostsTableConfig.enableBulkActions}
                    enableColumnManagement={topPostsTableConfig.enableColumnManagement}
                    stickyHeader={topPostsTableConfig.stickyHeader}
                    maxHeight={topPostsTableConfig.maxHeight}
                    emptyStateMessage="No posts found. Try adjusting your filters or check back later."
                    aria-label="Top performing posts with engagement metrics"
                />
            </Box>
        </Paper>
    );
};

export default TopPostsTable;
import React, { useEffect, useRef } from 'react';
import { Paper, Box, Alert } from '@mui/material';
import { EnhancedDataTable } from '@shared/components/tables';
import PostTableFilters from './components/PostTableFilters';
import PostSummaryStats from './components/PostSummaryStats';
import { usePostTableLogic } from './hooks/usePostTableLogic';
import { createTopPostsColumns, topPostsTableConfig } from './TopPostsTableConfig';

interface TopPostsTableProps {
    lastUpdated?: Date;
}

const TopPostsTable: React.FC<TopPostsTableProps> = ({ lastUpdated }) => {
    const {
        timeFilter,
        sortBy,
        loading,
        error,
        posts,
        summaryStats,
        setTimeFilter,
        setSortBy,
        loadTopPosts
    } = usePostTableLogic();

    const prevLastUpdatedRef = useRef<Date | undefined>(undefined);

    // Silent refresh when lastUpdated changes (from dashboard auto-refresh)
    useEffect(() => {
        if (lastUpdated && prevLastUpdatedRef.current && lastUpdated.getTime() !== prevLastUpdatedRef.current.getTime()) {
            // This is an auto-refresh from the dashboard - trigger silent reload
            console.log('🔄 TopPostsTable: Silent auto-refresh triggered');
            loadTopPosts(true); // Pass true for silent mode
        }
        prevLastUpdatedRef.current = lastUpdated;
    }, [lastUpdated, loadTopPosts]);

    // Create columns without menu click handler
    const columns = createTopPostsColumns();

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

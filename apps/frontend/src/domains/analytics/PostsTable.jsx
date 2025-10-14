import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { EnhancedDataTable } from '../../components/common/EnhancedDataTable';
import { useAppStore } from '../../store/appStore.js';
import {
    PostDisplayCell,
    ViewsCell,
    LikesCell,
    SharesCell,
    CommentsCell,
    EngagementCell,
    PerformanceCell,
    DateCell,
    StatusCell
} from './PostsDisplayComponents';
import { PostActions, PostBulkActions } from './PostsActions';
import { generateMockPosts } from './PostsUtils';

/**
 * Main Posts Table Component
 * Modular table implementation for top posts analytics
 */
const PostsTable = () => {
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const { dataSource } = useAppStore();

    // Load posts data
    const loadTopPosts = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);

            if (dataSource === 'mock') {
                // Use mock data
                setTimeout(() => {
                    setPosts(generateMockPosts(20));
                    setLoading(false);
                }, 500);
            } else {
                // For now, use mock data until we have channel selection
                // TODO: Implement real API call when channel context is available
                // const response = await fetch(`/analytics/top-posts/${channelId}`);
                // const data = await response.json();
                setPosts(generateMockPosts(20));
                setLoading(false);
            }
        } catch (err) {
            console.error('Error loading posts:', err);
            setError('Failed to load posts data');
            // Fallback to mock data
            setPosts(generateMockPosts(20));
            setLoading(false);
        }
    }, [dataSource]);

    useEffect(() => {
        loadTopPosts();

        // Listen for data source changes
        const handleDataSourceChange = () => loadTopPosts();
        window.addEventListener('dataSourceChanged', handleDataSourceChange);
        return () => window.removeEventListener('dataSourceChanged', handleDataSourceChange);
    }, [loadTopPosts]);

    // Action handlers
    const handleRowAction = useCallback((action, post) => {
        console.log(`Action ${action} on post:`, post);

        switch (action) {
            case 'view':
                // Open post details
                break;
            case 'analytics':
                // Open analytics view
                break;
            case 'edit':
                // Open edit form
                break;
            case 'share':
                // Share post
                break;
            case 'download':
                // Download report
                break;
            case 'delete':
                // Delete post with confirmation
                break;
            default:
                console.log('Unknown action:', action);
        }
    }, []);

    const handleBulkAction = useCallback((action, selectedPosts) => {
        console.log(`Bulk action ${action} on posts:`, selectedPosts);

        switch (action) {
            case 'download':
                // Download bulk reports
                break;
            case 'analytics':
                // Show bulk analytics
                break;
            case 'delete':
                // Bulk delete with confirmation
                break;
            default:
                console.log('Unknown bulk action:', action);
        }
    }, []);

    // Column definitions
    const columns = useMemo(() => [
        {
            id: 'post',
            header: 'Post',
            accessor: (row) => row,
            width: 300,
            Cell: ({ value }) => <PostDisplayCell row={value} />
        },
        {
            id: 'views',
            header: 'Views',
            accessor: (row) => row.views || 0,
            align: 'center',
            width: 120,
            Cell: ({ value }) => <ViewsCell value={value} />
        },
        {
            id: 'likes',
            header: 'Likes',
            accessor: (row) => row.likes || 0,
            align: 'center',
            width: 100,
            Cell: ({ value }) => <LikesCell value={value} />
        },
        {
            id: 'shares',
            header: 'Shares',
            accessor: (row) => row.shares || 0,
            align: 'center',
            width: 100,
            Cell: ({ value }) => <SharesCell value={value} />
        },
        {
            id: 'comments',
            header: 'Comments',
            accessor: (row) => row.comments || 0,
            align: 'center',
            width: 120,
            Cell: ({ value }) => <CommentsCell value={value} />
        },
        {
            id: 'engagement',
            header: 'Engagement',
            accessor: (row) => row,
            align: 'center',
            width: 140,
            Cell: ({ value }) => <EngagementCell row={value} />
        },
        {
            id: 'performance',
            header: 'Performance',
            accessor: (row) => row,
            align: 'center',
            width: 130,
            Cell: ({ value }) => <PerformanceCell row={value} />
        },
        {
            id: 'date',
            header: 'Published',
            accessor: (row) => row.date,
            align: 'center',
            width: 140,
            Cell: ({ value }) => <DateCell value={value} />
        },
        {
            id: 'status',
            header: 'Status',
            accessor: (row) => row,
            align: 'center',
            width: 120,
            Cell: ({ value }) => <StatusCell row={value} />
        },
        {
            id: 'actions',
            header: 'Actions',
            accessor: (row) => row,
            align: 'center',
            width: 80,
            disableSort: true,
            Cell: ({ value }) => (
                <PostActions
                    row={value}
                    onAction={handleRowAction}
                />
            )
        }
    ], [handleRowAction]);

    // Table configuration
    const tableConfig = {
        enableSelection: true,
        enableSorting: true,
        enableFiltering: true,
        enableExport: true,
        enableColumnManagement: true,
        enableDensityToggle: true,
        enableRefresh: true,
        defaultPageSize: 10,
        pageSizeOptions: [5, 10, 25, 50, 100]
    };

    return (
        <EnhancedDataTable
            data={posts}
            columns={columns}
            loading={loading}
            error={error}
            onRefresh={loadTopPosts}
            bulkActions={(selectedRows) => (
                <PostBulkActions
                    selectedRows={selectedRows}
                    onBulkAction={handleBulkAction}
                />
            )}
            {...tableConfig}
        />
    );
};

export default PostsTable;

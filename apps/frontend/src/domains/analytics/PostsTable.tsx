import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { EnhancedDataTable } from '@shared/components/tables';
import { useUIStore, useChannelStore, useAnalyticsStore } from '@store';
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
import { PostActions } from './PostsActions';
import { generateMockPosts } from './PostsUtils';

// ============================================================================
// Type Definitions
// ============================================================================

export interface Post {
    id: string | number;
    text?: string;
    media?: Array<{ url: string; type?: string }>;
    post_url?: string;
    views?: number;
    likes?: number;
    shares?: number;
    comments?: number;
    date?: string;
    created_at?: string;
    status?: string;
    engagement_rate?: number;
    performance_score?: number;
    [key: string]: any;
}

type RowAction = 'view' | 'analytics' | 'edit' | 'share' | 'download' | 'delete';

interface TableColumn {
    id: string;
    header: string;
    accessor: (row: Post) => any;
    width?: number;
    align?: 'left' | 'center' | 'right';
    disableSort?: boolean;
    Cell: React.FC<{ value: any }>;
}

interface TableConfig {
    enableSelection: boolean;
    enableSorting: boolean;
    enableFiltering: boolean;
    enableExport: boolean;
    enableColumnManagement: boolean;
    enableDensityToggle: boolean;
    enableRefresh: boolean;
    defaultPageSize: number;
    pageSizeOptions: number[];
}

// ============================================================================
// Main Posts Table Component
// ============================================================================

/**
 * Main Posts Table Component
 * Modular table implementation for top posts analytics
 */
const PostsTable: React.FC = () => {
    const [posts, setPosts] = useState<Post[]>([]);
    const [error, setError] = useState<string | null>(null);
    const { dataSource } = useUIStore();
    const { channels } = useChannelStore();
    const { fetchTopPosts, topPosts, isLoadingTopPosts } = useAnalyticsStore();

    // Load posts data
    const loadTopPosts = useCallback(async (): Promise<void> => {
        try {
            setError(null);

            if (dataSource === 'mock') {
                // Use mock data ONLY when explicitly in demo mode
                setPosts(generateMockPosts(20));
            } else {
                // Real API mode - NEVER use mock data
                if (channels && channels.length > 0) {
                    const channelId = channels[0].id;
                    await fetchTopPosts(channelId);
                    setPosts(topPosts || []); // Use from store
                } else {
                    // No channels - show empty state, NOT mock data
                    setPosts([]);
                }
            }
        } catch (err) {
            console.error('Error loading posts:', err);
            const errorMessage = err instanceof Error ? err.message : 'Failed to load posts data';
            setError(errorMessage);
            // In real API mode, show empty on error, NOT mock data
            if (dataSource !== 'mock') {
                setPosts([]);
            } else {
                // Only fallback to mock if in mock mode
                setPosts(generateMockPosts(20));
            }
        }
    }, [dataSource, channels, fetchTopPosts, topPosts]);

    useEffect(() => {
        loadTopPosts();

        // Listen for data source changes
        const handleDataSourceChange = (): void => {
            loadTopPosts();
        };
        window.addEventListener('dataSourceChanged', handleDataSourceChange);
        return () => window.removeEventListener('dataSourceChanged', handleDataSourceChange);
    }, [loadTopPosts]);

    // Action handlers
    const handleRowAction = useCallback((action: RowAction, post: Post): void => {
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

    // Column definitions
    const columns = useMemo<TableColumn[]>(() => [
        {
            id: 'post',
            header: 'Post',
            accessor: (row: Post) => row,
            width: 300,
            Cell: ({ value }: { value: Post }) => <PostDisplayCell row={value as any} />
        },
        {
            id: 'views',
            header: 'Views',
            accessor: (row: Post) => row.views || 0,
            align: 'center',
            width: 120,
            Cell: ({ value }: { value: number }) => <ViewsCell value={value} />
        },
        {
            id: 'likes',
            header: 'Likes',
            accessor: (row: Post) => row.likes || 0,
            align: 'center',
            width: 100,
            Cell: ({ value }: { value: number }) => <LikesCell value={value} />
        },
        {
            id: 'shares',
            header: 'Shares',
            accessor: (row: Post) => row.shares || 0,
            align: 'center',
            width: 100,
            Cell: ({ value }: { value: number }) => <SharesCell value={value} />
        },
        {
            id: 'comments',
            header: 'Comments',
            accessor: (row: Post) => row.comments || 0,
            align: 'center',
            width: 120,
            Cell: ({ value }: { value: number }) => <CommentsCell value={value} />
        },
        {
            id: 'engagement',
            header: 'Engagement',
            accessor: (row: Post) => row,
            align: 'center',
            width: 140,
            Cell: ({ value }: { value: Post }) => <EngagementCell row={value as any} />
        },
        {
            id: 'performance',
            header: 'Performance',
            accessor: (row: Post) => row,
            align: 'center',
            width: 130,
            Cell: ({ value }: { value: Post }) => <PerformanceCell row={value as any} />
        },
        {
            id: 'date',
            header: 'Published',
            accessor: (row: Post) => row.date,
            align: 'center',
            width: 140,
            Cell: ({ value }: { value: string }) => <DateCell value={value} />
        },
        {
            id: 'status',
            header: 'Status',
            accessor: (row: Post) => row,
            align: 'center',
            width: 120,
            Cell: ({ value }: { value: Post }) => <StatusCell row={value as any} />
        },
        {
            id: 'actions',
            header: 'Actions',
            accessor: (row: Post) => row,
            align: 'center',
            width: 80,
            disableSort: true,
            Cell: ({ value }: { value: Post }) => (
                <PostActions
                    row={value}
                    onAction={handleRowAction}
                />
            )
        }
    ], [handleRowAction]);

    // Table configuration
    const tableConfig: TableConfig = {
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
            columns={columns as any}
            loading={isLoadingTopPosts}
            error={error}
            onRefresh={loadTopPosts}
            {...tableConfig}
        />
    );
};

export default PostsTable;

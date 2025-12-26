import { useState, useEffect, useCallback, useMemo } from 'react';
import { useAnalyticsStore } from '@store';
import { useChannelStore } from '@store';
import { useUIStore } from '@store';
import { type Post, type SummaryStats } from '@features/posts/list/TopPostsTable/utils/postTableUtils';
import { DEFAULT_DEMO_CHANNEL_ID } from '@/__mocks__/constants';

interface UsePostTableLogicReturn {
    timeFilter: string;
    sortBy: string;
    limit: number;
    loading: boolean;
    error: string | null;
    posts: Post[];
    anchorEl: HTMLElement | null;
    selectedPostId: string | number | null;
    summaryStats: SummaryStats | null;
    setTimeFilter: (filter: string) => void;
    setSortBy: (sort: string) => void;
    setLimit: (limit: number) => void;
    handleMenuClick: (event: React.MouseEvent<HTMLElement>, postId: string | number) => void;
    handleMenuClose: () => void;
    loadTopPosts: (silent?: boolean) => Promise<void>;
}

export const usePostTableLogic = (): UsePostTableLogicReturn => {
    const [timeFilter, setTimeFilter] = useState<string>('all');  // Changed default to all
    const [sortBy, setSortBy] = useState<string>('views');
    const [limit, setLimit] = useState<number>(10);  // Default to 10 posts
    const [error, setError] = useState<string | null>(null);
    const [posts, setPosts] = useState<Post[]>([]);
    const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
    const [selectedPostId, setSelectedPostId] = useState<string | number | null>(null);

    // Get store methods and state
    const { fetchTopPosts, topPosts, isLoadingTopPosts, fetchTopPostsSummary, isLoadingTopPostsSummary } = useAnalyticsStore();
    const { selectedChannel } = useChannelStore();
    const { dataSource } = useUIStore();

    // Determine which channel ID to use
    // Priority: demo mode > selected channel > null
    const channelId = dataSource === 'demo'
        ? DEFAULT_DEMO_CHANNEL_ID
        : (selectedChannel?.id?.toString() || null);

    // Map frontend filter values to backend period values
    // Now directly compatible - no mapping needed!
    const mapTimFilterToPeriod = (filter: string): string => {
        // Frontend now uses same values as backend: 1h, 6h, 24h, 7d, 30d, 90d, all
        return filter;
    };

    // Map frontend sort values to backend sort_by values
    const mapSortByToBackend = (sort: string): string => {
        const mapping: Record<string, string> = {
            'views': 'views',
            'reactions': 'reactions_count',
            'shares': 'forwards',
            'comments': 'comments_count',  // Fixed: was 'replies_count', should be 'comments_count'
            'engagement': 'engagement_rate'
        };
        return mapping[sort] || 'views';
    };

    // Load top posts data
    const loadTopPosts = useCallback(async (silent: boolean = false) => {
        // Don't load if no channel selected and not in demo mode
        if (!channelId) {
            console.info('💡 No channel selected - select a channel to view top posts');
            setPosts([]);
            setError(null);
            return;
        }

        try {
            setError(null);
            const period = mapTimFilterToPeriod(timeFilter);
            const backendSortBy = mapSortByToBackend(sortBy);

            console.log('🔄 Loading top posts:', { channelId, period, sortBy: backendSortBy, limit });

            // Fetch both top posts table data AND summary statistics in parallel
            await Promise.all([
                fetchTopPosts(channelId, limit, period, backendSortBy, silent),
                fetchTopPostsSummary(channelId, period, silent)
            ]);

            console.log('✅ Top posts and summary loaded successfully');
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Unknown error';
            setError(errorMessage);
            console.error('Error loading top posts:', err);
        }
    }, [fetchTopPosts, fetchTopPostsSummary, channelId, timeFilter, sortBy, limit]); // Removed topPosts from dependencies!

    // Sync topPosts from store to local state
    useEffect(() => {
        if (topPosts) {
            setPosts(topPosts);
        }
    }, [topPosts]);

    // Load data on mount and when channel/filters change
    useEffect(() => {
        loadTopPosts();
    }, [loadTopPosts]);

    // Show helpful message when no data available
    useEffect(() => {
        if (!isLoadingTopPosts && posts.length === 0 && !error && channelId) {
            const endpoint = channelId === DEFAULT_DEMO_CHANNEL_ID
                ? '/unified-analytics/demo/top-posts'
                : `/analytics/posts/dynamics/top-posts/${channelId}`;
            console.info(`💡 No posts available - endpoint: ${endpoint}`);
        }
    }, [isLoadingTopPosts, posts.length, error, channelId]);

    // Transform summary from fetched posts (calculate from top N posts only)
    const summaryStats = useMemo(() => {
        if (!posts || posts.length === 0) {
            console.log('⚠️ No posts data available for summary');
            return null;
        }

        // Calculate summary from the fetched posts (top N based on limit)
        const totalViews = posts.reduce((sum, post) => sum + (post.views || 0), 0);
        const totalReactions = posts.reduce((sum, post) => sum + (post.reactions || 0), 0);
        const totalShares = posts.reduce((sum, post) => sum + (post.shares || 0), 0);
        const totalComments = posts.reduce((sum, post) => sum + (post.comments || 0), 0);
        const totalReplies = posts.reduce((sum, post) => sum + (post.replies || 0), 0);
        const avgEngagement = posts.reduce((sum, post) => sum + (post.engagementRate || 0), 0) / posts.length;

        console.log('📊 Summary calculated from top', posts.length, 'posts');

        return {
            totalViews,
            totalReactions,
            totalShares,
            totalComments,
            totalReplies,
            avgEngagement: avgEngagement.toFixed(1),
            topPost: posts[0] || null
        };
    }, [posts]);

    // Menu handlers
    const handleMenuClick = (event: React.MouseEvent<HTMLElement>, postId: string | number) => {
        setAnchorEl(event.currentTarget);
        setSelectedPostId(postId);
    };

    const handleMenuClose = () => {
        setAnchorEl(null);
        setSelectedPostId(null);
    };

    return {
        // State
        timeFilter,
        sortBy,
        limit,
        loading: isLoadingTopPosts || isLoadingTopPostsSummary,
        error,
        posts,
        anchorEl,
        selectedPostId,
        summaryStats,

        // Actions
        setTimeFilter,
        setSortBy,
        setLimit,
        handleMenuClick,
        handleMenuClose,
        loadTopPosts
    };
};

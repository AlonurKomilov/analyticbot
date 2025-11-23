import { useState, useEffect, useCallback, useMemo } from 'react';
import { useAnalyticsStore } from '@store';
import { useChannelStore } from '@store';
import { useUIStore } from '@store';
import { calculateSummaryStats, type Post, type SummaryStats } from '@features/posts/list/TopPostsTable/utils/postTableUtils';
import { DEFAULT_DEMO_CHANNEL_ID } from '@/__mocks__/constants';

interface UsePostTableLogicReturn {
    timeFilter: string;
    sortBy: string;
    loading: boolean;
    error: string | null;
    posts: Post[];
    anchorEl: HTMLElement | null;
    selectedPostId: string | number | null;
    summaryStats: SummaryStats | null;
    setTimeFilter: (filter: string) => void;
    setSortBy: (sort: string) => void;
    handleMenuClick: (event: React.MouseEvent<HTMLElement>, postId: string | number) => void;
    handleMenuClose: () => void;
    loadTopPosts: (silent?: boolean) => Promise<void>;
}

export const usePostTableLogic = (): UsePostTableLogicReturn => {
    const [timeFilter, setTimeFilter] = useState<string>('30d');  // Changed default to 30d
    const [sortBy, setSortBy] = useState<string>('views');
    const [error, setError] = useState<string | null>(null);
    const [posts, setPosts] = useState<Post[]>([]);
    const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
    const [selectedPostId, setSelectedPostId] = useState<string | number | null>(null);

    // Get store methods and state
    const { fetchTopPosts, topPosts, isLoadingTopPosts } = useAnalyticsStore();
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
            'likes': 'reactions_count',
            'shares': 'forwards',
            'comments': 'replies_count',
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
            await fetchTopPosts(channelId, 10, period, backendSortBy, silent);
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Unknown error';
            setError(errorMessage);
            console.error('Error loading top posts:', err);
        }
    }, [fetchTopPosts, channelId, timeFilter, sortBy]); // Removed topPosts from dependencies!

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

    // Calculate summary statistics
    const summaryStats = useMemo(() => {
        return calculateSummaryStats(posts);
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
        loading: isLoadingTopPosts,
        error,
        posts,
        anchorEl,
        selectedPostId,
        summaryStats,

        // Actions
        setTimeFilter,
        setSortBy,
        handleMenuClick,
        handleMenuClose,
        loadTopPosts
    };
};

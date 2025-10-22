import { useState, useEffect, useCallback, useMemo } from 'react';
import { useAnalyticsStore } from '@/stores';
import { calculateSummaryStats, type Post, type SummaryStats } from '../utils/postTableUtils';
import { DEFAULT_DEMO_CHANNEL_ID } from '../../../../__mocks__/constants';

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
    loadTopPosts: () => Promise<void>;
}

export const usePostTableLogic = (): UsePostTableLogicReturn => {
    const [timeFilter, setTimeFilter] = useState<string>('today');
    const [sortBy, setSortBy] = useState<string>('views');
    const [error, setError] = useState<string | null>(null);
    const [posts, setPosts] = useState<Post[]>([]);
    const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
    const [selectedPostId, setSelectedPostId] = useState<string | number | null>(null);

    // Get store methods and state
    const { fetchTopPosts, topPosts, isLoadingTopPosts } = useAnalyticsStore();

    // Load top posts data
    const loadTopPosts = useCallback(async () => {
        try {
            setError(null);
            await fetchTopPosts(DEFAULT_DEMO_CHANNEL_ID, 10);
            setPosts(topPosts || []);
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Unknown error';
            setError(errorMessage);
            console.error('Error loading top posts:', err);
        }
    }, [fetchTopPosts, topPosts]);

    // Load data on mount and when filters change
    useEffect(() => {
        loadTopPosts();
    }, [loadTopPosts]);

    // No auto-mock generation - data should come from backend (including demo data)
    useEffect(() => {
        if (!isLoadingTopPosts && posts.length === 0 && !error) {
            console.info('No posts available - user should sign in to demo account for mock data');
            // Don't auto-generate mock posts - let backend handle demo data through proper auth
        }
    }, [isLoadingTopPosts, posts.length, error]);

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

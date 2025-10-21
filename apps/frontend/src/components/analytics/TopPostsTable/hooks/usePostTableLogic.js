import { useState, useEffect, useCallback, useMemo } from 'react';
import { useAnalyticsStore } from '@/stores';
import { calculateSummaryStats } from '../utils/postTableUtils.js';
import { DEFAULT_DEMO_CHANNEL_ID } from '../../../../__mocks__/constants.js';

export const usePostTableLogic = () => {
    const [timeFilter, setTimeFilter] = useState('today');
    const [sortBy, setSortBy] = useState('views');
    const [error, setError] = useState(null);
    const [posts, setPosts] = useState([]);
    const [anchorEl, setAnchorEl] = useState(null);
    const [selectedPostId, setSelectedPostId] = useState(null);

    // Get store methods and state
    const { fetchTopPosts, topPosts, isLoadingTopPosts } = useAnalyticsStore();

    // Load top posts data
    const loadTopPosts = useCallback(async () => {
        try {
            setError(null);
            await fetchTopPosts(DEFAULT_DEMO_CHANNEL_ID, 10);
            setPosts(topPosts || []);
        } catch (err) {
            setError(err.message);
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
    const handleMenuClick = (event, postId) => {
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

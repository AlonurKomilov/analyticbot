import { useState, useEffect, useCallback, useMemo } from 'react';
import { useAppStore } from '../../../../store/appStore.js';
import { calculateSummaryStats } from '../utils/postTableUtils.js';

export const usePostTableLogic = () => {
    const [timeFilter, setTimeFilter] = useState('today');
    const [sortBy, setSortBy] = useState('views');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [posts, setPosts] = useState([]);
    const [anchorEl, setAnchorEl] = useState(null);
    const [selectedPostId, setSelectedPostId] = useState(null);
    
    // Get store methods
    const { fetchTopPosts } = useAppStore();

    // Load top posts data
    const loadTopPosts = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            
            // Get fresh store reference to avoid dependency issues
            const { fetchTopPosts } = useAppStore.getState();
            const result = await fetchTopPosts('demo_channel', timeFilter, sortBy);
            
            // Ensure we always set an array
            let postsData = [];
            if (Array.isArray(result)) {
                postsData = result;
            } else if (result && Array.isArray(result.posts)) {
                postsData = result.posts;
            } else if (result && result.data && Array.isArray(result.data)) {
                postsData = result.data;
            }
            
            setPosts(postsData);
            
        } catch (err) {
            setError(err.message);
            console.error('Error loading top posts:', err);
        } finally {
            setLoading(false);
        }
    }, [timeFilter, sortBy]);

    // Load data on mount and when filters change
    useEffect(() => {
        loadTopPosts();
    }, [loadTopPosts]);

    // Generate mock posts if needed (fallback)
    const generateMockPosts = useCallback(() => {
        const mockPosts = [
            {
                id: 1,
                title: "🚀 AnalyticBot new features: Real-time analytics and AI recommendations",
                content: "Our bot now provides real-time analytics...",
                type: "📊 Analytics",
                views: 15420,
                likes: 1542,
                shares: 234,
                comments: 89,
                created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
                thumbnail: null
            },
            {
                id: 2,
                title: "💡 Growing your Telegram channel: 10 effective tips",
                content: "Best strategies for growing your channels...",
                type: "🎯 Guide",
                views: 12300,
                likes: 987,
                shares: 156,
                comments: 67,
                created_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
                thumbnail: null
            },
            {
                id: 3,
                title: "🤖 AI-powered optimal posting time selection",
                content: "Machine Learning algorithms for your audience...",
                type: "🧠 AI/ML",
                views: 9800,
                likes: 756,
                shares: 89,
                comments: 45,
                created_at: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(),
                thumbnail: null
            }
        ];
        
        setPosts(mockPosts);
        setLoading(false);
    }, []);

    // Use mock data if no real data is available
    useEffect(() => {
        if (!loading && posts.length === 0 && !error) {
            generateMockPosts();
        }
    }, [loading, posts.length, error, generateMockPosts]);

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
        loading,
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
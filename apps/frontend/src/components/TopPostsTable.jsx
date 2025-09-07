import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
    Paper,
    Typography,
    Box,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Avatar,
    Chip,
    IconButton,
    Menu,
    MenuItem,
    FormControl,
    InputLabel,
    Select,
    CircularProgress,
    Alert,
    Tooltip,
    Card,
    CardContent
} from '@mui/material';
import {
    MoreVert as MoreVertIcon,
    TrendingUp as TrendingUpIcon,
    Favorite as LikeIcon,
    Share as ShareIcon,
    Comment as CommentIcon,
    Visibility as ViewsIcon,
    Star as StarIcon,
    CalendarToday as CalendarIcon
} from '@mui/icons-material';
import { useAppStore } from '../store/appStore.js';

const TopPostsTable = () => {
    const [timeFilter, setTimeFilter] = useState('today');
    const [sortBy, setSortBy] = useState('views');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [posts, setPosts] = useState([]);
    const [anchorEl, setAnchorEl] = useState(null);
    const [selectedPostId, setSelectedPostId] = useState(null);
    
    // Get store methods and data source
    const { fetchTopPosts, dataSource } = useAppStore();

    // Top posts loading data (stable function)
    const loadTopPosts = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            
            // Get fresh store reference to avoid dependency issues
            const { fetchTopPosts } = useAppStore.getState();
            const result = await fetchTopPosts(timeFilter, sortBy);
            setPosts(result.posts || []);
            
        } catch (err) {
            setError(err.message);
            console.error('Error loading top posts:', err);
        } finally {
            setLoading(false);
        }
    }, [timeFilter, sortBy]); // Remove fetchTopPosts dependency

    // Generate mock posts data
    const generateMockPosts = (timeFilter, sortBy) => {
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
            },
            {
                id: 4,
                title: "📱 TWA (Telegram Web App) development guide",
                content: "Creating and using Telegram Web Apps...",
                type: "💻 Development",
                views: 7600,
                likes: 456,
                shares: 67,
                comments: 34,
                created_at: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
                thumbnail: null
            },
            {
                id: 5,
                title: "📈 Channel statistics: weekly report",
                content: "This week's most viewed posts and trends...",
                type: "📊 Report",
                views: 6540,
                likes: 398,
                shares: 45,
                comments: 23,
                created_at: new Date(Date.now() - 18 * 60 * 60 * 1000).toISOString(),
                thumbnail: null
            },
            {
                id: 6,
                title: "🛡️ Protecting your channels: security considerations",
                content: "Protecting Telegram channels from spam and malicious users...",
                type: "🔒 Security",
                views: 5430,
                likes: 287,
                shares: 34,
                comments: 19,
                created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
                thumbnail: null
            }
        ];

        // Sort based on sortBy parameter
        return mockPosts.sort((a, b) => {
            switch (sortBy) {
                case 'likes':
                    return b.likes - a.likes;
                case 'engagement':
                    const aEngagement = (a.likes + a.shares + a.comments) / a.views;
                    const bEngagement = (b.likes + b.shares + b.comments) / b.views;
                    return bEngagement - aEngagement;
                case 'date':
                    return new Date(b.created_at) - new Date(a.created_at);
                case 'views':
                default:
                    return b.views - a.views;
            }
        });
    };

    // Component mount - load data only once
    useEffect(() => {
        let mounted = true;
        
        const initialLoad = async () => {
            // Small delay to avoid race conditions
            await new Promise(resolve => setTimeout(resolve, 100));
            if (mounted) {
                loadTopPosts();
            }
        };
        
        initialLoad();
        
        return () => {
            mounted = false;
        };
    }, []); // Empty dependency array for initial load only
    
    // Listen for data source changes (no dependencies to prevent infinite loops)
    useEffect(() => {
        let timeoutId;
        
        const handleDataSourceChange = () => {
            console.log('TopPostsTable: Data source changed, reloading...');
            
            // Clear any pending reload
            if (timeoutId) clearTimeout(timeoutId);
            
            // Debounce the reload to prevent rapid successive calls
            timeoutId = setTimeout(() => {
                loadTopPosts();
            }, 500);
        };
        
        window.addEventListener('dataSourceChanged', handleDataSourceChange);
        
        return () => {
            window.removeEventListener('dataSourceChanged', handleDataSourceChange);
            if (timeoutId) clearTimeout(timeoutId);
        };
    }, []); // No dependencies to prevent infinite loops

    // Menu handlers
    const handleMenuClick = (event, postId) => {
        setAnchorEl(event.currentTarget);
        setSelectedPostId(postId);
    };

    const handleMenuClose = () => {
        setAnchorEl(null);
        setSelectedPostId(null);
    };

    // Menu action handlers
    const handleMenuAction = (action) => {
        console.log(`Action ${action} for post ${selectedPostId}`);
        handleMenuClose();
    };

    // Metric formatters
    const formatNumber = (num) => {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        const now = new Date();
        const diffInHours = (now - date) / (1000 * 60 * 60);
        
        if (diffInHours < 1) {
            return `${Math.floor(diffInHours * 60)} min ago`;
        } else if (diffInHours < 24) {
            return `${Math.floor(diffInHours)} hours ago`;
        } else {
            return `${Math.floor(diffInHours / 24)} days ago`;
        }
    };

    // Calculate engagement rate
    const calculateEngagementRate = (post) => {
        const totalEngagement = (post.likes || 0) + (post.shares || 0) + (post.comments || 0);
        const views = post.views || 1;
        return ((totalEngagement / views) * 100).toFixed(1);
    };

    // Get performance badge
    const getPerformanceBadge = (post) => {
        const engagementRate = parseFloat(calculateEngagementRate(post));
        const views = post.views || 0;
        
        if (engagementRate > 10 && views > 10000) {
            return { label: <><span aria-hidden="true">🔥</span> Viral</>, color: 'error' };
        } else if (engagementRate > 5) {
            return { label: <><span aria-hidden="true">⭐</span> High</>, color: 'warning' };
        } else if (engagementRate > 2) {
            return { label: <><span aria-hidden="true">👍</span> Good</>, color: 'success' };
        } else {
            return { label: <><span aria-hidden="true">📊</span> Average</>, color: 'default' };
        }
    };

    // Summary statistics
    const summaryStats = useMemo(() => {
        if (!posts || posts.length === 0) return null;

        const totalViews = posts.reduce((sum, post) => sum + (post.views || 0), 0);
        const totalLikes = posts.reduce((sum, post) => sum + (post.likes || 0), 0);
        const totalShares = posts.reduce((sum, post) => sum + (post.shares || 0), 0);
        const totalComments = posts.reduce((sum, post) => sum + (post.comments || 0), 0);
        const avgEngagement = posts.reduce((sum, post) => sum + parseFloat(calculateEngagementRate(post)), 0) / posts.length;

        return {
            totalViews,
            totalLikes,
            totalShares,
            totalComments,
            avgEngagement: avgEngagement.toFixed(1),
            topPost: posts[0]
        };
    }, [posts]);

    if (error) {
        return (
            <Paper sx={{ p: 3 }}>
                <Alert severity="error" role="alert">
                    <strong>Unable to load posts:</strong> {error}
                </Alert>
            </Paper>
        );
    }

    return (
        <Paper sx={{ p: 3 }}>
            {/* Header */}
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <StarIcon color="primary" aria-hidden="true" />
                    <Typography variant="h2" sx={{ fontSize: '1.5rem' }}>
                        Top Performing Posts
                    </Typography>
                </Box>
                
                <Box sx={{ display: 'flex', gap: 2 }} role="group" aria-label="Filter options">
                    {/* Time Filter */}
                    <FormControl size="small" sx={{ minWidth: 120 }}>
                        <InputLabel id="time-filter-label">Time Period</InputLabel>
                        <Select
                            labelId="time-filter-label"
                            value={timeFilter}
                            label="Time Period"
                            onChange={(e) => setTimeFilter(e.target.value)}
                            aria-describedby="time-filter-help"
                        >
                            <MenuItem value="today">Today</MenuItem>
                            <MenuItem value="yesterday">Yesterday</MenuItem>
                            <MenuItem value="week">This Week</MenuItem>
                            <MenuItem value="month">This Month</MenuItem>
                        </Select>
                    </FormControl>

                    {/* Sort Filter */}
                    <FormControl size="small" sx={{ minWidth: 120 }}>
                        <InputLabel id="sort-filter-label">Sort By</InputLabel>
                        <Select
                            labelId="sort-filter-label"
                            value={sortBy}
                            label="Sort By"
                            onChange={(e) => setSortBy(e.target.value)}
                            aria-describedby="sort-filter-help"
                        >
                            <MenuItem value="views">Views</MenuItem>
                            <MenuItem value="likes">Likes</MenuItem>
                            <MenuItem value="engagement">Engagement</MenuItem>
                            <MenuItem value="date">Date</MenuItem>
                        </Select>
                    </FormControl>
                </Box>
            </Box>

            {/* Live region for loading/error states */}
            <div aria-live="polite" aria-atomic="true" className="sr-only">
                {loading && "Loading top posts data..."}
                {error && `Error loading posts: ${error}`}
                {!loading && posts.length > 0 && `Loaded ${posts.length} top posts`}
            </div>

            {/* Summary Stats */}
            {summaryStats && (
                <section aria-labelledby="summary-title">
                    <Typography variant="h3" id="summary-title" sx={{ fontSize: '1.25rem', mb: 2 }}>
                        Performance Summary
                    </Typography>
                    <Box sx={{ mb: 3, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                        <Card variant="outlined" sx={{ flex: '1 1 200px', minWidth: 200 }}>
                            <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                                    <ViewsIcon color="primary" fontSize="small" aria-hidden="true" />
                                    <Typography variant="caption" color="text.secondary">
                                        Total Views
                                    </Typography>
                                </Box>
                                <Typography variant="h4" sx={{ fontSize: '1.5rem' }}>
                                    {formatNumber(summaryStats.totalViews)}
                                </Typography>
                            </CardContent>
                        </Card>
                        
                        <Card variant="outlined" sx={{ flex: '1 1 200px', minWidth: 200 }}>
                            <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                                    <TrendingUpIcon color="success" fontSize="small" aria-hidden="true" />
                                    <Typography variant="caption" color="text.secondary">
                                        Average Engagement
                                    </Typography>
                                </Box>
                                <Typography variant="h4" sx={{ fontSize: '1.5rem' }}>
                                    {summaryStats.avgEngagement}%
                                </Typography>
                            </CardContent>
                        </Card>
                    </Box>
                </section>
            )}

            {/* Loading State */}
            {loading && (
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', p: 4 }}>
                    <CircularProgress aria-label="Loading posts" />
                    <Typography variant="body2" sx={{ ml: 2 }}>
                        Loading top posts...
                    </Typography>
                </Box>
            )}

            {/* Posts Table */}
            {!loading && posts.length > 0 && (
                <section aria-labelledby="posts-table-title">
                    <Typography variant="h3" id="posts-table-title" className="sr-only">
                        Top Posts Data Table
                    </Typography>
                    <TableContainer>
                        <Table 
                            aria-label="Top performing posts with engagement metrics"
                            role="table"
                        >
                            <caption className="sr-only">
                                List of top performing posts sorted by {sortBy} for the {timeFilter} period.
                                Table shows rank, post content, views, likes, shares, comments, engagement rate, status and publish time.
                            </caption>
                            <TableHead>
                                <TableRow>
                                    <TableCell scope="col">Rank</TableCell>
                                    <TableCell scope="col">Post Content</TableCell>
                                    <TableCell scope="col" align="center">
                                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                                            <ViewsIcon fontSize="small" aria-hidden="true" />
                                            Views
                                        </Box>
                                    </TableCell>
                                    <TableCell scope="col" align="center">
                                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                                            <LikeIcon fontSize="small" aria-hidden="true" />
                                            Likes
                                        </Box>
                                    </TableCell>
                                    <TableCell scope="col" align="center">
                                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                                            <ShareIcon fontSize="small" aria-hidden="true" />
                                            Shares
                                        </Box>
                                    </TableCell>
                                    <TableCell scope="col" align="center">
                                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                                            <CommentIcon fontSize="small" aria-hidden="true" />
                                            Comments
                                        </Box>
                                    </TableCell>
                                    <TableCell scope="col" align="center">Engagement Rate</TableCell>
                                    <TableCell scope="col" align="center">Status</TableCell>
                                    <TableCell scope="col" align="center">Published</TableCell>
                                    <TableCell scope="col" align="center">Actions</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {posts.map((post, index) => {
                                    const badge = getPerformanceBadge(post);
                                    return (
                                        <TableRow 
                                            key={post.id} 
                                            sx={{ 
                                                '&:hover': { bgcolor: 'action.hover' },
                                                bgcolor: index === 0 ? 'action.selected' : 'inherit'
                                            }}
                                        >
                                            <TableCell scope="row">
                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                    {index === 0 && <StarIcon color="warning" fontSize="small" aria-label="Top post" />}
                                                    <Typography variant="body2" fontWeight={index === 0 ? 'bold' : 'normal'}>
                                                        {index + 1}
                                                    </Typography>
                                                </Box>
                                            </TableCell>
                                            <TableCell>
                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, maxWidth: 300 }}>
                                                    {post.thumbnail && (
                                                        <Avatar 
                                                            src={post.thumbnail} 
                                                            alt=""
                                                            variant="rounded"
                                                            sx={{ width: 48, height: 48 }}
                                                            role="presentation"
                                                        />
                                                    )}
                                                    <Box sx={{ flex: 1, minWidth: 0 }}>
                                                        <Typography 
                                                            variant="body2" 
                                                            sx={{ 
                                                                fontWeight: index === 0 ? 'bold' : 'normal',
                                                                overflow: 'hidden',
                                                                textOverflow: 'ellipsis',
                                                                display: '-webkit-box',
                                                                WebkitLineClamp: 2,
                                                                WebkitBoxOrient: 'vertical'
                                                            }}
                                                        >
                                                            {post.title || post.content || 'Post content'}
                                                        </Typography>
                                                        {post.type && (
                                                            <Chip 
                                                                size="small" 
                                                                label={post.type} 
                                                                variant="outlined"
                                                                sx={{ mt: 0.5, height: 20, fontSize: '0.7rem' }}
                                                            />
                                                        )}
                                                    </Box>
                                                </Box>
                                            </TableCell>
                                            <TableCell align="center">
                                                <Typography variant="body2" fontWeight={index === 0 ? 'bold' : 'normal'}>
                                                    {formatNumber(post.views || 0)}
                                                </Typography>
                                            </TableCell>
                                            <TableCell align="center">
                                                <Typography variant="body2">
                                                    {formatNumber(post.likes || 0)}
                                                </Typography>
                                            </TableCell>
                                            <TableCell align="center">
                                                <Typography variant="body2">
                                                    {formatNumber(post.shares || 0)}
                                                </Typography>
                                            </TableCell>
                                            <TableCell align="center">
                                                <Typography variant="body2">
                                                    {formatNumber(post.comments || 0)}
                                                </Typography>
                                            </TableCell>
                                            <TableCell align="center">
                                                <Typography 
                                                    variant="body2" 
                                                    sx={{ 
                                                        fontWeight: 'bold',
                                                        color: parseFloat(calculateEngagementRate(post)) > 5 ? 'success.main' : 'text.primary'
                                                    }}
                                                >
                                                    {calculateEngagementRate(post)}%
                                                </Typography>
                                            </TableCell>
                                            <TableCell align="center">
                                                <Chip 
                                                    size="small" 
                                                    label={badge.label} 
                                                    color={badge.color}
                                                    variant="outlined"
                                                />
                                            </TableCell>
                                            <TableCell align="center">
                                                <Tooltip title={new Date(post.created_at).toLocaleString()}>
                                                    <Typography variant="caption" color="text.secondary">
                                                        {formatDate(post.created_at)}
                                                    </Typography>
                                                </Tooltip>
                                            </TableCell>
                                            <TableCell align="center">
                                                <IconButton
                                                    size="small"
                                                    onClick={(e) => handleMenuClick(e, post.id)}
                                                    aria-label={`Actions for post: ${post.title || 'Untitled'}`}
                                                    aria-haspopup="menu"
                                                >
                                                    <MoreVertIcon fontSize="small" />
                                                </IconButton>
                                            </TableCell>
                                        </TableRow>
                                    );
                                })}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </section>
            )}

            {/* Empty State */}
            {!loading && posts.length === 0 && (
                <Box sx={{ 
                    display: 'flex', 
                    flexDirection: 'column', 
                    alignItems: 'center', 
                    justifyContent: 'center', 
                    height: 300,
                    color: 'text.secondary'
                }}
                role="status"
                aria-label="No posts found"
                >
                    <StarIcon sx={{ fontSize: 64, mb: 2, opacity: 0.5 }} aria-hidden="true" />
                    <Typography variant="h3" gutterBottom sx={{ fontSize: '1.25rem' }}>
                        No Posts Found
                    </Typography>
                    <Typography variant="body2">
                        No top posts are available for the selected time period
                    </Typography>
                </Box>
            )}

            {/* Action Menu */}
            <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleMenuClose}
                aria-labelledby="post-actions-menu"
            >
                <MenuItem onClick={() => handleMenuAction('analyze')}>
                    <span aria-hidden="true">📊</span> View Analysis
                </MenuItem>
                <MenuItem onClick={() => handleMenuAction('edit')}>
                    <span aria-hidden="true">📝</span> Edit Post
                </MenuItem>
                <MenuItem onClick={() => handleMenuAction('share')}>
                    <span aria-hidden="true">📤</span> Share
                </MenuItem>
                <MenuItem onClick={() => handleMenuAction('delete')}>
                    <span aria-hidden="true">🗑️</span> Delete
                </MenuItem>
            </Menu>
        </Paper>
    );
};

export default TopPostsTable;

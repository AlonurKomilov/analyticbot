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

const TopPostsTable = () => {
    const [timeFilter, setTimeFilter] = useState('today');
    const [sortBy, setSortBy] = useState('views');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [posts, setPosts] = useState([]);
    const [anchorEl, setAnchorEl] = useState(null);
    const [selectedPostId, setSelectedPostId] = useState(null);

    // Top posts loading data
    const loadTopPosts = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            
            // Try to fetch from API, fallback to mock data
            try {
                const response = await fetch(`http://localhost:8000/api/v1/analytics/top-posts?period=${timeFilter}&sort=${sortBy}`);
                if (!response.ok) throw new Error('API not available');
                
                const result = await response.json();
                setPosts(result.posts || []);
            } catch {
                // Generate mock data for demonstration
                const mockPosts = generateMockPosts(timeFilter, sortBy);
                setPosts(mockPosts);
            }
        } catch (err) {
            setError(err.message);
            console.error('Top posts malumotlarini olishda xatolik:', err);
        } finally {
            setLoading(false);
        }
    }, [timeFilter, sortBy]);

    // Generate mock posts data
    const generateMockPosts = (timeFilter, sortBy) => {
        const mockPosts = [
            {
                id: 1,
                title: "🚀 AnalyticBot yangi imkoniyatlari: Real-time analytics va AI tavsiyalari",
                content: "Bizning botimiz endi real vaqtda analytics taqdim etadi...",
                type: "📊 Analytics",
                views: 15420,
                likes: 1542,
                shares: 234,
                comments: 89,
                created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
                thumbnail: null
            },
            {
                id: 2,
                title: "💡 Telegram kanalini o'stirish: 10 ta samarali maslahat",
                content: "Kanallaringizni o'stirish uchun eng yaxshi strategiyalar...",
                type: "🎯 Guide",
                views: 12300,
                likes: 987,
                shares: 156,
                comments: 67,
                created_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(), // 5 hours ago
                thumbnail: null
            },
            {
                id: 3,
                title: "🤖 AI yordamida eng yaxshi post vaqtini tanlash",
                content: "Machine Learning algoritmlari sizning auditoriyangiz...",
                type: "🧠 AI/ML",
                views: 9800,
                likes: 756,
                shares: 89,
                comments: 45,
                created_at: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(), // 8 hours ago
                thumbnail: null
            },
            {
                id: 4,
                title: "📱 TWA (Telegram Web App) dasturlash bo'yicha qo'llanma",
                content: "Telegram Web App yaratish va ishlatish bo'yicha...",
                type: "💻 Development",
                views: 7600,
                likes: 456,
                shares: 67,
                comments: 34,
                created_at: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(), // 12 hours ago
                thumbnail: null
            },
            {
                id: 5,
                title: "📈 Kanallaringizning statistikasi: haftalik hisobot",
                content: "Bu haftada eng ko'p ko'rilgan postlar va tendentsiyalar...",
                type: "📊 Report",
                views: 6540,
                likes: 398,
                shares: 45,
                comments: 23,
                created_at: new Date(Date.now() - 18 * 60 * 60 * 1000).toISOString(), // 18 hours ago
                thumbnail: null
            },
            {
                id: 6,
                title: "🛡️ Kanallaringizni himoya qilish: xavfsizlik masalalari",
                content: "Telegram kanallarini spam va zararli foydalanuvchilardan...",
                type: "🔒 Security",
                views: 5430,
                likes: 287,
                shares: 34,
                comments: 19,
                created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(), // 1 day ago
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

    // Component mount and filter when changes load data
    useEffect(() => {
        loadTopPosts();
    }, [loadTopPosts]);

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
            return `${Math.floor(diffInHours * 60)} min oldin`;
        } else if (diffInHours < 24) {
            return `${Math.floor(diffInHours)} soat oldin`;
        } else {
            return `${Math.floor(diffInHours / 24)} kun oldin`;
        }
    };

    // Calculate engagement rate calculation
    const calculateEngagementRate = (post) => {
        const totalEngagement = (post.likes || 0) + (post.shares || 0) + (post.comments || 0);
        const views = post.views || 1;
        return ((totalEngagement / views) * 100).toFixed(1);
    };

    // Get performance badge getting
    const getPerformanceBadge = (post) => {
        const engagementRate = parseFloat(calculateEngagementRate(post));
        const views = post.views || 0;
        
        if (engagementRate > 10 && views > 10000) {
            return { label: '🔥 Viral', color: 'error' };
        } else if (engagementRate > 5) {
            return { label: '⭐ Yuqori', color: 'warning' };
        } else if (engagementRate > 2) {
            return { label: '👍 Yaxshi', color: 'success' };
        } else {
            return { label: '📊 O\'rtacha', color: 'default' };
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
                <Alert severity="error">
                    {error}
                </Alert>
            </Paper>
        );
    }

    return (
        <Paper sx={{ p: 3 }}>
            {/* Header */}
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <StarIcon color="primary" />
                    <Typography variant="h6">
                        Top Posts
                    </Typography>
                </Box>
                
                <Box sx={{ display: 'flex', gap: 2 }}>
                    {/* Time Filter */}
                    <FormControl size="small" sx={{ minWidth: 120 }}>
                        <InputLabel>Vaqt</InputLabel>
                        <Select
                            value={timeFilter}
                            label="Vaqt"
                            onChange={(e) => setTimeFilter(e.target.value)}
                        >
                            <MenuItem value="today">Bugun</MenuItem>
                            <MenuItem value="yesterday">Kecha</MenuItem>
                            <MenuItem value="week">Bu hafta</MenuItem>
                            <MenuItem value="month">Bu oy</MenuItem>
                        </Select>
                    </FormControl>

                    {/* Sort Filter */}
                    <FormControl size="small" sx={{ minWidth: 120 }}>
                        <InputLabel>Tartiblash</InputLabel>
                        <Select
                            value={sortBy}
                            label="Tartiblash"
                            onChange={(e) => setSortBy(e.target.value)}
                        >
                            <MenuItem value="views">Ko'rishlar</MenuItem>
                            <MenuItem value="likes">Yoqtirishlar</MenuItem>
                            <MenuItem value="engagement">Faollik</MenuItem>
                            <MenuItem value="date">Sana</MenuItem>
                        </Select>
                    </FormControl>
                </Box>
            </Box>

            {/* Summary Stats */}
            {summaryStats && (
                <Box sx={{ mb: 3, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                    <Card variant="outlined" sx={{ flex: '1 1 200px', minWidth: 200 }}>
                        <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                                <ViewsIcon color="primary" fontSize="small" />
                                <Typography variant="caption" color="text.secondary">
                                    Jami Ko'rishlar
                                </Typography>
                            </Box>
                            <Typography variant="h6">
                                {formatNumber(summaryStats.totalViews)}
                            </Typography>
                        </CardContent>
                    </Card>
                    
                    <Card variant="outlined" sx={{ flex: '1 1 200px', minWidth: 200 }}>
                        <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                                <TrendingUpIcon color="success" fontSize="small" />
                                <Typography variant="caption" color="text.secondary">
                                    O'rtacha Faollik
                                </Typography>
                            </Box>
                            <Typography variant="h6">
                                {summaryStats.avgEngagement}%
                            </Typography>
                        </CardContent>
                    </Card>
                </Box>
            )}

            {/* Loading State */}
            {loading && (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                    <CircularProgress />
                    <Typography variant="body2" sx={{ ml: 2 }}>
                        Top posts yuklanmoqda...
                    </Typography>
                </Box>
            )}

            {/* Posts Table */}
            {!loading && posts.length > 0 && (
                <TableContainer>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>#</TableCell>
                                <TableCell>Post</TableCell>
                                <TableCell align="center">Ko'rishlar</TableCell>
                                <TableCell align="center">Yoqtirishlar</TableCell>
                                <TableCell align="center">Ulashishlar</TableCell>
                                <TableCell align="center">Izohlar</TableCell>
                                <TableCell align="center">Faollik %</TableCell>
                                <TableCell align="center">Holat</TableCell>
                                <TableCell align="center">Vaqt</TableCell>
                                <TableCell align="center">Amallar</TableCell>
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
                                        <TableCell>
                                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                {index === 0 && <StarIcon color="warning" fontSize="small" />}
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
                                                        variant="rounded"
                                                        sx={{ width: 48, height: 48 }}
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
                                            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                                                <ViewsIcon fontSize="small" color="action" />
                                                <Typography variant="body2" fontWeight={index === 0 ? 'bold' : 'normal'}>
                                                    {formatNumber(post.views || 0)}
                                                </Typography>
                                            </Box>
                                        </TableCell>
                                        <TableCell align="center">
                                            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                                                <LikeIcon fontSize="small" color="error" />
                                                <Typography variant="body2">
                                                    {formatNumber(post.likes || 0)}
                                                </Typography>
                                            </Box>
                                        </TableCell>
                                        <TableCell align="center">
                                            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                                                <ShareIcon fontSize="small" color="primary" />
                                                <Typography variant="body2">
                                                    {formatNumber(post.shares || 0)}
                                                </Typography>
                                            </Box>
                                        </TableCell>
                                        <TableCell align="center">
                                            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                                                <CommentIcon fontSize="small" color="action" />
                                                <Typography variant="body2">
                                                    {formatNumber(post.comments || 0)}
                                                </Typography>
                                            </Box>
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
                                                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                                                    <CalendarIcon fontSize="small" color="action" />
                                                    <Typography variant="caption" color="text.secondary">
                                                        {formatDate(post.created_at)}
                                                    </Typography>
                                                </Box>
                                            </Tooltip>
                                        </TableCell>
                                        <TableCell align="center">
                                            <IconButton
                                                size="small"
                                                onClick={(e) => handleMenuClick(e, post.id)}
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
                }}>
                    <StarIcon sx={{ fontSize: 64, mb: 2, opacity: 0.5 }} />
                    <Typography variant="h6" gutterBottom>
                        Post topilmadi
                    </Typography>
                    <Typography variant="body2">
                        Tanlangan vaqt oralig'ida top postlar mavjud emas
                    </Typography>
                </Box>
            )}

            {/* Action Menu */}
            <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleMenuClose}
            >
                <MenuItem onClick={() => handleMenuAction('analyze')}>
                    📊 Tahlil ko'rish
                </MenuItem>
                <MenuItem onClick={() => handleMenuAction('edit')}>
                    📝 Tahrirlash
                </MenuItem>
                <MenuItem onClick={() => handleMenuAction('share')}>
                    📤 Ulashish
                </MenuItem>
                <MenuItem onClick={() => handleMenuAction('delete')}>
                    🗑️ O'chirish
                </MenuItem>
            </Menu>
        </Paper>
    );
};

export default TopPostsTable;

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
    Box,
    Avatar,
    Chip,
    Typography,
    Tooltip,
    IconButton,
    Menu,
    MenuItem,
    ListItemIcon,
    ListItemText,
    Card,
    CardContent
} from '@mui/material';
import {
    Star as StarIcon,
    TrendingUp as TrendingUpIcon,
    Favorite as LikeIcon,
    Share as ShareIcon,
    Comment as CommentIcon,
    Visibility as ViewsIcon,
    CalendarToday as CalendarIcon,
    Analytics as AnalyticsIcon,
    Edit as EditIcon,
    Delete as DeleteIcon,
    GetApp as DownloadIcon,
    MoreVert as MoreVertIcon
} from '@mui/icons-material';
import { EnhancedDataTable } from './common/EnhancedDataTable';
import { Icon, StatusChip } from './common/IconSystem';
import { useAppStore } from '../store/appStore.js';

/**
 * Enhanced Top Posts Table Component
 * 
 * Professional data table with enterprise-grade features:
 * - Advanced sorting, filtering, and pagination
 * - Export capabilities (CSV, Excel, PDF)
 * - Bulk operations and row actions
 * - Real-time data refresh
 * - Column management and density controls
 * - Full accessibility compliance
 */

const EnhancedTopPostsTable = () => {
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [actionMenuAnchor, setActionMenuAnchor] = useState(null);
    const [selectedPost, setSelectedPost] = useState(null);
    
    // Get store methods and data source
    const { fetchTopPosts, dataSource } = useAppStore();

    // Load posts data
    const loadTopPosts = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            
            // Get fresh store reference to avoid dependency issues
            const { fetchTopPosts } = useAppStore.getState();
            const result = await fetchTopPosts('month', 'views'); // Load all data for enhanced table
            
            // Transform data for enhanced table format
            const transformedPosts = (result.posts || []).map(post => ({
                ...post,
                id: post.id || Math.random().toString(36).substr(2, 9),
                engagement_rate: calculateEngagementRate(post),
                performance_score: getPerformanceScore(post),
                formatted_date: post.created_at ? new Date(post.created_at) : new Date(),
                thumbnail_url: post.thumbnail || null
            }));
            
            setPosts(transformedPosts);
            
        } catch (err) {
            setError(err.message);
            console.error('Error loading top posts:', err);
        } finally {
            setLoading(false);
        }
    }, []);

    // Initial data load
    useEffect(() => {
        loadTopPosts();
    }, [loadTopPosts]);

    // Utility functions
    const formatNumber = (num) => {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num?.toString() || '0';
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

    // Get performance score (0-100)
    const getPerformanceScore = (post) => {
        const engagementRate = parseFloat(calculateEngagementRate(post));
        const views = post.views || 0;
        
        // Weight engagement rate and view count
        const engagementScore = Math.min(engagementRate * 10, 70); // Max 70 points for engagement
        const viewScore = Math.min((views / 1000) * 3, 30); // Max 30 points for views
        
        return Math.round(engagementScore + viewScore);
    };

    // Get performance badge
    const getPerformanceBadge = (post) => {
        const score = post.performance_score || 0;
        
        if (score >= 80) {
            return { label: '🔥 Viral', color: 'error' };
        } else if (score >= 60) {
            return { label: '⭐ High', color: 'warning' };
        } else if (score >= 40) {
            return { label: '👍 Good', color: 'success' };
        } else {
            return { label: '📊 Average', color: 'default' };
        }
    };

    // Column definitions for enhanced table
    const columns = useMemo(() => [
        {
            id: 'rank',
            header: 'Rank',
            accessor: (row, index) => index + 1,
            sortable: false,
            width: 80,
            Cell: ({ value, row }) => (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {value === 1 && <StarIcon color="warning" fontSize="small" />}
                    <Typography variant="body2" fontWeight={value === 1 ? 'bold' : 'normal'}>
                        {value}
                    </Typography>
                </Box>
            )
        },
        {
            id: 'content',
            header: 'Post Content',
            accessor: (row) => row.title || row.content || 'Untitled',
            minWidth: 300,
            Cell: ({ row }) => (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, maxWidth: 400 }}>
                    {row.thumbnail_url && (
                        <Avatar 
                            src={row.thumbnail_url} 
                            alt=""
                            variant="rounded"
                            sx={{ width: 48, height: 48 }}
                        />
                    )}
                    <Box sx={{ flex: 1, minWidth: 0 }}>
                        <Typography 
                            variant="body2" 
                            sx={{ 
                                fontWeight: 'medium',
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                display: '-webkit-box',
                                WebkitLineClamp: 2,
                                WebkitBoxOrient: 'vertical'
                            }}
                        >
                            {row.title || row.content || 'Post content'}
                        </Typography>
                        {row.type && (
                            <Chip 
                                size="small" 
                                label={row.type} 
                                variant="outlined"
                                sx={{ mt: 0.5, height: 20, fontSize: '0.7rem' }}
                            />
                        )}
                    </Box>
                </Box>
            )
        },
        {
            id: 'views',
            header: 'Views',
            accessor: (row) => row.views || 0,
            align: 'center',
            width: 120,
            Cell: ({ value }) => (
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                    <ViewsIcon fontSize="small" color="primary" />
                    <Typography variant="body2" fontWeight="medium">
                        {formatNumber(value)}
                    </Typography>
                </Box>
            )
        },
        {
            id: 'likes',
            header: 'Likes',
            accessor: (row) => row.likes || 0,
            align: 'center',
            width: 100,
            Cell: ({ value }) => (
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                    <LikeIcon fontSize="small" color="error" />
                    <Typography variant="body2">
                        {formatNumber(value)}
                    </Typography>
                </Box>
            )
        },
        {
            id: 'shares',
            header: 'Shares',
            accessor: (row) => row.shares || 0,
            align: 'center',
            width: 100,
            Cell: ({ value }) => (
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                    <ShareIcon fontSize="small" color="info" />
                    <Typography variant="body2">
                        {formatNumber(value)}
                    </Typography>
                </Box>
            )
        },
        {
            id: 'comments',
            header: 'Comments',
            accessor: (row) => row.comments || 0,
            align: 'center',
            width: 100,
            Cell: ({ value }) => (
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                    <CommentIcon fontSize="small" color="success" />
                    <Typography variant="body2">
                        {formatNumber(value)}
                    </Typography>
                </Box>
            )
        },
        {
            id: 'engagement_rate',
            header: 'Engagement',
            accessor: (row) => parseFloat(row.engagement_rate || 0),
            align: 'center',
            width: 120,
            Cell: ({ value }) => (
                <Typography 
                    variant="body2" 
                    sx={{ 
                        fontWeight: 'bold',
                        color: value > 5 ? 'success.main' : value > 2 ? 'warning.main' : 'text.primary'
                    }}
                >
                    {value}%
                </Typography>
            )
        },
        {
            id: 'performance_score',
            header: 'Score',
            accessor: (row) => row.performance_score || 0,
            align: 'center',
            width: 100,
            Cell: ({ value, row }) => {
                const badge = getPerformanceBadge(row);
                return (
                    <Tooltip title={`Performance Score: ${value}/100`}>
                        <Chip 
                            size="small" 
                            label={value}
                            color={badge.color}
                            variant="filled"
                        />
                    </Tooltip>
                );
            }
        },
        {
            id: 'status',
            header: 'Status',
            accessor: (row) => getPerformanceBadge(row),
            align: 'center',
            width: 120,
            sortable: false,
            Cell: ({ value }) => (
                <Chip 
                    size="small" 
                    label={value.label} 
                    color={value.color}
                    variant="outlined"
                />
            )
        },
        {
            id: 'created_at',
            header: 'Published',
            accessor: (row) => row.formatted_date,
            align: 'center',
            width: 120,
            Cell: ({ row }) => (
                <Tooltip title={row.formatted_date?.toLocaleString()}>
                    <Typography variant="caption" color="text.secondary">
                        {formatDate(row.created_at)}
                    </Typography>
                </Tooltip>
            )
        }
    ], []);

    // Row actions configuration
    const rowActions = [
        {
            icon: <AnalyticsIcon />,
            label: 'View Analytics',
            onClick: (row) => console.log('View analytics for:', row.id),
            color: 'primary'
        },
        {
            icon: <EditIcon />,
            label: 'Edit Post',
            onClick: (row) => console.log('Edit post:', row.id),
            color: 'default'
        },
        {
            icon: <DeleteIcon />,
            label: 'Delete Post',
            onClick: (row) => console.log('Delete post:', row.id),
            color: 'error'
        }
    ];

    // Bulk actions configuration
    const bulkActions = [
        {
            label: 'Export Selected',
            icon: <DownloadIcon />,
            onClick: (selectedIds) => console.log('Export posts:', selectedIds),
            color: 'primary'
        },
        {
            label: 'Bulk Edit',
            icon: <EditIcon />,
            onClick: (selectedIds) => console.log('Bulk edit posts:', selectedIds),
            color: 'default'
        },
        {
            label: 'Delete Selected',
            icon: <DeleteIcon />,
            onClick: (selectedIds) => console.log('Delete posts:', selectedIds),
            color: 'error'
        }
    ];

    // Event handlers
    const handleRowClick = (row) => {
        console.log('Row clicked:', row);
        // Could navigate to post detail page
    };

    const handleSelectionChange = (selectedIds) => {
        console.log('Selection changed:', selectedIds);
    };

    const handleSort = (columnId, direction) => {
        console.log('Sort changed:', columnId, direction);
    };

    const handleRefresh = () => {
        loadTopPosts();
    };

    // Summary stats component
    const SummaryStats = useMemo(() => {
        if (!posts || posts.length === 0) return null;

        const totalViews = posts.reduce((sum, post) => sum + (post.views || 0), 0);
        const totalLikes = posts.reduce((sum, post) => sum + (post.likes || 0), 0);
        const totalShares = posts.reduce((sum, post) => sum + (post.shares || 0), 0);
        const totalComments = posts.reduce((sum, post) => sum + (post.comments || 0), 0);
        const avgEngagement = posts.reduce((sum, post) => sum + parseFloat(post.engagement_rate || 0), 0) / posts.length;

        return (
            <Box sx={{ mb: 3, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Card variant="outlined" sx={{ flex: '1 1 200px', minWidth: 200 }}>
                    <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                            <ViewsIcon color="primary" fontSize="small" />
                            <Typography variant="caption" color="text.secondary">
                                Total Views
                            </Typography>
                        </Box>
                        <Typography variant="h4" sx={{ fontSize: '1.5rem' }}>
                            {formatNumber(totalViews)}
                        </Typography>
                    </CardContent>
                </Card>
                
                <Card variant="outlined" sx={{ flex: '1 1 200px', minWidth: 200 }}>
                    <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                            <TrendingUpIcon color="success" fontSize="small" />
                            <Typography variant="caption" color="text.secondary">
                                Average Engagement
                            </Typography>
                        </Box>
                        <Typography variant="h4" sx={{ fontSize: '1.5rem' }}>
                            {avgEngagement.toFixed(1)}%
                        </Typography>
                    </CardContent>
                </Card>
                
                <Card variant="outlined" sx={{ flex: '1 1 200px', minWidth: 200 }}>
                    <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                            <LikeIcon color="error" fontSize="small" />
                            <Typography variant="caption" color="text.secondary">
                                Total Interactions
                            </Typography>
                        </Box>
                        <Typography variant="h4" sx={{ fontSize: '1.5rem' }}>
                            {formatNumber(totalLikes + totalShares + totalComments)}
                        </Typography>
                    </CardContent>
                </Card>
            </Box>
        );
    }, [posts]);

    return (
        <Box sx={{ width: '100%' }}>
            {/* Summary Statistics */}
            {SummaryStats}
            
            {/* Enhanced Data Table */}
            <EnhancedDataTable
                title="Top Performing Posts"
                subtitle={`${posts.length} posts analyzed • Real-time analytics dashboard`}
                data={posts}
                columns={columns}
                loading={loading}
                error={error}
                
                // Table features
                enablePagination={true}
                defaultPageSize={10}
                enableSorting={true}
                defaultSortBy="views"
                defaultSortDirection="desc"
                
                // Search & filtering
                enableSearch={true}
                enableFiltering={true}
                searchPlaceholder="Search posts, content, types..."
                
                // Column management
                enableColumnVisibility={true}
                enableColumnReordering={false}
                
                // Selection & actions
                enableSelection={true}
                enableBulkActions={true}
                bulkActions={bulkActions}
                rowActions={rowActions}
                
                // Export
                enableExport={true}
                exportFilename="top-posts-analytics"
                
                // Real-time features
                enableRefresh={true}
                onRefresh={handleRefresh}
                enableRealTimeUpdates={true}
                refreshInterval={60000} // Refresh every minute
                
                // Density
                enableDensityToggle={true}
                defaultDensity="standard"
                
                // Event handlers
                onRowClick={handleRowClick}
                onSelectionChange={handleSelectionChange}
                onSort={handleSort}
                
                // Accessibility
                tableAriaLabel="Top performing posts analytics table with engagement metrics"
                
                // Styling
                sx={{ 
                    '& .MuiTableHead-root': {
                        bgcolor: 'grey.50'
                    },
                    '& .MuiTableCell-head': {
                        fontWeight: 600,
                        fontSize: '0.875rem'
                    }
                }}
            />
        </Box>
    );
};

export default EnhancedTopPostsTable;
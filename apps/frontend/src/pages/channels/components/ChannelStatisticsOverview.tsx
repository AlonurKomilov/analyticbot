/**
 * Channel Statistics Overview Component
 *
 * Displays aggregate statistics for all channels:
 * - Total channels (active/inactive)
 * - Total subscribers
 * - Total posts
 * - Total views
 */

import React from 'react';
import {
    Box,
    Grid,
    Card,
    CardContent,
    Typography,
    Skeleton
} from '@mui/material';
import {
    Tv as ChannelIcon,
    People as PeopleIcon,
    Article as ArticleIcon,
    Visibility as VisibilityIcon
} from '@mui/icons-material';

export interface AggregateStats {
    total_channels: number;
    total_subscribers: number;
    total_posts: number;
    total_views: number;
    active_channels: number;
    avg_views_per_post: number;
}

interface ChannelStatisticsOverviewProps {
    statistics: AggregateStats | null;
    isLoading: boolean;
}

export const ChannelStatisticsOverview: React.FC<ChannelStatisticsOverviewProps> = ({
    statistics,
    isLoading
}) => {
    if (isLoading) {
        return (
            <Grid container spacing={3} sx={{ mb: 4 }}>
                {[1, 2, 3, 4].map((i) => (
                    <Grid item xs={12} sm={6} md={3} key={i}>
                        <Card elevation={2}>
                            <CardContent>
                                <Skeleton variant="text" width="60%" height={24} />
                                <Skeleton variant="text" width="80%" height={48} sx={{ mt: 1 }} />
                            </CardContent>
                        </Card>
                    </Grid>
                ))}
            </Grid>
        );
    }

    if (!statistics) {
        return null;
    }

    return (
        <Grid container spacing={3} sx={{ mb: 4 }}>
            {/* Total Channels */}
            <Grid item xs={12} sm={6} md={3}>
                <Card
                    elevation={2}
                    sx={{
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        color: 'white',
                        transition: 'transform 0.2s',
                        '&:hover': { transform: 'translateY(-4px)' }
                    }}
                >
                    <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="h6" fontWeight={600}>
                                Total Channels
                            </Typography>
                            <ChannelIcon sx={{ fontSize: 40, opacity: 0.8 }} />
                        </Box>
                        <Typography variant="h3" fontWeight={700}>
                            {statistics.total_channels}
                        </Typography>
                        <Typography variant="body2" sx={{ opacity: 0.9, mt: 0.5 }}>
                            {statistics.active_channels} active
                        </Typography>
                    </CardContent>
                </Card>
            </Grid>

            {/* Total Subscribers */}
            <Grid item xs={12} sm={6} md={3}>
                <Card
                    elevation={2}
                    sx={{
                        background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                        color: 'white',
                        transition: 'transform 0.2s',
                        '&:hover': { transform: 'translateY(-4px)' }
                    }}
                >
                    <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="h6" fontWeight={600}>
                                Total Subscribers
                            </Typography>
                            <PeopleIcon sx={{ fontSize: 40, opacity: 0.8 }} />
                        </Box>
                        <Typography variant="h3" fontWeight={700}>
                            {(statistics.total_subscribers ?? 0).toLocaleString()}
                        </Typography>
                        <Typography variant="body2" sx={{ opacity: 0.9, mt: 0.5 }}>
                            Across all channels
                        </Typography>
                    </CardContent>
                </Card>
            </Grid>

            {/* Total Posts */}
            <Grid item xs={12} sm={6} md={3}>
                <Card
                    elevation={2}
                    sx={{
                        background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
                        color: 'white',
                        transition: 'transform 0.2s',
                        '&:hover': { transform: 'translateY(-4px)' }
                    }}
                >
                    <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="h6" fontWeight={600}>
                                Total Posts
                            </Typography>
                            <ArticleIcon sx={{ fontSize: 40, opacity: 0.8 }} />
                        </Box>
                        <Typography variant="h3" fontWeight={700}>
                            {(statistics.total_posts ?? 0).toLocaleString()}
                        </Typography>
                        <Typography variant="body2" sx={{ opacity: 0.9, mt: 0.5 }}>
                            Published content
                        </Typography>
                    </CardContent>
                </Card>
            </Grid>

            {/* Total Views */}
            <Grid item xs={12} sm={6} md={3}>
                <Card
                    elevation={2}
                    sx={{
                        background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
                        color: 'white',
                        transition: 'transform 0.2s',
                        '&:hover': { transform: 'translateY(-4px)' }
                    }}
                >
                    <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="h6" fontWeight={600}>
                                Total Views
                            </Typography>
                            <VisibilityIcon sx={{ fontSize: 40, opacity: 0.8 }} />
                        </Box>
                        <Typography variant="h3" fontWeight={700}>
                            {(statistics.total_views ?? 0).toLocaleString()}
                        </Typography>
                        <Typography variant="body2" sx={{ opacity: 0.9, mt: 0.5 }}>
                            Avg {(statistics.avg_views_per_post ?? 0).toLocaleString()} per post
                        </Typography>
                    </CardContent>
                </Card>
            </Grid>
        </Grid>
    );
};

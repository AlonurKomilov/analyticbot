/**
 * MetricsSummary Component
 *
 * Displays key performance metrics in a responsive grid layout.
 * Shows total views, average engagement, growth percentage, and peak performance.
 */

import React from 'react';
import { Grid, Paper, Box, Typography } from '@mui/material';
import {
    Visibility as VisibilityIcon,
    Favorite as ReactionIcon,
    Comment as CommentIcon,
    Share as ForwardIcon,
    TrendingUp as TrendingUpIcon,
    Whatshot as PeakIcon,
    BarChart as ChartIcon
} from '@mui/icons-material';

interface SummaryStats {
    totalViews: number;
    totalReactions: number;
    totalComments: number;      // Discussion group comments
    totalReplies?: number;      // Threaded replies (optional)
    totalForwards: number;
    growthPercentage: number;
    peakViews: number;
    totalPosts?: number;
    averageViews?: number;
}

interface MetricsSummaryProps {
    stats: SummaryStats;
}

interface MetricCardProps {
    title: string;
    value: string | number;
    icon: React.ReactElement;
    color: string;
}

const MetricCard: React.FC<MetricCardProps> = React.memo(({ title, value, icon, color }) => (
    <Grid item xs={6} sm={3}>
        <Paper
            elevation={2}
            sx={{
                p: 1.5,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                textAlign: 'center',
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: 4
                }
            }}
        >
            <Box
                sx={{
                    width: 48,
                    height: 48,
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    bgcolor: `${color}.lighter`,
                    color: `${color}.main`,
                    mb: 1
                }}
            >
                {icon}
            </Box>
            <Typography variant="h5" fontWeight={700} gutterBottom>
                {value}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.813rem' }}>
                {title}
            </Typography>
        </Paper>
    </Grid>
));

MetricCard.displayName = 'MetricCard';

const MetricsSummary: React.FC<MetricsSummaryProps> = React.memo(({ stats }) => {
    // Top row metrics (from dashboard - global stats)
    const topMetrics = stats.totalPosts !== undefined ? [
        {
            title: 'Total Posts Analyzed',
            value: stats.totalPosts?.toLocaleString() || '0',
            icon: <ChartIcon fontSize="medium" />,
            color: 'primary'
        },
        {
            title: 'Average Views',
            value: stats.averageViews?.toLocaleString() || '0',
            icon: <VisibilityIcon fontSize="medium" />,
            color: 'success'
        },
        {
            title: 'Growth Rate',
            value: `${stats.growthPercentage >= 0 ? '+' : ''}${stats.growthPercentage.toFixed(1)}%`,
            icon: <TrendingUpIcon fontSize="medium" />,
            color: stats.growthPercentage >= 0 ? 'success' : 'error'
        },
        {
            title: 'Peak Views',
            value: stats.peakViews.toLocaleString(),
            icon: <PeakIcon fontSize="medium" />,
            color: 'warning'
        }
    ] : [];

    // Bottom row metrics (Post View Dynamics specific)
    const bottomMetrics = [
        {
            title: 'Total Views',
            value: stats.totalViews.toLocaleString(),
            icon: <VisibilityIcon fontSize="medium" />,
            color: 'primary'
        },
        {
            title: 'Total Reactions',
            value: stats.totalReactions.toLocaleString(),
            icon: <ReactionIcon fontSize="medium" />,
            color: 'error'
        },
        {
            title: 'Total Forwards',
            value: stats.totalForwards.toLocaleString(),
            icon: <ForwardIcon fontSize="medium" />,
            color: 'success'
        },
        {
            title: 'Total Comments',
            value: stats.totalComments.toLocaleString(),
            icon: <CommentIcon fontSize="medium" />,
            color: 'warning'
        }
    ];

    return (
        <>
            {/* Top row - only show if we have the top stats */}
            {topMetrics.length > 0 && (
                <Grid container spacing={2} sx={{ mb: 2 }}>
                    {topMetrics.map((metric) => (
                        <MetricCard
                            key={metric.title}
                            title={metric.title}
                            value={metric.value}
                            icon={metric.icon}
                            color={metric.color}
                        />
                    ))}
                </Grid>
            )}

            {/* Bottom row */}
            <Grid container spacing={2} sx={{ mb: 2 }}>
                {bottomMetrics.map((metric) => (
                    <MetricCard
                        key={metric.title}
                        title={metric.title}
                        value={metric.value}
                        icon={metric.icon}
                        color={metric.color}
                    />
                ))}
            </Grid>
        </>
    );
});

MetricsSummary.displayName = 'MetricsSummary';

export default MetricsSummary;

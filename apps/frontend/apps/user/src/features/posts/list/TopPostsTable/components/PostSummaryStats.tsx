import React from 'react';
import {
    Grid,
    Typography,
    Box,
    Paper
} from '@mui/material';
import {
    Visibility as VisibilityIcon,
    Favorite as ReactionIcon,
    Share as ShareIcon,
    Comment as CommentIcon
} from '@mui/icons-material';
import { formatNumber } from '@features/posts/list/TopPostsTable/utils/postTableUtils';

interface SummaryStats {
    totalViews: number;
    totalReactions: number;
    totalShares: number;
    totalComments: number;
    avgEngagement: string;
}

interface PostSummaryStatsProps {
    summaryStats: SummaryStats | null;
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
                p: 2,
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
                    width: 56,
                    height: 56,
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    bgcolor: `${color}.lighter`,
                    color: `${color}.main`,
                    mb: 1.5
                }}
            >
                {icon}
            </Box>
            <Typography variant="h4" fontWeight={700} gutterBottom>
                {value}
            </Typography>
            <Typography variant="body2" color="text.secondary">
                {title}
            </Typography>
        </Paper>
    </Grid>
));

MetricCard.displayName = 'MetricCard';

const PostSummaryStats: React.FC<PostSummaryStatsProps> = ({ summaryStats }) => {
    if (!summaryStats) return null;

    const metrics = [
        {
            title: 'Total Views',
            value: formatNumber(summaryStats.totalViews),
            icon: <VisibilityIcon fontSize="large" />,
            color: 'info'  // Blue
        },
        {
            title: 'Total Reactions',
            value: formatNumber(summaryStats.totalReactions),
            icon: <ReactionIcon fontSize="large" />,
            color: 'error'  // Pink/Red
        },
        {
            title: 'Total Forwards',
            value: formatNumber(summaryStats.totalShares),
            icon: <ShareIcon fontSize="large" />,
            color: 'success'  // Green
        },
        {
            title: 'Total Comments',
            value: formatNumber(summaryStats.totalComments),
            icon: <CommentIcon fontSize="large" />,
            color: 'warning'  // Yellow/Orange
        }
    ];

    return (
        <section aria-labelledby="summary-stats-title">
            <Typography variant="h6" component="h2" sx={{ mb: 2, fontWeight: 600 }}>
                Top Posts Analytics
            </Typography>

            <Grid container spacing={3} sx={{ mb: 3 }}>
                {metrics.map((metric) => (
                    <MetricCard
                        key={metric.title}
                        title={metric.title}
                        value={metric.value}
                        icon={metric.icon}
                        color={metric.color}
                    />
                ))}
            </Grid>
        </section>
    );
};

export default PostSummaryStats;

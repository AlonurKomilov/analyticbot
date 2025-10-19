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
    Speed as SpeedIcon,
    TrendingUp as TrendingUpIcon,
    BarChart as ChartIcon
} from '@mui/icons-material';

interface SummaryStats {
    totalViews: number;
    averageEngagement: number;
    growthPercentage: number;
    peakViews: number;
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

const MetricsSummary: React.FC<MetricsSummaryProps> = React.memo(({ stats }) => {
    const metrics = [
        {
            title: 'Total Views',
            value: stats.totalViews.toLocaleString(),
            icon: <VisibilityIcon fontSize="large" />,
            color: 'primary'
        },
        {
            title: 'Average Engagement',
            value: `${stats.averageEngagement.toFixed(1)}%`,
            icon: <SpeedIcon fontSize="large" />,
            color: 'success'
        },
        {
            title: 'Growth Rate',
            value: `${stats.growthPercentage >= 0 ? '+' : ''}${stats.growthPercentage.toFixed(1)}%`,
            icon: <TrendingUpIcon fontSize="large" />,
            color: stats.growthPercentage >= 0 ? 'success' : 'error'
        },
        {
            title: 'Peak Views',
            value: stats.peakViews.toLocaleString(),
            icon: <ChartIcon fontSize="large" />,
            color: 'info'
        }
    ];

    return (
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
    );
});

MetricsSummary.displayName = 'MetricsSummary';

export default MetricsSummary;

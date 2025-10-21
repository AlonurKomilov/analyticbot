/**
 * HeroMetricsSection Component
 *
 * Prominent hero section displaying key performance indicators
 * with visual impact and trend indicators.
 *
 * Quick Win #1: Hero Section with Top-Level KPIs
 */

import React from 'react';
import {
    Box,
    Paper,
    Typography,
    Grid,
    useTheme
} from '@mui/material';
import {
    TrendingUp as TrendingUpIcon,
    TrendingDown as TrendingDownIcon,
    Visibility as ViewsIcon,
    ThumbUp as EngagementIcon,
    Article as PostsIcon,
    Speed as PerformanceIcon
} from '@mui/icons-material';

interface Metric {
    label: string;
    value: string;
    trend?: number; // Percentage change
    icon: React.ReactNode;
    color: string;
}

interface HeroMetricsSectionProps {
    totalViews?: string;
    totalPosts?: string;
    engagementRate?: string;
    growthRate?: number;
}

const HeroMetricsSection: React.FC<HeroMetricsSectionProps> = ({
    totalViews = '124.5K',
    totalPosts = '248',
    engagementRate = '18.7%',
    growthRate = 12.4
}) => {
    const theme = useTheme();

    const metrics: Metric[] = [
        {
            label: 'Total Views',
            value: totalViews,
            trend: growthRate,
            icon: <ViewsIcon sx={{ fontSize: 40 }} />,
            color: theme.palette.primary.main
        },
        {
            label: 'Total Posts',
            value: totalPosts,
            trend: 5.2,
            icon: <PostsIcon sx={{ fontSize: 40 }} />,
            color: theme.palette.success.main
        },
        {
            label: 'Engagement',
            value: engagementRate,
            trend: 8.1,
            icon: <EngagementIcon sx={{ fontSize: 40 }} />,
            color: theme.palette.warning.main
        },
        {
            label: 'Performance',
            value: '94/100',
            trend: 3.5,
            icon: <PerformanceIcon sx={{ fontSize: 40 }} />,
            color: theme.palette.error.main
        }
    ];

    return (
        <Paper
            elevation={3}
            sx={{
                mb: 3,
                background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
                position: 'relative',
                overflow: 'hidden',
                '&::before': {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background: 'url("data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%23ffffff" fill-opacity="0.05"%3E%3Cpath d="M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")',
                    opacity: 0.1
                }
            }}
        >
            <Box sx={{ p: 4, position: 'relative', zIndex: 1 }}>
                <Typography
                    variant="h4"
                    sx={{
                        color: 'white',
                        fontWeight: 700,
                        mb: 1,
                        textShadow: '0 2px 4px rgba(0,0,0,0.2)'
                    }}
                >
                    Analytics Overview
                </Typography>
                <Typography
                    variant="body1"
                    sx={{
                        color: 'rgba(255,255,255,0.9)',
                        mb: 3
                    }}
                >
                    Real-time performance metrics for your content
                </Typography>

                <Grid container spacing={3}>
                    {metrics.map((metric, index) => (
                        <Grid item xs={12} sm={6} md={3} key={index}>
                            <Box
                                sx={{
                                    bgcolor: 'rgba(255,255,255,0.15)',
                                    backdropFilter: 'blur(10px)',
                                    borderRadius: 2,
                                    p: 3,
                                    border: '1px solid rgba(255,255,255,0.2)',
                                    transition: 'all 0.3s ease',
                                    '&:hover': {
                                        bgcolor: 'rgba(255,255,255,0.25)',
                                        transform: 'translateY(-4px)',
                                        boxShadow: '0 8px 24px rgba(0,0,0,0.2)'
                                    }
                                }}
                            >
                                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                    <Box
                                        sx={{
                                            color: 'white',
                                            opacity: 0.9
                                        }}
                                    >
                                        {metric.icon}
                                    </Box>
                                </Box>

                                <Typography
                                    variant="h3"
                                    sx={{
                                        color: 'white',
                                        fontWeight: 700,
                                        mb: 0.5,
                                        textShadow: '0 2px 4px rgba(0,0,0,0.2)'
                                    }}
                                >
                                    {metric.value}
                                </Typography>

                                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                    <Typography
                                        variant="body2"
                                        sx={{
                                            color: 'rgba(255,255,255,0.9)',
                                            fontWeight: 500
                                        }}
                                    >
                                        {metric.label}
                                    </Typography>

                                    {metric.trend !== undefined && (
                                        <Box
                                            sx={{
                                                display: 'flex',
                                                alignItems: 'center',
                                                gap: 0.5,
                                                bgcolor: metric.trend >= 0 ? 'rgba(76, 175, 80, 0.3)' : 'rgba(244, 67, 54, 0.3)',
                                                px: 1,
                                                py: 0.5,
                                                borderRadius: 1
                                            }}
                                        >
                                            {metric.trend >= 0 ? (
                                                <TrendingUpIcon sx={{ fontSize: 16, color: 'white' }} />
                                            ) : (
                                                <TrendingDownIcon sx={{ fontSize: 16, color: 'white' }} />
                                            )}
                                            <Typography
                                                variant="caption"
                                                sx={{
                                                    color: 'white',
                                                    fontWeight: 600
                                                }}
                                            >
                                                {Math.abs(metric.trend)}%
                                            </Typography>
                                        </Box>
                                    )}
                                </Box>
                            </Box>
                        </Grid>
                    ))}
                </Grid>
            </Box>
        </Paper>
    );
};

export default HeroMetricsSection;

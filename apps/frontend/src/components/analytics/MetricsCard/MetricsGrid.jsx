import React from 'react';
import {
    Grid,
    Box,
    Avatar,
    Typography
} from '@mui/material';
import {
    Visibility as ViewsIcon,
    ThumbUp as EngagementIcon,
    Star as StarIcon
} from '@mui/icons-material';
import { getTrendIcon, formatMetricValue } from './metricsUtils.jsx';

const MetricsGrid = React.memo(({ metrics }) => {
    const {
        totalViews = 0,
        growthRate = 0,
        engagementRate = 0,
        performanceScore = 0
    } = metrics;

    return (
        <Grid container spacing={2}>
            {/* Total Views */}
            <Grid item xs={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                    <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', mx: 'auto', mb: 1 }}>
                        <ViewsIcon />
                    </Avatar>
                    <Typography variant="h5" fontWeight="bold">
                        {formatMetricValue(totalViews, 'compact')}
                    </Typography>
                    <Typography variant="caption" sx={{ opacity: 0.9 }}>
                        Total Views
                    </Typography>
                </Box>
            </Grid>

            {/* Growth Rate */}
            <Grid item xs={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                    <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', mx: 'auto', mb: 1 }}>
                        {getTrendIcon(growthRate)}
                    </Avatar>
                    <Typography variant="h5" fontWeight="bold">
                        {growthRate > 0 ? '+' : ''}{formatMetricValue(growthRate, 'percentage')}
                    </Typography>
                    <Typography variant="caption" sx={{ opacity: 0.9 }}>
                        Growth Rate
                    </Typography>
                </Box>
            </Grid>

            {/* Engagement Rate */}
            <Grid item xs={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                    <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', mx: 'auto', mb: 1 }}>
                        <EngagementIcon />
                    </Avatar>
                    <Typography variant="h5" fontWeight="bold">
                        {formatMetricValue(engagementRate, 'percentage')}
                    </Typography>
                    <Typography variant="caption" sx={{ opacity: 0.9 }}>
                        Engagement
                    </Typography>
                </Box>
            </Grid>

            {/* Performance Score */}
            <Grid item xs={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                    <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', mx: 'auto', mb: 1 }}>
                        <StarIcon />
                    </Avatar>
                    <Typography variant="h5" fontWeight="bold">
                        {formatMetricValue(performanceScore, 'score')}
                    </Typography>
                    <Typography variant="caption" sx={{ opacity: 0.9 }}>
                        Performance
                    </Typography>
                </Box>
            </Grid>
        </Grid>
    );
});

MetricsGrid.displayName = 'MetricsGrid';

export default MetricsGrid;
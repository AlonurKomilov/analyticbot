import React from 'react';
import {
    Grid,
    Card,
    CardContent,
    Typography,
    Box
} from '@mui/material';
import {
    Visibility as VisibilityIcon,
    Speed as SpeedIcon,
    TrendingUp as TrendingUpIcon,
    BarChart as ChartIcon
} from '@mui/icons-material';

/**
 * MetricsSummary - Memoized summary statistics grid for chart metrics
 *
 * Displays key metrics (total views, average, growth rate, peak views) in a responsive grid.
 * Optimized for multi-user performance by preventing unnecessary re-renders when
 * parent component state changes but summary stats remain the same.
 *
 * @param {Object} props - Component props
 * @param {Object} props.summaryStats - Summary statistics object
 * @param {number} props.summaryStats.totalViews - Total post views
 * @param {number} props.summaryStats.averageViews - Average views per post
 * @param {number} props.summaryStats.growthRate - Growth rate percentage
 * @param {number} props.summaryStats.peakViews - Peak views recorded
 */
const MetricsSummary = React.memo(({ summaryStats }) => {
    if (!summaryStats) {
        return null;
    }

    return (
        <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={6} sm={3}>
                <Card variant="outlined">
                    <CardContent variant="metric">
                        <Box variant="iconText">
                            <VisibilityIcon color="primary" fontSize="small" />
                            <Typography variant="caption" color="text.secondary">
                                Total Views
                            </Typography>
                        </Box>
                        <Typography variant="h6">
                            {summaryStats.totalViews.toLocaleString()}
                        </Typography>
                    </CardContent>
                </Card>
            </Grid>

            <Grid item xs={6} sm={3}>
                <Card variant="outlined">
                    <CardContent variant="metric">
                        <Box variant="iconText">
                            <SpeedIcon color="secondary" fontSize="small" />
                            <Typography variant="caption" color="text.secondary">
                                Average
                            </Typography>
                        </Box>
                        <Typography variant="h6">
                            {summaryStats.averageViews.toLocaleString()}
                        </Typography>
                    </CardContent>
                </Card>
            </Grid>

            <Grid item xs={6} sm={3}>
                <Card variant="outlined">
                    <CardContent variant="metric">
                        <Box variant="iconText">
                            <TrendingUpIcon color="success" fontSize="small" />
                            <Typography variant="caption" color="text.secondary">
                                Growth %
                            </Typography>
                        </Box>
                        <Typography variant="h6" sx={{
                            color: summaryStats.growthRate >= 0 ? 'success.main' : 'error.main'
                        }}>
                            {summaryStats.growthRate > 0 ? '+' : ''}{summaryStats.growthRate}%
                        </Typography>
                    </CardContent>
                </Card>
            </Grid>

            <Grid item xs={6} sm={3}>
                <Card variant="outlined">
                    <CardContent variant="metric">
                        <Box variant="iconText">
                            <ChartIcon color="warning" fontSize="small" />
                            <Typography variant="caption" color="text.secondary">
                                Peak Views
                            </Typography>
                        </Box>
                        <Typography variant="h6">
                            {summaryStats.peakViews.toLocaleString()}
                        </Typography>
                    </CardContent>
                </Card>
            </Grid>
        </Grid>
    );
});

MetricsSummary.displayName = 'MetricsSummary';

export default MetricsSummary;

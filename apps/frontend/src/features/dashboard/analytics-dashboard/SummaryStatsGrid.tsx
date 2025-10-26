import React from 'react';
import {
    Grid,
    Card,
    CardContent,
    Typography,
    Alert
} from '@mui/material';

interface Stats {
    totalPosts: string;
    averageViews: string;
    engagementRate: string;
    peakViews: string;
}

interface SummaryStatsGridProps {
    stats?: Stats;
}

/**
 * SummaryStatsGrid Component
 *
 * Extracted from AnalyticsDashboard.jsx (Phase 3.1)
 * Displays dashboard summary statistics in responsive grid
 *
 * Responsibilities:
 * - Four main statistics cards (Posts, Views, Engagement, Peak Views)
 * - Responsive grid layout (stacks on mobile, 4 columns on desktop)
 * - Consistent card styling and colors
 * - Centered text alignment for readability
 */
const SummaryStatsGrid: React.FC<SummaryStatsGridProps> = React.memo(({
    stats
}) => {
    // Show message if no stats (no channel selected)
    if (!stats || stats.totalPosts === '—') {
        return (
            <Alert severity="info" sx={{ mb: 3 }}>
                Please select a channel to view analytics summary
            </Alert>
        );
    }

    return (
        <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} md={3}>
                <Card sx={{ textAlign: 'center', height: '100%' }}>
                    <CardContent>
                        <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
                            {stats.totalPosts}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            Total Posts Analyzed
                        </Typography>
                    </CardContent>
                </Card>
            </Grid>

            <Grid item xs={12} md={3}>
                <Card sx={{ textAlign: 'center', height: '100%' }}>
                    <CardContent>
                        <Typography variant="h4" color="success.main" sx={{ fontWeight: 'bold' }}>
                            {stats.averageViews}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            Average Views
                        </Typography>
                    </CardContent>
                </Card>
            </Grid>

            <Grid item xs={12} md={3}>
                <Card sx={{ textAlign: 'center', height: '100%' }}>
                    <CardContent>
                        <Typography variant="h4" color="warning.main" sx={{ fontWeight: 'bold' }}>
                            {stats.engagementRate}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            Engagement Rate
                        </Typography>
                    </CardContent>
                </Card>
            </Grid>

            <Grid item xs={12} md={3}>
                <Card sx={{ textAlign: 'center', height: '100%' }}>
                    <CardContent>
                        <Typography variant="h4" color="error.main" sx={{ fontWeight: 'bold' }}>
                            {stats.peakViews}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            Peak Views Today
                        </Typography>
                    </CardContent>
                </Card>
            </Grid>
        </Grid>
    );
});

SummaryStatsGrid.displayName = 'SummaryStatsGrid';

export default SummaryStatsGrid;

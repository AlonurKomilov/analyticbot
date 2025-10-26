import React from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography
} from '@mui/material';
import {
    Visibility as ViewsIcon,
    TrendingUp as TrendingUpIcon
} from '@mui/icons-material';
import { formatNumber } from '@features/posts/list/TopPostsTable/utils/postTableUtils';

interface SummaryStats {
    totalViews: number;
    avgEngagement: number;
}

interface PostSummaryStatsProps {
    summaryStats: SummaryStats | null;
}

const PostSummaryStats: React.FC<PostSummaryStatsProps> = ({ summaryStats }) => {
    if (!summaryStats) return null;

    return (
        <section aria-labelledby="summary-stats-title" style={{ marginBottom: '24px' }}>
            <Typography variant="h3" id="summary-stats-title" className="sr-only">
                Posts Summary Statistics
            </Typography>

            <Box
                sx={{
                    display: 'flex',
                    gap: 2,
                    mb: 3,
                    flexWrap: 'wrap',
                    '& > *': { flex: '1 1 200px', minWidth: 200 }
                }}
            >
                <Card variant="outlined">
                    <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                            <ViewsIcon color="primary" fontSize="small" aria-hidden="true" />
                            <Typography variant="caption" color="text.secondary">
                                Total Views
                            </Typography>
                        </Box>
                        <Typography variant="h4" sx={{ fontSize: '1.5rem' }}>
                            {formatNumber(summaryStats.totalViews)}
                        </Typography>
                    </CardContent>
                </Card>

                <Card variant="outlined">
                    <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                            <TrendingUpIcon color="success" fontSize="small" aria-hidden="true" />
                            <Typography variant="caption" color="text.secondary">
                                Average Engagement
                            </Typography>
                        </Box>
                        <Typography variant="h4" sx={{ fontSize: '1.5rem' }}>
                            {summaryStats.avgEngagement}%
                        </Typography>
                    </CardContent>
                </Card>
            </Box>
        </section>
    );
};

export default PostSummaryStats;

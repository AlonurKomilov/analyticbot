/**
 * BestTimeRecommender Component
 *
 * Complete recommender interface that displays optimal posting times
 * based on historical performance data and AI analysis.
 */

import React, { useState } from 'react';
import { Box, Paper, Typography, Alert, CircularProgress } from '@mui/material';
import TimeFrameFilters, { TimeFrame, ContentType } from './components/TimeFrameFilters';
import BestTimeCards from './components/BestTimeCards';
import AIInsightsPanel from './components/AIInsightsPanel';
import RecommenderFooter from './components/RecommenderFooter';

const BestTimeRecommender: React.FC = () => {
    const [timeFrame, setTimeFrame] = useState<TimeFrame>('month');
    const [contentType, setContentType] = useState<ContentType>('all');
    const [isLoading] = useState(false);
    const [error] = useState<string | null>(null);
    const [recommendations] = useState<any>(null);
    const [heatmapData] = useState<any>(null);
    const [aiInsights] = useState<any>(null);

    if (error) {
        return (
            <Paper sx={{ p: 3 }}>
                <Alert severity="error">
                    <Typography variant="body2" fontWeight={600}>
                        Failed to load recommendations
                    </Typography>
                    <Typography variant="body2">
                        {error}
                    </Typography>
                </Alert>
            </Paper>
        );
    }

    return (
        <Paper sx={{ p: 3 }}>
            {/* Header */}
            <Typography variant="h5" gutterBottom fontWeight={600}>
                Best Time to Post Recommender
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
                AI-powered analysis of your channel's performance to identify optimal posting times
            </Typography>

            {/* Filters */}
            <TimeFrameFilters
                timeFrame={timeFrame}
                setTimeFrame={setTimeFrame}
                contentType={contentType}
                setContentType={setContentType}
            />

            {/* Loading State */}
            {isLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
                    <CircularProgress aria-label="Loading recommendations" />
                </Box>
            ) : (
                <>
                    {/* Best Time Cards */}
                    {recommendations && recommendations.length > 0 ? (
                        <BestTimeCards recommendations={recommendations} />
                    ) : (
                        <Alert severity="info" sx={{ my: 2 }}>
                            No recommendations available for the selected filters
                        </Alert>
                    )}

                    {/* Heatmap Visualization */}
                    {heatmapData && (
                        <Box sx={{ mt: 3 }}>
                            {/* HeatmapVisualization removed - component not available */}
                        </Box>
                    )}

                    {/* AI Insights */}
                    {aiInsights && (
                        <Box sx={{ mt: 3 }}>
                            <AIInsightsPanel aiInsights={aiInsights} />
                        </Box>
                    )}

                    {/* Footer */}
                    <RecommenderFooter recommendations={recommendations} />
                </>
            )}
        </Paper>
    );
};

export default BestTimeRecommender;

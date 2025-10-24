/**
 * BestTimeRecommender Component
 *
 * Complete recommender interface that displays optimal posting times
 * based on historical performance data and AI analysis.
 */

import React from 'react';
import { Box, Paper, Typography, Alert, CircularProgress } from '@mui/material';
import TimeFrameFilters, { TimeFrame, ContentType } from './components/TimeFrameFilters';
import BestTimeCards from './components/BestTimeCards';
import AIInsightsPanel from './components/AIInsightsPanel';
import RecommenderFooter from './components/RecommenderFooter';
import { useRecommenderLogic } from './hooks/useRecommenderLogic';

const BestTimeRecommender: React.FC = () => {
    const {
        timeFrame,
        contentType,
        loading,
        error,
        recommendations,
        aiInsights,
        setTimeFrame,
        setContentType
    } = useRecommenderLogic();

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
                timeFrame={timeFrame as TimeFrame}
                setTimeFrame={(tf) => setTimeFrame(tf)}
                contentType={contentType as ContentType}
                setContentType={(ct) => setContentType(ct)}
            />

            {/* Loading State */}
            {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
                    <CircularProgress aria-label="Loading recommendations" />
                </Box>
            ) : (
                <>
                    {/* Best Time Cards */}
                    {recommendations && recommendations.best_times && recommendations.best_times.length > 0 ? (
                        <BestTimeCards recommendations={recommendations as any} />
                    ) : (
                        <Alert severity="info" sx={{ my: 2 }}>
                            No recommendations available for the selected filters
                        </Alert>
                    )}

                    {/* AI Insights */}
                    {aiInsights && aiInsights.length > 0 && (
                        <Box sx={{ mt: 3 }}>
                            <AIInsightsPanel aiInsights={aiInsights} />
                        </Box>
                    )}

                    {/* Footer */}
                    <RecommenderFooter recommendations={recommendations || undefined} />
                </>
            )}
        </Paper>
    );
};

export default BestTimeRecommender;

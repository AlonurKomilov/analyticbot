import React from 'react';
import {
    Paper,
    CircularProgress,
    Alert,
    Box,
    Typography
} from '@mui/material';
import { Schedule as ScheduleIcon } from '@mui/icons-material';
import TimeFrameFilters from './components/TimeFrameFilters.jsx';
import BestTimeCards from './components/BestTimeCards.jsx';
import HeatmapVisualization from './components/HeatmapVisualization.jsx';
import AIInsightsPanel from './components/AIInsightsPanel.jsx';
import RecommenderFooter from './components/RecommenderFooter.jsx';
import { useRecommenderLogic } from './hooks/useRecommenderLogic.js';
import EmptyState from '../../EmptyState.jsx';

const BestTimeRecommender = () => {
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

    return (
        <Paper sx={{ p: 3, borderRadius: 2 }}>
            {/* Filters */}
            <TimeFrameFilters
                timeFrame={timeFrame}
                setTimeFrame={setTimeFrame}
                contentType={contentType}
                setContentType={setContentType}
            />

            {/* Error State */}
            {error && (
                <Alert
                    severity="warning"
                    sx={{ mb: 2 }}
                    aria-live="polite"
                >
                    {error.includes('Authentication')
                        ? 'Unable to load recommendations. Please check your connection or switch to Demo mode to explore features.'
                        : error}
                </Alert>
            )}

            {/* Loading State */}
            {loading && (
                <Box sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    p: 4
                }}>
                    <CircularProgress aria-label="Loading recommendations" />
                    <Typography variant="body2" sx={{ ml: 2 }}>
                        Loading AI recommendations...
                    </Typography>
                </Box>
            )}

            {/* Main Content */}
            {!loading && recommendations && (
                <>
                    {/* Best Time Cards */}
                    <BestTimeCards recommendations={recommendations} />

                    {/* Heatmap Visualization */}
                    <HeatmapVisualization recommendations={recommendations} />

                    {/* AI Insights Panel */}
                    <AIInsightsPanel aiInsights={aiInsights} />

                    {/* Footer */}
                    <RecommenderFooter recommendations={recommendations} />
                </>
            )}

            {/* No Data State - Show when not loading and no recommendations */}
            {!loading && !recommendations && (
                <EmptyState
                    message={error
                        ? "No data available. Please connect your channel or switch to Demo mode to see sample recommendations."
                        : "Wait for data collection to get AI-powered posting time recommendations"}
                    icon={<ScheduleIcon sx={{ fontSize: 48, color: 'text.secondary' }} />}
                />
            )}
        </Paper>
    );
};

export default BestTimeRecommender;

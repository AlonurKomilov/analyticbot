import React from 'react';
import {
    Paper,
    CircularProgress,
    Alert,
    Box,
    Typography
} from '@mui/material';
import TimeFrameFilters from './components/TimeFrameFilters.jsx';
import BestTimeCards from './components/BestTimeCards.jsx';
import HeatmapVisualization from './components/HeatmapVisualization.jsx';
import AIInsightsPanel from './components/AIInsightsPanel.jsx';
import RecommenderFooter from './components/RecommenderFooter.jsx';
import { useRecommenderLogic } from './hooks/useRecommenderLogic.js';

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
                    severity="error"
                    sx={{ mb: 2 }}
                    aria-live="polite"
                >
                    {error}
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
                        AI tavsiyalar yuklanmoqda...
                    </Typography>
                </Box>
            )}

            {/* Main Content */}
            {!loading && (
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

            {/* No Data State */}
            {!loading && !recommendations && !error && (
                <Box sx={{ textAlign: 'center', p: 4 }}>
                    <Typography variant="h6" color="text.secondary" gutterBottom>
                        Ma'lumotlar mavjud emas
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        AI tavsiyalarini olish uchun ma'lumotlarni kuting.
                    </Typography>
                </Box>
            )}
        </Paper>
    );
};

export default BestTimeRecommender;

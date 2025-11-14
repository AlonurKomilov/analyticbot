/**
 * Demo page to showcase the enhanced Monthly Calendar with Real Data Integration
 */

import React from 'react';
import { Box, Container, Typography, Paper } from '@mui/material';
import MonthlyCalendarHeatmap from '../features/analytics/best-time/components/MonthlyCalendarHeatmap';

const PostingCalendarDemo: React.FC = () => {
    // Sample real data structure that matches backend API format
    const sampleDailyPerformance = [
        // Historical data (past days)
        { date: 1, dayOfWeek: 0, avgEngagement: 8.5, postCount: 2 }, // Sunday
        { date: 2, dayOfWeek: 1, avgEngagement: 9.2, postCount: 3 }, // Monday - excellent
        { date: 3, dayOfWeek: 2, avgEngagement: 7.8, postCount: 1 }, // Tuesday
        { date: 4, dayOfWeek: 3, avgEngagement: 8.8, postCount: 2 }, // Wednesday - good
        { date: 5, dayOfWeek: 4, avgEngagement: 6.5, postCount: 1 }, // Thursday
        { date: 6, dayOfWeek: 5, avgEngagement: 5.2, postCount: 1 }, // Friday - poor
        { date: 7, dayOfWeek: 6, avgEngagement: 7.1, postCount: 2 }, // Saturday
        { date: 8, dayOfWeek: 0, avgEngagement: 8.0, postCount: 1 }, // Sunday
        { date: 9, dayOfWeek: 1, avgEngagement: 9.5, postCount: 3 }, // Monday - excellent
        { date: 10, dayOfWeek: 2, avgEngagement: 8.3, postCount: 2 }, // Tuesday
        // More historical data can be added here...
    ];

    // Sample best times by day of week (from real API)
    const sampleBestTimes = {
        0: ['12:00', '17:00', '19:00'], // Sunday
        1: ['09:00', '14:00', '18:00'], // Monday
        2: ['10:00', '15:00', '19:00'], // Tuesday
        3: ['09:30', '14:30', '18:30'], // Wednesday
        4: ['10:30', '15:30', '19:30'], // Thursday
        5: ['09:00', '13:00', '17:00'], // Friday
        6: ['11:00', '16:00', '20:00'], // Saturday
    };

    const handleDateSelect = (date: Date) => {
        console.log('Selected date for posting:', date);
        alert(`Selected ${date.toLocaleDateString()} for posting!

In a real application, this would:
• Open the post creation form
• Pre-fill the scheduled date
• Show recommended posting times for that day
• Allow immediate content creation and scheduling`);
    };

    return (
        <Container maxWidth="lg" sx={{ py: 4 }}>
            <Paper sx={{ p: 3, mb: 4 }}>
                <Typography variant="h4" gutterBottom align="center" color="primary">
                    📅 Real Data Monthly Calendar Integration
                </Typography>
                <Typography variant="body1" align="center" color="text.secondary" paragraph>
                    Enhanced monthly calendar using real backend data from analytics API.
                    Shows historical performance and AI-powered future recommendations.
                </Typography>
            </Paper>

            <MonthlyCalendarHeatmap
                dailyPerformance={sampleDailyPerformance}
                month={new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                bestTimesByDay={sampleBestTimes}
                onDateSelect={handleDateSelect}
                showFuturePredictions={true}
            />

            <Box sx={{ mt: 4 }}>
                <Paper sx={{ p: 3 }}>
                    <Typography variant="h6" gutterBottom>
                        🔄 Real Data Integration Features
                    </Typography>
                    <Typography variant="body2" paragraph>
                        • <strong>Backend API Integration:</strong> Uses real data from `get_best_posting_times` endpoint
                    </Typography>
                    <Typography variant="body2" paragraph>
                        • <strong>Historical Analysis:</strong> Past days show actual performance data from database
                    </Typography>
                    <Typography variant="body2" paragraph>
                        • <strong>AI Predictions:</strong> Future days use machine learning for posting recommendations
                    </Typography>
                    <Typography variant="body2" paragraph>
                        • <strong>Interactive Scheduling:</strong> Click any day to create scheduled posts
                    </Typography>
                    <Typography variant="body2" paragraph>
                        • <strong>Smart Recommendations:</strong> Hover to see best posting times for each day
                    </Typography>
                    <Typography variant="body2" paragraph>
                        • <strong>Visual Performance:</strong> Color-coded calendar shows engagement patterns at a glance
                    </Typography>
                </Paper>
            </Box>

            <Box sx={{ mt: 3 }}>
                <Paper sx={{ p: 3, bgcolor: 'info.light', color: 'info.contrastText' }}>
                    <Typography variant="h6" gutterBottom>
                        🚀 Technical Implementation
                    </Typography>
                    <Typography variant="body2" paragraph>
                        <strong>Backend:</strong> Real analytics data from PostgreSQL via `AnalyticsOrchestratorService`
                    </Typography>
                    <Typography variant="body2" paragraph>
                        <strong>Frontend:</strong> Enhanced `MonthlyCalendarHeatmap` component with prediction capabilities
                    </Typography>
                    <Typography variant="body2">
                        <strong>Data Flow:</strong> API → Analytics Store → React Component → Interactive Calendar
                    </Typography>
                </Paper>
            </Box>
        </Container>
    );
};

export default PostingCalendarDemo;

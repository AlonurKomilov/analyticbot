/**
 * BestTimeRecommender Component
 *
 * Complete recommender interface that displays optimal posting times
 * based on historical performance data and AI analysis.
 */

import React, { useState } from 'react';
import { Box, Paper, Typography, Alert, CircularProgress, Tabs, Tab } from '@mui/material';
import TimeFrameFilters, { TimeFrame, ContentType } from './components/TimeFrameFilters';
import BestTimeCards from './components/BestTimeCards';
import AIInsightsPanel from './components/AIInsightsPanel';
import RecommenderFooter from './components/RecommenderFooter';
import EngagementTrendChart from './components/EngagementTrendChart';
import ComparisonCard from './components/ComparisonCard';
import MonthlyCalendarHeatmap from './components/MonthlyCalendarHeatmap';
import { useRecommenderLogic } from './hooks/useRecommenderLogic';
import { useChannelStore } from '@store';
import { useNavigate } from 'react-router-dom';

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
    
    const { selectedChannel } = useChannelStore();
    const navigate = useNavigate();
    const [currentTab, setCurrentTab] = useState(0);

    // Process real data from backend API
    const calendarData = React.useMemo(() => {
        // Use daily_performance data from the real backend API response
        const dailyPerformance = (recommendations as any)?.daily_performance || [];
        
        console.log('📅 Processing calendar data:', dailyPerformance);
        
        // Convert backend format to component format
        return dailyPerformance.map((day: any) => ({
            date: day.date,
            dayOfWeek: day.dayOfWeek || day.day_of_week,
            avgEngagement: day.avgEngagement || day.avg_engagement,
            postCount: day.postCount || day.post_count
        }));
    }, [(recommendations as any)?.daily_performance]);

    // Extract best times by day from real recommendations
    const bestTimesByDay = React.useMemo(() => {
        if (!recommendations?.best_times) return {};
        
        const timesByDay: Record<number, string[]> = {};
        
        // Group times by day of week
        recommendations.best_times.forEach((time: any) => {
            const day = time.day;
            const hour = time.hour;
            if (day !== undefined && hour !== undefined) {
                if (!timesByDay[day]) timesByDay[day] = [];
                timesByDay[day].push(`${hour.toString().padStart(2, '0')}:00`);
            }
        });
        
        // Fill in intelligent fallbacks for days without specific recommendations
        // Use the most common times from available data, or industry standard times
        const allTimes = Object.values(timesByDay).flat();
        const fallbackTimes = allTimes.length > 0 ? 
            // Use the 3 most common times from actual data
            [...new Set(allTimes)].slice(0, 3) : 
            // Only if no data at all, use research-based optimal times
            ['10:00', '15:00', '20:00']; // Updated from 09:00, 14:00, 18:00
        
        for (let day = 0; day < 7; day++) {
            if (!timesByDay[day] || timesByDay[day].length === 0) {
                timesByDay[day] = fallbackTimes;
            }
        }
        
        return timesByDay;
    }, [recommendations]);

    const handleDateSelect = (date: Date) => {
        // Navigate to create post page with pre-selected date
        navigate(`/posts/create?scheduledDate=${date.toISOString()}`);
    };

    const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
        setCurrentTab(newValue);
    };

    return (
        <Paper sx={{ p: 3 }}>
            {/* Header */}
            <Typography variant="h5" gutterBottom fontWeight={600}>
                Best Time to Post Recommender
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
                Performance-based analysis of your channel's historical data to identify optimal posting times
            </Typography>

            {/* Filters */}
            <TimeFrameFilters
                timeFrame={timeFrame as TimeFrame}
                setTimeFrame={(tf) => setTimeFrame(tf)}
                contentType={contentType as ContentType}
                setContentType={(ct) => setContentType(ct)}
            />

            {/* Tabs */}
            <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
                <Tabs value={currentTab} onChange={handleTabChange} aria-label="recommendation views">
                    <Tab label="📊 Performance Charts" />
                    <Tab label="📅 Monthly Calendar" />
                </Tabs>
            </Box>

            {/* Loading State */}
            {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
                    <CircularProgress aria-label="Loading recommendations" />
                </Box>
            ) : error ? (
                <Alert severity="error">
                    <Typography variant="body2" fontWeight={600}>
                        Failed to load recommendations
                    </Typography>
                    <Typography variant="body2">
                        {error}
                    </Typography>
                </Alert>
            ) : (
                <>
                    {/* Tab Content */}
                    {currentTab === 0 ? (
                        // Performance Charts Tab
                        <>
                            {recommendations && recommendations.best_times && recommendations.best_times.length > 0 ? (
                                <>
                                    {/* NEW: Engagement Trend Chart */}
                                    {(recommendations as any).hourly_engagement_trend && (recommendations as any).hourly_engagement_trend.length > 0 && (
                                        <EngagementTrendChart 
                                            data={(recommendations as any).hourly_engagement_trend}
                                            bestHour={recommendations.best_times[0]?.hour}
                                        />
                                    )}

                                    {/* NEW: Comparison Card */}
                                    {recommendations.best_times[0] && (recommendations as any).current_avg_engagement && (
                                        <ComparisonCard
                                            comparison={{
                                                currentAvgEngagement: (recommendations as any).current_avg_engagement || 0,
                                                recommendedAvgEngagement: recommendations.best_times[0].avg_engagement,
                                                recommendedHour: recommendations.best_times[0].hour,
                                                recommendedDay: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][recommendations.best_times[0].day] || 'Monday',
                                                improvementPercentage: (
                                                    ((recommendations.best_times[0].avg_engagement - (recommendations as any).current_avg_engagement) / 
                                                    (recommendations as any).current_avg_engagement) * 100
                                                )
                                            }}
                                        />
                                    )}

                                    {/* Original Monthly Calendar Heatmap */}
                                    {(recommendations as any).daily_performance && (recommendations as any).daily_performance.length > 0 && (
                                        <MonthlyCalendarHeatmap
                                            dailyPerformance={(recommendations as any).daily_performance}
                                            month={new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                                        />
                                    )}

                                    {/* Best Time Cards */}
                                    <BestTimeCards 
                                        recommendations={recommendations as any}
                                        channelId={selectedChannel?.id.toString()}
                                    />
                                </>
                            ) : (
                                <Alert severity="info" sx={{ my: 2 }}>
                                    No recommendations available for the selected filters
                                </Alert>
                            )}
                        </>
                    ) : (
                        // Enhanced Monthly Calendar Tab with Real Data
                        <>
                            <MonthlyCalendarHeatmap
                                dailyPerformance={calendarData}
                                month={new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                                bestTimesByDay={bestTimesByDay}
                                onDateSelect={handleDateSelect}
                                showFuturePredictions={true}
                            />
                        </>
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

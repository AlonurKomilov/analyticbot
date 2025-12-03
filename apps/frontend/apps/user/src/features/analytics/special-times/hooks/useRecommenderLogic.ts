import { useState, useEffect, useCallback } from 'react';
import { useAnalyticsStore } from '@store';
import { useChannelStore } from '@store';
import type { AIInsight } from '../utils/timeUtils';
import { uiLogger } from '@/utils/logger';

interface BestTimeRecommendations {
    best_times?: Array<{
        hour: number;
        day: number;
        confidence: number;
        avg_engagement: number;
        avg_views: number;  // Added: average views for this time slot
        relative_performance?: number;  // Added: % above/below channel average
        confidence_level?: 'high' | 'medium' | 'low';  // Added: data quality indicator
    }>;
    best_day_hour_combinations?: Array<{
        day_name: string;
        hour: number;
        score: number;
        confidence: number;
        avg_views?: number;
        relative_performance?: number;
        confidence_level?: 'high' | 'medium' | 'low';
    }>;
    content_type_recommendations?: Array<{
        content_type: string;
        day_name: string;
        hour: number;
        score: number;
        confidence: number;
        avg_views?: number;
        relative_performance?: number;
    }>;
    content_type_summary?: Record<string, number>;  // Direct counts: { video: 995, image: 1219, text: 508 }
    accuracy?: number;
    global_avg_views?: number;  // Added: channel-wide average views for comparison
    [key: string]: any;
}

interface UseRecommenderLogicReturn {
    timeFrame: string;
    contentType: string;
    loading: boolean;
    error: string | null;
    recommendations: BestTimeRecommendations | null;
    aiInsights: AIInsight[];
    setTimeFrame: (timeFrame: string) => void;
    setContentType: (contentType: string) => void;
    loadRecommendations: (silent?: boolean) => Promise<void>;
}

export const useRecommenderLogic = (): UseRecommenderLogicReturn => {
    const [timeFrame, setTimeFrame] = useState<string>('all');
    const [contentType, setContentType] = useState<string>('all');
    const [error, setError] = useState<string | null>(null);
    const [aiInsights, setAiInsights] = useState<AIInsight[]>([]);
    const [bestTimeRecommendations, setBestTimeRecommendations] = useState<BestTimeRecommendations | null>(null);

    // Get store methods and data
    const { fetchBestTime, isLoadingBestTime, bestTimes, bestDayHourCombinations, contentTypeRecommendations, totalPostsAnalyzed, contentTypeSummary } = useAnalyticsStore();
    const { selectedChannel } = useChannelStore();

    // Generate performance insights based on recommendations
    const generateAIInsights = (data: BestTimeRecommendations): AIInsight[] => {
        if (!data.best_times || data.best_times.length === 0) {
            return [];
        }

        const insights: AIInsight[] = [];
        const daysOfWeek = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

        // Get best time - SORT BY CONFIDENCE FIRST to match BestTimeCards display
        const sortedTimes = [...data.best_times].sort((a, b) => b.confidence - a.confidence);
        const bestTime = sortedTimes[0];
        const dayName = daysOfWeek[bestTime.day] || 'Unknown';
        const hour = bestTime.hour;
        const period = hour >= 12 ? 'PM' : 'AM';
        const displayHour = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
        const timeStr = `${displayHour}:00 ${period}`;

        // Calculate performance metric - use relative_performance if available, otherwise confidence
        const performanceMetric = bestTime.relative_performance
            ? `${Math.abs(bestTime.relative_performance).toFixed(0)}% ${bestTime.relative_performance > 0 ? 'more views' : 'fewer views'}`
            : `${bestTime.confidence}% higher engagement`;

        // Insight 1: Optimal Posting Time (from real data)
        insights.push({
            type: 'time',
            message: `Highest performance observed on ${dayName} at ${timeStr}`,
            title: 'Best Performing Time',
            description: `Based on historical data analysis, posts on ${dayName} at ${timeStr} receive ${performanceMetric}`
        });

        // Insight 2: Audience Activity (based on time of day)
        const timeOfDay = hour < 12 ? 'morning' : hour < 17 ? 'afternoon' : 'evening';
        insights.push({
            type: 'audience',
            message: `Your audience is most active in the ${timeOfDay}`,
            title: 'Audience Activity Pattern',
            description: `Historical data shows peak activity during ${timeOfDay} hours across ${sortedTimes.length} analyzed time slots`
        });

        // Insight 3: Content Strategy (based on day type)
        const isWeekend = bestTime.day === 0 || bestTime.day === 6;
        const contentTip = isWeekend
            ? 'We recommend posting entertaining or lifestyle content on weekends'
            : 'We recommend posting professional or educational content on weekdays';
        insights.push({
            type: 'content',
            message: contentTip,
            title: 'Content Strategy',
            description: `${isWeekend ? 'Weekend' : 'Weekday'} posts perform best for your channel`
        });

        // Insight 4: Views Trend (calculate from view data if available)
        if (sortedTimes.length >= 2) {
            const avgViews = sortedTimes.reduce((sum, t) => sum + (t.avg_views || 0), 0) / sortedTimes.length;
            if (avgViews > 0) {
                insights.push({
                    type: 'trend',
                    message: `Average ${avgViews.toFixed(0)} views across top performing time slots`,
                    title: 'Views Trend',
                    description: `Consistent posting during optimal times can improve overall channel performance`
                });
            } else {
                insights.push({
                    type: 'trend',
                    message: `Consistent posting during optimal times can improve overall channel performance`,
                    title: 'Performance Trend',
                    description: `Your channel shows stable activity patterns across analyzed time slots`
                });
            }
        }

        return insights;
    };

    // Load best time recommendations using store
    const loadRecommendations = useCallback(async (silent: boolean = false) => {
        // Don't fetch if no channel is selected
        if (!selectedChannel?.id) {
            uiLogger.warn('SpecialTimesRecommender: No channel selected, skipping fetch');
            return;
        }

        try {
            setError(null);

            // Convert timeFrame to days (standardized format)
            const daysMap: Record<string, number | null> = {
                '1h': 1,        // Last 1 day (need recent data for hourly analysis)
                '6h': 1,        // Last 1 day
                '24h': 2,       // Last 2 days
                '7d': 7,        // Last 7 days
                '30d': 30,      // Last 30 days
                '90d': 90,      // Last 90 days
                '180d': 180,    // Last 6 months
                '1y': 365,      // Last 1 year
                'all': null     // All time (unlimited, backend will limit to 10k posts)
            };
            const days = daysMap[timeFrame] !== undefined ? daysMap[timeFrame] : 30;

            uiLogger.debug('SpecialTimesRecommender: Fetching data', {
                channelId: selectedChannel.id,
                timeFrame,
                days: days === null ? 'ALL TIME (unlimited)' : days,
                silent
            });

            await fetchBestTime(selectedChannel.id, days, silent);
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Unknown error';
            setError(errorMessage);
            uiLogger.error('Error loading recommendations', { error: err });
            setAiInsights([]);
        }
    }, [fetchBestTime, selectedChannel, timeFrame]);

    // Update recommendations when store data changes
    useEffect(() => {
        if (bestTimes && bestTimes.length > 0) {
            uiLogger.debug('Processing bestTimes from store', { count: bestTimes.length });

            // Convert BestTimeRecommendation[] to the expected format
            // Handle both API format (avg_engagement) and any legacy format (avgEngagement)
            // Now includes avg_views and relative_performance from view-based scoring
            const formatted: BestTimeRecommendations = {
                best_times: bestTimes.map(bt => ({
                    hour: bt.hour,
                    day: typeof bt.day === 'string' ? parseInt(bt.day) : bt.day,
                    confidence: bt.confidence,
                    avg_engagement: bt.avg_engagement || bt.avgEngagement || 0,
                    avg_views: bt.avg_views || 0,  // View-based metric
                    relative_performance: bt.relative_performance || 0,  // % above/below average
                    confidence_level: bt.confidence_level || 'low'  // Data quality indicator
                })),
                best_day_hour_combinations: bestDayHourCombinations || [],
                content_type_recommendations: contentTypeRecommendations || [],
                total_posts_analyzed: totalPostsAnalyzed || 0,
                content_type_summary: contentTypeSummary || undefined,  // Direct counts from API
                accuracy: Math.round(bestTimes.reduce((sum, bt) => sum + (bt.confidence || 0), 0) / bestTimes.length)
            };

            uiLogger.debug('Formatted recommendations', {
                bestTimesCount: formatted.best_times?.length || 0,
                dayHourCombinations: formatted.best_day_hour_combinations?.length || 0,
                contentTypeRecommendations: formatted.content_type_recommendations?.length || 0,
                totalPostsAnalyzed: formatted.total_posts_analyzed,
                contentTypeSummary: formatted.content_type_summary
            });
            setBestTimeRecommendations(formatted);

            // Generate performance insights
            const insights = generateAIInsights(formatted);
            setAiInsights(insights);
        } else {
            uiLogger.debug('No bestTimes data available');
            setBestTimeRecommendations(null);
            setAiInsights([]);
        }
    }, [bestTimes, bestDayHourCombinations, contentTypeRecommendations, totalPostsAnalyzed, contentTypeSummary]);

    // Load data on mount and when filters change
    useEffect(() => {
        loadRecommendations();
    }, [loadRecommendations]);

    // Listen for data source changes
    useEffect(() => {
        const handleDataSourceChange = () => {
            uiLogger.debug('SpecialTimesRecommender: Data source changed, reloading');
            loadRecommendations();
        };

        window.addEventListener('dataSourceChanged', handleDataSourceChange);
        return () => window.removeEventListener('dataSourceChanged', handleDataSourceChange);
    }, [loadRecommendations]);

    return {
        // State
        timeFrame,
        contentType,
        loading: isLoadingBestTime,
        error,
        recommendations: bestTimeRecommendations,
        aiInsights,

        // Actions
        setTimeFrame,
        setContentType,
        loadRecommendations
    };
};

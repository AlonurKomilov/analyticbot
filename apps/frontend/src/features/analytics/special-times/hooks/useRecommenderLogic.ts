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
    }>;
    best_day_hour_combinations?: Array<{
        day_name: string;
        hour: number;
        score: number;
        confidence: number;
    }>;
    content_type_recommendations?: Array<{
        content_type: string;
        day_name: string;
        hour: number;
        score: number;
        confidence: number;
    }>;
    accuracy?: number;
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
    const { fetchBestTime, isLoadingBestTime, bestTimes, bestDayHourCombinations, contentTypeRecommendations } = useAnalyticsStore();
    const { selectedChannel } = useChannelStore();

    // Generate performance insights based on recommendations
    const generateAIInsights = (data: BestTimeRecommendations): AIInsight[] => {
        if (!data.best_times || data.best_times.length === 0) {
            return [];
        }

        const insights: AIInsight[] = [];
        const daysOfWeek = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

        // Get best time (first recommendation)
        const bestTime = data.best_times[0];
        const dayName = daysOfWeek[bestTime.day] || 'Unknown';
        const hour = bestTime.hour;
        const period = hour >= 12 ? 'PM' : 'AM';
        const displayHour = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
        const timeStr = `${displayHour}:00 ${period}`;

        // Insight 1: Optimal Posting Time (from real data)
        insights.push({
            type: 'time',
            message: `Highest engagement observed on ${dayName} at ${timeStr}`,
            title: 'Best Performing Time',
            description: `Based on historical data analysis, posts on ${dayName} at ${timeStr} receive ${bestTime.confidence}% higher engagement`
        });

        // Insight 2: Audience Activity (based on time of day)
        const timeOfDay = hour < 12 ? 'morning' : hour < 17 ? 'afternoon' : 'evening';
        insights.push({
            type: 'audience',
            message: `Your audience is most active in the ${timeOfDay}`,
            title: 'Audience Activity Pattern',
            description: `Historical data shows peak engagement during ${timeOfDay} hours across ${data.best_times.length} analyzed time slots`
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

        // Insight 4: Engagement Trend (calculate from data if multiple times available)
        if (data.best_times.length >= 2) {
            const avgEngagement = data.best_times.reduce((sum, t) => sum + t.avg_engagement, 0) / data.best_times.length;
            insights.push({
                type: 'trend',
                message: `Average engagement rate is ${avgEngagement.toFixed(2)} across top performing times`,
                title: 'Engagement Trend',
                description: `Consistent posting during optimal times can improve overall channel performance`
            });
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
            const formatted: BestTimeRecommendations = {
                best_times: bestTimes.map(bt => ({
                    hour: bt.hour,
                    day: typeof bt.day === 'string' ? parseInt(bt.day) : bt.day,
                    confidence: bt.confidence,
                    avg_engagement: bt.avg_engagement || bt.avgEngagement || 0
                })),
                best_day_hour_combinations: bestDayHourCombinations || [],
                content_type_recommendations: contentTypeRecommendations || [],
                accuracy: Math.round(bestTimes.reduce((sum, bt) => sum + (bt.confidence || 0), 0) / bestTimes.length)
            };

            uiLogger.debug('Formatted recommendations', {
                bestTimesCount: formatted.best_times?.length || 0,
                dayHourCombinations: formatted.best_day_hour_combinations?.length || 0,
                contentTypeRecommendations: formatted.content_type_recommendations?.length || 0
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
    }, [bestTimes, bestDayHourCombinations, contentTypeRecommendations]);

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

import { useState, useEffect, useCallback } from 'react';
import { useAnalyticsStore } from '@store';
import { useChannelStore } from '@store';
import type { AIInsight } from '../utils/timeUtils';

interface BestTimeRecommendations {
    best_times?: Array<{
        hour: number;
        day: number;
        confidence: number;
        avg_engagement: number;
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
    loadRecommendations: () => Promise<void>;
}

export const useRecommenderLogic = (): UseRecommenderLogicReturn => {
    const [timeFrame, setTimeFrame] = useState<string>('week');
    const [contentType, setContentType] = useState<string>('all');
    const [error, setError] = useState<string | null>(null);
    const [aiInsights, setAiInsights] = useState<AIInsight[]>([]);
    const [bestTimeRecommendations, setBestTimeRecommendations] = useState<BestTimeRecommendations | null>(null);

    // Get store methods and data
    const { fetchBestTime, isLoadingBestTime, bestTimes } = useAnalyticsStore();
    const { selectedChannel } = useChannelStore();

    // Generate AI insights based on recommendations
    const generateAIInsights = (data: BestTimeRecommendations): AIInsight[] => {
        const insights: AIInsight[] = [
            {
                type: 'time',
                message: data.best_times?.[0] ? 'Juma kuni soat 20:00 da eng ko\'p faollik kuzatiladi' : 'Ma\'lumotlar tahlil qilinmoqda',
                title: 'Optimal Posting Time',
                description: data.best_times?.[0] ? 'Juma kuni soat 20:00 da eng ko\'p faollik kuzatiladi' : 'Ma\'lumotlar tahlil qilinmoqda'
            },
            {
                type: 'audience',
                message: 'Sizning auditoriyangiz kechqurun ko\'proq faol bo\'ladi',
                title: 'Audience Activity',
                description: 'Sizning auditoriyangiz kechqurun ko\'proq faol bo\'ladi'
            },
            {
                type: 'content',
                message: 'Hafta oxirida ko\'ngilochar kontent yuborishni tavsiya etamiz',
                title: 'Content Strategy',
                description: 'Hafta oxirida ko\'ngilochar kontent yuborishni tavsiya etamiz'
            },
            {
                type: 'trend',
                message: 'Faollik darajasi hafta davomida 15% oshgan',
                title: 'Engagement Trend',
                description: 'Faollik darajasi hafta davomida 15% oshgan'
            }
        ];

        return insights.slice(0, Math.min(insights.length, 4));
    };

    // Load best time recommendations using store
    const loadRecommendations = useCallback(async () => {
        // Don't fetch if no channel is selected
        if (!selectedChannel?.id) {
            console.warn('BestTimeRecommender: No channel selected, skipping fetch');
            return;
        }

        try {
            setError(null);
            console.log('BestTimeRecommender: Fetching for channel:', selectedChannel.id);
            await fetchBestTime(selectedChannel.id);
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Unknown error';
            setError(errorMessage);
            console.error('Error loading recommendations:', err);
            setAiInsights([]);
        }
    }, [fetchBestTime, selectedChannel]);

    // Update recommendations when store data changes
    useEffect(() => {
        if (bestTimes && bestTimes.length > 0) {
            // Convert BestTimeRecommendation[] to the expected format
            const formatted: BestTimeRecommendations = {
                best_times: bestTimes.map(bt => ({
                    hour: bt.hour,
                    day: typeof bt.day === 'string' ? parseInt(bt.day) : bt.day,
                    confidence: bt.confidence,
                    avg_engagement: bt.avgEngagement
                })),
                accuracy: Math.round(bestTimes.reduce((sum, bt) => sum + bt.confidence, 0) / bestTimes.length)
            };
            setBestTimeRecommendations(formatted);

            // Generate AI insights
            const insights = generateAIInsights(formatted);
            setAiInsights(insights);
        }
    }, [bestTimes]);

    // Load data on mount and when filters change
    useEffect(() => {
        loadRecommendations();
    }, [loadRecommendations]);

    // Listen for data source changes
    useEffect(() => {
        const handleDataSourceChange = () => {
            console.log('BestTimeRecommender: Data source changed, reloading...');
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

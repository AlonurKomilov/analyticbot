import { useState, useEffect, useCallback } from 'react';
import { useAnalyticsStore } from '@/stores';
import { DEFAULT_DEMO_CHANNEL_ID } from '../../../../__mocks__/constants';
import type { AIInsight } from '../utils/timeUtils';

interface BestTimeRecommendations {
    best_times?: Array<{ hour: number; confidence: number }>;
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

    // Get store methods and data
    const { fetchBestTime, isLoadingBestTime } = useAnalyticsStore();
    const [bestTimeRecommendations, _setBestTimeRecommendations] = useState<BestTimeRecommendations | null>(null);

    // Generate AI insights based on recommendations
    const generateAIInsights = (data: BestTimeRecommendations): AIInsight[] => {
        const insights: AIInsight[] = [
            {
                type: 'time',
                message: data.best_times?.[0] ? 'Juma kuni soat 20:00 da eng ko\'p faollik kuzatiladi' : 'Ma\'lumotlar tahlil qilinmoqda'
            },
            {
                type: 'audience',
                message: 'Sizning auditoriyangiz kechqurun ko\'proq faol bo\'ladi'
            },
            {
                type: 'content',
                message: 'Hafta oxirida ko\'ngilochar kontent yuborishni tavsiya etamiz'
            },
            {
                type: 'trend',
                message: 'Faollik darajasi hafta davomida 15% oshgan'
            }
        ];

        return insights.slice(0, Math.min(insights.length, 4));
    };

    // Load best time recommendations using store
    const loadRecommendations = useCallback(async () => {
        try {
            setError(null);
            await fetchBestTime(DEFAULT_DEMO_CHANNEL_ID);

            // For now, generate insights from mock data
            // In production, this would come from the API response
            if (bestTimeRecommendations) {
                const insights = generateAIInsights(bestTimeRecommendations);
                setAiInsights(insights);
            }

        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Unknown error';
            setError(errorMessage);
            console.error('Error loading recommendations:', err);
            setAiInsights([]);
        }
    }, [timeFrame, contentType, fetchBestTime, bestTimeRecommendations]);

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

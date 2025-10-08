import { useState, useEffect, useCallback } from 'react';
import { useAppStore } from '../../../../store/appStore.js';
import { DEFAULT_DEMO_CHANNEL_ID } from '../../../../__mocks__/constants.js';

export const useRecommenderLogic = () => {
    const [timeFrame, setTimeFrame] = useState('week');
    const [contentType, setContentType] = useState('all');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [recommendations, setRecommendations] = useState(null);
    const [aiInsights, setAiInsights] = useState([]);

    // Get store methods and data source
    const { fetchBestTime } = useAppStore();

    // Load best time recommendations using store
    const loadRecommendations = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);

            const result = await fetchBestTime(DEFAULT_DEMO_CHANNEL_ID, timeFrame, contentType);

            let recommendationsData = null;
            if (result && typeof result === 'object') {
                recommendationsData = result;
            }

            setRecommendations(recommendationsData);

            // Generate AI insights based on recommendations
            if (recommendationsData) {
                const insights = generateAIInsights(recommendationsData);
                setAiInsights(insights);
            } else {
                setAiInsights([]);
            }

        } catch (err) {
            setError(err.message);
            console.error('Error loading recommendations:', err);
            setRecommendations(null);
            setAiInsights([]);
        } finally {
            setLoading(false);
        }
    }, [timeFrame, contentType, fetchBestTime]);

    // Generate AI insights based on recommendations
    const generateAIInsights = (data) => {
        const insights = [
            {
                type: 'time',
                title: 'Eng yaxshi vaqt',
                description: `${data.best_times?.[0] ? 'Juma kuni soat 20:00 da eng ko\'p faollik kuzatiladi' : 'Ma\'lumotlar tahlil qilinmoqda'}`
            },
            {
                type: 'audience',
                title: 'Auditoriya faolligi',
                description: 'Sizning auditoriyangiz kechqurun ko\'proq faol bo\'ladi'
            },
            {
                type: 'content',
                title: 'Kontent strategiyasi',
                description: 'Hafta oxirida ko\'ngilochar kontent yuborishni tavsiya etamiz'
            },
            {
                type: 'trend',
                title: 'Haftalik trend',
                description: 'Faollik darajasi hafta davomida 15% oshgan'
            }
        ];

        return insights.slice(0, Math.min(insights.length, 4));
    };

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
        loading,
        error,
        recommendations,
        aiInsights,

        // Actions
        setTimeFrame,
        setContentType,
        loadRecommendations
    };
};

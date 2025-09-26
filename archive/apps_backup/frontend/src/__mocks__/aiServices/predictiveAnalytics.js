/**
 * Predictive Analytics Service Mock Data
 * Mock data for predictive analytics AI service including forecasts and trends
 */

export const predictiveAnalyticsStats = {
    accuracy: '94.2%',
    predictions: 156,
    trends: 8,
    status: 'active'
};

// Alias for backward compatibility
export const predictiveStats = predictiveAnalyticsStats;

export const mockPredictions = [
    { 
        metric: 'Engagement Rate', 
        current: '68%', 
        predicted: '71%', 
        trend: 'up', 
        confidence: '95%',
        timeframe: '14 days',
        factors: ['Optimal posting times', 'Content quality improvement', 'Audience growth']
    },
    { 
        metric: 'User Activity', 
        current: '89%', 
        predicted: '85%', 
        trend: 'down', 
        confidence: '79%',
        timeframe: '7 days',
        factors: ['Seasonal decline', 'Competition increase', 'Content saturation']
    },
    { 
        metric: 'Revenue Impact', 
        current: '$12.4K', 
        predicted: '$13.8K', 
        trend: 'up', 
        confidence: '91%',
        timeframe: '30 days',
        factors: ['New product launch', 'Marketing campaign', 'Customer retention']
    },
    { 
        metric: 'Follower Growth', 
        current: '2.3K/month', 
        predicted: '2.8K/month', 
        trend: 'up', 
        confidence: '87%',
        timeframe: '30 days',
        factors: ['Viral content potential', 'Influencer collaborations', 'Hashtag optimization']
    }
];

export const trendInsights = [
    {
        title: 'Peak Engagement Hours',
        insight: '2-4 PM shows highest engagement potential with 85% increase expected',
        impact: 'High',
        action: 'Schedule premium content during peak hours',
        confidence: 94,
        category: 'timing'
    },
    {
        title: 'Content Type Performance',
        insight: 'Video content outperforming static posts by 127%',
        impact: 'Very High',
        action: 'Increase video content production by 40%',
        confidence: 91,
        category: 'content'
    },
    {
        title: 'Seasonal Trend Alert',
        insight: 'Holiday season showing 67% engagement boost opportunity',
        impact: 'High',
        action: 'Prepare seasonal content strategy with themed campaigns',
        confidence: 88,
        category: 'seasonal'
    },
    {
        title: 'Audience Behavior Shift',
        insight: 'Mobile engagement up 45%, desktop declining',
        impact: 'Medium',
        action: 'Optimize content for mobile-first experience',
        confidence: 82,
        category: 'audience'
    }
];

export const forecastModels = [
    {
        name: 'ARIMA Model',
        accuracy: '94.2%',
        lastUpdated: '2024-01-15T08:00:00Z',
        predictions: 156,
        status: 'active'
    },
    {
        name: 'Neural Network',
        accuracy: '91.8%',
        lastUpdated: '2024-01-15T07:30:00Z',
        predictions: 89,
        status: 'training'
    },
    {
        name: 'Random Forest',
        accuracy: '88.5%',
        lastUpdated: '2024-01-15T06:00:00Z',
        predictions: 67,
        status: 'active'
    }
];

export const analysisSettings = {
    timeRange: '30d',
    modelType: 'engagement',
    confidenceThreshold: 0.8,
    autoRefresh: true,
    alertThreshold: {
        high: 0.9,
        medium: 0.7,
        low: 0.5
    }
};

// Alias for backward compatibility
export const mockForecasts = mockPredictions;

export default {
    predictiveAnalyticsStats,
    predictiveStats,
    mockPredictions,
    mockForecasts,
    trendInsights,
    forecastModels,
    analysisSettings
};
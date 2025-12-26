/**
 * Content Optimizer Service Mock Data
 * Mock data for content optimization AI service including stats and recent optimizations
 */

export const contentOptimizerStats = {
    totalOptimized: 1247,
    todayOptimized: 23,
    avgImprovement: '+34%',
    status: 'active'
};

export const recentOptimizations = [
    {
        id: 1,
        content: 'Product Launch Post',
        improvement: '+42%',
        timestamp: '2 minutes ago',
        status: 'success',
        originalScore: 68,
        optimizedScore: 96,
        suggestions: ['Added emotional triggers', 'Improved call-to-action', 'Optimized hashtags']
    },
    {
        id: 2,
        content: 'Weekly Newsletter',
        improvement: '+28%',
        timestamp: '15 minutes ago',
        status: 'success',
        originalScore: 72,
        optimizedScore: 92,
        suggestions: ['Enhanced readability', 'Better structure', 'Added urgency words']
    },
    {
        id: 3,
        content: 'Blog Article Draft',
        improvement: '+51%',
        timestamp: '1 hour ago',
        status: 'success',
        originalScore: 59,
        optimizedScore: 89,
        suggestions: ['SEO optimization', 'Improved headlines', 'Added engagement hooks']
    },
    {
        id: 4,
        content: 'Social Media Campaign',
        improvement: '+38%',
        timestamp: '2 hours ago',
        status: 'success',
        originalScore: 65,
        optimizedScore: 90,
        suggestions: ['Trend alignment', 'Audience targeting', 'Visual content tips']
    },
    {
        id: 5,
        content: 'Email Marketing Copy',
        improvement: '+29%',
        timestamp: '3 hours ago',
        status: 'success',
        originalScore: 70,
        optimizedScore: 90,
        suggestions: ['Subject line optimization', 'Personalization', 'CTA placement']
    }
];

export const optimizationSettings = {
    autoOptimization: true,
    targets: {
        engagementRate: true,
        readabilityScore: true,
        seoOptimization: false,
        sentimentAnalysis: true
    },
    schedule: {
        enabled: false,
        frequency: 'daily',
        time: '09:00'
    }
};

export const mockContentAnalysis = {
    originalContent: "Check out our new product! It's amazing and you should buy it now.",
    optimizedContent: "🚀 Discover our game-changing new product! Transform your workflow with innovative features that deliver real results. Limited-time exclusive offer - secure yours today! #Innovation #ProductLaunch",
    analysis: {
        overallScore: 85,
        sentimentScore: 0.8,
        readabilityScore: 78,
        engagementPrediction: 92
    },
    improvements: [
        "Added emotional trigger words (🚀, game-changing, transform)",
        "Enhanced call-to-action with urgency",
        "Included relevant hashtags for discoverability",
        "Improved structure and readability"
    ],
    scoreImprovement: 34.2
};

export const optimizationMetrics = [
    { metric: 'Engagement Rate', current: '+34%', target: '+40%', status: 'on-track' },
    { metric: 'Readability Score', current: '92', target: '90', status: 'excellent' },
    { metric: 'SEO Score', current: '85', target: '90', status: 'improving' },
    { metric: 'Sentiment Score', current: '0.8', target: '0.85', status: 'good' }
];

export const trendInsights = [
    {
        title: 'Emotional Triggers Work',
        insight: 'Content with emotional triggers shows 45% higher engagement',
        impact: 'High',
        action: 'Continue using emotional language in optimization'
    },
    {
        title: 'Timing Optimization',
        insight: 'Posts optimized for 2-4 PM show best performance',
        impact: 'Medium',
        action: 'Schedule optimized content during peak hours'
    },
    {
        title: 'Visual Content Impact',
        insight: 'Optimized posts with visuals get 60% more engagement',
        impact: 'Very High',
        action: 'Always include visual content suggestions'
    }
];

export default {
    contentOptimizerStats,
    recentOptimizations,
    optimizationSettings,
    mockContentAnalysis,
    optimizationMetrics,
    trendInsights
};

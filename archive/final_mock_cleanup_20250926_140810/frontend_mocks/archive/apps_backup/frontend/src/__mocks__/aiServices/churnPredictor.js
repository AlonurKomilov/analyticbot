/**
 * Churn Predictor Service Mock Data
 * Mock data for user churn prediction AI service including risk analysis and retention strategies
 */

export const churnPredictorStats = {
    usersAnalyzed: 892,
    highRiskUsers: 47,
    retentionSuccess: '78%',
    churnRate: '12.3%',
    savedCustomers: 23,
    status: 'beta'
};

export const mockChurnPredictions = [
    {
        userId: 12345,
        userName: 'alice_creator',
        churnProbability: 0.85,
        riskLevel: 'High',
        lastActivity: '5 days ago',
        engagementScore: 0.23,
        subscriptionTier: 'premium',
        keyFactors: [
            'Declining engagement rate (-45% last 30 days)',
            'Reduced posting frequency (2x per week → 1x)',
            'No interaction with new features',
            'Subscription expires in 15 days'
        ],
        recommendations: [
            'Send personalized re-engagement campaign',
            'Offer premium feature tutorial',
            'Provide discount for subscription renewal',
            'Schedule 1-on-1 success call'
        ],
        confidenceScore: 91
    },
    {
        userId: 67890,
        userName: 'tech_blogger_pro',
        churnProbability: 0.45,
        riskLevel: 'Medium',
        lastActivity: '2 days ago',
        engagementScore: 0.62,
        subscriptionTier: 'standard',
        keyFactors: [
            'Stable but not growing metrics',
            'Using only basic features',
            'Low community interaction',
            'Similar usage pattern for 3 months'
        ],
        recommendations: [
            'Introduce advanced features gradually',
            'Connect with similar creators',
            'Provide growth strategy consultation',
            'Highlight success stories'
        ],
        confidenceScore: 76
    },
    {
        userId: 11223,
        userName: 'social_maven',
        churnProbability: 0.15,
        riskLevel: 'Low',
        lastActivity: '1 hour ago',
        engagementScore: 0.89,
        subscriptionTier: 'enterprise',
        keyFactors: [
            'Consistent high engagement',
            'Regular feature adoption',
            'Active community participation',
            'Growing metrics trend'
        ],
        recommendations: [
            'Provide beta access to new features',
            'Invite to creator advisory board',
            'Offer referral incentives',
            'Feature in success case studies'
        ],
        confidenceScore: 94
    }
];

export const retentionStrategies = [
    {
        category: 'Engagement',
        strategies: [
            'Personalized content recommendations',
            'Gamification elements and achievements',
            'Interactive tutorials and onboarding',
            'Community challenges and contests'
        ]
    },
    {
        category: 'Communication',
        strategies: [
            'Proactive customer success outreach',
            'Educational email sequences',
            'Feature update notifications',
            'Success story sharing'
        ]
    },
    {
        category: 'Product',
        strategies: [
            'Advanced feature recommendations',
            'Workflow optimization suggestions',
            'Integration with preferred tools',
            'Custom reporting and insights'
        ]
    },
    {
        category: 'Commercial',
        strategies: [
            'Renewal discount offers',
            'Upgrade incentives',
            'Loyalty program benefits',
            'Flexible payment options'
        ]
    }
];

export const riskSegments = [
    {
        segment: 'High Risk',
        count: 47,
        percentage: 5.3,
        color: '#f44336',
        description: 'Users likely to churn within 30 days'
    },
    {
        segment: 'Medium Risk',
        count: 134,
        percentage: 15.0,
        color: '#ff9800',
        description: 'Users showing warning signs'
    },
    {
        segment: 'Low Risk',
        count: 711,
        percentage: 79.7,
        color: '#4caf50',
        description: 'Stable and engaged users'
    }
];

export const churnFactors = [
    { factor: 'Declining Engagement', weight: 0.35, description: 'Reduced interaction with platform features' },
    { factor: 'Support Tickets', weight: 0.25, description: 'Frequency and nature of customer support requests' },
    { factor: 'Feature Usage', weight: 0.20, description: 'Adoption rate of new and existing features' },
    { factor: 'Billing Issues', weight: 0.15, description: 'Payment failures and subscription concerns' },
    { factor: 'Competitor Activity', weight: 0.05, description: 'Market competition and alternative solutions' }
];

export const predictionSettings = {
    modelVersion: '2.1',
    lastTraining: '2024-01-10T15:30:00Z',
    accuracyScore: 87.3,
    alertThresholds: {
        high: 0.7,
        medium: 0.4,
        low: 0.2
    },
    autoAlerts: true,
    reportingFrequency: 'weekly'
};

export default {
    churnPredictorStats,
    mockChurnPredictions,
    retentionStrategies,
    riskSegments,
    churnFactors,
    predictionSettings
};
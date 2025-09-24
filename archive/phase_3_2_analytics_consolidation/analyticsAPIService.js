/**
 * Analytics API Service - Backend Integration
 * Replaces duplicate frontend mock data generation with backend API calls
 * 
 * This service now connects to backend mock endpoints instead of generating
 * data locally, creating a single source of truth for mock data.
 */

import { API_CONFIG } from '../../config/mockConfig.js';

class AnalyticsAPIService {
    constructor() {
        this.baseURL = API_CONFIG.API_BASE_URL || 'https://84dp9jc9-11400.euw.devtunnels.ms';
    }

    /**
     * Get post dynamics from backend mock API
     */
    async getPostDynamics(channelId, period = '24h') {
        try {
            const response = await fetch(`${this.baseURL}/api/mock/analytics/post-dynamics?period=${period}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.warn('Backend analytics API unavailable, using fallback data:', error.message);
            return this._getFallbackPostDynamics();
        }
    }

    /**
     * Get top posts from backend mock API
     */
    async getTopPosts(channelId, period = 'today', sortBy = 'views') {
        try {
            const response = await fetch(`${this.baseURL}/api/mock/analytics/top-posts?period=${period}&sortBy=${sortBy}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.warn('Backend analytics API unavailable, using fallback data:', error.message);
            return this._getFallbackTopPosts();
        }
    }

    /**
     * Get best time recommendations from backend mock API
     */
    async getBestTimeRecommendations(channelId, timeframe = 'week') {
        try {
            const response = await fetch(`${this.baseURL}/api/mock/analytics/best-time?timeframe=${timeframe}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.warn('Backend analytics API unavailable, using fallback data:', error.message);
            return this._getFallbackBestTime();
        }
    }

    /**
     * Get engagement metrics from backend mock API
     */
    async getEngagementMetrics(channelId, period = '7d') {
        try {
            const response = await fetch(`${this.baseURL}/api/mock/analytics/engagement?period=${period}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.warn('Backend analytics API unavailable, using fallback data:', error.message);
            return this._getFallbackEngagement();
        }
    }

    // Enhanced fallback data methods for demo user experience
    _getFallbackPostDynamics() {
        const now = new Date();
        const data = [];
        
        // Generate 24 hours of sample data
        for (let i = 0; i < 24; i++) {
            const timestamp = new Date(now.getTime() - (23 - i) * 60 * 60 * 1000);
            data.push({
                id: i + 1,
                timestamp: timestamp.toISOString(),
                views: Math.floor(Math.random() * 1000) + 100,
                reactions: Math.floor(Math.random() * 50) + 5,
                shares: Math.floor(Math.random() * 20) + 2,
                comments: Math.floor(Math.random() * 30) + 3,
                engagement_rate: Math.random() * 10 + 2,
                hour: timestamp.getHours(),
                day_of_week: timestamp.getDay(),
                performance_score: Math.floor(Math.random() * 40) + 60
            });
        }
        
        return data;
    }

    _getFallbackTopPosts() {
        const samplePosts = [
            {
                id: 'demo_post_1',
                title: '🚀 Welcome to AnalyticBot Demo!',
                content: 'Explore our powerful analytics features with this demo account.',
                views: 2547,
                likes: 189,
                shares: 47,
                comments: 23,
                engagement_rate: 10.2,
                published_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
                performance_score: 92,
                type: 'announcement',
                thumbnail: null
            },
            {
                id: 'demo_post_2', 
                title: '📊 Your Analytics Dashboard',
                content: 'See how your content performs with detailed insights and metrics.',
                views: 1823,
                likes: 134,
                shares: 28,
                comments: 41,
                engagement_rate: 11.1,
                published_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
                performance_score: 87,
                type: 'tutorial',
                thumbnail: null
            },
            {
                id: 'demo_post_3',
                title: '🎯 Optimize Your Content Strategy',
                content: 'Learn how to use AI-powered recommendations to boost engagement.',
                views: 1456,
                likes: 98,
                shares: 31,
                comments: 19,
                engagement_rate: 10.2,
                published_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
                performance_score: 85,
                type: 'guide',
                thumbnail: null
            },
            {
                id: 'demo_post_4',
                title: '💡 Best Time to Post Analysis',
                content: 'Discover when your audience is most active for maximum reach.',
                views: 1234,
                likes: 76,
                shares: 15,
                comments: 28,
                engagement_rate: 9.6,
                published_at: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(),
                performance_score: 81,
                type: 'analysis',
                thumbnail: null
            },
            {
                id: 'demo_post_5',
                title: '🔥 Trending Topics & Hashtags',
                content: 'Stay ahead of trends with our comprehensive analytics tools.',
                views: 987,
                likes: 62,
                shares: 22,
                comments: 16,
                engagement_rate: 10.1,
                published_at: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
                performance_score: 78,
                type: 'trends',
                thumbnail: null
            }
        ];
        
        return samplePosts;
    }

    _getFallbackEngagement() {
        const now = new Date();
        const engagementData = {
            total_views: 8547,
            total_likes: 559,
            total_shares: 143,
            total_comments: 127,
            average_engagement_rate: 10.2,
            engagement_trend: 'up',
            engagement_change: '+15.3%',
            top_engaging_content: [
                { type: 'announcement', engagement_rate: 12.4 },
                { type: 'tutorial', engagement_rate: 11.1 },
                { type: 'guide', engagement_rate: 10.2 }
            ],
            daily_metrics: []
        };

        // Generate daily engagement data for the past week
        for (let i = 6; i >= 0; i--) {
            const date = new Date(now.getTime() - i * 24 * 60 * 60 * 1000);
            engagementData.daily_metrics.push({
                date: date.toISOString().split('T')[0],
                views: Math.floor(Math.random() * 500) + 800,
                likes: Math.floor(Math.random() * 50) + 40,
                shares: Math.floor(Math.random() * 20) + 10,
                comments: Math.floor(Math.random() * 30) + 15,
                engagement_rate: Math.random() * 5 + 7.5
            });
        }

        return engagementData;
    }

    _getFallbackBestTime() {
        return {
            optimal_times: [{
                hour: 20,
                day: 'weekday',
                engagement_rate: 7.5,
                confidence: 0.85,
                reason: 'Peak engagement observed at 20:00'
            }],
            recommendations: ['Post during evening hours for maximum reach'],
            analysis_period: 'Last 30 days'
        };
    }

    _getFallbackEngagement() {
        return {
            period: '7d',
            total_views: 10000,
            total_engagements: 1000,
            average_engagement_rate: 7.5,
            growth_rate: 5.2
        };
    }

    /**
     * Get analytics overview from backend mock API
     */
    async getAnalyticsOverview(channelId) {
        try {
            const response = await fetch(`${this.baseURL}/api/mock/analytics/overview/${channelId}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.warn('Backend analytics API unavailable, using fallback data:', error.message);
            return this._getFallbackAnalyticsOverview();
        }
    }

    _getFallbackAnalyticsOverview() {
        return {
            channel_id: 'demo_channel',
            name: 'Demo Analytics Channel',
            total_subscribers: 15420,
            total_views: 234567,
            total_posts: 127,
            engagement_rate: 8.7,
            growth_rate: '+12.5%',
            last_updated: new Date().toISOString(),
            metrics: {
                daily_views: 3400,
                daily_new_subscribers: 45,
                daily_engagement: 7.8,
                top_content_type: 'tutorial'
            },
            recent_performance: {
                views_trend: 'up',
                engagement_trend: 'up',
                subscriber_trend: 'up'
            }
        };
    }

    _getFallbackChannels() {
        return [
            {
                id: 'demo_channel_1',
                name: 'Demo Analytics Channel',
                title: 'Demo Analytics Channel',
                username: '@demo_analytics',
                platform: 'telegram',
                subscriber_count: 15420,
                status: 'active',
                connected_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
                last_updated: new Date().toISOString(),
                avatar_url: null,
                description: 'Demo channel for analytics showcase'
            },
            {
                id: 'demo_channel_2',
                name: 'Tech News Channel',
                title: 'Tech News Channel',
                username: '@tech_news_demo',
                platform: 'telegram',
                subscriber_count: 8950,
                status: 'active',
                connected_at: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString(),
                last_updated: new Date().toISOString(),
                avatar_url: null,
                description: 'Demo tech news channel'
            },
            {
                id: 'demo_channel_3',
                name: 'Marketing Tips',
                title: 'Marketing Tips',
                username: '@marketing_tips_demo',
                platform: 'telegram',
                subscriber_count: 12340,
                status: 'active',
                connected_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
                last_updated: new Date().toISOString(),
                avatar_url: null,
                description: 'Demo marketing channel'
            }
        ];
    }
}

// Export singleton instance
export const analyticsAPIService = new AnalyticsAPIService();

// Backward compatibility exports (deprecated)
export const generatePostDynamics = (hoursBack = 24) => {
    console.warn('generatePostDynamics is deprecated. Use analyticsAPIService.getPostDynamics() instead.');
    return analyticsAPIService._getFallbackPostDynamics();
};

export const generateTopPosts = (count = 10) => {
    console.warn('generateTopPosts is deprecated. Use analyticsAPIService.getTopPosts() instead.');
    return analyticsAPIService._getFallbackTopPosts();
};

export const generateBestTimeRecommendations = () => {
    console.warn('generateBestTimeRecommendations is deprecated. Use analyticsAPIService.getBestTimeRecommendations() instead.');
    return analyticsAPIService._getFallbackBestTime();
};

// Keep the demoAnalyticsService for backward compatibility but mark as legacy
export const demoAnalyticsService = analyticsAPIService;
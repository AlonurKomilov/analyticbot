/**
 * Analytics Demo Data Service
 * Provides comprehensive demo data for analytics endpoints
 * Moved from backend API to keep production endpoints clean
 */

import { DEFAULT_DEMO_CHANNEL_ID } from '../constants.js';

import { MOCK_CONFIG } from '../../config/mockConfig.js';

/**
 * Generate demo post dynamics data
 * @param {number} hoursBack - Hours to look back (1-168)
 * @returns {Array} Post dynamics data
 */
export function generatePostDynamics(hoursBack = 24) {
    const dynamics = [];
    const now = new Date();
    
    for (let i = hoursBack; i >= 0; i--) {
        const timestamp = new Date(now.getTime() - i * 60 * 60 * 1000);
        dynamics.push({
            id: dynamics.length + 1,
            timestamp: timestamp.toISOString(),
            views: Math.floor(Math.random() * 1000) + 100,
            reactions: Math.floor(Math.random() * 50) + 5,
            shares: Math.floor(Math.random() * 20) + 1,
            comments: Math.floor(Math.random() * 30) + 2,
            engagement_rate: Math.round((Math.random() * 8 + 2) * 100) / 100, // 2-10%
            hour: timestamp.getHours(),
            day_of_week: timestamp.getDay(),
            trend: Math.random() > 0.5 ? 'up' : 'down'
        });
    }
    
    return dynamics;
}

/**
 * Generate demo top posts data
 * @param {number} count - Number of posts to generate (1-100)
 * @returns {Array} Top posts data
 */
export function generateTopPosts(count = 10) {
    const posts = [];
    const sampleTitles = [
        "🚀 Major breakthrough in AI technology",
        "📊 Market analysis reveals surprising trends",
        "🎯 New marketing strategy shows 300% ROI",
        "💡 Innovation spotlight: Future tech predictions",
        "📈 Growth hacking techniques that actually work",
        "🔥 Viral content creation masterclass",
        "💼 Business transformation success story",
        "🌟 Industry leaders share their secrets",
        "📱 Mobile-first strategy drives engagement",
        "🎨 Creative campaigns that changed everything"
    ];
    
    for (let i = 0; i < Math.min(count, 100); i++) {
        const baseViews = Math.floor(Math.random() * 50000) + 1000;
        posts.push({
            id: i + 1,
            title: sampleTitles[i % sampleTitles.length],
            views: baseViews,
            reactions: Math.floor(baseViews * 0.08), // ~8% reaction rate
            shares: Math.floor(baseViews * 0.03), // ~3% share rate
            comments: Math.floor(baseViews * 0.05), // ~5% comment rate
            engagement_rate: Math.round((Math.random() * 12 + 3) * 100) / 100, // 3-15%
            published_at: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
            channel_id: `${DEFAULT_DEMO_CHANNEL_ID}_${Math.floor(Math.random() * 3) + 1}`,
            performance_score: Math.round((Math.random() * 40 + 60) * 100) / 100, // 60-100
            trending: Math.random() > 0.7
        });
    }
    
    // Sort by views descending
    return posts.sort((a, b) => b.views - a.views);
}

/**
 * Generate demo best posting times recommendations
 * @returns {Array} Best time recommendations
 */
export function generateBestTimeRecommendations() {
    const recommendations = [];
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    
    days.forEach((day, index) => {
        // Generate 2-3 time slots per day
        const slotsCount = Math.floor(Math.random() * 2) + 2;
        
        for (let slot = 0; slot < slotsCount; slot++) {
            const hour = [9, 12, 15, 18, 21][Math.floor(Math.random() * 5)];
            const minute = [0, 15, 30, 45][Math.floor(Math.random() * 4)];
            
            recommendations.push({
                id: recommendations.length + 1,
                day_of_week: index,
                day_name: day,
                hour: hour,
                minute: minute,
                time_slot: `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`,
                engagement_score: Math.round((Math.random() * 30 + 70) * 100) / 100, // 70-100
                audience_activity: Math.round((Math.random() * 40 + 60) * 100) / 100, // 60-100
                competition_level: ['low', 'medium', 'high'][Math.floor(Math.random() * 3)],
                recommended: Math.random() > 0.3, // 70% recommended
                confidence: Math.round((Math.random() * 25 + 75) * 100) / 100, // 75-100%
                historical_performance: Math.round((Math.random() * 20 + 80) * 100) / 100 // 80-100%
            });
        }
    });
    
    // Sort by engagement score descending
    return recommendations.sort((a, b) => b.engagement_score - a.engagement_score);
}

/**
 * Generate demo AI recommendations
 * @returns {Array} AI recommendations
 */
export function generateAIRecommendations() {
    const recommendations = [
        {
            id: 1,
            type: "content_optimization",
            title: "Optimize posting schedule",
            description: "Post during peak engagement hours (18:00-20:00) to increase reach by 45%",
            impact_score: 85,
            confidence: 92,
            category: "timing",
            priority: "high",
            estimated_improvement: "45% more reach",
            implementation_effort: "low",
            tags: ["timing", "engagement", "reach"]
        },
        {
            id: 2,
            type: "content_strategy",
            title: "Use more visual content",
            description: "Posts with images get 65% more engagement than text-only posts",
            impact_score: 78,
            confidence: 88,
            category: "content",
            priority: "medium",
            estimated_improvement: "65% more engagement",
            implementation_effort: "medium",
            tags: ["visual", "engagement", "content"]
        },
        {
            id: 3,
            type: "hashtag_optimization",
            title: "Optimize hashtag strategy",
            description: "Use 3-5 targeted hashtags instead of 10+ for better discoverability",
            impact_score: 72,
            confidence: 85,
            category: "hashtags",
            priority: "medium",
            estimated_improvement: "30% better reach",
            implementation_effort: "low",
            tags: ["hashtags", "discoverability", "reach"]
        },
        {
            id: 4,
            type: "engagement_boost",
            title: "Increase call-to-action usage",
            description: "Posts with clear CTAs get 23% more comments and shares",
            impact_score: 68,
            confidence: 80,
            category: "engagement",
            priority: "low",
            estimated_improvement: "23% more interaction",
            implementation_effort: "low",
            tags: ["cta", "engagement", "interaction"]
        },
        {
            id: 5,
            type: "audience_targeting",
            title: "Focus on trending topics",
            description: "Leverage trending topics in your niche for 3x organic reach",
            impact_score: 90,
            confidence: 76,
            category: "trending",
            priority: "high",
            estimated_improvement: "300% organic reach",
            implementation_effort: "medium",
            tags: ["trending", "organic", "reach"]
        }
    ];
    
    return recommendations.sort((a, b) => b.impact_score - a.impact_score);
}

/**
 * Demo Analytics Service Class
 * Provides organized access to all demo analytics data
 */
export class DemoAnalyticsService {
    constructor() {
        this.cache = new Map();
        this.cacheTTL = {
            postDynamics: 5 * 60 * 1000,    // 5 minutes
            topPosts: 10 * 60 * 1000,       // 10 minutes
            bestTimes: 30 * 60 * 1000,      // 30 minutes
            aiRecommendations: 15 * 60 * 1000 // 15 minutes
        };
    }
    
    /**
     * Get cached data or generate new
     */
    getCached(key, generator, ttl) {
        const cached = this.cache.get(key);
        const now = Date.now();
        
        if (cached && (now - cached.timestamp < ttl)) {
            return cached.data;
        }
        
        const data = generator();
        this.cache.set(key, { data, timestamp: now });
        return data;
    }
    
    /**
     * Get demo post dynamics with caching
     */
    getPostDynamics(hours = 24) {
        const key = `postDynamics_${hours}`;
        return this.getCached(key, () => generatePostDynamics(hours), this.cacheTTL.postDynamics);
    }
    
    /**
     * Get demo top posts with caching
     */
    getTopPosts(count = 10) {
        const key = `topPosts_${count}`;
        return this.getCached(key, () => generateTopPosts(count), this.cacheTTL.topPosts);
    }
    
    /**
     * Get demo best times with caching
     */
    getBestTimes() {
        const key = 'bestTimes';
        return this.getCached(key, generateBestTimeRecommendations, this.cacheTTL.bestTimes);
    }
    
    /**
     * Get demo AI recommendations with caching
     */
    getAIRecommendations() {
        const key = 'aiRecommendations';
        return this.getCached(key, generateAIRecommendations, this.cacheTTL.aiRecommendations);
    }
    
    /**
     * Clear specific cache or all cache
     */
    clearCache(key = null) {
        if (key) {
            this.cache.delete(key);
        } else {
            this.cache.clear();
        }
    }
    
    /**
     * Get cache statistics
     */
    getCacheStats() {
        return {
            totalEntries: this.cache.size,
            entries: Array.from(this.cache.keys()),
            lastUpdated: new Date().toISOString()
        };
    }
}

// Create singleton instance
export const demoAnalyticsService = new DemoAnalyticsService();

export default demoAnalyticsService;
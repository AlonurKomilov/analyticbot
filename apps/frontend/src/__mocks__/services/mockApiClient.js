import axios from 'axios';

// Mock churn data
import {
    churnPredictorStats,
    mockChurnPredictions,
    retentionStrategies,
    riskSegments
} from '../aiServices/churnPredictor.js';

/**
 * Mock API Client for demo users
 * Simulates real API calls with mock data
 */
class MockApiClient {
    constructor() {
        this.baseURL = 'https://84dp9jc9-11400.euw.devtunnels.ms';
        this.timeout = 5000;
    }

    // Simulate network delay
    async delay(ms = 500) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // GET method simulation
    async get(url) {
        await this.delay();

        // Route mock responses based on URL
        switch (url) {
            case '/ai/churn/stats':
                return { data: churnPredictorStats };

            case '/ai/churn/predictions':
                return { data: mockChurnPredictions };

            case '/ai/churn/strategies':
                return { data: retentionStrategies };

            case '/ai/predictive/stats':
                const { predictiveStats } = await import('../aiServices/predictiveAnalytics.js');
                return { data: predictiveStats };

            case '/ai/predictive/forecasts':
                const { mockForecasts } = await import('../aiServices/predictiveAnalytics.js');
                return { data: mockForecasts };

            case '/ai/predictive/insights':
                const { trendInsights } = await import('../aiServices/predictiveAnalytics.js');
                return { data: trendInsights };

            case '/ai/predictive/models':
                const { forecastModels } = await import('../aiServices/predictiveAnalytics.js');
                return { data: forecastModels };

            case '/health':
                return {
                    data: {
                        status: "ok",
                        environment: "demo",
                        version: "demo-mode",
                        timestamp: new Date().toISOString()
                    }
                };

            case '/analytics/channels':
                // Return demo channels data
                return {
                    data: [
                        {
                            id: 'demo_channel_1',
                            title: 'Demo Analytics Channel',
                            username: '@demo_analytics',
                            subscriber_count: 15420,
                            total_posts: 1250,
                            avg_views: 8750,
                            engagement_rate: 12.5,
                            created_at: '2024-01-15T10:00:00Z'
                        },
                        {
                            id: 'demo_channel_2',
                            title: 'Demo Marketing Channel',
                            username: '@demo_marketing',
                            subscriber_count: 8350,
                            total_posts: 890,
                            avg_views: 5420,
                            engagement_rate: 15.8,
                            created_at: '2024-02-20T14:30:00Z'
                        }
                    ]
                };

            // Handle dynamic analytics endpoints
            default:
                // Handle analytics insights for any channel ID
                if (url.startsWith('/analytics/insights/')) {
                    return {
                        data: {
                            channel_analytics: {
                                total_views: 125430,
                                total_subscribers: 15420,
                                engagement_rate: 12.5,
                                avg_views_per_post: 8750,
                                growth_rate: 8.3
                            }
                        }
                    };
                }

                // Handle channel metrics
                if (url.includes('/analytics/channels/') && url.includes('/metrics')) {
                    return {
                        data: {
                            metrics: {
                                views: 125430,
                                subscribers: 15420,
                                posts: 1250,
                                engagement: 12.5,
                                growth: 8.3
                            }
                        }
                    };
                }

                // Handle demo top posts
                if (url.includes('/analytics/demo/top-posts')) {
                    return {
                        data: {
                            posts: [
                                {
                                    id: 1,
                                    text: "Demo post with high engagement",
                                    views: 15420,
                                    reactions: 850,
                                    date: "2024-09-20"
                                },
                                {
                                    id: 2,
                                    text: "Another popular demo post",
                                    views: 12300,
                                    reactions: 650,
                                    date: "2024-09-19"
                                }
                            ]
                        }
                    };
                }

                // Handle advanced recommendations
                if (url.includes('/api/v2/analytics/advanced/recommendations/')) {
                    return {
                        data: {
                            recommendations: [
                                {
                                    type: "posting_time",
                                    suggestion: "Post between 6-8 PM for best engagement",
                                    confidence: 85
                                },
                                {
                                    type: "content_type",
                                    suggestion: "Images get 40% more engagement than text-only posts",
                                    confidence: 92
                                }
                            ]
                        }
                    };
                }

                // If no dynamic endpoint matches, throw error
                throw new Error(`Mock endpoint not implemented: ${url}`);
        }
    }

    // POST method simulation
    async post(url, data, config = {}) {
        await this.delay();

        // Handle authentication endpoints
        if (url === '/auth/login') {
            console.log('🎭 Mock login for demo user:', data.email);

            // Validate demo credentials (matching backend)
            const validDemoEmails = [
                'demo@analyticbot.com',
                'viewer@analyticbot.com',
                'guest@analyticbot.com',
                'admin@analyticbot.com'
            ];
            const isDemoEmail = data.email && (
                validDemoEmails.includes(data.email) ||
                data.email.includes('demo@') ||
                data.email.includes('viewer@') ||
                data.email.includes('guest@')
            );

            if (isDemoEmail) {
                return {
                    data: {
                        access_token: `demo_token_${Date.now()}`,
                        refresh_token: `demo_refresh_${Date.now()}`,
                        user: {
                            id: 999999,
                            email: data.email,
                            username: data.email.split('@')[0],
                            is_demo: true,
                            plan: 'demo',
                            created_at: new Date().toISOString()
                        }
                    }
                };
            } else {
                // For non-demo emails during mock mode, simulate authentication error
                throw new Error('Demo mode: Use demo email addresses (demo@, viewer@, guest@)');
            }
        }

        if (url === '/auth/register') {
            console.log('🎭 Mock registration for demo user:', data.email);

            return {
                data: {
                    access_token: `demo_token_${Date.now()}`,
                    refresh_token: `demo_refresh_${Date.now()}`,
                    user: {
                        id: Date.now(),
                        email: data.email,
                        username: data.username || data.email.split('@')[0],
                        is_demo: true,
                        plan: 'demo',
                        created_at: new Date().toISOString()
                    }
                }
            };
        }

        // Handle file uploads
        if (url === '/upload' || url.includes('upload')) {
            return {
                data: {
                    success: true,
                    file_id: `demo_file_${Date.now()}`,
                    filename: data instanceof FormData ? 'demo_file.csv' : 'demo_data.json',
                    size: 1024,
                    upload_url: `https://demo-cdn.analyticbot.com/uploads/demo_file_${Date.now()}`,
                    message: 'Demo file upload completed successfully'
                }
            };
        }

        // Default success response
        return {
            data: {
                success: true,
                message: 'Mock operation completed',
                data: data
            }
        };
    }

    // PUT method simulation
    async put(url, data) {
        await this.delay();
        return {
            data: {
                success: true,
                message: 'Mock update completed',
                data: data
            }
        };
    }

    // DELETE method simulation
    async delete(url) {
        await this.delay();
        return {
            data: {
                success: true,
                message: 'Mock deletion completed'
            }
        };
    }

    // File upload simulation
    async uploadFileDirect(file, onProgress) {
        console.info('🎭 Demo mode: Simulating file upload');

        // Simulate upload progress
        if (onProgress) {
            const progressSteps = [10, 25, 50, 75, 90, 100];
            for (const progress of progressSteps) {
                await new Promise(resolve => setTimeout(resolve, 100));
                onProgress(progress);
            }
        }

        return {
            success: true,
            file_id: `demo_file_${Date.now()}`,
            file_name: file.name,
            file_size: file.size,
            file_type: file.type,
            upload_url: `https://demo-cdn.analyticbot.com/uploads/demo_file_${Date.now()}`,
            message: 'Demo file upload completed successfully'
        };
    }
}

export default new MockApiClient();

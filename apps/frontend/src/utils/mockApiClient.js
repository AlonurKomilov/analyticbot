/**
 * Mock API for TWA Development
 * 
 * This provides mock data for frontend development and testing
 * when the backend is not available or during development.
 */

const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Mock data
const mockChannels = [
    {
        id: 1,
        title: "Tech News",
        username: "@technews",
        subscriber_count: 15420,
        is_active: true
    },
    {
        id: 2,
        title: "Daily Updates",
        username: "@dailyupdates",
        subscriber_count: 8930,
        is_active: true
    }
];

const mockScheduledPosts = [
    {
        id: 1,
        title: "Breaking: New Tech Announcement",
        content: "Major tech company announces revolutionary product...",
        channel_id: 1,
        scheduled_at: new Date(Date.now() + 3600000).toISOString(),
        status: "scheduled",
        views: 0
    },
    {
        id: 2,
        title: "Daily Market Update",
        content: "Stock market shows positive trends today...",
        channel_id: 2,
        scheduled_at: new Date(Date.now() + 7200000).toISOString(),
        status: "scheduled",
        views: 0
    }
];

const mockAnalytics = {
    postDynamics: {
        period: '24h',
        data: Array.from({ length: 24 }, (_, i) => ({
            hour: i,
            timestamp: new Date(Date.now() - (23 - i) * 3600000).toISOString(),
            views: Math.floor(Math.random() * 1000) + 100,
            engagement: Math.floor(Math.random() * 50) + 10,
            clicks: Math.floor(Math.random() * 100) + 5
        }))
    },
    topPosts: [
        {
            id: 1,
            title: "Viral Tech News",
            views: 25430,
            engagement_rate: 8.5,
            clicks: 1250,
            ctr: 4.9,
            published_at: new Date(Date.now() - 86400000).toISOString()
        },
        {
            id: 2,
            title: "Market Analysis",
            views: 18920,
            engagement_rate: 6.2,
            clicks: 890,
            ctr: 4.7,
            published_at: new Date(Date.now() - 172800000).toISOString()
        },
        {
            id: 3,
            title: "Product Review",
            views: 12340,
            engagement_rate: 9.1,
            clicks: 670,
            ctr: 5.4,
            published_at: new Date(Date.now() - 259200000).toISOString()
        }
    ],
    bestTimeRecommendations: {
        timeframe: 'week',
        recommendations: [
            {
                day: 'Monday',
                optimal_times: ['09:00', '14:00', '19:00'],
                engagement_score: 8.5,
                reasoning: 'Highest engagement rates on Mondays at these times'
            },
            {
                day: 'Tuesday',
                optimal_times: ['10:00', '15:00', '20:00'],
                engagement_score: 7.8,
                reasoning: 'Good engagement for tech content on Tuesdays'
            },
            {
                day: 'Wednesday',
                optimal_times: ['11:00', '16:00', '21:00'],
                engagement_score: 8.2,
                reasoning: 'Mid-week peak engagement times'
            }
        ],
        overall_best_time: '14:00',
        confidence: 0.85
    }
};

export const mockApiClient = {
    // Initial data
    get: async (endpoint) => {
        await delay(500); // Simulate network delay
        
        switch (endpoint) {
            case '/initial-data':
                return {
                    channels: mockChannels,
                    scheduled_posts: mockScheduledPosts,
                    plan: {
                        name: 'Pro',
                        max_channels: 10,
                        max_posts_per_month: 500
                    }
                };
            
            case '/analytics/post-dynamics':
                return mockAnalytics.postDynamics;
            
            case '/analytics/top-posts':
                return { posts: mockAnalytics.topPosts };
            
            case '/analytics/best-time':
                return mockAnalytics.bestTimeRecommendations;
            
            default:
                throw new Error(`Mock endpoint not implemented: ${endpoint}`);
        }
    },
    
    // POST requests
    post: async (endpoint, data) => {
        await delay(800);
        
        switch (endpoint) {
            case '/channels': {
                const newChannel = {
                    id: Date.now(),
                    title: data.title,
                    username: data.username,
                    subscriber_count: 0,
                    is_active: true
                };
                mockChannels.push(newChannel);
                return newChannel;
            }
            
            case '/schedule': {
                const newPost = {
                    id: Date.now(),
                    title: data.title,
                    content: data.content,
                    channel_id: data.channel_id,
                    scheduled_at: data.scheduled_at,
                    status: 'scheduled',
                    views: 0
                };
                mockScheduledPosts.push(newPost);
                return newPost;
            }
            
            case '/media/upload-direct': {
                // Simulate file upload with progress
                const uploadResult = {
                    file_id: `file_${Date.now()}`,
                    file_name: data.get ? data.get('file')?.name : 'uploaded_file.jpg',
                    file_size: 1024 * 1024, // 1MB
                    file_type: 'image/jpeg',
                    telegram_file_id: `telegram_${Date.now()}`,
                    storage_channel_id: data.get ? data.get('channel_id') : -1001234567890,
                    upload_timestamp: new Date().toISOString(),
                    metadata: {
                        compression_applied: true,
                        compression_ratio: 0.85
                    }
                };
                return uploadResult;
            }
            
            default:
                throw new Error(`Mock POST endpoint not implemented: ${endpoint}`);
        }
    },
    
    // DELETE requests
    delete: async (endpoint) => {
        await delay(300);
        
        if (endpoint.startsWith('/schedule/')) {
            const postId = parseInt(endpoint.split('/')[2]);
            const index = mockScheduledPosts.findIndex(p => p.id === postId);
            if (index !== -1) {
                mockScheduledPosts.splice(index, 1);
                return { message: 'Post deleted successfully' };
            }
        }
        
        if (endpoint.startsWith('/channels/')) {
            const channelId = parseInt(endpoint.split('/')[2]);
            const index = mockChannels.findIndex(c => c.id === channelId);
            if (index !== -1) {
                mockChannels.splice(index, 1);
                return { message: 'Channel deleted successfully' };
            }
        }
        
        throw new Error(`Mock DELETE endpoint not implemented: ${endpoint}`);
    }
};

// Development mode detection
export const isDevelopment = import.meta.env.DEV;

// Enhanced API client that can switch between mock and real API
export const createApiClient = () => {
    const useMockApi = isDevelopment && localStorage.getItem('useMockApi') === 'true';
    
    if (useMockApi) {
        console.log('🔧 Using Mock API for development');
        return mockApiClient;
    }
    
    // Real API client (existing implementation)
    const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
    
    return {
        get: async (endpoint) => {
            const response = await fetch(`${baseURL}${endpoint}`, {
                headers: {
                    'Accept': 'application/json',
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return response.json();
        },
        
        post: async (endpoint, data) => {
            const isFormData = data instanceof FormData;
            
            const response = await fetch(`${baseURL}${endpoint}`, {
                method: 'POST',
                headers: isFormData ? {} : {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                body: isFormData ? data : JSON.stringify(data)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return response.json();
        },
        
        delete: async (endpoint) => {
            const response = await fetch(`${baseURL}${endpoint}`, {
                method: 'DELETE',
                headers: {
                    'Accept': 'application/json',
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return response.json();
        }
    };
};

// Export the default API client
export const apiClient = createApiClient();

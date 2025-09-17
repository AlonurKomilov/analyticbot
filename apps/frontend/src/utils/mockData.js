/**
 * @deprecated This file is deprecated - use __mocks__ structure instead
 * 
 * MIGRATION NOTICE:
 * This 380-line monolithic mock data file has been migrated to a modular structure:
 * 
 * OLD: import { mockAnalyticsData } from './utils/mockData.js'
 * NEW: import { mockAnalyticsData } from '../__mocks__/index.js'
 * 
 * Benefits of new structure:
 * - Modular organization by domain (analytics, user, channels, system)
 * - Easier to maintain and find specific mock data
 * - Better separation of concerns
 * - TypeScript-ready structure
 * 
 * This file will be removed in a future version.
 */

export const mockAnalyticsData = {
  // Post dynamics for charts
  postDynamics: {
    timeline: [
      { timestamp: '2025-08-31T00:00:00Z', views: 1250, likes: 45, shares: 12, comments: 8 },
      { timestamp: '2025-08-31T02:00:00Z', views: 890, likes: 32, shares: 8, comments: 5 },
      { timestamp: '2025-08-31T04:00:00Z', views: 650, likes: 18, shares: 5, comments: 3 },
      { timestamp: '2025-08-31T06:00:00Z', views: 1100, likes: 38, shares: 15, comments: 7 },
      { timestamp: '2025-08-31T08:00:00Z', views: 2350, likes: 89, shares: 32, comments: 15 },
      { timestamp: '2025-08-31T10:00:00Z', views: 3200, likes: 124, shares: 45, comments: 22 },
      { timestamp: '2025-08-31T12:00:00Z', views: 4100, likes: 156, shares: 67, comments: 31 },
      { timestamp: '2025-08-31T14:00:00Z', views: 3800, likes: 142, shares: 52, comments: 28 },
      { timestamp: '2025-08-31T16:00:00Z', views: 4500, likes: 178, shares: 78, comments: 35 },
      { timestamp: '2025-08-31T18:00:00Z', views: 5200, likes: 198, shares: 89, comments: 42 },
      { timestamp: '2025-08-31T20:00:00Z', views: 4800, likes: 165, shares: 72, comments: 38 },
      { timestamp: '2025-08-31T22:00:00Z', views: 3500, likes: 125, shares: 48, comments: 25 }
    ],
    summary: {
      totalViews: 35340,
      totalReactions: 1310,
      totalForwards: 551,
      avgEngagement: 5.27,
      peakHour: '18:00',
      growthRate: 12.5
    }
  },

  // Top performing posts
  topPosts: [
    {
      id: 1,
      title: "🚀 New Feature: AI Analytics Dashboard",
      views: 8540,
      reactions: 324,
      forwards: 89,
      engagement: 4.83,
      date: "2025-08-29T10:30:00Z",
      channel: "AnalyticBot Updates"
    },
    {
      id: 2,
      title: "📊 Weekly Performance Report",
      views: 7230,
      reactions: 298,
      forwards: 67,
      engagement: 5.05,
      date: "2025-08-28T14:15:00Z",
      channel: "Analytics Channel"
    },
    {
      id: 3,
      title: "🎯 Best Practices for Content",
      views: 6890,
      reactions: 287,
      forwards: 78,
      engagement: 5.29,
      date: "2025-08-27T16:45:00Z",
      channel: "Marketing Tips"
    },
    {
      id: 4,
      title: "🧠 AI-Powered Insights",
      views: 6540,
      reactions: 267,
      forwards: 54,
      engagement: 4.91,
      date: "2025-08-26T12:20:00Z",
      channel: "Tech Updates"
    },
    {
      id: 5,
      title: "📈 Growth Metrics Analysis",
      views: 5980,
      reactions: 234,
      forwards: 43,
      engagement: 4.63,
      date: "2025-08-25T09:10:00Z",
      channel: "Business Analytics"
    }
  ],

  // Best posting times
  bestTimeRecommendations: {
    weekdays: [
      { day: 'Monday', bestTimes: ['09:00', '14:00', '18:00'], score: 8.5 },
      { day: 'Tuesday', bestTimes: ['10:00', '15:00', '19:00'], score: 9.2 },
      { day: 'Wednesday', bestTimes: ['09:30', '14:30', '18:30'], score: 8.8 },
      { day: 'Thursday', bestTimes: ['10:30', '15:30', '19:30'], score: 9.0 },
      { day: 'Friday', bestTimes: ['09:00', '13:00', '17:00'], score: 8.3 },
      { day: 'Saturday', bestTimes: ['11:00', '16:00', '20:00'], score: 7.8 },
      { day: 'Sunday', bestTimes: ['12:00', '17:00', '19:00'], score: 7.5 }
    ],
    optimal: {
      time: '18:00',
      day: 'Tuesday',
      expectedEngagement: 9.2,
      confidence: 94
    }
  },

  // Engagement metrics
  engagementMetrics: {
    overview: {
      totalSubscribers: 15847,
      activeSubscribers: 12456,
      avgViewsPerPost: 4285,
      avgReactionsPerPost: 167,
      avgForwardsPerPost: 45,
      engagementRate: 4.94
    },
    trends: {
      subscribersGrowth: 8.5,
      engagementGrowth: 12.3,
      viewsGrowth: 15.7,
      reactionsGrowth: 9.8
    },
    byChannel: [
      { name: 'AnalyticBot Updates', subscribers: 5420, engagement: 6.2 },
      { name: 'Analytics Channel', subscribers: 4230, engagement: 5.8 },
      { name: 'Marketing Tips', subscribers: 3890, engagement: 5.5 },
      { name: 'Tech Updates', subscribers: 2307, engagement: 4.9 }
    ]
  },

  // User channels
  channels: [
    {
      id: 1,
      name: 'AnalyticBot Updates',
      username: '@analyticbot_updates',
      subscribers: 5420,
      status: 'active',
      lastPost: '2025-08-29T10:30:00Z'
    },
    {
      id: 2,
      name: 'Analytics Channel',
      username: '@analytics_insights',
      subscribers: 4230,
      status: 'active',
      lastPost: '2025-08-28T14:15:00Z'
    },
    {
      id: 3,
      name: 'Marketing Tips',
      username: '@marketing_pro_tips',
      subscribers: 3890,
      status: 'active',
      lastPost: '2025-08-27T16:45:00Z'
    }
  ],

  // User plan info
  plan: {
    name: 'Professional',
    maxChannels: 10,
    maxPostsPerMonth: 500,
    features: ['Advanced Analytics', 'AI Insights', 'Custom Branding', 'Priority Support']
  },

  // System status
  systemStatus: {
    botStatus: 'online',
    apiStatus: 'operational',
    analyticsStatus: 'processing',
    lastUpdate: new Date().toISOString()
  }
};

// Mock initial data for app initialization (enhanced version)
const generateMockInitialDataEnhanced = () => ({
  user: {
    id: 'demo_user_123',
    username: 'analytics_pro',
    first_name: 'Analytics',
    last_name: 'Pro',
    language_code: 'en'
  },
  plan: {
    name: 'Professional Demo',
    max_channels: 10,
    max_scheduled_posts: 100,
    analytics_enabled: true,
    features: ['analytics', 'scheduling', 'media_upload', 'best_time_recommendations']
  },
  channels: [
    {
      id: 'demo_channel_1',
      username: '@demo_tech_channel',
      title: 'Tech Innovations',
      member_count: 15420,
      type: 'channel',
      is_active: true,
      last_post_date: '2025-08-31T10:30:00Z'
    },
    {
      id: 'demo_channel_2',
      username: '@demo_marketing_tips',
      title: 'Marketing Tips',
      member_count: 8750,
      type: 'channel',
      is_active: true,
      last_post_date: '2025-08-31T08:15:00Z'
    },
    {
      id: 'demo_channel_3',
      username: '@demo_startup_news',
      title: 'Startup News',
      member_count: 12300,
      type: 'channel',
      is_active: true,
      last_post_date: '2025-08-31T07:45:00Z'
    }
  ],
  scheduled_posts: [
    {
      id: 'scheduled_1',
      channel_id: 'demo_channel_1',
      message: 'Exciting new AI developments are coming! Stay tuned for our deep dive analysis. 🚀\n\n#AI #Technology #Innovation',
      schedule_time: '2025-08-31T18:00:00Z',
      media_type: 'photo',
      status: 'scheduled'
    },
    {
      id: 'scheduled_2',
      channel_id: 'demo_channel_2',
      message: '5 Marketing Strategies That Actually Work in 2025 📈\n\nThread below 👇\n\n#Marketing #Strategy #Business',
      schedule_time: '2025-08-31T20:30:00Z',
      media_type: null,
      status: 'scheduled'
    },
    {
      id: 'scheduled_3',
      channel_id: 'demo_channel_3',
      message: 'BREAKING: New startup funding round hits $2.5M 💰\n\nFull details in our analysis:\n\n#Startup #Funding #Investment',
      schedule_time: '2025-09-01T09:00:00Z',
      media_type: 'document',
      status: 'scheduled'
    }
  ],
  analytics_summary: mockAnalyticsData
});

/**
 * Simulates API delay for realistic loading experience
 */
export const mockApiCall = async (data, delay = 300) => {
  await new Promise(resolve => setTimeout(resolve, delay));
  return data;
};

/**
 * Get mock post dynamics data
 */
export const getMockPostDynamics = async (period = '24h') => {
  return mockApiCall({
    ...mockAnalyticsData.postDynamics,
    period,
    timestamp: new Date().toISOString()
  });
};

/**
 * Get mock top posts data
 */
export const getMockTopPosts = async (period = 'today', sortBy = 'views') => {
  const posts = [...mockAnalyticsData.topPosts];
  
  // Sort based on criteria
  if (sortBy === 'engagement') {
    posts.sort((a, b) => b.engagement - a.engagement);
  } else if (sortBy === 'reactions') {
    posts.sort((a, b) => b.reactions - a.reactions);
  }
  
  return mockApiCall({
    posts,
    period,
    sortBy,
    total: posts.length
  });
};

/**
 * Get mock best time recommendations
 */
export const getMockBestTime = async (timeframe = 'week') => {
  return mockApiCall({
    ...mockAnalyticsData.bestTimeRecommendations,
    timeframe,
    generatedAt: new Date().toISOString()
  });
};

/**
 * Get mock engagement metrics
 */
export const getMockEngagementMetrics = async (period = '7d') => {
  return mockApiCall({
    ...mockAnalyticsData.engagementMetrics,
    period,
    calculatedAt: new Date().toISOString()
  });
};

/**
 * Get mock initial data for app (enhanced with data source switching)
 */
export const getMockInitialData = () => {
    return new Promise(resolve => {
        setTimeout(() => {
            resolve(generateMockInitialDataEnhanced());
        }, 200); // Fast loading for better UX
    });
};

/**
 * Get mock storage files for media browser
 */
export const getMockStorageFiles = (limit = 20, offset = 0) => {
    const mockFiles = [
        {
            id: 1,
            filename: "sample-image-1.jpg",
            size: 245760,
            type: "image/jpeg",
            uploaded_at: "2025-09-06T10:30:00Z",
            url: "https://picsum.photos/800/600?random=1"
        },
        {
            id: 2,
            filename: "demo-video.mp4",
            size: 15728640,
            type: "video/mp4",
            uploaded_at: "2025-09-06T09:15:00Z",
            url: "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4"
        },
        {
            id: 3,
            filename: "presentation.pdf",
            size: 1048576,
            type: "application/pdf",
            uploaded_at: "2025-09-05T14:20:00Z",
            url: "#"
        },
        {
            id: 4,
            filename: "chart-data.png",
            size: 156000,
            type: "image/png",
            uploaded_at: "2025-09-05T11:45:00Z",
            url: "https://picsum.photos/600/400?random=2"
        },
        {
            id: 5,
            filename: "audio-clip.mp3",
            size: 3145728,
            type: "audio/mpeg",
            uploaded_at: "2025-09-04T16:30:00Z",
            url: "#"
        }
    ];

    // Simulate pagination
    const total = mockFiles.length;
    const paginatedFiles = mockFiles.slice(offset, offset + limit);

    return {
        files: paginatedFiles,
        total: total,
        limit: limit,
        offset: offset,
        hasMore: offset + limit < total
    };
};
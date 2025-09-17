/**
 * Mock Registry - Central Index for all Mock Data
 * 
 * This file provides a centralized way to access all mock data
 * while maintaining the modular structure.
 */

// Import all mock data modules
import * as analytics from './analytics/index.js';
import * as channels from './channels/index.js';
import * as user from './user/index.js';
import * as system from './system/index.js';

// Re-export everything for easy access
export { analytics, channels, user, system };

// Backward compatibility - recreate the original mockAnalyticsData structure
export const mockAnalyticsData = {
  postDynamics: analytics.postDynamicsData,
  topPosts: analytics.topPostsData,
  bestTimeRecommendations: analytics.bestTimeData,
  engagementMetrics: analytics.engagementData,
  channels: channels.channelsData,
  plan: user.planData,
  systemStatus: system.systemStatusData
};

// Mock API functions for backward compatibility
export const getMockPostDynamics = analytics.getPostDynamics;
export const getMockTopPosts = analytics.getTopPosts;
export const getMockBestTime = analytics.getBestTime;
export const getMockEngagementMetrics = analytics.getEngagementMetrics;

// Enhanced mock data generator for initialization
const generateMockInitialDataEnhanced = () => ({
  user: user.userData,
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
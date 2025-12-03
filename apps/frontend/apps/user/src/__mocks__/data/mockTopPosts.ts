/**
 * Fallback Mock Data Generator for Top Posts
 * Used when backend demo endpoint is unavailable
 */

import type { TopPost } from '@/types/api';

export interface MockTopPost {
  id: string | number;
  content: string;
  views: number;
  shares: number;
  reactions: number;
  engagementRate: number;
  publishedTime: string;
  viralityScore?: number;
  // Optional extra fields for richer mock data
  title?: string;
  likes?: number;
  comments?: number;
  engagement?: number;
  created_at?: string;
  thumbnail?: string;
  type?: string;
}

/**
 * Generate mock top posts for demo/fallback purposes
 */
export function generateMockTopPosts(count: number = 10): TopPost[] {
  const postTypes = ['article', 'video', 'image', 'poll', 'general'];
  const titles = [
    '🚀 Breaking: New Product Launch Success!',
    '📊 Monthly Analytics Report - Record Growth',
    '💡 Top 10 Tips for Better Engagement',
    '🎯 Achievement Unlocked: 10K Followers!',
    '🔥 Trending Now: Community Highlights',
    '📸 Behind the Scenes: Team Update',
    '⚡ Quick Win: Optimization Results',
    '🎨 Design Showcase: Latest Projects',
    '📱 Mobile App Update Released',
    '🌟 Customer Success Stories',
    '💬 Q&A Session Recap',
    '🎉 Milestone Celebration',
    '📈 Growth Strategy Deep Dive',
    '🔍 Industry Insights & Trends',
    '✨ Feature Spotlight'
  ];

  const posts: TopPost[] = [];
  const now = Date.now();

  for (let i = 0; i < count; i++) {
    const baseViews = 1000 + Math.floor(Math.random() * 10000);
    const views = baseViews + (count - i) * 500; // Higher views for earlier posts
    const likes = Math.floor(views * (0.05 + Math.random() * 0.15)); // 5-20% engagement
    const shares = Math.floor(likes * (0.1 + Math.random() * 0.3)); // 10-40% of likes
    const reactions = Math.floor(likes * (0.8 + Math.random() * 0.4)); // Similar to likes
    const comments = Math.floor(likes * (0.2 + Math.random() * 0.4)); // 20-60% of likes
    const engagementRate = ((likes + shares + reactions) / views);
    const viralityScore = (shares / views) * 100;

    // Create post date (within last 30 days)
    const daysAgo = Math.floor(Math.random() * 30);
    const postDate = new Date(now - daysAgo * 24 * 60 * 60 * 1000);

    posts.push({
      id: `demo_post_${i + 1}`,
      content: `${titles[i % titles.length]} - Demo post content. This is sample data used when the backend is unavailable.`,
      views,
      shares,
      reactions,
      engagementRate: parseFloat(engagementRate.toFixed(4)),
      publishedTime: postDate.toISOString(),
      viralityScore: parseFloat(viralityScore.toFixed(2)),
      // Extra fields as any for backward compatibility
      ...(likes && { likes }),
      ...(comments && { comments }),
      title: titles[i % titles.length],
      thumbnail: `https://picsum.photos/200/200?random=${i}`,
      type: postTypes[Math.floor(Math.random() * postTypes.length)]
    } as TopPost);
  }

  // Sort by views descending (top posts)
  return posts.sort((a, b) => b.views - a.views);
}

/**
 * Generate mock top posts with specific parameters
 */
export function generateMockTopPostsWithParams(params: {
  count?: number;
  minViews?: number;
  maxViews?: number;
  engagementRate?: number;
}): TopPost[] {
  const {
    count = 10,
    minViews = 1000,
    maxViews = 50000,
    engagementRate = 0.1
  } = params;

  const posts = generateMockTopPosts(count);

  // Adjust views to be within specified range
  const viewRange = maxViews - minViews;
  posts.forEach((post, index) => {
    // Distribute views evenly from max to min
    post.views = maxViews - Math.floor((viewRange / count) * index);

    // Recalculate engagement based on new views
    const totalEngagement = Math.floor(post.views * engagementRate);
    post.shares = Math.floor(totalEngagement * 0.2);
    post.reactions = Math.floor(totalEngagement * 0.5);
    post.engagementRate = engagementRate;

    // Add extra properties through type assertion
    (post as any).likes = Math.floor(totalEngagement * 0.5);
    (post as any).comments = Math.floor(totalEngagement * 0.3);
    (post as any).engagement = parseFloat((engagementRate * 100).toFixed(2));
  });

  return posts;
}

/**
 * Create empty top posts response (for true offline mode)
 */
export function createEmptyTopPostsResponse(channelId: string) {
  return {
    channelId,
    posts: [],
    source: 'offline',
    message: 'Backend unavailable. Please check your connection or use demo mode.',
    generatedAt: new Date().toISOString()
  };
}

/**
 * Create demo top posts response with fallback data
 */
export function createDemoTopPostsResponse(channelId: string, count: number = 10) {
  return {
    channelId,
    posts: generateMockTopPosts(count),
    source: 'client_fallback',
    message: 'Using client-side fallback data (backend unavailable)',
    generatedAt: new Date().toISOString()
  };
}

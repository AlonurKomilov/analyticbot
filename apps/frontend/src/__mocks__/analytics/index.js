/**
 * Analytics Mock Data - Main Index
 * Exports all analytics-related mock data in a structured way
 */

export { postDynamicsData, getPostDynamics } from './postDynamics.js';
export { topPostsData, getTopPosts } from './topPosts.js';
export { engagementData, getEngagementMetrics } from './engagementMetrics.js';
export { bestTimeData, getBestTime } from './bestTime.js';

// Combined analytics data for backward compatibility
import { postDynamicsData } from './postDynamics.js';
import { topPostsData } from './topPosts.js';
import { bestTimeData } from './bestTime.js';
import { engagementData } from './engagementMetrics.js';

export const mockAnalyticsData = {
  get postDynamics() {
    return postDynamicsData;
  },
  get topPosts() {
    return topPostsData;
  },
  get bestTimeRecommendations() {
    return bestTimeData;
  },
  get engagementMetrics() {
    return engagementData;
  }
};
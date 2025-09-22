/**
 * Analytics Mock Data - Main Index
 * Exports all analytics-related mock data in a structured way
 */

export { postDynamicsData, getPostDynamics } from './postDynamics.js';
export { topPostsData, getTopPosts } from './topPosts.js';
export { engagementData, getEngagementMetrics } from './engagementMetrics.js';
export { bestTimeData, getBestTime } from './bestTime.js';

// Demo Analytics Services (moved from backend API)
export { demoAnalyticsService, generatePostDynamics, generateTopPosts, generateBestTimeRecommendations, generateAIRecommendations } from './demoAnalyticsService.js';
export { demoAPI, demoEndpoints, DemoAPIService } from './demoAPI.js';

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
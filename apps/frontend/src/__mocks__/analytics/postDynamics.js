/**
 * Post Dynamics Mock Data
 * Separated from the main mockData.js for better organization
 */

export const postDynamicsData = {
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
};

export const getPostDynamics = async (period = '24h') => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 300));
  
  return {
    ...postDynamicsData,
    period,
    timestamp: new Date().toISOString()
  };
};
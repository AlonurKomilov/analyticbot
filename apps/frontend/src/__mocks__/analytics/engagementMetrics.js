/**
 * Engagement Metrics Mock Data
 * Separated from the main mockData.js for better organization
 */

export const engagementData = {
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
};

export const getEngagementMetrics = async (period = '7d') => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 300));

  return {
    ...engagementData,
    period,
    calculatedAt: new Date().toISOString()
  };
};

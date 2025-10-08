// Dashboard utility functions for AdvancedAnalyticsDashboard components

export const formatNumber = (num) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
  return num?.toString() || '0';
};

export const getMetricColor = (value, thresholds = { good: 10, warning: 5 }, theme) => {
  if (value >= thresholds.good) return theme.palette.success.main;
  if (value >= thresholds.warning) return theme.palette.warning.main;
  return theme.palette.error.main;
};

export const generateSmartAlerts = (overviewData, dynamicsData, topPostsData) => {
  const newAlerts = [];

  if (!overviewData) return newAlerts;

  // Growth spike alert
  if (overviewData.growthRate && overviewData.growthRate > 15) {
    newAlerts.push({
      id: 'growth-spike',
      type: 'success',
      title: '🚀 Growth Spike Detected!',
      message: `${overviewData.growthRate.toFixed(1)}% growth detected`,
      timestamp: new Date().toISOString(),
    });
  }

  // Low engagement alert
  if (overviewData.avgEngagement && overviewData.avgEngagement < 3) {
    newAlerts.push({
      id: 'low-engagement',
      type: 'warning',
      title: '⚠️ Low Engagement Alert',
      message: `Engagement rate is ${overviewData.avgEngagement.toFixed(1)}%`,
      timestamp: new Date().toISOString(),
    });
  }

  // High views but low engagement
  if (overviewData.totalViews > 50000 && overviewData.avgEngagement < 2) {
    newAlerts.push({
      id: 'views-engagement-gap',
      type: 'info',
      title: '📊 Views vs Engagement Gap',
      message: 'High views but low engagement - optimize content',
      timestamp: new Date().toISOString(),
    });
  }

  // Viral post detection
  if (topPostsData?.length && topPostsData[0]?.views > 100000) {
    newAlerts.push({
      id: 'viral-post',
      type: 'success',
      title: '🔥 Viral Post Alert!',
      message: `Post "${topPostsData[0].title}" has ${formatNumber(topPostsData[0].views)} views`,
      timestamp: new Date().toISOString(),
    });
  }

  return newAlerts;
};

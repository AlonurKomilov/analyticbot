/**
 * Top Posts Mock Data
 * Separated from the main mockData.js for better organization
 */

export const topPostsData = [
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
];

export const getTopPosts = async (period = 'today', sortBy = 'views') => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 300));
  
  const posts = [...topPostsData];
  
  // Sort based on criteria
  if (sortBy === 'engagement') {
    posts.sort((a, b) => b.engagement - a.engagement);
  } else if (sortBy === 'reactions') {
    posts.sort((a, b) => b.reactions - a.reactions);
  }
  
  return {
    posts,
    period,
    sortBy,
    total: posts.length
  };
};
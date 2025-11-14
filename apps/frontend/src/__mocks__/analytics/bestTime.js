/**
 * Best Time Recommendations Mock Data
 * Separated from the main mockData.js for better organization
 * 
 * NOTE: This mock data is now primarily used for fallback when real API is unavailable.
 * The main application uses real data from the backend API.
 */

// Generate daily performance data for current month (fallback only)
const generateDailyPerformance = () => {
  const today = new Date();
  const year = today.getFullYear();
  const month = today.getMonth();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const dailyPerformance = [];

  for (let day = 1; day <= daysInMonth; day++) {
    const date = new Date(year, month, day);
    const dayOfWeek = date.getDay();
    const isToday = date.toDateString() === today.toDateString();
    const isPast = date < today && !isToday;
    
    // Only add historical data for past days
    if (isPast) {
      const baseScore = [75, 85, 82, 88, 80, 65, 70][dayOfWeek]; // Sun-Sat scores
      const variance = (Math.random() - 0.5) * 30; // Add some randomness
      const avgEngagement = Math.max(1, baseScore + variance) / 10; // Convert to engagement rate
      
      dailyPerformance.push({
        date: day,
        dayOfWeek,
        avgEngagement,
        postCount: Math.floor(Math.random() * 3) + 1, // 1-3 posts
        score: avgEngagement > 8 ? 'excellent' : 
               avgEngagement > 6 ? 'good' : 
               avgEngagement > 4 ? 'average' : 'poor'
      });
    }
  }

  return dailyPerformance;
};

export const bestTimeData = {
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
  },
  // Daily performance data (fallback only)
  daily_performance: generateDailyPerformance()
};

export const getBestTime = async (timeframe = 'week') => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 300));

  return {
    ...bestTimeData,
    timeframe,
    generatedAt: new Date().toISOString(),
    // Format matching real API response
    best_times: [
      { day: 1, hour: 9, avg_engagement: 8.5, confidence: 85 },
      { day: 1, hour: 14, avg_engagement: 8.2, confidence: 82 },
      { day: 1, hour: 18, avg_engagement: 9.2, confidence: 94 },
      { day: 2, hour: 10, avg_engagement: 8.8, confidence: 88 },
      { day: 2, hour: 15, avg_engagement: 8.5, confidence: 85 },
      { day: 2, hour: 19, avg_engagement: 9.0, confidence: 90 }
    ],
    current_avg_engagement: 6.5,
    daily_performance: generateDailyPerformance(),
    hourly_engagement_trend: [
      { hour: 8, engagement: 5.2 },
      { hour: 9, engagement: 7.1 },
      { hour: 10, engagement: 8.3 },
      { hour: 11, engagement: 7.8 },
      { hour: 12, engagement: 8.9 },
      { hour: 13, engagement: 8.1 },
      { hour: 14, engagement: 9.1 },
      { hour: 15, engagement: 8.7 },
      { hour: 16, engagement: 8.2 },
      { hour: 17, engagement: 8.8 },
      { hour: 18, engagement: 9.5 },
      { hour: 19, engagement: 9.2 },
      { hour: 20, engagement: 8.4 },
      { hour: 21, engagement: 7.9 },
      { hour: 22, engagement: 6.8 }
    ],
    data_source: 'fallback_mock'
  };
};

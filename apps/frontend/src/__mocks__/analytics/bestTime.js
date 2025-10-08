/**
 * Best Time Recommendations Mock Data
 * Separated from the main mockData.js for better organization
 */

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
  }
};

export const getBestTime = async (timeframe = 'week') => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 300));

  return {
    ...bestTimeData,
    timeframe,
    generatedAt: new Date().toISOString()
  };
};

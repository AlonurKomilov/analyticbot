/**
 * Analytics Calculation Service
 *
 * Pure business logic for analytics calculations and transformations
 * Separated from store for better testability and reusability
 */

export interface MetricsCalculation {
  total: number;
  average: number;
  median: number;
  min: number;
  max: number;
  change?: number;
  changePercentage?: number;
}

export interface EngagementMetrics {
  engagementRate: number;
  reachScore: number;
  growthRate: number;
  avgViewsPerPost: number;
}

/**
 * Calculate basic statistics from number array
 */
export function calculateStatistics(values: number[]): MetricsCalculation {
  if (values.length === 0) {
    return {
      total: 0,
      average: 0,
      median: 0,
      min: 0,
      max: 0,
    };
  }

  const total = values.reduce((sum, val) => sum + val, 0);
  const average = total / values.length;

  // Calculate median
  const sorted = [...values].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  const median =
    sorted.length % 2 === 0 ? (sorted[mid - 1] + sorted[mid]) / 2 : sorted[mid];

  const min = Math.min(...values);
  const max = Math.max(...values);

  return {
    total,
    average,
    median,
    min,
    max,
  };
}

/**
 * Calculate change between two values
 */
export function calculateChange(current: number, previous: number): {
  change: number;
  changePercentage: number;
  direction: 'up' | 'down' | 'neutral';
} {
  const change = current - previous;
  const changePercentage = previous === 0 ? 0 : (change / previous) * 100;

  let direction: 'up' | 'down' | 'neutral' = 'neutral';
  if (change > 0) direction = 'up';
  else if (change < 0) direction = 'down';

  return {
    change,
    changePercentage,
    direction,
  };
}

/**
 * Calculate engagement rate
 * Formula: (Reactions + Comments + Shares) / Views * 100
 */
export function calculateEngagementRate(metrics: {
  views?: number;
  reactions?: number;
  comments?: number;
  shares?: number;
}): number {
  const { views = 0, reactions = 0, comments = 0, shares = 0 } = metrics;

  if (views === 0) return 0;

  const totalEngagements = reactions + comments + shares;
  return (totalEngagements / views) * 100;
}

/**
 * Calculate reach score (0-100)
 * Based on views, subscribers, and engagement
 */
export function calculateReachScore(metrics: {
  views?: number;
  subscribers?: number;
  engagementRate?: number;
}): number {
  const { views = 0, subscribers = 1, engagementRate = 0 } = metrics;

  // Calculate reach percentage
  const reachPercentage = (views / subscribers) * 100;

  // Weight factors
  const reachWeight = 0.6;
  const engagementWeight = 0.4;

  // Normalize reach percentage to 0-100 scale (cap at 100)
  const normalizedReach = Math.min(reachPercentage, 100);

  // Calculate weighted score
  const score = normalizedReach * reachWeight + engagementRate * engagementWeight;

  // Ensure score is between 0 and 100
  return Math.max(0, Math.min(100, score));
}

/**
 * Calculate growth rate over time period
 * Formula: ((Current - Previous) / Previous) * 100
 */
export function calculateGrowthRate(current: number, previous: number): number {
  if (previous === 0) return current > 0 ? 100 : 0;
  return ((current - previous) / previous) * 100;
}

/**
 * Calculate engagement metrics for a channel
 */
export function calculateEngagementMetrics(data: {
  totalViews: number;
  totalReactions: number;
  totalComments: number;
  totalShares: number;
  subscribers: number;
  postCount: number;
  previousSubscribers?: number;
}): EngagementMetrics {
  const engagementRate = calculateEngagementRate({
    views: data.totalViews,
    reactions: data.totalReactions,
    comments: data.totalComments,
    shares: data.totalShares,
  });

  const reachScore = calculateReachScore({
    views: data.totalViews,
    subscribers: data.subscribers,
    engagementRate,
  });

  const growthRate = data.previousSubscribers
    ? calculateGrowthRate(data.subscribers, data.previousSubscribers)
    : 0;

  const avgViewsPerPost = data.postCount > 0 ? data.totalViews / data.postCount : 0;

  return {
    engagementRate: Number(engagementRate.toFixed(2)),
    reachScore: Number(reachScore.toFixed(2)),
    growthRate: Number(growthRate.toFixed(2)),
    avgViewsPerPost: Number(avgViewsPerPost.toFixed(0)),
  };
}

/**
 * Format number with appropriate suffix (K, M, B)
 */
export function formatNumber(num: number): string {
  if (num >= 1000000000) {
    return (num / 1000000000).toFixed(1) + 'B';
  }
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  }
  return num.toString();
}

/**
 * Format percentage with sign
 */
export function formatPercentage(value: number, showSign: boolean = true): string {
  const sign = showSign && value > 0 ? '+' : '';
  return `${sign}${value.toFixed(1)}%`;
}

/**
 * Calculate percentile rank
 */
export function calculatePercentile(value: number, dataset: number[]): number {
  if (dataset.length === 0) return 0;

  const sorted = [...dataset].sort((a, b) => a - b);
  const index = sorted.findIndex((v) => v >= value);

  if (index === -1) return 100; // Value is higher than all data points

  return (index / sorted.length) * 100;
}

/**
 * Calculate moving average
 */
export function calculateMovingAverage(values: number[], window: number = 7): number[] {
  const result: number[] = [];

  for (let i = 0; i < values.length; i++) {
    const start = Math.max(0, i - window + 1);
    const subset = values.slice(start, i + 1);
    const average = subset.reduce((sum, val) => sum + val, 0) / subset.length;
    result.push(average);
  }

  return result;
}

/**
 * Detect trends in data
 */
export function detectTrend(values: number[]): {
  trend: 'increasing' | 'decreasing' | 'stable';
  confidence: number;
} {
  if (values.length < 2) {
    return { trend: 'stable', confidence: 0 };
  }

  // Simple linear regression
  const n = values.length;
  const sumX = (n * (n - 1)) / 2;
  const sumY = values.reduce((sum, val) => sum + val, 0);
  const sumXY = values.reduce((sum, val, i) => sum + i * val, 0);
  const sumX2 = (n * (n - 1) * (2 * n - 1)) / 6;

  const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);

  // Calculate confidence based on R-squared
  const avgY = sumY / n;
  const ssTotal = values.reduce((sum, val) => sum + Math.pow(val - avgY, 2), 0);
  const ssPredicted = values.reduce(
    (sum, _val, i) => sum + Math.pow(slope * i - avgY, 2),
    0
  );
  const rSquared = ssTotal === 0 ? 0 : ssPredicted / ssTotal;
  const confidence = Math.min(100, Math.abs(rSquared) * 100);

  let trend: 'increasing' | 'decreasing' | 'stable';
  if (Math.abs(slope) < 0.01) {
    trend = 'stable';
  } else if (slope > 0) {
    trend = 'increasing';
  } else {
    trend = 'decreasing';
  }

  return {
    trend,
    confidence: Number(confidence.toFixed(1)),
  };
}

/**
 * Group data by time period
 */
export function groupByPeriod<T extends { date: Date | string }>(
  data: T[],
  period: 'day' | 'week' | 'month'
): Record<string, T[]> {
  const grouped: Record<string, T[]> = {};

  data.forEach((item) => {
    const date = typeof item.date === 'string' ? new Date(item.date) : item.date;
    let key: string;

    switch (period) {
      case 'day':
        key = date.toISOString().split('T')[0];
        break;
      case 'week':
        const weekStart = new Date(date);
        weekStart.setDate(date.getDate() - date.getDay());
        key = weekStart.toISOString().split('T')[0];
        break;
      case 'month':
        key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
        break;
    }

    if (!grouped[key]) {
      grouped[key] = [];
    }
    grouped[key].push(item);
  });

  return grouped;
}

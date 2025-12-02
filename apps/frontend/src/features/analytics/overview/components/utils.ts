/**
 * Overview Page Utility Functions
 * Enhanced with performance indicators, benchmarks, and user-friendly formatting
 */

import React from 'react';
import { TrendingUp, TrendingDown, TrendingFlat } from '@mui/icons-material';

export function formatNumber(num: number | undefined | null): string {
  if (num === undefined || num === null) return '0';
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
  return num.toLocaleString();
}

export function formatPercentage(num: number | undefined | null, decimals = 2): string {
  if (num === undefined || num === null) return '0%';
  return `${num.toFixed(decimals)}%`;
}

export interface ChangeInfo {
  text: string;
  color: string;
  icon: React.ReactNode | null;
}

export function formatChange(change: number): ChangeInfo {
  if (change > 0) {
    return {
      text: `+${formatNumber(change)}`,
      color: 'success.main',
      icon: React.createElement(TrendingUp, { fontSize: 'small' }),
    };
  } else if (change < 0) {
    return {
      text: formatNumber(change),
      color: 'error.main',
      icon: React.createElement(TrendingDown, { fontSize: 'small' }),
    };
  }
  return {
    text: '0',
    color: 'text.secondary',
    icon: React.createElement(TrendingFlat, { fontSize: 'small' }),
  };
}

// ============================================================================
// Performance Rating System
// ============================================================================

export type PerformanceLevel = 'excellent' | 'good' | 'average' | 'below_average' | 'poor';

export interface PerformanceInfo {
  level: PerformanceLevel;
  label: string;
  color: string;
  emoji: string;
  description: string;
}

// Engagement Rate Benchmarks (industry standard for Telegram)
export function getEngagementRatePerformance(rate: number): PerformanceInfo {
  if (rate >= 5) {
    return { level: 'excellent', label: 'Excellent', color: '#4caf50', emoji: '🔥', description: 'Top-tier engagement, highly active audience' };
  } else if (rate >= 2) {
    return { level: 'good', label: 'Good', color: '#8bc34a', emoji: '✨', description: 'Above average engagement' };
  } else if (rate >= 1) {
    return { level: 'average', label: 'Average', color: '#ff9800', emoji: '📊', description: 'Typical for most channels' };
  } else if (rate >= 0.5) {
    return { level: 'below_average', label: 'Below Avg', color: '#ff5722', emoji: '📉', description: 'Room for improvement' };
  } else {
    return { level: 'poor', label: 'Low', color: '#f44336', emoji: '⚠️', description: 'Consider content optimization' };
  }
}

// Views per post benchmarks
export function getViewsPerformance(avgViews: number, subscriberCount: number): PerformanceInfo {
  const viewRate = subscriberCount > 0 ? (avgViews / subscriberCount) * 100 : 0;
  
  if (viewRate >= 50) {
    return { level: 'excellent', label: 'Excellent', color: '#4caf50', emoji: '🔥', description: '50%+ subscribers see each post' };
  } else if (viewRate >= 30) {
    return { level: 'good', label: 'Good', color: '#8bc34a', emoji: '✨', description: '30-50% reach rate' };
  } else if (viewRate >= 15) {
    return { level: 'average', label: 'Average', color: '#ff9800', emoji: '📊', description: '15-30% reach rate' };
  } else if (viewRate >= 5) {
    return { level: 'below_average', label: 'Below Avg', color: '#ff5722', emoji: '📉', description: 'Low reach rate' };
  } else {
    return { level: 'poor', label: 'Low', color: '#f44336', emoji: '⚠️', description: 'Very low visibility' };
  }
}

// Citation Index (virality) benchmarks
export function getCitationIndexPerformance(index: number): PerformanceInfo {
  if (index >= 10) {
    return { level: 'excellent', label: 'Viral', color: '#4caf50', emoji: '🚀', description: 'Content is widely shared' };
  } else if (index >= 5) {
    return { level: 'good', label: 'High Sharing', color: '#8bc34a', emoji: '📤', description: 'Good forward rate' };
  } else if (index >= 2) {
    return { level: 'average', label: 'Moderate', color: '#ff9800', emoji: '📊', description: 'Average sharing' };
  } else if (index >= 0.5) {
    return { level: 'below_average', label: 'Low', color: '#ff5722', emoji: '📉', description: 'Low virality' };
  } else {
    return { level: 'poor', label: 'Minimal', color: '#f44336', emoji: '💤', description: 'Rarely shared' };
  }
}

// Subscriber growth rate benchmarks
export function getGrowthPerformance(growthRate: number): PerformanceInfo {
  if (growthRate >= 10) {
    return { level: 'excellent', label: 'Rapid Growth', color: '#4caf50', emoji: '🚀', description: '10%+ growth rate' };
  } else if (growthRate >= 5) {
    return { level: 'good', label: 'Growing', color: '#8bc34a', emoji: '📈', description: 'Healthy growth' };
  } else if (growthRate >= 1) {
    return { level: 'average', label: 'Steady', color: '#ff9800', emoji: '➡️', description: 'Stable growth' };
  } else if (growthRate >= 0) {
    return { level: 'below_average', label: 'Stagnant', color: '#ff5722', emoji: '⏸️', description: 'Flat growth' };
  } else {
    return { level: 'poor', label: 'Declining', color: '#f44336', emoji: '📉', description: 'Losing subscribers' };
  }
}

// Posting frequency benchmarks
export function getPostingFrequencyPerformance(postsPerDay: number): PerformanceInfo {
  if (postsPerDay >= 5) {
    return { level: 'excellent', label: 'Very Active', color: '#4caf50', emoji: '⚡', description: '5+ posts daily' };
  } else if (postsPerDay >= 2) {
    return { level: 'good', label: 'Active', color: '#8bc34a', emoji: '✅', description: '2-5 posts daily' };
  } else if (postsPerDay >= 0.5) {
    return { level: 'average', label: 'Regular', color: '#ff9800', emoji: '📅', description: 'Every 1-2 days' };
  } else if (postsPerDay >= 0.1) {
    return { level: 'below_average', label: 'Occasional', color: '#ff5722', emoji: '🐢', description: 'Few posts per week' };
  } else {
    return { level: 'poor', label: 'Inactive', color: '#f44336', emoji: '💤', description: 'Rarely posts' };
  }
}

// ============================================================================
// Tooltip Descriptions for Metrics
// ============================================================================

export const METRIC_TOOLTIPS = {
  subscribers: {
    title: 'Subscribers',
    description: 'Total number of people subscribed to this channel.',
    calculation: 'Direct count from Telegram.',
  },
  totalPosts: {
    title: 'Total Posts',
    description: 'Total number of posts published in this channel.',
    calculation: 'Count of all non-deleted messages.',
  },
  totalViews: {
    title: 'Total Views',
    description: 'Cumulative views across all posts.',
    calculation: 'Sum of views from all posts.',
  },
  avgViewsPerPost: {
    title: 'Avg Views Per Post',
    description: 'Average number of views each post receives.',
    calculation: 'Total Views ÷ Total Posts',
  },
  engagementRate: {
    title: 'Engagement Rate (ER)',
    description: 'Percentage of viewers who interact with your content through reactions, comments, or forwards.',
    calculation: '(Reactions + Forwards + Comments) ÷ Total Views × 100',
    benchmark: 'Average: 1-3% | Good: 3-5% | Excellent: 5%+',
  },
  err: {
    title: 'ERR (Engagement Rate Ratio)',
    description: 'Average engagement actions per post.',
    calculation: 'Total Engagements ÷ Number of Posts',
  },
  avgPostReach: {
    title: 'Average Post Reach',
    description: 'How many unique users typically see each post.',
    calculation: 'Based on view patterns and subscriber count.',
  },
  citationIndex: {
    title: 'Citation Index',
    description: 'Measures how viral your content is - how often it gets shared/forwarded.',
    calculation: '(Total Forwards ÷ Posts) × 10',
    benchmark: 'Low: <2 | Moderate: 2-5 | High: 5-10 | Viral: 10+',
  },
  adReach: {
    title: 'Advertising Reach',
    description: 'Estimated reach for sponsored posts (typically lower than organic).',
    calculation: 'Avg Post Reach × 0.7 (70% estimate)',
  },
};

// Format large numbers with context
export function formatNumberWithContext(num: number, context: 'views' | 'subscribers' | 'posts' | 'general' = 'general'): string {
  const formatted = formatNumber(num);
  
  if (context === 'views' && num >= 1000000) {
    return `${formatted} views 🔥`;
  } else if (context === 'subscribers' && num >= 100000) {
    return `${formatted} 👥`;
  }
  
  return formatted;
}

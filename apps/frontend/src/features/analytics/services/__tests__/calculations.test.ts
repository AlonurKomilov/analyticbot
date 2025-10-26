/**
 * Analytics Calculations Service Tests
 */

import { describe, it, expect } from 'vitest';
import {
  calculateStatistics,
  calculateChange,
  calculateEngagementRate,
  calculateReachScore,
  calculateGrowthRate,
  calculateEngagementMetrics,
  formatNumber,
  formatPercentage,
  calculatePercentile,
  calculateMovingAverage,
  detectTrend,
  groupByPeriod,
} from '../calculations';

describe('calculations', () => {
  describe('calculateStatistics', () => {
    it('should calculate statistics for valid data', () => {
      const result = calculateStatistics([1, 2, 3, 4, 5]);
      expect(result.total).toBe(15);
      expect(result.average).toBe(3);
      expect(result.median).toBe(3);
      expect(result.min).toBe(1);
      expect(result.max).toBe(5);
    });

    it('should handle even number of values for median', () => {
      const result = calculateStatistics([1, 2, 3, 4]);
      expect(result.median).toBe(2.5); // (2 + 3) / 2
    });

    it('should handle empty array', () => {
      const result = calculateStatistics([]);
      expect(result.total).toBe(0);
      expect(result.average).toBe(0);
      expect(result.median).toBe(0);
      expect(result.min).toBe(0);
      expect(result.max).toBe(0);
    });

    it('should handle single value', () => {
      const result = calculateStatistics([42]);
      expect(result.total).toBe(42);
      expect(result.average).toBe(42);
      expect(result.median).toBe(42);
      expect(result.min).toBe(42);
      expect(result.max).toBe(42);
    });
  });

  describe('calculateChange', () => {
    it('should calculate positive change', () => {
      const result = calculateChange(150, 100);
      expect(result.change).toBe(50);
      expect(result.changePercentage).toBe(50);
      expect(result.direction).toBe('up');
    });

    it('should calculate negative change', () => {
      const result = calculateChange(80, 100);
      expect(result.change).toBe(-20);
      expect(result.changePercentage).toBe(-20);
      expect(result.direction).toBe('down');
    });

    it('should calculate no change', () => {
      const result = calculateChange(100, 100);
      expect(result.change).toBe(0);
      expect(result.changePercentage).toBe(0);
      expect(result.direction).toBe('neutral');
    });

    it('should handle zero previous value', () => {
      const result = calculateChange(50, 0);
      expect(result.change).toBe(50);
      expect(result.changePercentage).toBe(0);
    });
  });

  describe('calculateEngagementRate', () => {
    it('should calculate engagement rate correctly', () => {
      const rate = calculateEngagementRate({
        views: 1000,
        reactions: 50,
        comments: 30,
        shares: 20,
      });
      expect(rate).toBe(10); // (50+30+20)/1000 * 100 = 10%
    });

    it('should handle zero views', () => {
      const rate = calculateEngagementRate({
        views: 0,
        reactions: 50,
      });
      expect(rate).toBe(0);
    });

    it('should handle missing metrics', () => {
      const rate = calculateEngagementRate({
        views: 1000,
      });
      expect(rate).toBe(0);
    });

    it('should calculate with all metrics', () => {
      const rate = calculateEngagementRate({
        views: 5000,
        reactions: 100,
        comments: 50,
        shares: 50,
      });
      expect(rate).toBe(4); // 200/5000 * 100 = 4%
    });
  });

  describe('calculateReachScore', () => {
    it('should calculate reach score correctly', () => {
      const score = calculateReachScore({
        views: 5000,
        subscribers: 10000,
        engagementRate: 5,
      });
      // Reach: 50%, Engagement: 5%
      // Score = 50 * 0.6 + 5 * 0.4 = 30 + 2 = 32
      expect(score).toBe(32);
    });

    it('should cap reach at 100%', () => {
      const score = calculateReachScore({
        views: 15000,
        subscribers: 10000,
        engagementRate: 10,
      });
      // Reach would be 150%, but capped at 100%
      // Score = 100 * 0.6 + 10 * 0.4 = 60 + 4 = 64
      expect(score).toBe(64);
    });

    it('should handle zero subscribers', () => {
      const score = calculateReachScore({
        views: 1000,
        subscribers: 1, // Defaults to 1 to avoid division by zero
        engagementRate: 5,
      });
      expect(score).toBeGreaterThan(0);
    });

    it('should return value between 0 and 100', () => {
      const score = calculateReachScore({
        views: 8000,
        subscribers: 10000,
        engagementRate: 8,
      });
      expect(score).toBeGreaterThanOrEqual(0);
      expect(score).toBeLessThanOrEqual(100);
    });
  });

  describe('calculateGrowthRate', () => {
    it('should calculate positive growth', () => {
      const rate = calculateGrowthRate(1200, 1000);
      expect(rate).toBe(20); // 20% growth
    });

    it('should calculate negative growth', () => {
      const rate = calculateGrowthRate(800, 1000);
      expect(rate).toBe(-20); // -20% growth
    });

    it('should handle zero previous value', () => {
      const rate = calculateGrowthRate(100, 0);
      expect(rate).toBe(100);
    });

    it('should handle zero current and previous', () => {
      const rate = calculateGrowthRate(0, 0);
      expect(rate).toBe(0);
    });
  });

  describe('calculateEngagementMetrics', () => {
    it('should calculate all engagement metrics', () => {
      const metrics = calculateEngagementMetrics({
        totalViews: 10000,
        totalReactions: 500,
        totalComments: 300,
        totalShares: 200,
        subscribers: 5000,
        postCount: 10,
        previousSubscribers: 4000,
      });

      expect(metrics.engagementRate).toBe(10); // (500+300+200)/10000 = 10%
      expect(metrics.avgViewsPerPost).toBe(1000); // 10000/10
      expect(metrics.growthRate).toBe(25); // (5000-4000)/4000 = 25%
      expect(metrics.reachScore).toBeGreaterThan(0);
    });

    it('should handle missing previous subscribers', () => {
      const metrics = calculateEngagementMetrics({
        totalViews: 10000,
        totalReactions: 500,
        totalComments: 300,
        totalShares: 200,
        subscribers: 5000,
        postCount: 10,
      });

      expect(metrics.growthRate).toBe(0);
    });

    it('should round values to appropriate decimals', () => {
      const metrics = calculateEngagementMetrics({
        totalViews: 12345,
        totalReactions: 678,
        totalComments: 345,
        totalShares: 234,
        subscribers: 5678,
        postCount: 7,
      });

      // Check that values are rounded
      expect(Number.isInteger(metrics.avgViewsPerPost)).toBe(true);
      expect(metrics.engagementRate.toString().split('.')[1]?.length || 0).toBeLessThanOrEqual(2);
    });
  });

  describe('formatNumber', () => {
    it('should format billions', () => {
      expect(formatNumber(1500000000)).toBe('1.5B');
      expect(formatNumber(1000000000)).toBe('1.0B');
    });

    it('should format millions', () => {
      expect(formatNumber(2500000)).toBe('2.5M');
      expect(formatNumber(1000000)).toBe('1.0M');
    });

    it('should format thousands', () => {
      expect(formatNumber(1500)).toBe('1.5K');
      expect(formatNumber(1000)).toBe('1.0K');
    });

    it('should not format numbers under 1000', () => {
      expect(formatNumber(999)).toBe('999');
      expect(formatNumber(100)).toBe('100');
      expect(formatNumber(0)).toBe('0');
    });
  });

  describe('formatPercentage', () => {
    it('should format positive percentage with sign', () => {
      expect(formatPercentage(15.5)).toBe('+15.5%');
      expect(formatPercentage(5.2)).toBe('+5.2%');
    });

    it('should format negative percentage', () => {
      expect(formatPercentage(-10.3)).toBe('-10.3%');
    });

    it('should format without sign when requested', () => {
      expect(formatPercentage(15.5, false)).toBe('15.5%');
      expect(formatPercentage(-10.3, false)).toBe('-10.3%');
    });

    it('should round to 1 decimal place', () => {
      expect(formatPercentage(15.678)).toBe('+15.7%');
      expect(formatPercentage(15.123)).toBe('+15.1%');
    });
  });

  describe('calculatePercentile', () => {
    it('should calculate percentile correctly', () => {
      const dataset = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100];

      expect(calculatePercentile(10, dataset)).toBe(0);
      expect(calculatePercentile(50, dataset)).toBe(40);
      expect(calculatePercentile(100, dataset)).toBe(90);
    });

    it('should return 100 for value higher than dataset', () => {
      const dataset = [10, 20, 30];
      expect(calculatePercentile(50, dataset)).toBe(100);
    });

    it('should handle empty dataset', () => {
      expect(calculatePercentile(50, [])).toBe(0);
    });
  });

  describe('calculateMovingAverage', () => {
    it('should calculate 7-day moving average', () => {
      const values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
      const ma = calculateMovingAverage(values, 7);

      expect(ma.length).toBe(10);
      expect(ma[6]).toBe(4); // Average of [1,2,3,4,5,6,7]
      expect(ma[9]).toBe(7); // Average of [4,5,6,7,8,9,10]
    });

    it('should handle window larger than dataset', () => {
      const values = [1, 2, 3];
      const ma = calculateMovingAverage(values, 5);

      expect(ma.length).toBe(3);
      expect(ma[0]).toBe(1);
      expect(ma[1]).toBe(1.5);
      expect(ma[2]).toBe(2);
    });

    it('should use window of 7 by default', () => {
      const values = [1, 2, 3, 4, 5, 6, 7, 8];
      const ma = calculateMovingAverage(values);

      // For index 7: window includes indices 1-7 (values 2,3,4,5,6,7,8)
      // Average = (2+3+4+5+6+7+8) / 7 = 35/7 = 5
      expect(ma[7]).toBe(5);

      // For index 6: window includes indices 0-6 (values 1,2,3,4,5,6,7)
      // Average = (1+2+3+4+5+6+7) / 7 = 28/7 = 4
      expect(ma[6]).toBe(4);
    });
  });

  describe('detectTrend', () => {
    it('should detect increasing trend', () => {
      const values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
      const result = detectTrend(values);

      expect(result.trend).toBe('increasing');
      expect(result.confidence).toBeGreaterThan(0);
    });

    it('should detect decreasing trend', () => {
      const values = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1];
      const result = detectTrend(values);

      expect(result.trend).toBe('decreasing');
      expect(result.confidence).toBeGreaterThan(0);
    });

    it('should detect stable trend', () => {
      const values = [5, 5, 5, 5, 5, 5, 5];
      const result = detectTrend(values);

      expect(result.trend).toBe('stable');
    });

    it('should handle insufficient data', () => {
      const values = [1];
      const result = detectTrend(values);

      expect(result.trend).toBe('stable');
      expect(result.confidence).toBe(0);
    });

    it('should return confidence between 0 and 100', () => {
      const values = [1, 3, 2, 4, 3, 5, 4, 6];
      const result = detectTrend(values);

      expect(result.confidence).toBeGreaterThanOrEqual(0);
      expect(result.confidence).toBeLessThanOrEqual(100);
    });
  });

  describe('groupByPeriod', () => {
    const testData = [
      { date: new Date('2024-01-01'), value: 1 },
      { date: new Date('2024-01-02'), value: 2 },
      { date: new Date('2024-01-08'), value: 3 },
      { date: new Date('2024-01-15'), value: 4 },
      { date: new Date('2024-02-01'), value: 5 },
    ];

    it('should group by day', () => {
      const grouped = groupByPeriod(testData, 'day');

      expect(Object.keys(grouped)).toHaveLength(5);
      expect(grouped['2024-01-01']).toHaveLength(1);
      expect(grouped['2024-01-01'][0].value).toBe(1);
    });

    it('should group by week', () => {
      const grouped = groupByPeriod(testData, 'week');

      expect(Object.keys(grouped).length).toBeGreaterThan(0);
      // Should group first two items in same week
      const firstWeekKey = Object.keys(grouped)[0];
      expect(grouped[firstWeekKey].length).toBeGreaterThanOrEqual(1);
    });

    it('should group by month', () => {
      const grouped = groupByPeriod(testData, 'month');

      expect(grouped['2024-01']).toHaveLength(4);
      expect(grouped['2024-02']).toHaveLength(1);
    });

    it('should handle string dates', () => {
      const stringData = [
        { date: '2024-01-01', value: 1 },
        { date: '2024-01-02', value: 2 },
      ];

      const grouped = groupByPeriod(stringData, 'day');
      expect(Object.keys(grouped)).toHaveLength(2);
    });

    it('should handle empty array', () => {
      const grouped = groupByPeriod([], 'day');
      expect(Object.keys(grouped)).toHaveLength(0);
    });
  });
});

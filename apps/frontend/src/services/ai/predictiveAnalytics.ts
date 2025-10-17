/**
 * Predictive Analytics Service
 * Pure business logic for analytics forecasting and predictions - NO React dependencies
 *
 * This service handles:
 * - Engagement predictions
 * - Growth forecasting
 * - Trend analysis
 * - Performance predictions
 */

import { PredictiveAnalyticsAPI } from '../aiServicesAPI.js';

/**
 * Forecast result
 */
export interface ForecastResult {
  channelId: string;
  predictions: {
    date: string;
    value: number;
    confidence: number;
  }[];
  modelType: string;
  accuracy: number;
  timeframe: string;
}

/**
 * Analytics insight
 */
export interface AnalyticsInsight {
  type: 'positive' | 'negative' | 'neutral';
  title: string;
  description: string;
  confidence: number;
  recommendation?: string;
}

/**
 * Predictive Analytics Statistics
 */
export interface PredictiveAnalyticsStats {
  totalPredictions: number;
  accuracy: number;
  modelsActive: number;
  status: 'active' | 'inactive' | 'training';
}

/**
 * Forecast options
 */
export interface ForecastOptions {
  modelType?: 'engagement' | 'growth' | 'reach' | 'revenue';
  timeframe?: '7d' | '14d' | '30d' | '90d';
  confidenceThreshold?: number;
}

/**
 * Predictive Analytics Service Class
 */
export class PredictiveAnalyticsService {
  /**
   * Generate forecast for a channel
   */
  async generateForecast(
    channelId: string,
    options: ForecastOptions = {}
  ): Promise<ForecastResult> {
    if (!channelId || channelId.trim().length === 0) {
      throw new Error('Channel ID is required');
    }

    try {
      const result = await PredictiveAnalyticsAPI.generateForecast(channelId, options);

      return {
        channelId: result.channel_id || channelId,
        predictions: result.predictions || [],
        modelType: result.model_type || options.modelType || 'engagement',
        accuracy: result.accuracy || 0,
        timeframe: result.timeframe || options.timeframe || '7d'
      };
    } catch (error) {
      console.error('Forecast generation failed:', error);
      throw new Error('Failed to generate forecast');
    }
  }

  /**
   * Get analytics insights for a channel
   */
  async getInsights(channelId: string): Promise<AnalyticsInsight[]> {
    if (!channelId || channelId.trim().length === 0) {
      throw new Error('Channel ID is required');
    }

    try {
      const result = await PredictiveAnalyticsAPI.getInsights(channelId);
      return result.insights || [];
    } catch (error) {
      console.error('Failed to fetch insights:', error);
      throw new Error('Failed to load analytics insights');
    }
  }

  /**
   * Calculate forecast accuracy
   */
  calculateAccuracy(
    predictions: number[],
    actualValues: number[]
  ): number {
    if (predictions.length !== actualValues.length || predictions.length === 0) {
      return 0;
    }

    const errors = predictions.map((pred, i) =>
      Math.abs(pred - actualValues[i]) / Math.max(actualValues[i], 1)
    );

    const mape = errors.reduce((sum, error) => sum + error, 0) / errors.length;
    return Math.max(0, (1 - mape) * 100);
  }

  /**
   * Get trend direction from predictions
   */
  getTrend(predictions: { date: string; value: number }[]): {
    direction: 'increasing' | 'decreasing' | 'stable';
    strength: 'weak' | 'moderate' | 'strong';
    changePercent: number;
  } {
    if (predictions.length < 2) {
      return { direction: 'stable', strength: 'weak', changePercent: 0 };
    }

    const firstValue = predictions[0].value;
    const lastValue = predictions[predictions.length - 1].value;
    const changePercent = ((lastValue - firstValue) / Math.max(firstValue, 1)) * 100;

    let direction: 'increasing' | 'decreasing' | 'stable' = 'stable';
    if (Math.abs(changePercent) > 5) {
      direction = changePercent > 0 ? 'increasing' : 'decreasing';
    }

    let strength: 'weak' | 'moderate' | 'strong' = 'weak';
    if (Math.abs(changePercent) > 20) strength = 'strong';
    else if (Math.abs(changePercent) > 10) strength = 'moderate';

    return {
      direction,
      strength,
      changePercent
    };
  }

  /**
   * Generate recommendations based on predictions
   */
  generateRecommendations(forecast: ForecastResult): string[] {
    const recommendations: string[] = [];
    const trend = this.getTrend(forecast.predictions);

    if (trend.direction === 'decreasing' && trend.strength !== 'weak') {
      recommendations.push('Consider increasing content frequency to boost engagement');
      recommendations.push('Analyze top-performing posts and replicate successful patterns');
    }

    if (trend.direction === 'increasing') {
      recommendations.push('Maintain current content strategy - showing positive results');
      recommendations.push('Consider scaling up content production to capitalize on growth');
    }

    if (forecast.accuracy < 70) {
      recommendations.push('Low prediction confidence - collect more data for better accuracy');
    }

    if (recommendations.length === 0) {
      recommendations.push('Continue monitoring metrics and maintain current strategy');
    }

    return recommendations;
  }

  /**
   * Validate forecast data
   */
  validateForecast(forecast: Partial<ForecastResult>): {
    valid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];

    if (!forecast.channelId) {
      errors.push('Channel ID is required');
    }

    if (!forecast.predictions || forecast.predictions.length === 0) {
      errors.push('Predictions array cannot be empty');
    }

    if (forecast.accuracy !== undefined && (forecast.accuracy < 0 || forecast.accuracy > 100)) {
      errors.push('Accuracy must be between 0 and 100');
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }

  /**
   * Format timeframe for display
   */
  formatTimeframe(timeframe: string): string {
    const formats: Record<string, string> = {
      '7d': '7 Days',
      '14d': '2 Weeks',
      '30d': '1 Month',
      '90d': '3 Months'
    };
    return formats[timeframe] || timeframe;
  }

  /**
   * Get model type display name
   */
  getModelTypeName(modelType: string): string {
    const names: Record<string, string> = {
      'engagement': 'Engagement Prediction',
      'growth': 'Growth Forecast',
      'reach': 'Reach Prediction',
      'revenue': 'Revenue Forecast'
    };
    return names[modelType] || modelType;
  }
}

// Export singleton instance
export const predictiveAnalyticsService = new PredictiveAnalyticsService();

export default predictiveAnalyticsService;

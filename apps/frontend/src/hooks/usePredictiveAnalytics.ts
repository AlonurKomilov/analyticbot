/**
 * usePredictiveAnalytics Hook
 * React hook for predictive analytics using the new PredictiveAnalyticsAPI
 */

import { useState, useEffect, useCallback } from 'react';
import {
  predictiveAnalyticsService,
  ForecastResult,
  AnalyticsInsight,
  ForecastOptions
} from '@services/ai/predictiveAnalytics';

export interface UsePredictiveAnalyticsOptions {
  channelId?: string;
  autoFetch?: boolean;
}

export interface UsePredictiveAnalyticsReturn {
  // Data
  forecast: ForecastResult | null;
  insights: AnalyticsInsight[];

  // Loading states
  loading: boolean;
  loadingForecast: boolean;
  loadingInsights: boolean;

  // Error states
  error: string | null;

  // Actions
  generateForecast: (channelId: string, options?: ForecastOptions) => Promise<ForecastResult>;
  fetchInsights: (channelId: string) => Promise<void>;
  refresh: () => Promise<void>;

  // Utilities
  getTrend: () => ReturnType<typeof predictiveAnalyticsService.getTrend> | null;
  generateRecommendations: () => string[];
  calculateAccuracy: (predictions: number[], actualValues: number[]) => number;
}

/**
 * usePredictiveAnalytics Hook
 * Provides predictive analytics functionality
 */
export function usePredictiveAnalytics(
  options: UsePredictiveAnalyticsOptions = {}
): UsePredictiveAnalyticsReturn {
  const { channelId: initialChannelId, autoFetch = false } = options;

  // State
  const [forecast, setForecast] = useState<ForecastResult | null>(null);
  const [insights, setInsights] = useState<AnalyticsInsight[]>([]);

  const [loading, setLoading] = useState(false);
  const [loadingForecast, setLoadingForecast] = useState(false);
  const [loadingInsights, setLoadingInsights] = useState(false);

  const [error, setError] = useState<string | null>(null);

  /**
   * Generate forecast for a channel
   */
  const generateForecast = useCallback(async (
    channelId: string,
    options: ForecastOptions = {}
  ): Promise<ForecastResult> => {
    if (!channelId) {
      throw new Error('Channel ID is required');
    }

    setLoadingForecast(true);
    setError(null);

    try {
      const result = await predictiveAnalyticsService.generateForecast(channelId, options);
      setForecast(result);
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate forecast';
      setError(errorMessage);
      console.error('Failed to generate forecast:', err);
      throw err;
    } finally {
      setLoadingForecast(false);
    }
  }, []);

  /**
   * Fetch insights for a channel
   */
  const fetchInsights = useCallback(async (channelId: string) => {
    if (!channelId) {
      setError('Channel ID is required');
      return;
    }

    setLoadingInsights(true);
    setError(null);

    try {
      const result = await predictiveAnalyticsService.getInsights(channelId);
      setInsights(result);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch insights';
      setError(errorMessage);
      console.error('Failed to fetch insights:', err);
    } finally {
      setLoadingInsights(false);
    }
  }, []);

  /**
   * Refresh all data for current channel
   */
  const refresh = useCallback(async () => {
    if (!initialChannelId) {
      console.warn('No channel ID provided for refresh');
      return;
    }

    setLoading(true);

    await Promise.all([
      generateForecast(initialChannelId),
      fetchInsights(initialChannelId)
    ]);

    setLoading(false);
  }, [initialChannelId, generateForecast, fetchInsights]);

  /**
   * Get trend from current forecast
   */
  const getTrend = useCallback(() => {
    if (!forecast || !forecast.predictions) {
      return null;
    }
    return predictiveAnalyticsService.getTrend(forecast.predictions);
  }, [forecast]);

  /**
   * Generate recommendations from current forecast
   */
  const generateRecommendations = useCallback(() => {
    if (!forecast) {
      return [];
    }
    return predictiveAnalyticsService.generateRecommendations(forecast);
  }, [forecast]);

  /**
   * Calculate accuracy
   */
  const calculateAccuracy = useCallback((predictions: number[], actualValues: number[]) => {
    return predictiveAnalyticsService.calculateAccuracy(predictions, actualValues);
  }, []);

  /**
   * Auto-fetch on mount if enabled
   */
  useEffect(() => {
    if (autoFetch && initialChannelId) {
      refresh();
    }
  }, [autoFetch, initialChannelId, refresh]);

  return {
    // Data
    forecast,
    insights,

    // Loading states
    loading,
    loadingForecast,
    loadingInsights,

    // Error
    error,

    // Actions
    generateForecast,
    fetchInsights,
    refresh,

    // Utilities
    getTrend,
    generateRecommendations,
    calculateAccuracy
  };
}

export default usePredictiveAnalytics;

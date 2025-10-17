/**
 * React Hook for Content Optimizer Service
 * Connects React components to the pure business logic service
 */

import { useState, useCallback } from 'react';
import { contentOptimizerService, ContentAnalysisResult, ContentOptimizerStats, OptimizationOptions } from '@services/ai/contentOptimizer';

export const useContentOptimizer = () => {
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [stats, setStats] = useState<ContentOptimizerStats>({
    totalOptimized: 0,
    todayOptimized: 0,
    avgImprovement: 0,
    status: 'inactive'
  });
  const [error, setError] = useState<string | null>(null);

  /**
   * Load service statistics
   */
  const loadStats = useCallback(async () => {
    try {
      setError(null);
      const serviceStats = await contentOptimizerService.getStats();
      setStats(serviceStats);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load statistics';
      setError(errorMessage);
      console.error('Failed to load stats:', err);
    }
  }, []);

  /**
   * Analyze and optimize content
   */
  const optimizeContent = useCallback(async (
    content: string,
    options?: OptimizationOptions
  ): Promise<ContentAnalysisResult | null> => {
    // Validate content first
    const validation = contentOptimizerService.validateContent(content);
    if (!validation.valid) {
      setError(validation.error || 'Invalid content');
      return null;
    }

    setIsOptimizing(true);
    setError(null);

    try {
      const result = await contentOptimizerService.analyzeContent(content, options);

      // Refresh stats after optimization
      await loadStats();

      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Optimization failed';
      setError(errorMessage);
      console.error('Optimization error:', err);
      return null;
    } finally {
      setIsOptimizing(false);
    }
  }, [loadStats]);

  /**
   * Calculate local metrics without API call
   */
  const calculateMetrics = useCallback((content: string) => {
    return contentOptimizerService.calculateLocalMetrics(content);
  }, []);

  /**
   * Generate suggestions based on content
   */
  const getSuggestions = useCallback((content: string, metrics?: any) => {
    return contentOptimizerService.generateSuggestions(content, metrics);
  }, []);

  return {
    // State
    isOptimizing,
    stats,
    error,

    // Actions
    optimizeContent,
    loadStats,
    calculateMetrics,
    getSuggestions,
    clearError: () => setError(null)
  };
};

export default useContentOptimizer;

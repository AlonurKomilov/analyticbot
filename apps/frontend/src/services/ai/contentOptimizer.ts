/**
 * Content Optimizer Service
 * Pure business logic for content optimization - NO React dependencies
 *
 * This service handles:
 * - Content analysis and scoring
 * - AI-powered content optimization
 * - Performance metrics calculation
 * - Optimization recommendations
 */

import { ContentOptimizerAPI, AIServicesAPI } from '../aiServicesAPI.js';

/**
 * Content analysis result type
 */
export interface ContentAnalysisResult {
  score: number;
  scoreImprovement: number;
  suggestions: string[];
  optimizedContent?: string;
  metrics: {
    readability: number;
    engagement: number;
    seoScore: number;
    sentiment: number;
  };
}

/**
 * Optimization options
 */
export interface OptimizationOptions {
  channelId?: string;
  tone?: 'professional' | 'casual' | 'enthusiastic' | 'informative';
  targetAudience?: string;
  includeEmojis?: boolean;
  maxLength?: number;
}

/**
 * Service statistics
 */
export interface ContentOptimizerStats {
  totalOptimized: number;
  todayOptimized: number;
  avgImprovement: number;
  status: 'active' | 'inactive' | 'error';
}

/**
 * Content Optimizer Service Class
 * Encapsulates all business logic for content optimization
 */
export class ContentOptimizerService {
  /**
   * Analyze content and get optimization suggestions
   */
  async analyzeContent(
    content: string,
    options: OptimizationOptions = {}
  ): Promise<ContentAnalysisResult> {
    if (!content || content.trim().length === 0) {
      throw new Error('Content cannot be empty');
    }

    try {
      const result = await ContentOptimizerAPI.analyzeContent(content, options);

      return {
        score: result.score || 0,
        scoreImprovement: result.score_improvement || 0,
        suggestions: result.suggestions || [],
        optimizedContent: result.optimized_content,
        metrics: {
          readability: result.metrics?.readability || 0,
          engagement: result.metrics?.engagement || 0,
          seoScore: result.metrics?.seo_score || 0,
          sentiment: result.metrics?.sentiment || 0,
        }
      };
    } catch (error) {
      console.error('Content analysis failed:', error);
      throw new Error('Failed to analyze content. Please try again.');
    }
  }

  /**
   * Get service statistics
   */
  async getStats(): Promise<ContentOptimizerStats> {
    try {
      const stats = await AIServicesAPI.getAllStats();
      const optimizerStats = stats.content_optimizer;

      return {
        totalOptimized: optimizerStats.total_optimized || 0,
        todayOptimized: optimizerStats.today_count || 0,
        avgImprovement: optimizerStats.avg_improvement || 0,
        status: optimizerStats.status || 'inactive',
      };
    } catch (error) {
      console.error('Failed to fetch stats:', error);
      throw new Error('Failed to load service statistics');
    }
  }

  /**
   * Validate content before optimization
   */
  validateContent(content: string, maxLength: number = 4096): {
    valid: boolean;
    error?: string;
  } {
    if (!content || content.trim().length === 0) {
      return { valid: false, error: 'Content cannot be empty' };
    }

    if (content.length > maxLength) {
      return {
        valid: false,
        error: `Content exceeds maximum length of ${maxLength} characters`
      };
    }

    return { valid: true };
  }

  /**
   * Calculate content metrics locally (without API call)
   */
  calculateLocalMetrics(content: string) {
    const words = content.trim().split(/\s+/).length;
    const sentences = content.split(/[.!?]+/).filter(s => s.trim()).length;
    const avgWordsPerSentence = sentences > 0 ? words / sentences : 0;

    // Simple readability estimation (Flesch-Kincaid approximation)
    const readabilityScore = Math.max(
      0,
      Math.min(100, 206.835 - 1.015 * avgWordsPerSentence)
    );

    // Simple engagement estimation based on length and structure
    const hasEmojis = /[\u{1F300}-\u{1F9FF}]/u.test(content);
    const hasQuestions = /\?/.test(content);
    const engagementScore =
      (words > 10 && words < 100 ? 30 : 0) +
      (hasEmojis ? 25 : 0) +
      (hasQuestions ? 25 : 0) +
      (sentences > 2 ? 20 : 0);

    return {
      words,
      sentences,
      avgWordsPerSentence: Math.round(avgWordsPerSentence * 10) / 10,
      readabilityScore: Math.round(readabilityScore),
      engagementScore: Math.min(100, engagementScore),
      estimatedReadingTime: Math.ceil(words / 200), // minutes
    };
  }

  /**
   * Generate optimization suggestions based on content analysis
   */
  generateSuggestions(content: string, _metrics?: any): string[] {
    const suggestions: string[] = [];
    const localMetrics = this.calculateLocalMetrics(content);

    if (localMetrics.words < 10) {
      suggestions.push('Content is too short. Add more details to engage readers.');
    }

    if (localMetrics.words > 200) {
      suggestions.push('Content might be too long. Consider breaking into multiple posts.');
    }

    if (localMetrics.avgWordsPerSentence > 20) {
      suggestions.push('Sentences are too long. Try shorter, punchier sentences.');
    }

    if (!/[\u{1F300}-\u{1F9FF}]/u.test(content)) {
      suggestions.push('Consider adding relevant emojis to increase engagement.');
    }

    if (!/[!?]/.test(content) && localMetrics.sentences > 1) {
      suggestions.push('Add questions or exclamations to make content more engaging.');
    }

    if (localMetrics.readabilityScore < 60) {
      suggestions.push('Simplify language for better readability.');
    }

    return suggestions;
  }
}

// Export singleton instance
export const contentOptimizerService = new ContentOptimizerService();

// Export for testing
export default contentOptimizerService;

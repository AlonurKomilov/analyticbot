/**
 * Churn Predictor Service
 * Pure business logic for customer retention and churn prediction - NO React dependencies
 *
 * This service handles:
 * - Churn risk prediction
 * - User retention analysis
 * - Risk scoring and categorization
 * - Retention strategy recommendations
 */

import { ChurnPredictorAPI, AIServicesAPI } from '@features/ai-services/api';

/**
 * Churn prediction result
 */
export interface ChurnPredictionResult {
  userId: string;
  churnProbability: number;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  factors: string[];
  recommendations: string[];
  confidence: number;
}

/**
 * Churn statistics
 */
export interface ChurnStats {
  usersAnalyzed: number;
  highRiskUsers: number;
  mediumRiskUsers: number;
  lowRiskUsers: number;
  avgChurnProbability: number;
  retentionRate: number;
  status: 'active' | 'inactive';
}

/**
 * At-risk user
 */
export interface AtRiskUser {
  id: string;
  name: string;
  email?: string;
  churnProbability: number;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  lastActivity: string;
  factors: string[];
  recommendations: string[];
}

/**
 * Retention strategy
 */
export interface RetentionStrategy {
  name: string;
  description: string;
  targetRiskLevel: 'low' | 'medium' | 'high' | 'critical';
  effectiveness: number;
  cost: 'low' | 'medium' | 'high';
  timeframe: string;
}

/**
 * Churn Predictor Service Class
 */
export class ChurnPredictorService {
  /**
   * Predict churn for a specific user
   */
  async predictChurn(
    userId: string,
    options: { channelId?: string; includeRecommendations?: boolean } = {}
  ): Promise<ChurnPredictionResult> {
    if (!userId || userId.trim().length === 0) {
      throw new Error('User ID is required');
    }

    try {
      const result = await ChurnPredictorAPI.predictChurn(userId, options);

      return {
        userId: result.user_id || userId,
        churnProbability: result.churn_probability || 0,
        riskLevel: this.calculateRiskLevel(result.churn_probability),
        factors: result.risk_factors || [],
        recommendations: result.recommendations || [],
        confidence: result.confidence || 0
      };
    } catch (error) {
      console.error('Churn prediction failed:', error);
      throw new Error('Failed to predict churn for user');
    }
  }

  /**
   * Get churn prediction statistics
   */
  async getStats(): Promise<ChurnStats> {
    try {
      const stats = await AIServicesAPI.getAllStats();
      const churnStats = stats.churn_predictor || {};

      return {
        usersAnalyzed: churnStats.users_analyzed || 0,
        highRiskUsers: churnStats.high_risk_users || 0,
        mediumRiskUsers: churnStats.medium_risk_users || 0,
        lowRiskUsers: churnStats.low_risk_users || 0,
        avgChurnProbability: churnStats.avg_churn_probability || 0,
        retentionRate: churnStats.retention_rate || 0,
        status: churnStats.status || 'inactive'
      };
    } catch (error) {
      console.error('Failed to fetch churn stats:', error);
      throw new Error('Failed to load churn statistics');
    }
  }

  /**
   * Calculate risk level based on churn probability
   */
  calculateRiskLevel(probability: number): 'low' | 'medium' | 'high' | 'critical' {
    if (probability >= 0.8) return 'critical';
    if (probability >= 0.6) return 'high';
    if (probability >= 0.4) return 'medium';
    return 'low';
  }

  /**
   * Get risk color for UI
   */
  getRiskColor(riskLevel: string): 'success' | 'warning' | 'error' | 'default' {
    switch (riskLevel) {
      case 'critical': return 'error';
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'success';
      default: return 'default';
    }
  }

  /**
   * Filter users by risk threshold
   */
  filterByRiskThreshold(
    users: AtRiskUser[],
    threshold: 'low' | 'medium' | 'high' | 'critical'
  ): AtRiskUser[] {
    const thresholdValues = {
      low: 0.4,
      medium: 0.6,
      high: 0.8,
      critical: 1.0
    };

    const minProbability = thresholdValues[threshold];
    return users.filter(user => user.churnProbability >= minProbability);
  }

  /**
   * Sort users by churn risk (highest first)
   */
  sortByRisk(users: AtRiskUser[]): AtRiskUser[] {
    return [...users].sort((a, b) => b.churnProbability - a.churnProbability);
  }

  /**
   * Generate retention strategies based on risk level
   */
  getRetentionStrategies(riskLevel: 'low' | 'medium' | 'high' | 'critical'): RetentionStrategy[] {
    const allStrategies: RetentionStrategy[] = [
      {
        name: 'Personalized Engagement',
        description: 'Send personalized content based on user interests',
        targetRiskLevel: 'low',
        effectiveness: 75,
        cost: 'low',
        timeframe: '1-2 weeks'
      },
      {
        name: 'Special Offer',
        description: 'Provide exclusive discount or premium features',
        targetRiskLevel: 'medium',
        effectiveness: 85,
        cost: 'medium',
        timeframe: '3-5 days'
      },
      {
        name: 'Direct Outreach',
        description: 'Personal call or message from account manager',
        targetRiskLevel: 'high',
        effectiveness: 90,
        cost: 'high',
        timeframe: '1-2 days'
      },
      {
        name: 'VIP Treatment',
        description: 'Upgrade to premium tier with dedicated support',
        targetRiskLevel: 'critical',
        effectiveness: 95,
        cost: 'high',
        timeframe: 'Immediate'
      }
    ];

    const riskOrder = ['low', 'medium', 'high', 'critical'];
    const minRiskIndex = riskOrder.indexOf(riskLevel);

    return allStrategies.filter(strategy =>
      riskOrder.indexOf(strategy.targetRiskLevel) >= minRiskIndex
    );
  }

  /**
   * Calculate retention ROI
   */
  calculateRetentionROI(
    strategy: RetentionStrategy,
    userLifetimeValue: number,
    churnProbability: number
  ): {
    expectedReturn: number;
    roi: number;
    worthwhile: boolean;
  } {
    const costMultipliers = { low: 0.1, medium: 0.2, high: 0.4 };
    const strategyCost = userLifetimeValue * costMultipliers[strategy.cost];

    const retentionIncrease = (strategy.effectiveness / 100) * churnProbability;
    const expectedReturn = userLifetimeValue * retentionIncrease;

    const roi = ((expectedReturn - strategyCost) / strategyCost) * 100;

    return {
      expectedReturn,
      roi,
      worthwhile: roi > 100 // ROI > 100% is worthwhile
    };
  }

  /**
   * Validate user data for churn prediction
   */
  validateUserData(userData: Partial<AtRiskUser>): {
    valid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];

    if (!userData.id) {
      errors.push('User ID is required');
    }

    if (userData.churnProbability !== undefined) {
      if (userData.churnProbability < 0 || userData.churnProbability > 1) {
        errors.push('Churn probability must be between 0 and 1');
      }
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }

  /**
   * Generate churn risk report summary
   */
  generateRiskSummary(users: AtRiskUser[]): {
    totalUsers: number;
    criticalRisk: number;
    highRisk: number;
    mediumRisk: number;
    lowRisk: number;
    avgProbability: number;
    topFactors: { factor: string; count: number }[];
  } {
    const summary = {
      totalUsers: users.length,
      criticalRisk: 0,
      highRisk: 0,
      mediumRisk: 0,
      lowRisk: 0,
      avgProbability: 0,
      topFactors: [] as { factor: string; count: number }[]
    };

    const factorCounts = new Map<string, number>();

    users.forEach(user => {
      // Count risk levels
      switch (user.riskLevel) {
        case 'critical': summary.criticalRisk++; break;
        case 'high': summary.highRisk++; break;
        case 'medium': summary.mediumRisk++; break;
        case 'low': summary.lowRisk++; break;
      }

      // Count factors
      user.factors?.forEach(factor => {
        factorCounts.set(factor, (factorCounts.get(factor) || 0) + 1);
      });
    });

    // Calculate average probability
    summary.avgProbability = users.length > 0
      ? users.reduce((sum, user) => sum + user.churnProbability, 0) / users.length
      : 0;

    // Get top 5 factors
    summary.topFactors = Array.from(factorCounts.entries())
      .map(([factor, count]) => ({ factor, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5);

    return summary;
  }
}

// Export singleton instance
export const churnPredictorService = new ChurnPredictorService();

export default churnPredictorService;

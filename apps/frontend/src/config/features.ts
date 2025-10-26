/**
 * Feature Flags Configuration
 * Controls access to features based on user tier and roles
 */

import type { UserTier } from '@/types';

export interface FeatureConfig {
  enabled: boolean;
  requiresAuth: boolean;
  minTier?: UserTier;
  requiresRole?: string[];
  betaOnly?: boolean;
}

/**
 * Feature flag definitions
 */
export const FEATURES: Record<string, FeatureConfig> = {
  // Core Features
  DASHBOARD: {
    enabled: true,
    requiresAuth: true,
  },

  ANALYTICS: {
    enabled: true,
    requiresAuth: true,
    minTier: 'start',
  },

  ADVANCED_ANALYTICS: {
    enabled: true,
    requiresAuth: true,
    minTier: 'pro',
  },

  // AI Services
  AI_SERVICES: {
    enabled: true,
    requiresAuth: true,
    minTier: 'pro',
  },

  CONTENT_OPTIMIZER: {
    enabled: true,
    requiresAuth: true,
    minTier: 'pro',
  },

  PREDICTIVE_ANALYTICS: {
    enabled: true,
    requiresAuth: true,
    minTier: 'premium',
  },

  SECURITY_MONITORING: {
    enabled: true,
    requiresAuth: true,
    minTier: 'pro',
  },

  // Content Protection
  CONTENT_PROTECTION: {
    enabled: true,
    requiresAuth: true,
    minTier: 'pro',
  },

  // Payment Features
  PAYMENT: {
    enabled: true,
    requiresAuth: true,
  },

  SUBSCRIPTION_MANAGEMENT: {
    enabled: true,
    requiresAuth: true,
  },

  // Admin Features
  ADMIN_PANEL: {
    enabled: true,
    requiresAuth: true,
    requiresRole: ['admin', 'superadmin'],
  },

  USER_MANAGEMENT: {
    enabled: true,
    requiresAuth: true,
    requiresRole: ['admin', 'superadmin'],
  },

  CHANNEL_MANAGEMENT: {
    enabled: true,
    requiresAuth: true,
    minTier: 'start',
  },

  // Posts Features
  POST_CREATION: {
    enabled: true,
    requiresAuth: true,
    minTier: 'start',
  },

  POST_SCHEDULING: {
    enabled: true,
    requiresAuth: true,
    minTier: 'pro',
  },

  BULK_POSTING: {
    enabled: true,
    requiresAuth: true,
    minTier: 'premium',
  },

  // Beta Features
  MOBILE_APP: {
    enabled: false,
    requiresAuth: true,
    betaOnly: true,
  },

  TEAM_COLLABORATION: {
    enabled: false,
    requiresAuth: true,
    minTier: 'premium',
    betaOnly: true,
  },
} as const;

export type FeatureName = keyof typeof FEATURES;

/**
 * Check if a feature is enabled
 */
export function isFeatureEnabled(feature: FeatureName): boolean {
  return FEATURES[feature]?.enabled ?? false;
}

/**
 * Check if user has access to a feature
 */
export function hasFeatureAccess(
  feature: FeatureName,
  userTier?: UserTier,
  userRole?: string
): boolean {
  const config = FEATURES[feature];
  
  if (!config || !config.enabled) {
    return false;
  }

  // Check tier requirement
  if (config.minTier && userTier) {
    const tierOrder: UserTier[] = ['free', 'start', 'pro', 'premium'];
    const userTierIndex = tierOrder.indexOf(userTier);
    const minTierIndex = tierOrder.indexOf(config.minTier);
    
    if (userTierIndex < minTierIndex) {
      return false;
    }
  }

  // Check role requirement
  if (config.requiresRole && userRole) {
    if (!config.requiresRole.includes(userRole)) {
      return false;
    }
  }

  return true;
}

/**
 * Get all enabled features for a user
 */
export function getEnabledFeatures(userTier?: UserTier, userRole?: string): FeatureName[] {
  return (Object.keys(FEATURES) as FeatureName[]).filter(feature =>
    hasFeatureAccess(feature, userTier, userRole)
  );
}

/**
 * Get feature configuration
 */
export function getFeatureConfig(feature: FeatureName): FeatureConfig | undefined {
  return FEATURES[feature];
}

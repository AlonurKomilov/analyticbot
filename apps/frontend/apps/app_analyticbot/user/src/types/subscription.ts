/**
 * User Subscription Tier System
 * Aligned with backend UserTier enum
 *
 * Updated: October 25, 2025
 * Tier names: free, start, pro, premium
 */

/**
 * User subscription tiers
 * Determines feature access and limits
 */
export type UserTier =
  | 'free'        // Free tier - basic features only
  | 'start'       // Start tier - enhanced features (formerly 'starter')
  | 'pro'         // Pro tier - advanced features
  | 'premium';    // Premium tier - all features + priority support (formerly 'enterprise')

/**
 * Feature limits per tier
 */
export interface TierLimits {
  maxChannels: number;
  maxPostsPerMonth: number;
  maxFileSize: number; // MB
  watermarksEnabled: boolean;
  theftDetectionEnabled: boolean;
  customEmojisEnabled: boolean;
  prioritySupport: boolean;
  apiAccess: boolean;
  advancedAnalytics: boolean;
}

/**
 * Get feature limits for a tier
 */
export function getTierLimits(tier: UserTier): TierLimits {
  switch (tier) {
    case 'free':
      return {
        maxChannels: 1,
        maxPostsPerMonth: 30,
        maxFileSize: 5,
        watermarksEnabled: false,
        theftDetectionEnabled: false,
        customEmojisEnabled: false,
        prioritySupport: false,
        apiAccess: false,
        advancedAnalytics: false
      };

    case 'start':
      return {
        maxChannels: 3,
        maxPostsPerMonth: 100,
        maxFileSize: 25,
        watermarksEnabled: true,
        theftDetectionEnabled: false,
        customEmojisEnabled: false,
        prioritySupport: false,
        apiAccess: false,
        advancedAnalytics: false
      };

    case 'pro':
      return {
        maxChannels: 10,
        maxPostsPerMonth: 500,
        maxFileSize: 100,
        watermarksEnabled: true,
        theftDetectionEnabled: true,
        customEmojisEnabled: true,
        prioritySupport: false,
        apiAccess: true,
        advancedAnalytics: true
      };

    case 'premium':
      return {
        maxChannels: 9999, // Unlimited
        maxPostsPerMonth: 9999,
        maxFileSize: 500,
        watermarksEnabled: true,
        theftDetectionEnabled: true,
        customEmojisEnabled: true,
        prioritySupport: true,
        apiAccess: true,
        advancedAnalytics: true
      };
  }
}

/**
 * Tier display information
 */
export interface TierDisplayInfo {
  name: string;
  displayName: string;
  description: string;
  color: string;
  icon: string;
  popular?: boolean;
  price?: string;
}

export const TIER_DISPLAY_INFO: Record<UserTier, TierDisplayInfo> = {
  free: {
    name: 'free',
    displayName: 'Free',
    description: 'Get started with basic features',
    color: '#6B7280',
    icon: '🆓',
    price: '$0'
  },
  start: {
    name: 'start',
    displayName: 'Start',
    description: 'Perfect for small channels',
    color: '#3B82F6',
    icon: '🚀',
    price: '$9'
  },
  pro: {
    name: 'pro',
    displayName: 'Pro',
    description: 'Advanced features for growth',
    color: '#8B5CF6',
    icon: '⭐',
    popular: true,
    price: '$29'
  },
  premium: {
    name: 'premium',
    displayName: 'Premium',
    description: 'Full power for large operations',
    color: '#F59E0B',
    icon: '🏢',
    price: '$99'
  }
};

/**
 * Tier hierarchy for comparisons
 */
const TIER_HIERARCHY: Record<UserTier, number> = {
  free: 0,
  start: 1,
  pro: 2,
  premium: 3
};

/**
 * Check if user's tier meets minimum requirement
 */
export function hasTierAccess(userTier: UserTier, requiredTier: UserTier): boolean {
  return TIER_HIERARCHY[userTier] >= TIER_HIERARCHY[requiredTier];
}

/**
 * Check if feature is available for user's tier
 */
export function hasFeatureAccess(userTier: UserTier, feature: string): boolean {
  const limits = getTierLimits(userTier);

  switch (feature) {
    case 'watermarks':
      return limits.watermarksEnabled;
    case 'theft_detection':
      return limits.theftDetectionEnabled;
    case 'custom_emojis':
      return limits.customEmojisEnabled;
    case 'api':
      return limits.apiAccess;
    case 'priority_support':
      return limits.prioritySupport;
    case 'advanced_analytics':
      return limits.advancedAnalytics;
    default:
      return false;
  }
}

/**
 * Get tier upgrade recommendations
 */
export function getTierUpgradeRecommendation(currentTier: UserTier): UserTier | null {
  switch (currentTier) {
    case 'free':
      return 'start';
    case 'start':
      return 'pro';
    case 'pro':
      return 'premium';
    case 'premium':
      return null; // Already at highest tier
  }
}

/**
 * Check if tier is valid
 */
export function isValidTier(tier: string): tier is UserTier {
  return ['free', 'start', 'pro', 'premium'].includes(tier);
}

/**
 * Get tier by name (with fallback to free)
 */
export function getTierByName(tierName: string): UserTier {
  if (isValidTier(tierName)) {
    return tierName;
  }
  console.warn(`Invalid tier name: ${tierName}, defaulting to 'free'`);
  return 'free';
}

/**
 * Compare two tiers
 * Returns: -1 if tier1 < tier2, 0 if equal, 1 if tier1 > tier2
 */
export function compareTiers(tier1: UserTier, tier2: UserTier): number {
  const hierarchy1 = TIER_HIERARCHY[tier1];
  const hierarchy2 = TIER_HIERARCHY[tier2];

  if (hierarchy1 < hierarchy2) return -1;
  if (hierarchy1 > hierarchy2) return 1;
  return 0;
}

/**
 * Get all available tiers in order
 */
export function getAllTiers(): UserTier[] {
  return ['free', 'start', 'pro', 'premium'];
}

/**
 * Get tier benefits comparison
 */
export function getTierBenefits(tier: UserTier): string[] {
  const limits = getTierLimits(tier);
  const benefits: string[] = [];

  benefits.push(`Up to ${limits.maxChannels === 9999 ? 'unlimited' : limits.maxChannels} channel${limits.maxChannels !== 1 ? 's' : ''}`);
  benefits.push(`${limits.maxPostsPerMonth === 9999 ? 'Unlimited' : limits.maxPostsPerMonth} posts per month`);
  benefits.push(`${limits.maxFileSize}MB file size limit`);

  if (limits.watermarksEnabled) benefits.push('Watermark protection');
  if (limits.theftDetectionEnabled) benefits.push('Theft detection');
  if (limits.customEmojisEnabled) benefits.push('Custom emojis');
  if (limits.advancedAnalytics) benefits.push('Advanced analytics');
  if (limits.apiAccess) benefits.push('API access');
  if (limits.prioritySupport) benefits.push('Priority support');

  return benefits;
}

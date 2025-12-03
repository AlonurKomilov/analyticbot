/**
 * Tier Comparison and Feature Access Utilities
 *
 * Helper functions for checking tier access and feature availability
 * Created: October 25, 2025
 */

import { UserTier, getTierLimits, hasFeatureAccess as baseHasFeatureAccess } from '@/types';

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
 *
 * @param userTier - The user's current tier
 * @param requiredTier - The minimum tier required
 * @returns true if user tier >= required tier
 *
 * @example
 * hasTierAccess('pro', 'start') // true
 * hasTierAccess('start', 'pro') // false
 */
export function hasTierAccess(userTier: UserTier, requiredTier: UserTier): boolean {
  return TIER_HIERARCHY[userTier] >= TIER_HIERARCHY[requiredTier];
}

/**
 * Check if feature is available for user's tier
 *
 * @param userTier - The user's current tier
 * @param feature - Feature name to check
 * @returns true if feature is available
 */
export function hasFeatureAccess(userTier: UserTier, feature: string): boolean {
  return baseHasFeatureAccess(userTier, feature);
}

/**
 * Check if user can create more channels
 *
 * @param userTier - The user's current tier
 * @param currentChannelCount - Number of channels user currently has
 * @returns true if user can create more channels
 */
export function canCreateMoreChannels(userTier: UserTier, currentChannelCount: number): boolean {
  const limits = getTierLimits(userTier);
  return currentChannelCount < limits.maxChannels;
}

/**
 * Check if user can upload file of given size
 *
 * @param userTier - The user's current tier
 * @param fileSizeMB - File size in megabytes
 * @returns true if file size is within tier limit
 */
export function canUploadFile(userTier: UserTier, fileSizeMB: number): boolean {
  const limits = getTierLimits(userTier);
  return fileSizeMB <= limits.maxFileSize;
}

/**
 * Check if user can post more this month
 *
 * @param userTier - The user's current tier
 * @param currentMonthPosts - Number of posts this month
 * @returns true if user can post more
 */
export function canPostMore(userTier: UserTier, currentMonthPosts: number): boolean {
  const limits = getTierLimits(userTier);
  return currentMonthPosts < limits.maxPostsPerMonth;
}

/**
 * Get tier restriction message
 *
 * @param userTier - The user's current tier
 * @param feature - Feature being restricted
 * @returns User-friendly message about the restriction
 */
export function getTierRestrictionMessage(userTier: UserTier, feature: string): string {
  const limits = getTierLimits(userTier);

  switch (feature) {
    case 'channels':
      return `Your ${userTier} plan allows up to ${limits.maxChannels} channel${limits.maxChannels !== 1 ? 's' : ''}. Upgrade to create more.`;
    case 'posts':
      return `Your ${userTier} plan allows ${limits.maxPostsPerMonth} posts per month. Upgrade for more.`;
    case 'file_size':
      return `Your ${userTier} plan allows files up to ${limits.maxFileSize}MB. Upgrade for larger files.`;
    case 'watermarks':
      return `Watermark protection is available on Start plan and above.`;
    case 'theft_detection':
      return `Theft detection is available on Pro plan and above.`;
    case 'custom_emojis':
      return `Custom emojis are available on Pro plan and above.`;
    case 'api':
      return `API access is available on Pro plan and above.`;
    case 'priority_support':
      return `Priority support is available on Premium plan only.`;
    case 'advanced_analytics':
      return `Advanced analytics are available on Pro plan and above.`;
    default:
      return `This feature is not available on your ${userTier} plan. Please upgrade.`;
  }
}

/**
 * Get channels remaining for user
 *
 * @param userTier - The user's current tier
 * @param currentChannelCount - Number of channels user currently has
 * @returns Number of channels remaining, or Infinity for unlimited
 */
export function getChannelsRemaining(userTier: UserTier, currentChannelCount: number): number {
  const limits = getTierLimits(userTier);

  if (limits.maxChannels === 9999) {
    return Infinity; // Unlimited
  }

  return Math.max(0, limits.maxChannels - currentChannelCount);
}

/**
 * Get posts remaining for current month
 *
 * @param userTier - The user's current tier
 * @param currentMonthPosts - Number of posts this month
 * @returns Number of posts remaining, or Infinity for unlimited
 */
export function getPostsRemaining(userTier: UserTier, currentMonthPosts: number): number {
  const limits = getTierLimits(userTier);

  if (limits.maxPostsPerMonth === 9999) {
    return Infinity; // Unlimited
  }

  return Math.max(0, limits.maxPostsPerMonth - currentMonthPosts);
}

/**
 * Suggest upgrade tier based on user needs
 *
 * @param userTier - The user's current tier
 * @param reason - Reason for upgrade suggestion
 * @returns Suggested tier and upgrade message
 */
export function suggestTierUpgrade(
  userTier: UserTier,
  reason: 'channels' | 'posts' | 'file_size' | 'features'
): { suggestedTier: UserTier; message: string } | null {

  switch (userTier) {
    case 'free':
      return {
        suggestedTier: 'start',
        message: reason === 'features'
          ? 'Upgrade to Start plan for watermark protection and more channels'
          : 'Upgrade to Start plan for more capacity'
      };

    case 'start':
      return {
        suggestedTier: 'pro',
        message: reason === 'features'
          ? 'Upgrade to Pro plan for theft detection, custom emojis, and API access'
          : 'Upgrade to Pro plan for 10 channels and 500 posts/month'
      };

    case 'pro':
      return {
        suggestedTier: 'premium',
        message: 'Upgrade to Premium plan for unlimited capacity and priority support'
      };

    case 'premium':
      return null; // Already at highest tier
  }
}

/**
 * Check if user is on a paid tier
 *
 * @param userTier - The user's current tier
 * @returns true if tier is paid (not free)
 */
export function isPaidTier(userTier: UserTier): boolean {
  return userTier !== 'free';
}

/**
 * Get tier monthly cost (for display purposes)
 *
 * @param tier - The tier to get cost for
 * @returns Monthly cost in dollars
 */
export function getTierMonthlyCost(tier: UserTier): number {
  switch (tier) {
    case 'free':
      return 0;
    case 'start':
      return 9;
    case 'pro':
      return 29;
    case 'premium':
      return 99;
  }
}

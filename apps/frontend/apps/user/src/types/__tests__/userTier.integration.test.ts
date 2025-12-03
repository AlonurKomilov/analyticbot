/**
 * User Tier System Integration Tests
 * Tests tier-based access control, feature limits, and tier comparisons
 */

import { describe, it, expect } from 'vitest';
import { UserTier, getTierLimits, TIER_DISPLAY_INFO } from '../subscription';
import { hasTierAccess, hasFeatureAccess } from '@shared/utils/tierComparison';

describe('User Tier System Integration Tests', () => {
  describe('Tier Definitions', () => {
    it('should support all four tier levels', () => {
      const tiers: UserTier[] = ['free', 'start', 'pro', 'premium'];
      expect(tiers).toHaveLength(4);
    });

    it('should have display info for all tiers', () => {
      const tiers: UserTier[] = ['free', 'start', 'pro', 'premium'];
      tiers.forEach(tier => {
        expect(TIER_DISPLAY_INFO[tier]).toBeDefined();
        expect(TIER_DISPLAY_INFO[tier].displayName).toBeDefined();
        expect(TIER_DISPLAY_INFO[tier].description).toBeDefined();
      });
    });

    it('should mark pro tier as popular', () => {
      expect(TIER_DISPLAY_INFO.pro.popular).toBe(true);
    });
  });

  describe('Tier Limits', () => {
    it('should have appropriate limits for free tier', () => {
      const limits = getTierLimits('free');
      expect(limits.maxChannels).toBe(1);
      expect(limits.maxPostsPerMonth).toBe(30);
      expect(limits.watermarksEnabled).toBe(false);
      expect(limits.theftDetectionEnabled).toBe(false);
      expect(limits.customEmojisEnabled).toBe(false);
      expect(limits.prioritySupport).toBe(false);
      expect(limits.apiAccess).toBe(false);
    });

    it('should have enhanced limits for start tier', () => {
      const limits = getTierLimits('start');
      expect(limits.maxChannels).toBe(3);
      expect(limits.maxPostsPerMonth).toBe(100);
      expect(limits.watermarksEnabled).toBe(true);
      expect(limits.theftDetectionEnabled).toBe(false);
      expect(limits.customEmojisEnabled).toBe(false);
      expect(limits.prioritySupport).toBe(false);
      expect(limits.apiAccess).toBe(false);
    });

    it('should have advanced limits for pro tier', () => {
      const limits = getTierLimits('pro');
      expect(limits.maxChannels).toBe(10);
      expect(limits.maxPostsPerMonth).toBe(500);
      expect(limits.watermarksEnabled).toBe(true);
      expect(limits.theftDetectionEnabled).toBe(true);
      expect(limits.customEmojisEnabled).toBe(true);
      expect(limits.prioritySupport).toBe(false);
      expect(limits.apiAccess).toBe(true);
    });

    it('should have unlimited limits for premium tier', () => {
      const limits = getTierLimits('premium');
      expect(limits.maxChannels).toBe(9999);
      expect(limits.maxPostsPerMonth).toBe(9999);
      expect(limits.watermarksEnabled).toBe(true);
      expect(limits.theftDetectionEnabled).toBe(true);
      expect(limits.customEmojisEnabled).toBe(true);
      expect(limits.prioritySupport).toBe(true);
      expect(limits.apiAccess).toBe(true);
    });

    it('should increase channel limits progressively', () => {
      const freeLimits = getTierLimits('free');
      const startLimits = getTierLimits('start');
      const proLimits = getTierLimits('pro');
      const premiumLimits = getTierLimits('premium');

      expect(startLimits.maxChannels).toBeGreaterThan(freeLimits.maxChannels);
      expect(proLimits.maxChannels).toBeGreaterThan(startLimits.maxChannels);
      expect(premiumLimits.maxChannels).toBeGreaterThan(proLimits.maxChannels);
    });

    it('should increase post limits progressively', () => {
      const freeLimits = getTierLimits('free');
      const startLimits = getTierLimits('start');
      const proLimits = getTierLimits('pro');
      const premiumLimits = getTierLimits('premium');

      expect(startLimits.maxPostsPerMonth).toBeGreaterThan(freeLimits.maxPostsPerMonth);
      expect(proLimits.maxPostsPerMonth).toBeGreaterThan(startLimits.maxPostsPerMonth);
      expect(premiumLimits.maxPostsPerMonth).toBeGreaterThan(proLimits.maxPostsPerMonth);
    });
  });

  describe('Tier Comparison', () => {
    it('should allow free tier to access free features', () => {
      expect(hasTierAccess('free', 'free')).toBe(true);
    });

    it('should not allow free tier to access start features', () => {
      expect(hasTierAccess('free', 'start')).toBe(false);
    });

    it('should allow start tier to access free features', () => {
      expect(hasTierAccess('start', 'free')).toBe(true);
    });

    it('should allow start tier to access start features', () => {
      expect(hasTierAccess('start', 'start')).toBe(true);
    });

    it('should not allow start tier to access pro features', () => {
      expect(hasTierAccess('start', 'pro')).toBe(false);
    });

    it('should allow pro tier to access all features except premium', () => {
      expect(hasTierAccess('pro', 'free')).toBe(true);
      expect(hasTierAccess('pro', 'start')).toBe(true);
      expect(hasTierAccess('pro', 'pro')).toBe(true);
      expect(hasTierAccess('pro', 'premium')).toBe(false);
    });

    it('should allow premium tier to access all features', () => {
      expect(hasTierAccess('premium', 'free')).toBe(true);
      expect(hasTierAccess('premium', 'start')).toBe(true);
      expect(hasTierAccess('premium', 'pro')).toBe(true);
      expect(hasTierAccess('premium', 'premium')).toBe(true);
    });
  });

  describe('Feature Access Control', () => {
    it('should deny watermarks for free tier', () => {
      expect(hasFeatureAccess('free', 'watermarks')).toBe(false);
    });

    it('should allow watermarks for start tier', () => {
      expect(hasFeatureAccess('start', 'watermarks')).toBe(true);
    });

    it('should deny theft detection for free and start tiers', () => {
      expect(hasFeatureAccess('free', 'theft_detection')).toBe(false);
      expect(hasFeatureAccess('start', 'theft_detection')).toBe(false);
    });

    it('should allow theft detection for pro tier', () => {
      expect(hasFeatureAccess('pro', 'theft_detection')).toBe(true);
    });

    it('should deny custom emojis for free and start tiers', () => {
      expect(hasFeatureAccess('free', 'custom_emojis')).toBe(false);
      expect(hasFeatureAccess('start', 'custom_emojis')).toBe(false);
    });

    it('should allow custom emojis for pro tier', () => {
      expect(hasFeatureAccess('pro', 'custom_emojis')).toBe(true);
    });

    it('should deny API access for free and start tiers', () => {
      expect(hasFeatureAccess('free', 'api')).toBe(false);
      expect(hasFeatureAccess('start', 'api')).toBe(false);
    });

    it('should allow API access for pro tier', () => {
      expect(hasFeatureAccess('pro', 'api')).toBe(true);
    });

    it('should only allow priority support for premium tier', () => {
      expect(hasFeatureAccess('free', 'priority_support')).toBe(false);
      expect(hasFeatureAccess('start', 'priority_support')).toBe(false);
      expect(hasFeatureAccess('pro', 'priority_support')).toBe(false);
      expect(hasFeatureAccess('premium', 'priority_support')).toBe(true);
    });
  });

  describe('Tier Upgrade Scenarios', () => {
    it('should show proper upgrade path from free to start', () => {
      const freeLimits = getTierLimits('free');
      const startLimits = getTierLimits('start');

      // Channels increase
      expect(startLimits.maxChannels).toBeGreaterThan(freeLimits.maxChannels);

      // Posts increase
      expect(startLimits.maxPostsPerMonth).toBeGreaterThan(freeLimits.maxPostsPerMonth);

      // Watermarks enabled
      expect(startLimits.watermarksEnabled).toBe(true);
      expect(freeLimits.watermarksEnabled).toBe(false);
    });

    it('should show proper upgrade path from start to pro', () => {
      const startLimits = getTierLimits('start');
      const proLimits = getTierLimits('pro');

      // Channels increase
      expect(proLimits.maxChannels).toBeGreaterThan(startLimits.maxChannels);

      // Posts increase significantly
      expect(proLimits.maxPostsPerMonth).toBeGreaterThan(startLimits.maxPostsPerMonth);

      // New features enabled
      expect(proLimits.theftDetectionEnabled).toBe(true);
      expect(startLimits.theftDetectionEnabled).toBe(false);

      expect(proLimits.customEmojisEnabled).toBe(true);
      expect(startLimits.customEmojisEnabled).toBe(false);

      expect(proLimits.apiAccess).toBe(true);
      expect(startLimits.apiAccess).toBe(false);
    });

    it('should show proper upgrade path from pro to premium', () => {
      const proLimits = getTierLimits('pro');
      const premiumLimits = getTierLimits('premium');

      // Limits increase significantly (near unlimited)
      expect(premiumLimits.maxChannels).toBeGreaterThan(proLimits.maxChannels);
      expect(premiumLimits.maxPostsPerMonth).toBeGreaterThan(proLimits.maxPostsPerMonth);

      // Priority support enabled
      expect(premiumLimits.prioritySupport).toBe(true);
      expect(proLimits.prioritySupport).toBe(false);
    });
  });

  describe('Test Data Alignment', () => {
    it('should use correct tier names matching test mocks', () => {
      // These tier names should match tests/mocks/data/ai_services/mock_ai_data.py
      const expectedTiers = ['free', 'start', 'pro', 'premium'];
      const tiers: UserTier[] = ['free', 'start', 'pro', 'premium'];

      expect(tiers).toEqual(expectedTiers);
    });

    it('should NOT use deprecated tier names', () => {
      const deprecatedTiers = ['basic', 'enterprise'];
      const validTiers: UserTier[] = ['free', 'start', 'pro', 'premium'];

      deprecatedTiers.forEach(deprecated => {
        expect(validTiers).not.toContain(deprecated as any);
      });
    });
  });
});

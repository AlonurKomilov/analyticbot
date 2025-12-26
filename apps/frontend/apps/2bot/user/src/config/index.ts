/**
 * Configuration Module
 * Centralized exports for all configuration
 */

export * from './env';
export { FEATURES, getFeatureConfig, hasFeatureAccess, getEnabledFeatures } from './features';
export type { FeatureConfig, FeatureName } from './features';
export * from './routes';

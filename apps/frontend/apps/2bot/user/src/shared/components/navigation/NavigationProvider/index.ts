/**
 * Navigation Provider
 *
 * Refactored from 508 lines to 8 files:
 * - types.ts: Type definitions
 * - useNavigationAnalytics.ts: Page view tracking
 * - useUserPreferences.ts: Preferences with localStorage
 * - useNavigationHistory.ts: Bookmarks and recent pages
 * - useNavigationSearch.ts: Search history
 * - useNotifications.ts: Notification management
 * - NavigationProvider.tsx: Main provider component
 * - index.ts: Barrel exports
 */

// Main exports
export {
  NavigationProvider,
  useNavigation,
  useNavigationPreferences,
  useNavigationHistory,
  useNavigationSearch,
  useNotifications,
  default,
} from './NavigationProvider';

// Types
export * from './types';

// Internal hooks (for advanced usage)
export { useNavigationAnalytics } from './useNavigationAnalytics';
export { useUserPreferences } from './useUserPreferences';
export { useNavigationHistoryInternal } from './useNavigationHistory';
export { useNavigationSearchInternal } from './useNavigationSearch';
export { useNotificationsInternal } from './useNotifications';

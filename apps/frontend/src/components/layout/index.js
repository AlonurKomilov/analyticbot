/**
 * Layout Components Index
 *
 * Enhanced layout system for improved visual hierarchy and mobile responsiveness
 */

export { default as EnhancedDashboardLayout } from './EnhancedDashboardLayout.jsx';
export { default as EnhancedSection } from './EnhancedSection.tsx';
export { default as EnhancedCard } from './EnhancedCard.jsx';
export {
  default as LayoutUtils,
  HierarchyContainer,
  ResponsiveWrapper,
  HierarchyDivider,
  FocusRing
} from './LayoutUtils.jsx';

// Mobile Responsive Components
export {
  MobileNavigationDrawer,
  SwipeableTabNavigation,
  MobileCardStack,
  ResponsiveGrid
} from './MobileResponsiveEnhancements.jsx';

// Tablet Optimizations
export {
  TabletDashboardLayout,
  TabletCollapsibleCard,
  TabletAnalyticsGrid,
  TabletButtonGroup,
  TabletSplitView,
  TabletStatusBar
} from './TabletOptimizations.jsx';

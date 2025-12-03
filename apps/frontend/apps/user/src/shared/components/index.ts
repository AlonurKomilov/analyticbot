/**
 * Shared Components
 * Barrel export for all shared UI components
 */

// Base components
export * from './base';

// Forms
export * from './forms';

// Tables
export * from './tables';

// Feedback (errors, loading, notifications)
export * from './feedback';

// UI (buttons, cards, badges)
export * from './ui';

// Navigation
export * from './navigation';

// ========================================
// Convenient Aliases (matching legacy common/index.ts)
// ========================================

import {
  StandardCard,
  StandardStatusChip,
  SectionHeader,
  GridContainer
} from './ui';

import UnifiedButton, {
  PrimaryButton,
  SecondaryButton,
  TertiaryButton,
  DangerButton,
  SuccessButton,
  SmallButton,
  LargeButton,
  LoadingButton
} from './ui/UnifiedButton';

// Standard UI Components - Aliased for convenience
export {
  StandardCard as Card,
  StandardStatusChip as StatusChip,
  SectionHeader,
  GridContainer
};

// Unified Button - Main export as "Button"
export {
  UnifiedButton as Button,
  PrimaryButton,
  SecondaryButton,
  TertiaryButton,
  DangerButton,
  SuccessButton,
  SmallButton,
  LargeButton,
  LoadingButton
};

// Backward compatibility
export { UnifiedButton as AccessibleButton };

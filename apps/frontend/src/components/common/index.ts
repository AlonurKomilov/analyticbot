/**
 * Enhanced Component Index
 *
 * Centralized exports for all standardized UI components.
 * Import from this file to ensure consistent component usage.
 */

// Standard UI Components - NEW (Updated with Unified Button)
export {
  StandardCard as Card,
  StandardInput as Input,
  StandardTypography as Typography,
  StandardStatusChip as StatusChip,
  SectionHeader,
  PageContainer,
  GridContainer
} from './StandardComponents';

// Unified Button Component (Replaces AccessibleButton, LoadingButton, StandardButton)
export {
  default as Button,
  PrimaryButton,
  SecondaryButton,
  TertiaryButton,
  DangerButton,
  SuccessButton,
  SmallButton,
  LargeButton,
  LoadingButton
} from './UnifiedButton';

// Design tokens and utilities - NEW
export {
  DESIGN_TOKENS,
  getButtonProps,
  getCardProps,
  getStatusColor,
  getChartColors,
  createTransition,
  createElevation
} from '../../theme/designTokens';

// Existing specialized components
export { default as ModernCard } from './ModernCard';
export { default as GlobalDataSourceSwitch } from './GlobalDataSourceSwitch';
export { TouchTargetProvider } from './TouchTargetCompliance';
export { Icon, StatusChip as LegacyStatusChip } from './IconSystem';
export { default as AccessibleFormField } from './AccessibleFormField';
export { default as EnhancedDataTable } from './EnhancedDataTable';
export { default as ErrorBoundary } from './ErrorBoundary';
export { default as ExportButton } from './ExportButton';
// Backwards-compatible ShareButton wrapper (keeps legacy imports working)
export { default as ShareButton } from './ShareButton';
export { default as ToastNotification } from './ToastNotification';

// Legacy aliases for backward compatibility (DEPRECATED)
// These will be removed in future versions
export { default as AccessibleButton } from './UnifiedButton';

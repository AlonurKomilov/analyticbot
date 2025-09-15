/**
 * Enhanced Component Index
 * 
 * Centralized exports for all standardized UI components.
 * Import from this file to ensure consistent component usage.
 */

// Standard UI Components - NEW
export {
  StandardButton as Button,
  StandardCard as Card,
  StandardInput as Input,
  StandardTypography as Typography,
  StandardStatusChip as StatusChip,
  SectionHeader,
  PageContainer,
  GridContainer
} from './StandardComponents.jsx';

// Design tokens and utilities - NEW
export {
  DESIGN_TOKENS,
  getButtonProps,
  getCardProps,
  getStatusColor,
  getChartColors,
  createTransition,
  createElevation
} from '../../theme/designTokens.js';

// Existing specialized components
export { default as ModernCard } from './ModernCard.jsx';
export { default as GlobalDataSourceSwitch } from './GlobalDataSourceSwitch.jsx';
export { TouchTargetProvider } from './TouchTargetCompliance.jsx';
export { Icon, StatusChip as LegacyStatusChip } from './IconSystem.jsx';
export { default as AccessibleButton } from './AccessibleButton';
export { default as AccessibleFormField } from './AccessibleFormField';
export { default as EnhancedDataTable } from './EnhancedDataTable';
export { default as ErrorBoundary } from './ErrorBoundary';
export { default as ExportButton } from './ExportButton';
export { default as LoadingButton } from './LoadingButton';
export { default as ShareButton } from './ShareButton';
export { default as ToastNotification } from './ToastNotification';

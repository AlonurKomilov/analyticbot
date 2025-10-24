/**
 * BaseAlert Component
 * 
 * Reusable alert/notification component with severity variants and consistent styling.
 * Consolidates 12+ alert patterns across the application.
 * 
 * Features:
 * - Severity variants (info, success, warning, error)
 * - Dismissible option
 * - Custom icon support
 * - Title and description
 * - Action buttons
 * - Auto-dismiss timer
 * - Accessibility (ARIA live regions, proper roles)
 * - Uses design tokens
 * 
 * Usage:
 * ```tsx
 * <BaseAlert
 *   severity="success"
 *   title="Success"
 *   message="Your changes have been saved"
 *   dismissible
 *   onDismiss={handleDismiss}
 * />
 * ```
 */

import React, { useState, useEffect } from 'react';
import { Alert, AlertTitle, IconButton, Box, Button } from '@mui/material';
import {
  Close as CloseIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { spacing, colors, radius, sizing, typography, animation } from '@/theme/tokens';

// =============================================================================
// Types
// =============================================================================

export type AlertSeverity = 'info' | 'success' | 'warning' | 'error';

export interface AlertAction {
  label: string;
  onClick: () => void;
  variant?: 'text' | 'outlined' | 'contained';
}

export interface BaseAlertProps {
  // Required
  severity: AlertSeverity;
  message: string | React.ReactNode;
  
  // Optional - Content
  title?: string;
  icon?: React.ReactNode;
  hideIcon?: boolean;
  
  // Optional - Actions
  action?: AlertAction;
  dismissible?: boolean;
  onDismiss?: () => void;
  
  // Optional - Auto-dismiss
  autoDismiss?: boolean;
  autoDismissDuration?: number; // in milliseconds
  
  // Optional - Styling
  variant?: 'standard' | 'filled' | 'outlined';
  fullWidth?: boolean;
  
  // Optional - Accessibility
  role?: 'alert' | 'status';
  ariaLive?: 'polite' | 'assertive' | 'off';
}

// =============================================================================
// Helper Functions
// =============================================================================

const getAlertColors = (severity: AlertSeverity) => {
  const colorMap = {
    info: {
      bg: colors.info.bg,
      main: colors.info.main,
      dark: colors.info.dark,
    },
    success: {
      bg: colors.success.bg,
      main: colors.success.main,
      dark: colors.success.dark,
    },
    warning: {
      bg: colors.warning.bg,
      main: colors.warning.main,
      dark: colors.warning.dark,
    },
    error: {
      bg: colors.error.bg,
      main: colors.error.main,
      dark: colors.error.dark,
    },
  };
  return colorMap[severity];
};

const getDefaultIcon = (severity: AlertSeverity) => {
  const iconMap = {
    info: <InfoIcon sx={{ fontSize: sizing.icon.md }} />,
    success: <SuccessIcon sx={{ fontSize: sizing.icon.md }} />,
    warning: <WarningIcon sx={{ fontSize: sizing.icon.md }} />,
    error: <ErrorIcon sx={{ fontSize: sizing.icon.md }} />,
  };
  return iconMap[severity];
};

// =============================================================================
// Component
// =============================================================================

const BaseAlert: React.FC<BaseAlertProps> = ({
  // Required
  severity,
  message,
  
  // Optional - Content
  title,
  icon,
  hideIcon = false,
  
  // Optional - Actions
  action,
  dismissible = false,
  onDismiss,
  
  // Optional - Auto-dismiss
  autoDismiss = false,
  autoDismissDuration = 5000,
  
  // Optional - Styling
  variant = 'standard',
  fullWidth = true,
  
  // Optional - Accessibility
  role = severity === 'error' ? 'alert' : 'status',
  ariaLive = severity === 'error' ? 'assertive' : 'polite',
}) => {
  const [visible, setVisible] = useState(true);
  const alertColors = getAlertColors(severity);

  // Auto-dismiss timer
  useEffect(() => {
    if (autoDismiss && visible) {
      const timer = setTimeout(() => {
        handleDismiss();
      }, autoDismissDuration);

      return () => clearTimeout(timer);
    }
    return undefined;
  }, [autoDismiss, autoDismissDuration, visible]);

  const handleDismiss = () => {
    setVisible(false);
    setTimeout(() => {
      onDismiss?.();
    }, 200); // Wait for fade-out animation
  };

  if (!visible) {
    return null;
  }

  return (
    <Alert
      severity={severity}
      variant={variant}
      icon={hideIcon ? false : (icon || getDefaultIcon(severity))}
      role={role}
      aria-live={ariaLive}
      action={
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: spacing.xs,
          }}
        >
          {/* Custom action button */}
          {action && (
            <Button
              size="small"
              variant={action.variant || 'text'}
              onClick={action.onClick}
              sx={{
                minHeight: sizing.button.small,
                padding: `${spacing.xs} ${spacing.sm}`,
                borderRadius: radius.button,
                fontSize: typography.fontSize.sm,
                fontWeight: typography.fontWeight.medium,
                color: alertColors.main,
                '&:hover': {
                  backgroundColor: alertColors.bg,
                },
              }}
            >
              {action.label}
            </Button>
          )}

          {/* Dismiss button */}
          {dismissible && (
            <IconButton
              size="small"
              onClick={handleDismiss}
              aria-label="Dismiss alert"
              sx={{
                minWidth: sizing.touchTarget.min,
                minHeight: sizing.touchTarget.min,
                color: alertColors.main,
                padding: spacing.xs,
                '&:hover': {
                  backgroundColor: alertColors.bg,
                },
              }}
            >
              <CloseIcon sx={{ fontSize: sizing.icon.sm }} />
            </IconButton>
          )}
        </Box>
      }
      sx={{
        width: fullWidth ? '100%' : 'auto',
        borderRadius: radius.md,
        transition: animation.transition.normal,
        opacity: visible ? 1 : 0,
        
        // Standard variant styling
        ...(variant === 'standard' && {
          backgroundColor: alertColors.bg,
          color: alertColors.main,
          border: `1px solid ${alertColors.main}`,
          '& .MuiAlert-icon': {
            color: alertColors.main,
          },
        }),
        
        // Filled variant styling
        ...(variant === 'filled' && {
          backgroundColor: alertColors.main,
          color: colors.primary.contrast,
          '& .MuiAlert-icon': {
            color: colors.primary.contrast,
          },
        }),
        
        // Outlined variant styling
        ...(variant === 'outlined' && {
          backgroundColor: 'transparent',
          color: alertColors.main,
          border: `1px solid ${alertColors.main}`,
          '& .MuiAlert-icon': {
            color: alertColors.main,
          },
        }),
      }}
    >
      {/* Title */}
      {title && (
        <AlertTitle
          sx={{
            fontSize: typography.fontSize.md,
            fontWeight: typography.fontWeight.semibold,
            marginBottom: spacing.xs,
            lineHeight: typography.lineHeight.tight,
          }}
        >
          {title}
        </AlertTitle>
      )}

      {/* Message */}
      {typeof message === 'string' ? (
        <Box
          sx={{
            fontSize: typography.fontSize.sm,
            lineHeight: typography.lineHeight.relaxed,
          }}
        >
          {message}
        </Box>
      ) : (
        message
      )}
    </Alert>
  );
};

export default BaseAlert;

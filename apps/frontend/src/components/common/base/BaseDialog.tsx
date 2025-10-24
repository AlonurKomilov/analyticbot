/**
 * BaseDialog Component
 * 
 * Reusable dialog component with consistent layout, styling, and behavior.
 * Consolidates 20+ dialog patterns across the application.
 * 
 * Features:
 * - Title with optional close button
 * - Scrollable content area
 * - Action buttons (cancel/confirm)
 * - Size variants (xs, sm, md, lg, xl, full)
 * - Loading state
 * - Backdrop click handling
 * - Keyboard shortcuts (ESC to close)
 * - Accessibility (focus trap, ARIA labels)
 * - Uses design tokens
 * 
 * Usage:
 * ```tsx
 * <BaseDialog
 *   open={open}
 *   onClose={handleClose}
 *   title="Confirm Action"
 *   content="Are you sure you want to proceed?"
 *   actions={{
 *     cancel: { label: 'Cancel', onClick: handleClose },
 *     confirm: { label: 'Confirm', onClick: handleConfirm, loading: isSubmitting }
 *   }}
 * />
 * ```
 */

import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Button,
  Typography,
  Box,
  CircularProgress,
} from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';
import { spacing, colors, radius, shadows, sizing, typography } from '@/theme/tokens';

// =============================================================================
// Types
// =============================================================================

export type DialogSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'full';

export interface DialogAction {
  label: string;
  onClick: () => void;
  variant?: 'text' | 'outlined' | 'contained';
  color?: 'primary' | 'secondary' | 'error' | 'warning' | 'success';
  loading?: boolean;
  disabled?: boolean;
  startIcon?: React.ReactNode;
  endIcon?: React.ReactNode;
}

export interface BaseDialogProps {
  // Required
  open: boolean;
  onClose: () => void;
  
  // Optional - Content
  title?: string | React.ReactNode;
  subtitle?: string;
  content?: React.ReactNode;
  children?: React.ReactNode; // Alternative to content
  
  // Optional - Actions
  actions?: {
    cancel?: DialogAction;
    confirm?: DialogAction;
    additional?: DialogAction[];
  };
  
  // Optional - Configuration
  size?: DialogSize;
  showCloseButton?: boolean;
  closeOnBackdropClick?: boolean;
  closeOnEscape?: boolean;
  dividers?: boolean; // Show dividers between sections
  
  // Optional - Loading state
  loading?: boolean;
  loadingMessage?: string;
  
  // Optional - Styling
  maxWidth?: string | number;
  fullScreen?: boolean;
  
  // Optional - Accessibility
  ariaLabelledBy?: string;
  ariaDescribedBy?: string;
}

// =============================================================================
// Helper Functions
// =============================================================================

const getSizeWidth = (size: DialogSize): string => {
  const sizeMap: Record<DialogSize, string> = {
    xs: sizing.dialog.xs,
    sm: sizing.dialog.sm,
    md: sizing.dialog.md,
    lg: sizing.dialog.lg,
    xl: sizing.dialog.xl,
    full: '100vw',
  };
  return sizeMap[size];
};

// =============================================================================
// Component
// =============================================================================

const BaseDialog: React.FC<BaseDialogProps> = ({
  // Required
  open,
  onClose,
  
  // Optional - Content
  title,
  subtitle,
  content,
  children,
  
  // Optional - Actions
  actions,
  
  // Optional - Configuration
  size = 'md',
  showCloseButton = true,
  closeOnBackdropClick = true,
  closeOnEscape = true,
  dividers = false,
  
  // Optional - Loading state
  loading = false,
  loadingMessage = 'Loading...',
  
  // Optional - Styling
  maxWidth,
  fullScreen = false,
  
  // Optional - Accessibility
  ariaLabelledBy = 'dialog-title',
  ariaDescribedBy = 'dialog-content',
}) => {
  // Handle close
  const handleClose = (_: any, reason: 'backdropClick' | 'escapeKeyDown') => {
    if (reason === 'backdropClick' && !closeOnBackdropClick) return;
    if (reason === 'escapeKeyDown' && !closeOnEscape) return;
    onClose();
  };

  // Render action buttons
  const renderActions = () => {
    if (!actions) return null;

    const { cancel, confirm, additional = [] } = actions;
    const allActions = [
      ...(cancel ? [{ ...cancel, key: 'cancel' }] : []),
      ...additional.map((action, index) => ({ ...action, key: `additional-${index}` })),
      ...(confirm ? [{ ...confirm, key: 'confirm' }] : []),
    ];

    return (
      <DialogActions
        sx={{
          padding: spacing.lg,
          gap: spacing.sm,
          ...(dividers && {
            borderTop: `1px solid ${colors.border.default}`,
          }),
        }}
      >
        {allActions.map((action) => (
          <Button
            key={action.key}
            variant={action.variant || (action.key === 'confirm' ? 'contained' : 'text')}
            color={action.color || (action.key === 'confirm' ? 'primary' : undefined)}
            onClick={action.onClick}
            disabled={action.disabled || loading}
            startIcon={action.loading ? <CircularProgress size={16} /> : action.startIcon}
            endIcon={action.endIcon}
            sx={{
              minHeight: sizing.button.medium,
              padding: `${spacing.sm} ${spacing.md}`,
              borderRadius: radius.button,
            }}
          >
            {action.label}
          </Button>
        ))}
      </DialogActions>
    );
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      fullScreen={fullScreen}
      maxWidth={false}
      aria-labelledby={ariaLabelledBy}
      aria-describedby={ariaDescribedBy}
      sx={{
        '& .MuiDialog-paper': {
          width: fullScreen ? '100vw' : (maxWidth || getSizeWidth(size)),
          maxWidth: fullScreen ? '100vw' : '90vw',
          borderRadius: fullScreen ? 0 : radius.dialog,
          boxShadow: shadows.dialog,
          backgroundColor: colors.background.paper,
        },
      }}
    >
      {/* Title */}
      {title && (
        <DialogTitle
          id={ariaLabelledBy}
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            padding: spacing.lg,
            ...(dividers && {
              borderBottom: `1px solid ${colors.border.default}`,
            }),
          }}
        >
          <Box sx={{ flex: 1, paddingRight: showCloseButton ? spacing.md : 0 }}>
            {typeof title === 'string' ? (
              <Typography
                sx={{
                  fontSize: typography.fontSize.xl,
                  fontWeight: typography.fontWeight.semibold,
                  color: colors.text.primary,
                  lineHeight: typography.lineHeight.tight,
                }}
              >
                {title}
              </Typography>
            ) : (
              title
            )}
            
            {subtitle && (
              <Typography
                sx={{
                  fontSize: typography.fontSize.sm,
                  color: colors.text.secondary,
                  marginTop: spacing.xs,
                  lineHeight: typography.lineHeight.normal,
                }}
              >
                {subtitle}
              </Typography>
            )}
          </Box>

          {/* Close button */}
          {showCloseButton && (
            <IconButton
              onClick={onClose}
              disabled={loading}
              aria-label="Close dialog"
              sx={{
                minWidth: sizing.touchTarget.min,
                minHeight: sizing.touchTarget.min,
                color: colors.text.secondary,
                marginTop: '-8px',
                marginRight: '-8px',
                '&:hover': {
                  backgroundColor: colors.state.hover,
                },
              }}
            >
              <CloseIcon sx={{ fontSize: sizing.icon.md }} />
            </IconButton>
          )}
        </DialogTitle>
      )}

      {/* Content */}
      <DialogContent
        id={ariaDescribedBy}
        sx={{
          padding: spacing.lg,
          ...(dividers && title && {
            paddingTop: spacing.lg,
          }),
        }}
      >
        {loading ? (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              padding: spacing.xxl,
              minHeight: '200px',
            }}
          >
            <CircularProgress size={40} sx={{ marginBottom: spacing.md }} />
            <Typography
              sx={{
                fontSize: typography.fontSize.sm,
                color: colors.text.secondary,
              }}
            >
              {loadingMessage}
            </Typography>
          </Box>
        ) : (
          <>
            {typeof content === 'string' ? (
              <Typography
                sx={{
                  fontSize: typography.fontSize.md,
                  color: colors.text.primary,
                  lineHeight: typography.lineHeight.relaxed,
                }}
              >
                {content}
              </Typography>
            ) : (
              content || children
            )}
          </>
        )}
      </DialogContent>

      {/* Actions */}
      {renderActions()}
    </Dialog>
  );
};

export default BaseDialog;

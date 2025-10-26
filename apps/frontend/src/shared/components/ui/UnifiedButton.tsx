/**
 * Unified Button Component
 *
 * Consolidates AccessibleButton, LoadingButton, and StandardButton into a single,
 * comprehensive button component with all features:
 * - Accessibility compliance (WCAG 2.1 AA)
 * - Loading states with progress indicators
 * - Design token integration
 * - Multiple variants and sizes
 * - Hover animations and micro-interactions
 * - High contrast and reduced motion support
 */

import React from 'react';
import { Button as MuiButton, CircularProgress, SxProps, Theme, ButtonProps as MuiButtonProps } from '@mui/material';
import { styled } from '@mui/material/styles';
import { DESIGN_TOKENS, getButtonProps, createTransition, createElevation } from '@/theme/designTokens.js';

/**
 * Button variant types
 */
export type ButtonVariant = 'primary' | 'secondary' | 'tertiary' | 'danger' | 'success';

/**
 * Button size types
 */
export type ButtonSize = 'small' | 'medium' | 'large';

/**
 * Props for UnifiedButton component
 */
export interface UnifiedButtonProps extends Omit<MuiButtonProps, 'variant' | 'size'> {
  /** Show loading state with spinner */
  loading?: boolean;
  /** Text to display when loading (for screen readers) */
  loadingText?: string;
  /** Button content */
  children: React.ReactNode;
  /** Button visual variant */
  variant?: ButtonVariant;
  /** Button size */
  size?: ButtonSize;
  /** Accessible label for screen readers */
  ariaLabel?: string;
  /** ID of element describing the button */
  ariaDescribedBy?: string;
  /** Click handler */
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  /** Disabled state */
  disabled?: boolean;
  /** Additional MUI styles */
  sx?: SxProps<Theme>;
  /** Button HTML type */
  type?: 'button' | 'submit' | 'reset';
  /** Icon displayed before button text */
  startIcon?: React.ReactElement;
  /** Icon displayed after button text */
  endIcon?: React.ReactElement;
}

interface StyledButtonProps {
  buttonVariant?: string;
  loading?: boolean;
}

// Enhanced styled button with all accessibility and design features
const StyledButton = styled(MuiButton, {
  shouldForwardProp: (prop) => prop !== 'buttonVariant' && prop !== 'loading'
})<StyledButtonProps>(({ theme, size, loading }) => {
  const sizeKey = (size || 'medium') as ButtonSize;
  const sizeConfig = DESIGN_TOKENS.components.button.sizes[sizeKey] || DESIGN_TOKENS.components.button.sizes.medium;

  return {
    textTransform: 'none',
    fontWeight: DESIGN_TOKENS.typography.weights.medium,
    borderRadius: '8px',
    minHeight: sizeConfig.height,
    padding: sizeConfig.padding,
    fontSize: sizeConfig.fontSize,
    cursor: loading ? 'not-allowed' : 'pointer',
    ...createTransition('all', 'fast'),

    // Accessibility focus styles
    '&:focus-visible': {
      outline: `3px solid ${theme.palette.primary.main}`,
      outlineOffset: '2px',
      borderRadius: '8px',
    },

    // Disabled state styling
    '&:disabled': {
      opacity: loading ? 0.8 : 0.6,
      cursor: 'not-allowed',
      pointerEvents: 'auto', // Allow focus for screen readers
    },

    // Hover effects (disabled when loading)
    '&:hover:not(:disabled)': !loading ? {
      transform: 'translateY(-1px)',
      ...createElevation(2)
    } : {},



    // High contrast mode support
    '@media (prefers-contrast: high)': {
      '&:focus-visible': {
        outline: '3px solid #000000',
        outlineOffset: '2px',
      }
    },

    // Reduced motion support
    '@media (prefers-reduced-motion: reduce)': {
      transition: 'none',
      '&:hover:not(:disabled)': {
        transform: 'none',
      }
    },

    // Icon spacing
    '& .MuiButton-startIcon': {
      marginRight: '8px',
    },
    '& .MuiButton-endIcon': {
      marginLeft: '8px',
    }
  };
});

/**
 * UnifiedButton - A comprehensive button component with loading states and accessibility
 *
 * @component
 * @example
 * ```tsx
 * // Basic button
 * <UnifiedButton variant="primary" onClick={handleClick}>
 *   Click Me
 * </UnifiedButton>
 *
 * // Loading button
 * <UnifiedButton loading loadingText="Saving...">
 *   Save
 * </UnifiedButton>
 *
 * // Button with icon
 * <UnifiedButton startIcon={<SaveIcon />} variant="success">
 *   Save Changes
 * </UnifiedButton>
 * ```
 */
const UnifiedButton = React.forwardRef<HTMLButtonElement, UnifiedButtonProps>(({
  loading = false,
  loadingText = "Processing...",
  children,
  variant = 'primary',
  size = 'medium',
  ariaLabel,
  ariaDescribedBy,
  onClick,
  disabled = false,
  sx = {},
  type = 'button',
  startIcon,
  endIcon,
  ...props
}, ref: React.Ref<HTMLButtonElement>) => {

  // Get design token button properties
  const buttonProps = getButtonProps(size, variant);
  const isDisabled = disabled || loading;

  // Generate accessible attributes
  const accessibleProps = {
    'aria-label': ariaLabel || (typeof children === 'string' ? children : undefined),
    'aria-describedby': ariaDescribedBy,
    'aria-disabled': isDisabled,
    'aria-busy': loading,
    type,
    ref,
    ...props
  };

  // Loading spinner configuration
  const spinnerSize = size === 'small' ? 14 : size === 'large' ? 20 : 16;

  return (
    <div style={{ position: 'relative', display: 'inline-block' }}>
      <StyledButton
        variant={buttonProps.variant as 'text' | 'outlined' | 'contained'}
        color={buttonProps.color as 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success'}
        size={size}
        buttonVariant={buttonProps.color}
        loading={loading}
        disabled={isDisabled}
        onClick={loading ? undefined : onClick}
        startIcon={!loading ? startIcon : undefined}
        endIcon={!loading ? endIcon : undefined}
        sx={sx}
        {...accessibleProps}
      >
        {loading ? loadingText : children}
      </StyledButton>

      {/* Loading indicator overlay */}
      {loading && (
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            pointerEvents: 'none',
            zIndex: 1,
            color: 'white'
          }}
        >
          <CircularProgress
            size={spinnerSize}
            color="inherit"
            aria-hidden="true"
          />
          <span aria-live="polite" className="sr-only">
            {loadingText}
          </span>
        </div>
      )}
    </div>
  );
});

UnifiedButton.displayName = 'UnifiedButton';

// Pre-configured button variants for common use cases
export const PrimaryButton: React.FC<Omit<UnifiedButtonProps, 'variant'>> = (props) => (
  <UnifiedButton variant="primary" {...props} />
);

export const SecondaryButton: React.FC<Omit<UnifiedButtonProps, 'variant'>> = (props) => (
  <UnifiedButton variant="secondary" {...props} />
);

export const TertiaryButton: React.FC<Omit<UnifiedButtonProps, 'variant'>> = (props) => (
  <UnifiedButton variant="tertiary" {...props} />
);

export const DangerButton: React.FC<Omit<UnifiedButtonProps, 'variant'>> = (props) => (
  <UnifiedButton variant="danger" {...props} />
);

export const SuccessButton: React.FC<Omit<UnifiedButtonProps, 'variant'>> = (props) => (
  <UnifiedButton variant="success" {...props} />
);

// Size variants
export const SmallButton: React.FC<Omit<UnifiedButtonProps, 'size'>> = (props) => (
  <UnifiedButton size="small" {...props} />
);

export const LargeButton: React.FC<Omit<UnifiedButtonProps, 'size'>> = (props) => (
  <UnifiedButton size="large" {...props} />
);

// Loading button with common loading text
export const LoadingButton: React.FC<UnifiedButtonProps> = ({ loadingText = "Loading...", ...props }) => (
  <UnifiedButton loadingText={loadingText} {...props} />
);

export default UnifiedButton;

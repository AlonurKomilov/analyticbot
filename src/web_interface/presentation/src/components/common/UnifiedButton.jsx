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
import { Button as MuiButton, CircularProgress } from '@mui/material';
import { styled } from '@mui/material/styles';
import { DESIGN_TOKENS, getButtonProps, createTransition, createElevation } from '../../theme/designTokens.js';

// Enhanced styled button with all accessibility and design features
const StyledButton = styled(MuiButton)(({ theme, size, buttonVariant, loading }) => {
  const sizeConfig = DESIGN_TOKENS.components.button.sizes[size] || DESIGN_TOKENS.components.button.sizes.medium;
  
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
 * Unified Button Component
 * 
 * @param {Object} props - Component props
 * @param {boolean} props.loading - Show loading state
 * @param {string} props.loadingText - Text to show when loading (for screen readers)
 * @param {ReactNode} props.children - Button content
 * @param {string} props.variant - Button variant (primary, secondary, tertiary, danger, success)
 * @param {string} props.size - Button size (small, medium, large)
 * @param {string} props.ariaLabel - Accessible label for screen readers
 * @param {string} props.ariaDescribedBy - ID of element describing the button
 * @param {Function} props.onClick - Click handler
 * @param {boolean} props.disabled - Disabled state
 * @param {Object} props.sx - Additional styles
 * @param {string} props.type - Button type (button, submit, reset)
 * @param {ReactElement} props.startIcon - Icon before button text
 * @param {ReactElement} props.endIcon - Icon after button text
 */
const UnifiedButton = React.forwardRef(({
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
}, ref) => {
  
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
        variant={buttonProps.variant}
        color={buttonProps.color}
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
export const PrimaryButton = (props) => (
  <UnifiedButton variant="primary" {...props} />
);

export const SecondaryButton = (props) => (
  <UnifiedButton variant="secondary" {...props} />
);

export const TertiaryButton = (props) => (
  <UnifiedButton variant="tertiary" {...props} />
);

export const DangerButton = (props) => (
  <UnifiedButton variant="danger" {...props} />
);

export const SuccessButton = (props) => (
  <UnifiedButton variant="success" {...props} />
);

// Size variants
export const SmallButton = (props) => (
  <UnifiedButton size="small" {...props} />
);

export const LargeButton = (props) => (
  <UnifiedButton size="large" {...props} />
);

// Loading button with common loading text
export const LoadingButton = ({ loadingText = "Loading...", ...props }) => (
  <UnifiedButton loadingText={loadingText} {...props} />
);

export default UnifiedButton;
import React from 'react';
import { Button, CircularProgress } from '@mui/material';
import { styled } from '@mui/material/styles';

// Enhanced button with consistent accessibility features
const StyledButton = styled(Button)(({ theme, size }) => ({
    textTransform: 'none',
    fontWeight: 500,
    borderRadius: theme.shape.borderRadius || '6px',
    minHeight: size === 'small' ? '36px' : '44px', // Adequate touch targets
    padding: size === 'small' ? '6px 12px' : '8px 16px',
    transition: 'all 0.2s ease-in-out',
    
    '&:focus-visible': {
        outline: `3px solid ${theme.palette.primary.main}`,
        outlineOffset: '2px',
        borderRadius: '6px',
    },
    
    '&:disabled': {
        opacity: 0.6,
        cursor: 'not-allowed',
        pointerEvents: 'auto', // Allow focus for screen readers
    },
    
    '&:hover:not(:disabled)': {
        transform: 'translateY(-1px)',
        boxShadow: theme.shadows[4],
    },
    
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
    }
}));

/**
 * Accessible button component with enhanced UX features
 * 
 * @param {Object} props - Component props
 * @param {boolean} props.loading - Show loading state
 * @param {string} props.loadingText - Text to show when loading
 * @param {ReactNode} props.children - Button content
 * @param {string} props.ariaLabel - Accessible label for screen readers
 * @param {string} props.ariaDescribedBy - ID of element describing the button
 * @param {Function} props.onClick - Click handler
 * @param {boolean} props.disabled - Disabled state
 * @param {string} props.variant - Button variant (contained, outlined, text)
 * @param {string} props.color - Button color
 * @param {string} props.size - Button size (small, medium, large)
 * @param {Object} props.sx - Additional styles
 * @param {string} props.type - Button type (button, submit, reset)
 */
const AccessibleButton = React.forwardRef(({
    loading = false,
    loadingText = "Processing...",
    children,
    ariaLabel,
    ariaDescribedBy,
    onClick,
    disabled = false,
    variant = 'contained',
    color = 'primary',
    size = 'medium',
    sx = {},
    type = 'button',
    startIcon,
    endIcon,
    ...props
}, ref) => {
    
    // Generate accessible attributes
    const accessibleProps = {
        'aria-label': ariaLabel || (typeof children === 'string' ? children : undefined),
        'aria-describedby': ariaDescribedBy,
        'aria-disabled': disabled || loading,
        'aria-busy': loading,
        type,
        ref,
        ...props
    };
    
    // Handle loading state
    const buttonContent = loading ? (
        <>
            <CircularProgress 
                size={size === 'small' ? 14 : 16} 
                sx={{ mr: 1 }} 
                color="inherit" 
                aria-hidden="true"
            />
            {loadingText}
        </>
    ) : (
        <>
            {startIcon && startIcon}
            {children}
            {endIcon && endIcon}
        </>
    );
    
    return (
        <StyledButton
            variant={variant}
            color={color}
            size={size}
            disabled={disabled || loading}
            onClick={loading ? undefined : onClick}
            sx={{
                ...sx,
                // Ensure icons don't interfere with accessibility
                '& .MuiButton-startIcon': {
                    marginRight: '8px',
                },
                '& .MuiButton-endIcon': {
                    marginLeft: '8px',
                }
            }}
            {...accessibleProps}
        >
            {buttonContent}
        </StyledButton>
    );
});

AccessibleButton.displayName = 'AccessibleButton';

export default AccessibleButton;

// Pre-configured button variants for common use cases
export const PrimaryButton = (props) => (
    <AccessibleButton variant="contained" color="primary" {...props} />
);

export const SecondaryButton = (props) => (
    <AccessibleButton variant="outlined" color="primary" {...props} />
);

export const DangerButton = (props) => (
    <AccessibleButton variant="contained" color="error" {...props} />
);

export const SuccessButton = (props) => (
    <AccessibleButton variant="contained" color="success" {...props} />
);

export const LinkButton = (props) => (
    <AccessibleButton variant="text" color="primary" {...props} />
);

import React from 'react';
import { Button, CircularProgress } from '@mui/material';

/**
 * Enhanced loading button with better accessibility
 * 
 * @param {Object} props - Component props
 * @param {boolean} props.loading - Show loading state
 * @param {ReactNode} props.children - Button content when not loading
 * @param {string} props.loadingText - Text to show when loading
 * @param {number} props.size - Size of loading spinner
 * @param {string} props.ariaLabel - Accessible label
 */
const LoadingButton = ({ 
    loading = false, 
    children, 
    loadingText = "Processing...",
    size = 16,
    ariaLabel,
    ...props 
}) => {
    // Generate accessible props
    const accessibleProps = {
        'aria-label': ariaLabel || (typeof children === 'string' ? children : undefined),
        'aria-busy': loading,
        'aria-disabled': loading || props.disabled,
        disabled: loading || props.disabled,
        ...props
    };

    return (
        <Button 
            {...accessibleProps}
            sx={{
                minHeight: '44px', // Adequate touch target
                '&:focus-visible': {
                    outline: '3px solid #2196F3',
                    outlineOffset: '2px'
                },
                '&:disabled': {
                    opacity: 0.6,
                    cursor: 'not-allowed',
                    pointerEvents: 'auto', // Allow focus for screen readers
                },
                // High contrast mode support
                '@media (prefers-contrast: high)': {
                    '&:focus-visible': {
                        outline: '3px solid #000000',
                        outlineOffset: '2px',
                    }
                },
                ...props.sx
            }}
        >
            {loading ? (
                <>
                    <CircularProgress 
                        size={size} 
                        sx={{ mr: 1 }} 
                        color="inherit" 
                        aria-hidden="true"
                        role="progressbar"
                        aria-label="Loading"
                    />
                    <span aria-live="polite">{loadingText}</span>
                </>
            ) : children}
        </Button>
    );
};

export default LoadingButton;

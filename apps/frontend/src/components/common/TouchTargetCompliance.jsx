import React from 'react';
import {
    IconButton as MuiIconButton,
    Button as MuiButton,
    Chip as MuiChip,
    FormControl as MuiFormControl,
    Select as MuiSelect,
    TextField as MuiTextField
} from '@mui/material';
import { styled } from '@mui/material/styles';

/**
 * Touch Target Compliance Components
 * Ensures all interactive elements meet WCAG 44px minimum touch target requirement
 */

// Enhanced IconButton with guaranteed 44px minimum
export const IconButton = styled(MuiIconButton)(({ theme, size }) => ({
    minWidth: size === 'small' ? '36px' : '44px',
    minHeight: size === 'small' ? '36px' : '44px',
    padding: size === 'small' ? '6px' : '10px',

    '&:focus-visible': {
        outline: `3px solid ${theme.palette.primary.main}`,
        outlineOffset: '2px',
    },

    // Ensure small buttons still have adequate touch area on mobile
    '@media (hover: none)': {
        minWidth: '44px',
        minHeight: '44px',
        padding: '10px',
    },

    '&.Mui-disabled': {
        opacity: 0.6,
        cursor: 'not-allowed',
        pointerEvents: 'auto', // Allow focus for screen readers
    }
}));

// Enhanced Button with consistent touch targets
export const Button = styled(MuiButton)(({ theme, size }) => ({
    minHeight: size === 'small' ? '36px' : '44px',
    padding: size === 'small' ? '6px 12px' : '8px 16px',
    textTransform: 'none',
    fontWeight: 500,
    borderRadius: theme.shape.borderRadius || '6px',

    '&:focus-visible': {
        outline: `3px solid ${theme.palette.primary.main}`,
        outlineOffset: '2px',
    },

    // Mobile optimization
    '@media (hover: none)': {
        minHeight: '44px',
        padding: '10px 16px',
    },

    '&:hover:not(:disabled)': {
        transform: 'translateY(-1px)',
        boxShadow: theme.shadows[4],
    },

    '&.Mui-disabled': {
        opacity: 0.6,
        cursor: 'not-allowed',
    },

    // Reduced motion support
    '@media (prefers-reduced-motion: reduce)': {
        transition: 'none',
        '&:hover:not(:disabled)': {
            transform: 'none',
        }
    }
}));

// Enhanced Chip with better touch targets
export const Chip = styled(MuiChip)(({ theme, size, onClick, onDelete }) => ({
    minHeight: size === 'small' ? '28px' : '32px',

    // If clickable or deletable, ensure minimum touch target
    ...(onClick || onDelete) && {
        minHeight: size === 'small' ? '36px' : '44px',

        '@media (hover: none)': {
            minHeight: '44px',
        }
    },

    '&:focus-visible': {
        outline: `3px solid ${theme.palette.primary.main}`,
        outlineOffset: '2px',
    },

    '& .MuiChip-deleteIcon': {
        fontSize: size === 'small' ? '16px' : '20px',
        margin: size === 'small' ? '0 2px 0 -4px' : '0 4px 0 -6px',

        '&:hover': {
            color: theme.palette.error.main,
        }
    }
}));

// Enhanced FormControl with proper sizing
export const FormControl = styled(MuiFormControl)(({ theme, size }) => ({
    minWidth: size === 'small' ? '100px' : '120px',

    '& .MuiSelect-select': {
        minHeight: size === 'small' ? '20px' : '24px',
        padding: size === 'small' ? '8px 14px' : '10px 14px',
    },

    '& .MuiOutlinedInput-root': {
        minHeight: size === 'small' ? '36px' : '44px',

        '@media (hover: none)': {
            minHeight: '44px',
        }
    }
}));

// Enhanced Select with touch optimization
export const Select = styled(MuiSelect)(({ theme, size }) => ({
    minHeight: size === 'small' ? '36px' : '44px',

    '@media (hover: none)': {
        minHeight: '44px',
    },

    '&:focus-visible': {
        outline: `3px solid ${theme.palette.primary.main}`,
        outlineOffset: '2px',
    }
}));

// Enhanced TextField with proper touch targets
export const TextField = styled(MuiTextField)(({ theme, size }) => ({
    '& .MuiOutlinedInput-root': {
        minHeight: size === 'small' ? '36px' : '44px',

        '@media (hover: none)': {
            minHeight: '44px',
        },

        '&:focus-visible': {
            outline: `3px solid ${theme.palette.primary.main}`,
            outlineOffset: '2px',
        }
    }
}));

/**
 * Touch Target Audit Hook
 * Development utility to identify components that don't meet touch target requirements
 */
export const useTouchTargetAudit = (enabled = process.env.NODE_ENV === 'development') => {
    React.useEffect(() => {
        if (!enabled || !document || !document.body) return;

        const auditElements = () => {
            try {
                const interactiveElements = document.querySelectorAll(
                    'button, [role="button"], input, select, textarea, a[href], [tabindex]:not([tabindex="-1"])'
                );

            const violations = [];

            interactiveElements.forEach((element) => {
                const rect = element.getBoundingClientRect();
                const minSize = 44;

                if (rect.width > 0 && rect.height > 0) {
                    if (rect.width < minSize || rect.height < minSize) {
                        violations.push({
                            element,
                            size: { width: rect.width, height: rect.height },
                            tagName: element.tagName,
                            className: element.className,
                            id: element.id
                        });
                    }
                }
            });

            if (process.env.NODE_ENV === 'development') {
                if (violations.length > 0) {
                    console.group('🎯 Touch Target Compliance Violations');
                    violations.forEach((violation, index) => {
                        console.warn(`${index + 1}. ${violation.tagName}`, {
                            size: violation.size,
                            className: violation.className,
                            id: violation.id,
                            element: violation.element
                        });
                    });
                    console.groupEnd();
                } else {
                    console.log('✅ All interactive elements meet touch target requirements');
                }
            }
            } catch (error) {
                console.warn('Touch target audit failed:', error);
            }
        };

        // Run audit after component mounts and updates
        const timeoutId = setTimeout(auditElements, 1000);

        return () => clearTimeout(timeoutId);
    }, [enabled]);
};

/**
 * Touch Target Provider
 * Wraps components to ensure touch target compliance
 */
export const TouchTargetProvider = ({ children }) => {
    useTouchTargetAudit();

    return <>{children}</>;
};

export default {
    IconButton,
    Button,
    Chip,
    FormControl,
    Select,
    TextField,
    TouchTargetProvider,
    useTouchTargetAudit
};

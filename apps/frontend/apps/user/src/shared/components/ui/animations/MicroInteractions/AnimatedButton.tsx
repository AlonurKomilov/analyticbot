/**
 * Animated Button with Ripple Effect
 */
import { Box, styled } from '@mui/material';
import { DESIGN_TOKENS } from '@theme/designTokens';
import type { AnimatedButtonProps } from './types';

export const AnimatedButton = styled(Box)<AnimatedButtonProps>(
  ({ theme, variant = 'contained', disabled = false }) => ({
    position: 'relative',
    overflow: 'hidden',
    borderRadius: DESIGN_TOKENS.layout.borderRadius.md,
    padding: '12px 24px',
    fontSize: '1rem',
    fontWeight: 500,
    cursor: disabled ? 'not-allowed' : 'pointer',
    opacity: disabled ? 0.6 : 1,
    transition: 'all 0.2s ease-in-out',
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '44px',

    // Variant styles
    ...(variant === 'contained' && {
      backgroundColor: theme.palette.primary.main,
      color: theme.palette.primary.contrastText,
      '&:hover':
        !disabled && {
          backgroundColor: theme.palette.primary.dark,
          transform: 'translateY(-1px)',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
        },
    }),

    ...(variant === 'outlined' && {
      backgroundColor: 'transparent',
      color: theme.palette.primary.main,
      border: `1px solid ${theme.palette.primary.main}`,
      '&:hover':
        !disabled && {
          backgroundColor: theme.palette.primary.main,
          color: theme.palette.primary.contrastText,
          transform: 'translateY(-1px)',
        },
    }),

    // Ripple effect container
    '&::before': {
      content: '""',
      position: 'absolute',
      top: '50%',
      left: '50%',
      width: 0,
      height: 0,
      borderRadius: '50%',
      backgroundColor: 'rgba(255, 255, 255, 0.3)',
      transform: 'translate(-50%, -50%)',
      transition: 'width 0.6s, height 0.6s',
    },

    '&:active::before':
      !disabled && {
        width: '300px',
        height: '300px',
      },
  })
);

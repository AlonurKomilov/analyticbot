/**
 * Interactive Card with Hover Effects
 */
import { Box, styled } from '@mui/material';
import { DESIGN_TOKENS } from '@theme/designTokens';
import type { InteractiveCardProps } from './types';

export const InteractiveCard = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'interactive' && prop !== 'hoverEffect',
})<InteractiveCardProps>(({ theme, interactive = true, hoverEffect = 'lift' }) => ({
  borderRadius: DESIGN_TOKENS.layout.borderRadius.md,
  border: `1px solid ${theme.palette.divider}`,
  backgroundColor: theme.palette.background.paper,
  transition: 'all 0.2s ease-in-out',
  cursor: interactive ? 'pointer' : 'default',

  ...(interactive && {
    '&:hover': {
      ...(hoverEffect === 'lift' && {
        transform: 'translateY(-4px)',
        boxShadow: '0 8px 24px rgba(0, 0, 0, 0.12)',
        borderColor: theme.palette.primary.main,
      }),
      ...(hoverEffect === 'glow' && {
        boxShadow: `0 0 0 2px ${theme.palette.primary.main}20`,
        borderColor: theme.palette.primary.main,
      }),
      ...(hoverEffect === 'scale' && {
        transform: 'scale(1.02)',
      }),
    },

    '&:active': {
      transform: hoverEffect === 'lift' ? 'translateY(-2px)' : 'scale(0.98)',
      transition: 'all 0.1s ease-in-out',
    },
  }),
}));

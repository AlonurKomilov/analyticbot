import React from 'react';
import { Card, CardContent, CardActions, Box, alpha } from '@mui/material';
import { styled } from '@mui/material/styles';
import { SPACING_SCALE, SEMANTIC_SPACING } from '../../theme/spacingSystem.js';

/**
 * ModernCard - Enhanced card component with contemporary design
 *
 * Features:
 * - Subtle elevation and hover effects
 * - Rounded corners with consistent border radius
 * - Smooth transitions and micro-interactions
 * - Multiple variants (default, elevated, interactive)
 * - Consistent spacing and typography
 */

const StyledCard = styled(Card, {
  shouldForwardProp: (prop) => !['variant', 'interactive'].includes(prop),
})(({ theme, variant = 'default', interactive = false }) => ({
  borderRadius: theme.spacing(1.5), // 12px
  transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
  border: `1px solid ${alpha(theme.palette.divider, 0.12)}`,

  // Base styles for all variants
  ...(variant === 'default' && {
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
    '&:hover': interactive ? {
      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
      transform: 'translateY(-2px)',
    } : {},
  }),

  // Elevated variant - more prominent shadow
  ...(variant === 'elevated' && {
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
    '&:hover': interactive ? {
      boxShadow: '0 8px 24px rgba(0, 0, 0, 0.15)',
      transform: 'translateY(-4px)',
    } : {},
  }),

  // Interactive variant - clear hover intent
  ...(variant === 'interactive' && {
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
    cursor: interactive ? 'pointer' : 'default',
    '&:hover': {
      boxShadow: '0 8px 24px rgba(0, 0, 0, 0.12)',
      transform: 'translateY(-3px)',
      borderColor: alpha(theme.palette.primary.main, 0.3),
    },
    '&:active': interactive ? {
      transform: 'translateY(-1px)',
      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
    } : {},
  }),

  // Flat variant - minimal shadow
  ...(variant === 'flat' && {
    boxShadow: 'none',
    backgroundColor: alpha(theme.palette.background.paper, 0.6),
    '&:hover': interactive ? {
      backgroundColor: theme.palette.background.paper,
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
    } : {},
  }),
}));

const ModernCard = React.forwardRef(({
  children,
  variant = 'default',
  interactive = false,
  padding = 'standard', // 'none', 'compact', 'standard', 'comfortable'
  onClick,
  sx = {},
  ...props
}, ref) => {
  const getPadding = () => {
    switch (padding) {
      case 'none': return 0;
      case 'compact': return SPACING_SCALE.lg;      // 16px
      case 'standard': return SEMANTIC_SPACING.ui.cardPadding;  // 24px
      case 'comfortable': return SPACING_SCALE.xxl; // 32px
      default: return SEMANTIC_SPACING.ui.cardPadding; // 24px
    }
  };

  return (
    <StyledCard
      ref={ref}
      variant={variant}
      interactive={interactive || !!onClick}
      onClick={onClick}
      sx={sx}
      {...props}
    >
      {padding !== 'none' ? (
        <CardContent sx={{ p: getPadding(), '&:last-child': { pb: getPadding() } }}>
          {children}
        </CardContent>
      ) : (
        children
      )}
    </StyledCard>
  );
});

ModernCard.displayName = 'ModernCard';

/**
 * ModernCardHeader - Standardized card header with consistent styling
 */
export const ModernCardHeader = ({
  title,
  subtitle,
  action,
  icon,
  sx = {}
}) => (
  <Box
    sx={{
      display: 'flex',
      alignItems: 'flex-start',
      justifyContent: 'space-between',
      mb: subtitle ? SPACING_SCALE.sm : SPACING_SCALE.lg, // 8px or 16px
      ...sx
    }}
  >
    <Box sx={{ display: 'flex', alignItems: 'center', gap: SPACING_SCALE.md, minWidth: 0 }}> {/* 12px gap */}
      {icon && (
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            color: 'primary.main',
            flexShrink: 0
          }}
        >
          {icon}
        </Box>
      )}

      <Box sx={{ minWidth: 0 }}>
        {title && (
          <Box
            component="h3"
            sx={{
              m: 0,
              typography: 'h6',
              fontWeight: 600,
              color: 'text.primary',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap'
            }}
          >
            {title}
          </Box>
        )}

        {subtitle && (
          <Box
            component="p"
            sx={{
              m: 0,
              mt: SPACING_SCALE.xs, // 4px
              typography: 'body2',
              color: 'text.secondary',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap'
            }}
          >
            {subtitle}
          </Box>
        )}
      </Box>
    </Box>

    {action && (
      <Box sx={{ flexShrink: 0, ml: SPACING_SCALE.lg }}> {/* 16px */}
        {action}
      </Box>
    )}
  </Box>
);

/**
 * ModernCardActions - Standardized card actions area
 */
export const ModernCardActions = ({
  children,
  justify = 'flex-end',
  sx = {}
}) => (
  <CardActions
    sx={{
      pt: SPACING_SCALE.lg,  // 16px
      px: 0,
      justifyContent: justify,
      gap: SPACING_SCALE.sm, // 8px
      ...sx
    }}
  >
    {children}
  </CardActions>
);

export default ModernCard;

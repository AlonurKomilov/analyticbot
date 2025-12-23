/**
 * Enhanced Card Component
 *
 * Improved card design with:
 * - Better visual hierarchy
 * - Consistent spacing and elevation
 * - Interactive states and animations
 * - Flexible header and footer layouts
 * - Status indicators and badges
 */

import React from 'react';
import {
  Card as MuiCard,
  CardContent,
  CardHeader as MuiCardHeader,
  CardActions,
  Box,
  Typography,
  Chip,
  Skeleton,
  CardProps
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { DESIGN_TOKENS } from '@theme/designTokens';

interface StyledCardProps {
  variant?: 'elevated' | 'outlined' | 'filled';
  interactive?: boolean;
  loading?: boolean;
}

interface StatusConfig {
  label: string;
  color?: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning';
}

interface BadgeConfig {
  text: string;
  color?: string;
}

interface EnhancedCardHeaderProps {
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  status?: StatusConfig;
  badge?: BadgeConfig;
  actions?: React.ReactNode;
  loading?: boolean;
  [key: string]: any;
}

interface EnhancedCardProps extends Omit<CardProps, 'variant' | 'title'> {
  variant?: 'elevated' | 'outlined' | 'filled';
  interactive?: boolean;
  loading?: boolean;
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  status?: StatusConfig;
  badge?: BadgeConfig;
  headerActions?: React.ReactNode;
  children?: React.ReactNode;
  footerActions?: React.ReactNode;
  onClick?: () => void;
}

const StyledCard = styled(MuiCard, {
  // Filter out custom props to prevent them from being passed to the DOM
  shouldForwardProp: (prop) => !['interactive', 'loading', 'variant'].includes(prop as string)
})<StyledCardProps>(({ theme, variant = 'elevated', interactive, loading }) => ({
  borderRadius: DESIGN_TOKENS.layout.borderRadius.lg,
  transition: 'all 0.2s ease-in-out',
  border: '1px solid',
  borderColor: theme.palette.divider,

  // Variant styles
  ...(variant === 'elevated' && {
    boxShadow: theme.shadows[2],
    '&:hover': interactive ? {
      boxShadow: theme.shadows[4],
      transform: 'translateY(-2px)'
    } : {}
  }),

  ...(variant === 'outlined' && {
    boxShadow: 'none',
    borderColor: theme.palette.divider
  }),

  ...(variant === 'filled' && {
    backgroundColor: theme.palette.grey[50],
    border: 'none'
  }),

  // Interactive states
  ...(interactive && {
    cursor: 'pointer',
    '&:hover': {
      borderColor: theme.palette.primary.main,
      boxShadow: theme.shadows[3]
    }
  }),

  // Loading state
  ...(loading && {
    opacity: 0.7,
    pointerEvents: 'none'
  })
}));

const EnhancedCardHeader: React.FC<EnhancedCardHeaderProps> = ({
  title,
  subtitle,
  status,
  badge,
  actions,
  loading,
  ...props
}) => {
  if (loading) {
    return (
      <MuiCardHeader
        title={<Skeleton width="60%" />}
        subheader={<Skeleton width="40%" />}
        action={<Skeleton variant="rectangular" width={32} height={32} />}
        {...props}
      />
    );
  }

  return (
    <MuiCardHeader
      title={
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            {title}
          </Typography>
          {status && (
            <Chip
              label={status.label}
              color={status.color || 'default'}
              size="small"
              sx={{ height: 20, fontSize: '0.75rem' }}
            />
          )}
          {badge && (
            <Box
              sx={{
                bgcolor: badge.color || 'primary.main',
                color: 'white',
                px: 1,
                py: 0.25,
                borderRadius: 1,
                fontSize: '0.75rem',
                fontWeight: 600
              }}
            >
              {badge.text}
            </Box>
          )}
        </Box>
      }
      subheader={subtitle && (
        <Typography
          variant="body2"
          sx={{
            color: 'text.secondary',
            mt: 0.5,
            lineHeight: 1.4
          }}
        >
          {subtitle}
        </Typography>
      )}
      action={actions && (
        <Box sx={{ display: 'flex', gap: 0.5 }}>
          {actions}
        </Box>
      )}
      sx={{
        pb: 1,
        '& .MuiCardHeader-content': {
          minWidth: 0,
          flex: 1
        }
      }}
      {...props}
    />
  );
};

const EnhancedCard: React.FC<EnhancedCardProps> = ({
  variant = 'elevated',
  interactive = false,
  loading = false,
  title,
  subtitle,
  status,
  badge,
  headerActions,
  children,
  footerActions,
  onClick,
  sx = {},
  ...props
}) => {
  const hasHeader = title || subtitle || status || badge || headerActions;

  return (
    <StyledCard
      variant={variant as any}
      interactive={interactive}
      loading={loading}
      onClick={interactive ? onClick : undefined}
      sx={sx}
      {...props}
    >
      {hasHeader && (
        <EnhancedCardHeader
          title={title}
          subtitle={subtitle}
          status={status}
          badge={badge}
          actions={headerActions}
          loading={loading}
        />
      )}

      <CardContent sx={{ pt: hasHeader ? 1 : 3 }}>
        {loading ? (
          <Box>
            <Skeleton width="100%" height={60} sx={{ mb: 1 }} />
            <Skeleton width="80%" height={40} sx={{ mb: 1 }} />
            <Skeleton width="60%" height={40} />
          </Box>
        ) : (
          children
        )}
      </CardContent>

      {footerActions && !loading && (
        <CardActions sx={{ pt: 0, px: 3, pb: 2 }}>
          {footerActions}
        </CardActions>
      )}
    </StyledCard>
  );
};

// Pre-configured variants
export const PrimaryCard: React.FC<EnhancedCardProps> = (props) => (
  <EnhancedCard variant="elevated" {...props} />
);

export const SecondaryCard: React.FC<EnhancedCardProps> = (props) => (
  <EnhancedCard variant="outlined" {...props} />
);

export const InteractiveCard: React.FC<EnhancedCardProps> = (props) => (
  <EnhancedCard variant="elevated" interactive {...props} />
);

export const StatusCard: React.FC<EnhancedCardProps> = ({ status, ...props }) => (
  <EnhancedCard
    variant="filled"
    status={status}
    {...props}
  />
);

export default EnhancedCard;

/**
 * BaseEmptyState Component
 * 
 * Reusable empty state component with icon/illustration, title, description, and action button.
 * Consolidates 8+ empty state patterns across the application.
 * 
 * Features:
 * - Customizable icon or illustration
 * - Title and description text
 * - Optional action button
 * - Consistent spacing and sizing
 * - Accessibility support
 * - Uses design tokens
 * 
 * Usage:
 * ```tsx
 * <BaseEmptyState
 *   icon={<SearchIcon />}
 *   title="No results found"
 *   description="Try adjusting your search criteria"
 *   action={<Button>Clear filters</Button>}
 * />
 * ```
 */

import React from 'react';
import { Box, Typography, SvgIconProps } from '@mui/material';
import { Inbox as InboxIcon } from '@mui/icons-material';
import { spacing, colors, typography } from '@/theme/tokens';

// =============================================================================
// Types
// =============================================================================

export interface BaseEmptyStateProps {
  // Optional - Icon
  icon?: React.ReactElement<SvgIconProps> | React.ReactNode;
  iconSize?: 'sm' | 'md' | 'lg' | 'xl';
  
  // Optional - Text
  title?: string;
  description?: string;
  
  // Optional - Action
  action?: React.ReactNode;
  
  // Optional - Styling
  compact?: boolean;
  minHeight?: string | number;
}

// =============================================================================
// Component
// =============================================================================

const BaseEmptyState: React.FC<BaseEmptyStateProps> = ({
  icon = <InboxIcon />,
  iconSize = 'lg',
  title = 'No data',
  description,
  action,
  compact = false,
  minHeight,
}) => {
  // Icon size mapping
  const iconSizeMap = {
    sm: '48px',
    md: '64px',
    lg: '96px',
    xl: '128px',
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: compact ? spacing.lg : spacing.xxl,
        minHeight: minHeight || (compact ? '200px' : '400px'),
        textAlign: 'center',
      }}
      role="status"
      aria-live="polite"
    >
      {/* Icon */}
      {icon && (
        <Box
          sx={{
            marginBottom: spacing.lg,
            color: colors.text.disabled,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            '& .MuiSvgIcon-root': {
              fontSize: iconSizeMap[iconSize],
            },
          }}
        >
          {icon}
        </Box>
      )}

      {/* Title */}
      {title && (
        <Typography
          variant="h3"
          sx={{
            fontSize: compact ? typography.fontSize.lg : typography.fontSize.xl,
            fontWeight: typography.fontWeight.semibold,
            color: colors.text.primary,
            marginBottom: description ? spacing.xs : spacing.md,
          }}
        >
          {title}
        </Typography>
      )}

      {/* Description */}
      {description && (
        <Typography
          variant="body2"
          sx={{
            fontSize: typography.fontSize.sm,
            color: colors.text.secondary,
            marginBottom: action ? spacing.lg : 0,
            maxWidth: '400px',
            lineHeight: typography.lineHeight.relaxed,
          }}
        >
          {description}
        </Typography>
      )}

      {/* Action */}
      {action && (
        <Box
          sx={{
            marginTop: spacing.md,
          }}
        >
          {action}
        </Box>
      )}
    </Box>
  );
};

export default BaseEmptyState;

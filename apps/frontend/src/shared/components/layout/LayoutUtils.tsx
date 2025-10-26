/**
 * Layout Utils
 *
 * Utility functions and components for enhanced layout system
 */

import React from 'react';
import { Box, alpha, useTheme, Theme, BoxProps } from '@mui/material';
import { DESIGN_TOKENS } from '@theme/designTokens';

type EmphasisLevel = 'primary' | 'secondary' | 'default';

interface EmphasisStyles {
  bgcolor: string;
  border: string;
  borderRadius: number | string;
}

type HierarchyLevel = 1 | 2 | 3;
type SpacingLevel = 'sm' | 'md' | 'lg';

interface HierarchySpacing {
  mb: number;
  mt: number;
}

/**
 * Visual Hierarchy Utility Functions
 */
export const LayoutUtils = {
  /**
   * Get emphasis styles for different content levels
   */
  getEmphasisStyles: (level: EmphasisLevel = 'default', theme: Theme): EmphasisStyles => {
    const styles: Record<EmphasisLevel, EmphasisStyles> = {
      primary: {
        bgcolor: alpha(theme.palette.primary.main, 0.02),
        border: `2px solid ${alpha(theme.palette.primary.main, 0.1)}`,
        borderRadius: DESIGN_TOKENS.shape.borderRadius.lg
      },
      secondary: {
        bgcolor: alpha(theme.palette.secondary.main, 0.02),
        border: `1px solid ${alpha(theme.palette.secondary.main, 0.1)}`,
        borderRadius: DESIGN_TOKENS.shape.borderRadius.md
      },
      default: {
        bgcolor: theme.palette.background.paper,
        border: `1px solid ${theme.palette.divider}`,
        borderRadius: DESIGN_TOKENS.shape.borderRadius.sm
      }
    };

    return styles[level] || styles.default;
  },

  /**
   * Get responsive grid props
   */
  getResponsiveGrid: () => ({
    container: true,
    spacing: { xs: 2, md: 3, lg: 4 },
    sx: {
      maxWidth: '100%',
      margin: 0,
      width: '100%'
    }
  }),

  /**
   * Get visual hierarchy spacing
   */
  getHierarchySpacing: (level: HierarchyLevel | 'default'): HierarchySpacing => {
    const spacing: Record<HierarchyLevel | 'default', HierarchySpacing> = {
      1: { mb: 4, mt: 2 },
      2: { mb: 3, mt: 2 },
      3: { mb: 2, mt: 1 },
      default: { mb: 2, mt: 1 }
    };

    return spacing[level] || spacing.default;
  }
};

interface HierarchyContainerProps extends BoxProps {
  children: React.ReactNode;
  level?: EmphasisLevel;
  emphasis?: boolean;
}

/**
 * Enhanced Container with visual hierarchy support
 */
export const HierarchyContainer: React.FC<HierarchyContainerProps> = ({
  children,
  level = 'default',
  emphasis = false,
  ...props
}) => {
  const theme = useTheme();

  const emphasisStyles = emphasis
    ? LayoutUtils.getEmphasisStyles(level, theme)
    : {};

  return (
    <Box
      sx={{
        p: DESIGN_TOKENS.spacing.component.padding.md,
        ...emphasisStyles,
        ...props.sx
      }}
      {...props}
    >
      {children}
    </Box>
  );
};

interface ResponsiveWrapperProps extends BoxProps {
  children: React.ReactNode;
  maxWidth?: string;
}

/**
 * Responsive Content Wrapper
 */
export const ResponsiveWrapper: React.FC<ResponsiveWrapperProps> = ({
  children,
  maxWidth = 'xl',
  ...props
}) => (
  <Box
    sx={{
      maxWidth: { xs: '100%', sm: '100%', md: maxWidth },
      margin: '0 auto',
      px: { xs: 2, sm: 3, md: 4 },
      ...props.sx
    }}
    {...props}
  >
    {children}
  </Box>
);

interface HierarchyDividerProps {
  level?: HierarchyLevel;
  spacing?: SpacingLevel;
}

/**
 * Visual Divider with hierarchy support
 */
export const HierarchyDivider: React.FC<HierarchyDividerProps> = ({
  level = 1,
  spacing = 'md'
}) => {
  const theme = useTheme();
  const spacingValue = DESIGN_TOKENS.spacing.section.gap[spacing];

  const styles: Record<HierarchyLevel, any> = {
    1: {
      height: 2,
      bgcolor: theme.palette.primary.main,
      opacity: 0.2
    },
    2: {
      height: 1,
      bgcolor: theme.palette.divider,
      opacity: 0.6
    },
    3: {
      height: 1,
      bgcolor: theme.palette.divider,
      opacity: 0.3
    }
  };

  return (
    <Box
      sx={{
        width: '100%',
        my: spacingValue,
        ...styles[level]
      }}
    />
  );
};

interface FocusRingProps extends BoxProps {
  children: React.ReactNode;
}

/**
 * Focus Ring for accessibility
 */
export const FocusRing: React.FC<FocusRingProps> = ({ children, ...props }) => (
  <Box
    sx={{
      '&:focus-within': {
        outline: `2px solid ${DESIGN_TOKENS.colors.focus.ring}`,
        outlineOffset: '2px',
        borderRadius: DESIGN_TOKENS.shape.borderRadius.sm
      }
    }}
    {...props}
  >
    {children}
  </Box>
);

export default LayoutUtils;

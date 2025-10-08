/**
 * Responsive Design System - Mobile-optimized layouts and breakpoints
 *
 * This module provides:
 * - Standardized breakpoints for responsive design
 * - Mobile-first utility functions
 * - Responsive spacing and sizing utilities
 * - Component-specific responsive patterns
 */

import { useTheme, useMediaQuery } from '@mui/material';
import { SEMANTIC_SPACING } from './spacingSystem.js';

/**
 * Standard Material Design Breakpoints
 */
export const BREAKPOINTS = {
  xs: 0,     // Extra small devices (phones)
  sm: 600,   // Small devices (large phones)
  md: 900,   // Medium devices (tablets)
  lg: 1200,  // Large devices (desktops)
  xl: 1536   // Extra large devices (large desktops)
};

/**
 * Responsive Spacing - Mobile-first approach
 */
export const RESPONSIVE_SPACING = {
  // Container padding adjusts based on screen size
  containerPadding: {
    xs: SEMANTIC_SPACING.COMPONENT_SPACING,     // 16px on mobile
    sm: SEMANTIC_SPACING.SECTION_SPACING,      // 24px on tablet+
    md: SEMANTIC_SPACING.LAYOUT_SPACING        // 32px on desktop+
  },

  // Section spacing scales with screen size
  sectionSpacing: {
    xs: SEMANTIC_SPACING.COMPONENT_SPACING,     // 16px on mobile
    sm: SEMANTIC_SPACING.COMPONENT_SPACING,     // 16px on tablet
    md: SEMANTIC_SPACING.SECTION_SPACING       // 24px on desktop+
  },

  // Grid spacing optimized for different screens
  gridSpacing: {
    xs: 2,    // 16px on mobile
    sm: 3,    // 24px on tablet+
    md: 4     // 32px on desktop+
  }
};

/**
 * Responsive Grid Patterns
 */
export const RESPONSIVE_GRID = {
  // Dashboard cards - responsive columns
  dashboardCards: {
    xs: 12,   // Full width on mobile
    sm: 6,    // 2 columns on tablet
    md: 4,    // 3 columns on desktop
    lg: 3     // 4 columns on large desktop
  },

  // Service cards - 2-column max on mobile
  serviceCards: {
    xs: 12,   // Full width on small mobile
    sm: 6,    // 2 columns on larger mobile+
    md: 4,    // 3 columns on tablet
    lg: 3     // 4 columns on desktop
  },

  // Analytics widgets
  analyticsWidgets: {
    xs: 12,   // Full width on mobile
    sm: 12,   // Full width on tablet
    md: 6,    // 2 columns on desktop
    lg: 4     // 3 columns on large desktop
  },

  // Two-column layout (main content + sidebar)
  mainContent: {
    xs: 12,   // Full width on mobile
    md: 8     // 2/3 width on desktop
  },

  sidebar: {
    xs: 12,   // Full width on mobile (stacked)
    md: 4     // 1/3 width on desktop
  }
};

/**
 * Responsive Typography
 */
export const RESPONSIVE_TYPOGRAPHY = {
  pageTitle: {
    fontSize: {
      xs: '2rem',    // 32px on mobile
      sm: '2.5rem',  // 40px on tablet
      md: '3rem'     // 48px on desktop
    }
  },

  sectionHeader: {
    fontSize: {
      xs: '1.5rem',  // 24px on mobile
      sm: '1.75rem', // 28px on tablet
      md: '2rem'     // 32px on desktop
    }
  },

  cardTitle: {
    fontSize: {
      xs: '1rem',    // 16px on mobile
      sm: '1.125rem', // 18px on tablet+
    }
  }
};

/**
 * Custom Responsive Hooks
 */
export const useResponsive = () => {
  const theme = useTheme();

  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.between('sm', 'md'));
  const isDesktop = useMediaQuery(theme.breakpoints.up('md'));
  const isLargeScreen = useMediaQuery(theme.breakpoints.up('lg'));

  return {
    isMobile,
    isTablet,
    isDesktop,
    isLargeScreen,

    // Responsive values getter
    getValue: (responsiveObj) => {
      if (isLargeScreen && responsiveObj.lg !== undefined) return responsiveObj.lg;
      if (isDesktop && responsiveObj.md !== undefined) return responsiveObj.md;
      if (isTablet && responsiveObj.sm !== undefined) return responsiveObj.sm;
      return responsiveObj.xs;
    }
  };
};

/**
 * Responsive Container Utilities
 */
export const getResponsiveContainerProps = (responsive) => {
  return {
    sx: {
      px: responsive.getValue(RESPONSIVE_SPACING.containerPadding),
      py: responsive.getValue(RESPONSIVE_SPACING.sectionSpacing)
    }
  };
};

/**
 * Responsive Grid Props Generator
 */
export const getResponsiveGridProps = (pattern) => {
  return {
    xs: pattern.xs,
    sm: pattern.sm,
    md: pattern.md,
    lg: pattern.lg
  };
};

/**
 * Mobile-First Component Patterns
 */
export const MOBILE_PATTERNS = {
  // Stack navigation on mobile, horizontal on desktop
  navigation: {
    mobile: {
      direction: 'column',
      spacing: 1,
      alignItems: 'stretch'
    },
    desktop: {
      direction: 'row',
      spacing: 2,
      alignItems: 'center'
    }
  },

  // Action buttons - full width on mobile
  actionButtons: {
    mobile: {
      fullWidth: true,
      size: 'large',
      sx: { mb: 2 }
    },
    desktop: {
      fullWidth: false,
      size: 'medium',
      sx: { mr: 2 }
    }
  },

  // Cards - different padding and margins
  cards: {
    mobile: {
      sx: {
        mx: 1,
        my: 2,
        borderRadius: 2
      }
    },
    desktop: {
      sx: {
        mx: 0,
        my: 3,
        borderRadius: 3
      }
    }
  }
};

/**
 * Responsive Helper Utilities
 * Note: These functions should be called inside React components where hooks are available
 */
export const createResponsiveBoxProps = (responsive, pattern = 'default') => {
  switch (pattern) {
    case 'container':
      return getResponsiveContainerProps(responsive);
    case 'section':
      return {
        sx: {
          mb: responsive.getValue(RESPONSIVE_SPACING.sectionSpacing)
        }
      };
    default:
      return {};
  }
};

/**
 * Export everything as a cohesive responsive system
 */
export const ResponsiveSystem = {
  breakpoints: BREAKPOINTS,
  spacing: RESPONSIVE_SPACING,
  grid: RESPONSIVE_GRID,
  typography: RESPONSIVE_TYPOGRAPHY,
  patterns: MOBILE_PATTERNS,
  useResponsive,
  getResponsiveContainerProps,
  getResponsiveGridProps,
  createResponsiveBoxProps
};

export default ResponsiveSystem;

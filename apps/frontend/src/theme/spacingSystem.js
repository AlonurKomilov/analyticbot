/**
 * Spacing System - Standardized spacing tokens and utilities
 *
 * This module provides:
 * - Consistent spacing scale based on 8px grid system
 * - Responsive spacing utilities
 * - Typography spacing tokens
 * - Component-specific spacing constants
 */

// Base spacing unit (8px)
export const SPACING_UNIT = 8;

/**
 * Spacing Scale - Based on Material Design 8px grid
 * Each unit represents 8px (0.5rem at 16px base font size)
 */
export const SPACING_SCALE = {
  // Micro spacing (0-2px)
  xxs: 0.25,    // 2px

  // Small spacing (4-8px)
  xs: 0.5,      // 4px
  sm: 1,        // 8px

  // Medium spacing (12-24px)
  md: 1.5,      // 12px
  lg: 2,        // 16px
  xl: 3,        // 24px

  // Large spacing (32-64px)
  xxl: 4,       // 32px
  xxxl: 6,      // 48px
  xxxxl: 8,     // 64px
};

/**
 * Semantic Spacing - Context-specific spacing values
 */
export const SEMANTIC_SPACING = {
  // Component internal spacing
  component: {
    padding: SPACING_SCALE.lg,        // 16px
    paddingSmall: SPACING_SCALE.sm,   // 8px
    paddingLarge: SPACING_SCALE.xl,   // 24px
  },

  // Layout spacing
  layout: {
    containerPadding: SPACING_SCALE.xl,   // 24px
    sectionGap: SPACING_SCALE.xxl,        // 32px
    pageMargin: SPACING_SCALE.xxxl,       // 48px
  },

  // Typography spacing
  typography: {
    paragraphSpacing: SPACING_SCALE.lg,   // 16px
    headingSpacing: SPACING_SCALE.xl,     // 24px
    listItemSpacing: SPACING_SCALE.xs,    // 4px
  },

  // UI element spacing
  ui: {
    buttonGap: SPACING_SCALE.sm,          // 8px
    inputSpacing: SPACING_SCALE.md,       // 12px
    cardPadding: SPACING_SCALE.xl,        // 24px
    dialogPadding: SPACING_SCALE.xl,      // 24px
  },

  // Grid and flex spacing
  grid: {
    gutters: SPACING_SCALE.xl,            // 24px
    itemGap: SPACING_SCALE.lg,            // 16px
    columnGap: SPACING_SCALE.lg,          // 16px
  },

  // Typography and content spacing constants
  SECTION_SPACING: SPACING_SCALE.xxl,     // 32px - Major section spacing
  COMPONENT_SPACING: SPACING_SCALE.xl,    // 24px - Component spacing
  ELEMENT_SPACING: SPACING_SCALE.lg,      // 16px - Element spacing
  TEXT_SPACING: SPACING_SCALE.md,         // 12px - Text spacing
  BORDER_RADIUS: SPACING_SCALE.sm,        // 8px - Standard border radius

  // Card and UI specific spacing (for backward compatibility)
  CARD_PADDING: SPACING_SCALE.xl,         // 24px
  GRID_SPACING: SPACING_SCALE.xl,         // 24px
  LAYOUT_SPACING: SPACING_SCALE.xxl       // 32px
};

/**
 * Responsive Spacing - Breakpoint-based spacing adjustments
 */
export const RESPONSIVE_SPACING = {
  container: {
    xs: SPACING_SCALE.lg,    // 16px on mobile
    sm: SPACING_SCALE.xl,    // 24px on tablet
    md: SPACING_SCALE.xxl,   // 32px on desktop
    lg: SPACING_SCALE.xxxl,  // 48px on large screens
  },

  section: {
    xs: SPACING_SCALE.xl,    // 24px on mobile
    sm: SPACING_SCALE.xxl,   // 32px on tablet
    md: SPACING_SCALE.xxxl,  // 48px on desktop
  }
};

/**
 * Spacing Utilities - Helper functions for consistent spacing
 */
export const spacingUtils = {
  /**
   * Get spacing value from scale
   */
  space: (scale) => SPACING_SCALE[scale],

  /**
   * Get semantic spacing
   */
  semantic: (category, property) => SEMANTIC_SPACING[category]?.[property],

  /**
   * Get responsive spacing object for sx prop
   */
  responsive: (spacingConfig) => ({
    xs: spacingConfig.xs || spacingConfig,
    sm: spacingConfig.sm || spacingConfig,
    md: spacingConfig.md || spacingConfig,
    lg: spacingConfig.lg || spacingConfig,
  }),

  /**
   * Convert hardcoded pixel values to spacing scale
   */
  fromPixels: (pixels) => {
    const unit = pixels / SPACING_UNIT;
    // Find closest spacing scale value
    const scales = Object.values(SPACING_SCALE);
    const closest = scales.reduce((prev, curr) =>
      Math.abs(curr - unit) < Math.abs(prev - unit) ? curr : prev
    );
    return closest;
  },

  /**
   * Common spacing patterns
   */
  patterns: {
    // Stack components vertically
    stack: (gap = 'lg') => ({ display: 'flex', flexDirection: 'column', gap: SPACING_SCALE[gap] }),

    // Horizontal row with gaps
    row: (gap = 'lg') => ({ display: 'flex', gap: SPACING_SCALE[gap], alignItems: 'center' }),

    // Card-like padding
    cardPadding: () => ({ p: SEMANTIC_SPACING.ui.cardPadding }),

    // Form field spacing
    fieldSpacing: () => ({ mb: SEMANTIC_SPACING.ui.inputSpacing }),

    // Container margins
    containerSpacing: () => ({
      mx: 'auto',
      px: {
        xs: RESPONSIVE_SPACING.container.xs,
        sm: RESPONSIVE_SPACING.container.sm,
        md: RESPONSIVE_SPACING.container.md
      }
    }),
  }
};

/**
 * Migration helpers - Convert common hardcoded values
 */
export const MIGRATION_MAP = {
  // Common hardcoded values to spacing scale mapping
  '2px': SPACING_SCALE.xxs,
  '4px': SPACING_SCALE.xs,
  '8px': SPACING_SCALE.sm,
  '12px': SPACING_SCALE.md,
  '16px': SPACING_SCALE.lg,
  '24px': SPACING_SCALE.xl,
  '32px': SPACING_SCALE.xxl,
  '48px': SPACING_SCALE.xxxl,
  '64px': SPACING_SCALE.xxxxl,

  // Common decimal values
  0.5: SPACING_SCALE.xs,
  1: SPACING_SCALE.sm,
  1.5: SPACING_SCALE.md,
  2: SPACING_SCALE.lg,
  3: SPACING_SCALE.xl,
  4: SPACING_SCALE.xxl,
  6: SPACING_SCALE.xxxl,
  8: SPACING_SCALE.xxxxl,
};

export default {
  SPACING_SCALE,
  SEMANTIC_SPACING,
  RESPONSIVE_SPACING,
  spacingUtils,
  MIGRATION_MAP
};

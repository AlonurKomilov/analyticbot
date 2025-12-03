/**
 * Design Tokens System
 *
 * Centralized design tokens for consistent spacing, sizing, colors, shadows, and animations.
 * These tokens replace inline sx props and ensure design consistency across all components.
 *
 * Usage:
 * import { spacing, colors, shadows } from '@/theme/tokens';
 *
 * sx={{ padding: spacing.lg, color: colors.text.primary, boxShadow: shadows.md }}
 */

// =============================================================================
// SPACING TOKENS (8px base unit system)
// =============================================================================
export const spacing = {
  // Base units
  xxs: '4px',   // 0.5x base - minimal spacing, icon gaps
  xs: '8px',    // 1x base - compact padding
  sm: '12px',   // 1.5x base - small padding, button padding
  md: '16px',   // 2x base - standard padding
  lg: '24px',   // 3x base - section padding
  xl: '32px',   // 4x base - large section padding
  xxl: '48px',  // 6x base - major section spacing

  // Semantic spacing
  section: '32px',      // Between major sections
  component: '16px',    // Between components
  element: '8px',       // Between elements within a component
  inline: '4px',        // Between inline elements (badges, icons)
} as const;

// =============================================================================
// SIZING TOKENS
// =============================================================================
export const sizing = {
  // Touch targets (mobile-first)
  touchTarget: {
    min: '44px',        // Minimum touch target (WCAG AAA)
    comfortable: '48px', // Comfortable touch target
    large: '56px',      // Large touch target
  },

  // Input heights
  input: {
    small: '36px',
    medium: '44px',
    large: '52px',
  },

  // Button heights
  button: {
    small: '36px',
    medium: '44px',
    large: '52px',
  },

  // Icon sizes
  icon: {
    xs: '16px',
    sm: '20px',
    md: '24px',
    lg: '32px',
    xl: '48px',
  },

  // Container widths
  container: {
    xs: '400px',
    sm: '600px',
    md: '900px',
    lg: '1200px',
    xl: '1440px',
    full: '100%',
  },

  // Dialog widths
  dialog: {
    xs: '400px',
    sm: '600px',
    md: '800px',
    lg: '1000px',
    xl: '1200px',
  },
} as const;

// =============================================================================
// COLOR TOKENS (Extended from theme.ts)
// =============================================================================
export const colors = {
  // Brand colors
  primary: {
    main: '#58a6ff',
    light: '#79c0ff',
    dark: '#388bfd',
    contrast: '#ffffff',
  },
  secondary: {
    main: '#f85149',
    light: '#ff7b7b',
    dark: '#da3633',
    contrast: '#ffffff',
  },

  // Semantic colors
  success: {
    main: '#3fb950',
    light: '#56d364',
    dark: '#238636',
    bg: 'rgba(63, 185, 80, 0.1)',
  },
  warning: {
    main: '#f2cc60',
    light: '#ffdf5d',
    dark: '#e3b341',
    bg: 'rgba(242, 204, 96, 0.1)',
  },
  error: {
    main: '#f85149',
    light: '#ff7b7b',
    dark: '#da3633',
    bg: 'rgba(248, 81, 73, 0.1)',
  },
  info: {
    main: '#58a6ff',
    light: '#79c0ff',
    dark: '#388bfd',
    bg: 'rgba(88, 166, 255, 0.1)',
  },

  // Background colors
  background: {
    default: '#0d1117',
    paper: '#161b22',
    elevated: '#1c2128',
    overlay: 'rgba(13, 17, 23, 0.8)',
  },

  // Text colors
  text: {
    primary: '#f0f6fc',
    secondary: '#8b949e',
    disabled: '#484f58',
    inverse: '#0d1117',
  },

  // Border & divider colors
  border: {
    subtle: '#21262d',
    default: '#30363d',
    emphasis: '#6e7681',
    focus: '#58a6ff',
  },

  // State colors
  state: {
    hover: 'rgba(177, 186, 196, 0.08)',
    active: 'rgba(177, 186, 196, 0.12)',
    selected: 'rgba(88, 166, 255, 0.15)',
    disabled: 'rgba(139, 148, 158, 0.3)',
  },
} as const;

// =============================================================================
// SHADOW TOKENS (Elevation system)
// =============================================================================
export const shadows = {
  none: 'none',
  xs: '0 1px 2px 0 rgba(0, 0, 0, 0.3)',
  sm: '0 1px 3px 0 rgba(0, 0, 0, 0.4), 0 1px 2px -1px rgba(0, 0, 0, 0.4)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -2px rgba(0, 0, 0, 0.4)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.5), 0 4px 6px -4px rgba(0, 0, 0, 0.5)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5)',
  xxl: '0 25px 50px -12px rgba(0, 0, 0, 0.6)',

  // Semantic shadows
  card: '0 1px 3px 0 rgba(0, 0, 0, 0.4), 0 1px 2px -1px rgba(0, 0, 0, 0.4)',
  dialog: '0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5)',
  dropdown: '0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -4px rgba(0, 0, 0, 0.4)',
  focus: '0 0 0 3px rgba(88, 166, 255, 0.3)',
} as const;

// =============================================================================
// BORDER RADIUS TOKENS
// =============================================================================
export const radius = {
  none: '0',
  xs: '2px',
  sm: '4px',
  md: '6px',
  lg: '8px',
  xl: '12px',
  xxl: '16px',
  full: '9999px',

  // Semantic radius
  button: '6px',
  input: '6px',
  card: '8px',
  dialog: '12px',
  badge: '9999px',
} as const;

// =============================================================================
// ANIMATION TOKENS (Duration & Easing)
// =============================================================================
export const animation = {
  // Durations
  duration: {
    instant: '50ms',
    fast: '150ms',
    normal: '250ms',
    slow: '350ms',
    slower: '500ms',
  },

  // Easing functions
  easing: {
    linear: 'linear',
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    sharp: 'cubic-bezier(0.4, 0, 0.6, 1)',
  },

  // Common transitions
  transition: {
    fast: 'all 150ms cubic-bezier(0.4, 0, 0.2, 1)',
    normal: 'all 250ms cubic-bezier(0.4, 0, 0.2, 1)',
    slow: 'all 350ms cubic-bezier(0.4, 0, 0.2, 1)',
  },
} as const;

// =============================================================================
// TYPOGRAPHY TOKENS (Font sizes, weights, line heights)
// =============================================================================
export const typography = {
  // Font families
  fontFamily: {
    default: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif',
    mono: '"SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas, monospace',
  },

  // Font sizes
  fontSize: {
    xs: '0.75rem',    // 12px
    sm: '0.875rem',   // 14px
    md: '1rem',       // 16px
    lg: '1.125rem',   // 18px
    xl: '1.25rem',    // 20px
    xxl: '1.5rem',    // 24px
    xxxl: '2rem',     // 32px
  },

  // Font weights
  fontWeight: {
    light: 300,
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },

  // Line heights
  lineHeight: {
    tight: 1.25,
    snug: 1.375,
    normal: 1.5,
    relaxed: 1.625,
    loose: 1.75,
  },

  // Letter spacing
  letterSpacing: {
    tighter: '-0.05em',
    tight: '-0.025em',
    normal: '0',
    wide: '0.025em',
    wider: '0.05em',
  },
} as const;

// =============================================================================
// Z-INDEX TOKENS (Layering system)
// =============================================================================
export const zIndex = {
  base: 0,
  dropdown: 1000,
  sticky: 1100,
  fixed: 1200,
  backdrop: 1300,
  drawer: 1400,
  modal: 1500,
  snackbar: 1600,
  tooltip: 1700,
} as const;

// =============================================================================
// BREAKPOINT TOKENS (Responsive design)
// =============================================================================
const breakpointValues = {
  xs: 0,
  sm: 600,
  md: 900,
  lg: 1200,
  xl: 1536,
} as const;

export const breakpoints = {
  values: breakpointValues,

  // Media query helpers
  up: (breakpoint: keyof typeof breakpointValues) =>
    `@media (min-width: ${breakpointValues[breakpoint]}px)`,

  down: (breakpoint: keyof typeof breakpointValues) =>
    `@media (max-width: ${breakpointValues[breakpoint] - 0.05}px)`,

  between: (start: keyof typeof breakpointValues, end: keyof typeof breakpointValues) =>
    `@media (min-width: ${breakpointValues[start]}px) and (max-width: ${breakpointValues[end] - 0.05}px)`,
} as const;

// =============================================================================
// GRID TOKENS (Layout system)
// =============================================================================
export const grid = {
  // Grid columns
  columns: {
    mobile: 4,
    tablet: 8,
    desktop: 12,
  },

  // Grid gaps
  gap: {
    xs: spacing.xs,
    sm: spacing.sm,
    md: spacing.md,
    lg: spacing.lg,
    xl: spacing.xl,
  },

  // Container padding
  containerPadding: {
    mobile: spacing.md,
    tablet: spacing.lg,
    desktop: spacing.xl,
  },
} as const;

// =============================================================================
// UTILITY: Token Usage Examples
// =============================================================================
export const tokenExamples = {
  // Card styling
  card: {
    padding: spacing.lg,
    borderRadius: radius.card,
    boxShadow: shadows.card,
    backgroundColor: colors.background.paper,
  },

  // Button styling
  button: {
    padding: `${spacing.sm} ${spacing.md}`,
    minHeight: sizing.button.medium,
    borderRadius: radius.button,
    transition: animation.transition.fast,
  },

  // Input styling
  input: {
    height: sizing.input.medium,
    padding: `0 ${spacing.md}`,
    borderRadius: radius.input,
    fontSize: typography.fontSize.md,
  },

  // Dialog styling
  dialog: {
    borderRadius: radius.dialog,
    boxShadow: shadows.dialog,
    maxWidth: sizing.dialog.md,
    padding: spacing.xl,
  },
} as const;

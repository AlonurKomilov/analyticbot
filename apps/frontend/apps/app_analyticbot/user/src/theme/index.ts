/**
 * Theme System Entry Point
 *
 * Exports the MUI theme and design tokens for use throughout the application.
 *
 * Usage:
 * import theme from '@/theme';
 * import { spacing, colors, shadows } from '@/theme/tokens';
 */

// Re-export the MUI theme as default
import theme from '../theme';
export default theme;
export { theme };

// Re-export all design tokens
export {
  spacing,
  sizing,
  colors,
  shadows,
  radius,
  animation,
  typography,
  zIndex,
  breakpoints,
  grid,
  tokenExamples,
} from './tokens';

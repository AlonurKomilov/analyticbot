/**
 * 🔄 Loading Spinner Component
 *
 * A flexible loading spinner component used throughout the application.
 * Supports various sizes, colors, and can be centered within its container.
 *
 * @component
 * @example
 * ```tsx
 * // Basic usage
 * <LoadingSpinner />
 *
 * // Large centered spinner
 * <LoadingSpinner size={48} centered />
 *
 * // Custom color
 * <LoadingSpinner color="secondary" />
 * ```
 */

import React from 'react';
import { CircularProgress, Box, SxProps, Theme } from '@mui/material';

/**
 * LoadingSpinner component props
 */
export interface LoadingSpinnerPropsLocal {
  /** Size of the spinner in pixels */
  size?: number;
  /** Color variant of the spinner */
  color?: 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' | 'inherit';
  /** Whether to center the spinner in its container */
  centered?: boolean;
  /** Additional MUI sx prop for custom styling */
  sx?: SxProps<Theme>;
}

/**
 * LoadingSpinner - Displays a circular progress indicator
 *
 * Used throughout the application to indicate loading states.
 * Can be configured with different sizes and colors, and optionally centered.
 */
const LoadingSpinner: React.FC<LoadingSpinnerPropsLocal> = ({
  size = 24,
  color = 'primary',
  centered = false,
  sx = {}
}) => {
  const spinner = <CircularProgress size={size} color={color} sx={sx} />;

  if (centered) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100px',
          ...sx
        }}
      >
        {spinner}
      </Box>
    );
  }

  return spinner;
};

export default LoadingSpinner;

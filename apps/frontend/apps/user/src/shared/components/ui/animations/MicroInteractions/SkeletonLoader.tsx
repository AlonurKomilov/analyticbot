/**
 * Skeleton Loader Component
 */
import React from 'react';
import { Box } from '@mui/material';
import { DESIGN_TOKENS } from '@theme/designTokens';
import { skeletonPulse, skeletonWave } from './keyframes';
import type { SkeletonLoaderProps } from './types';

export const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({
  width = '100%',
  height = '20px',
  variant = 'rectangular',
  animation = 'pulse',
}) => {
  return (
    <Box
      sx={{
        width,
        height,
        backgroundColor: 'grey.300',
        borderRadius:
          variant === 'circular' ? '50%' : DESIGN_TOKENS.layout.borderRadius.sm,
        animation:
          animation === 'pulse'
            ? `${skeletonPulse} 1.5s ease-in-out infinite`
            : `${skeletonWave} 2s ease-in-out infinite`,
        position: 'relative',
        overflow: 'hidden',

        ...(animation === 'wave' && {
          '&::after': {
            content: '""',
            position: 'absolute',
            top: 0,
            right: 0,
            bottom: 0,
            left: 0,
            background:
              'linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)',
            animation: `${skeletonWave} 2s ease-in-out infinite`,
          },
        }),
      }}
    />
  );
};

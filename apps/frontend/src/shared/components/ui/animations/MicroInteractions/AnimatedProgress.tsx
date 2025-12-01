/**
 * Animated Progress Components
 */
import React, { useState, useEffect } from 'react';
import { Box, CircularProgress, LinearProgress } from '@mui/material';
import { DESIGN_TOKENS } from '@theme/designTokens';
import type { AnimatedProgressProps } from './types';

export const AnimatedProgress: React.FC<AnimatedProgressProps> = ({
  value = 0,
  type = 'linear',
  showValue = false,
  color = 'primary',
}) => {
  const [animatedValue, setAnimatedValue] = useState<number>(0);

  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedValue(value);
    }, 100);
    return () => clearTimeout(timer);
  }, [value]);

  if (type === 'circular') {
    return (
      <Box sx={{ position: 'relative', display: 'inline-flex' }}>
        <CircularProgress
          variant="determinate"
          value={animatedValue}
          color={color}
          sx={{
            transition: 'all 0.8s ease-in-out',
          }}
        />
        {showValue && (
          <Box
            sx={{
              top: 0,
              left: 0,
              bottom: 0,
              right: 0,
              position: 'absolute',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Box sx={{ fontSize: '0.875rem', fontWeight: 500 }}>
              {`${Math.round(animatedValue)}%`}
            </Box>
          </Box>
        )}
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%' }}>
      <LinearProgress
        variant="determinate"
        value={animatedValue}
        color={color}
        sx={{
          height: 8,
          borderRadius: DESIGN_TOKENS.layout.borderRadius.sm,
          transition: 'all 0.8s ease-in-out',
          '& .MuiLinearProgress-bar': {
            borderRadius: DESIGN_TOKENS.layout.borderRadius.sm,
          },
        }}
      />
      {showValue && (
        <Box sx={{ mt: 1, textAlign: 'center', fontSize: '0.875rem' }}>
          {`${Math.round(animatedValue)}%`}
        </Box>
      )}
    </Box>
  );
};

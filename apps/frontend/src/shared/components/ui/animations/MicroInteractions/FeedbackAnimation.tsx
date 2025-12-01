/**
 * Feedback Animation Component
 */
import React, { useState, useEffect } from 'react';
import { Box, Zoom } from '@mui/material';
import { bounceAnimation, shakeAnimation, pulseAnimation } from './keyframes';
import type { FeedbackAnimationProps, FeedbackType } from './types';

export const FeedbackAnimation: React.FC<FeedbackAnimationProps> = ({
  type = 'success',
  show = false,
  children,
  duration = 2000,
}) => {
  const [isVisible, setIsVisible] = useState<boolean>(false);

  useEffect(() => {
    if (show) {
      setIsVisible(true);
      const timer = setTimeout(() => setIsVisible(false), duration);
      return () => clearTimeout(timer);
    }
    return undefined;
  }, [show, duration]);

  const getAnimation = (): any => {
    const animations: Record<FeedbackType, any> = {
      success: bounceAnimation,
      error: shakeAnimation,
      pulse: pulseAnimation,
    };
    return animations[type] || bounceAnimation;
  };

  return (
    <Zoom in={isVisible} timeout={300}>
      <Box
        sx={{
          animation: isVisible ? `${getAnimation()} 0.6s ease-in-out` : 'none',
        }}
      >
        {children}
      </Box>
    </Zoom>
  );
};

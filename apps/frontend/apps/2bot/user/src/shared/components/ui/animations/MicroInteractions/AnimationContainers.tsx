/**
 * Floating and Staggered Animation Components
 */
import React, { useState, useEffect } from 'react';
import { Box } from '@mui/material';
import { createFloatAnimation, slideInAnimation, bounceAnimation } from './keyframes';
import type { FloatingElementProps, StaggeredAnimationProps, AnimationType } from './types';

/**
 * Floating Animation Component
 */
export const FloatingElement: React.FC<FloatingElementProps> = ({
  children,
  duration = 3,
  delay = 0,
}) => {
  const floatAnimation = createFloatAnimation(10);

  return (
    <Box
      sx={{
        animation: `${floatAnimation} ${duration}s ease-in-out infinite`,
        animationDelay: `${delay}s`,
      }}
    >
      {children}
    </Box>
  );
};

/**
 * Staggered Animation Container
 */
export const StaggeredAnimation: React.FC<StaggeredAnimationProps> = ({
  children,
  animation = 'slideIn',
  delay = 100,
  duration = 300,
}) => {
  const [isVisible, setIsVisible] = useState<boolean>(false);

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), 50);
    return () => clearTimeout(timer);
  }, []);

  const getAnimation = (index: number): string => {
    const animations: Record<AnimationType, string> = {
      slideIn: `${slideInAnimation} ${duration}ms ease-out ${index * delay}ms both`,
      fadeIn: `fadeIn ${duration}ms ease-out ${index * delay}ms both`,
      bounce: `${bounceAnimation} ${duration}ms ease-out ${index * delay}ms both`,
    };
    return animations[animation] || animations.slideIn;
  };

  return (
    <>
      {React.Children.map(children, (child, index) => (
        <Box
          sx={{
            animation: isVisible ? getAnimation(index) : 'none',
            opacity: isVisible ? 1 : 0,
          }}
        >
          {child}
        </Box>
      ))}
    </>
  );
};

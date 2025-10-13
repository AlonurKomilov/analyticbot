/**
 * Micro-interactions System
 *
 * Subtle animations, hover effects, and feedback mechanisms to enhance UX:
 * - Smooth transitions and animations
 * - Interactive hover states
 * - Loading feedback
 * - Success/error feedback
 * - Touch feedback for mobile
 * - Focus animations
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Fade,
  Grow,
  Slide,
  Zoom,
  Collapse,
  CircularProgress,
  LinearProgress,
  keyframes,
  styled
} from '@mui/material';
import { DESIGN_TOKENS } from '../../theme/designTokens.js';

// Custom keyframe animations
const pulseAnimation = keyframes`
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.05);
    opacity: 0.8;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
`;

const shakeAnimation = keyframes`
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-4px); }
  75% { transform: translateX(4px); }
`;

const bounceAnimation = keyframes`
  0%, 20%, 53%, 80%, 100% {
    transform: translate3d(0, 0, 0);
  }
  40%, 43% {
    transform: translate3d(0, -8px, 0);
  }
  70% {
    transform: translate3d(0, -4px, 0);
  }
  90% {
    transform: translate3d(0, -2px, 0);
  }
`;

const slideInAnimation = keyframes`
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
`;

const rippleAnimation = keyframes`
  0% {
    transform: scale(0);
    opacity: 0.6;
  }
  100% {
    transform: scale(4);
    opacity: 0;
  }
`;

/**
 * Interactive Card with Hover Effects
 */
export const InteractiveCard = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'interactive' && prop !== 'hoverEffect'
})(({ theme, interactive = true, hoverEffect = 'lift' }) => ({
  borderRadius: DESIGN_TOKENS.layout.borderRadius.md,
  border: `1px solid ${theme.palette.divider}`,
  backgroundColor: theme.palette.background.paper,
  transition: 'all 0.2s ease-in-out',
  cursor: interactive ? 'pointer' : 'default',

  ...(interactive && {
    '&:hover': {
      ...(hoverEffect === 'lift' && {
        transform: 'translateY(-4px)',
        boxShadow: '0 8px 24px rgba(0, 0, 0, 0.12)',
        borderColor: theme.palette.primary.main
      }),
      ...(hoverEffect === 'glow' && {
        boxShadow: `0 0 0 2px ${theme.palette.primary.main}20`,
        borderColor: theme.palette.primary.main
      }),
      ...(hoverEffect === 'scale' && {
        transform: 'scale(1.02)'
      })
    },

    '&:active': {
      transform: hoverEffect === 'lift' ? 'translateY(-2px)' : 'scale(0.98)',
      transition: 'all 0.1s ease-in-out'
    }
  })
}));

/**
 * Animated Button with Ripple Effect
 */
export const AnimatedButton = styled(Box)(({ theme, variant = 'contained', disabled = false }) => ({
  position: 'relative',
  overflow: 'hidden',
  borderRadius: DESIGN_TOKENS.layout.borderRadius.md,
  padding: '12px 24px',
  fontSize: '1rem',
  fontWeight: 500,
  cursor: disabled ? 'not-allowed' : 'pointer',
  opacity: disabled ? 0.6 : 1,
  transition: 'all 0.2s ease-in-out',
  display: 'inline-flex',
  alignItems: 'center',
  justifyContent: 'center',
  minHeight: '44px',

  // Variant styles
  ...(variant === 'contained' && {
    backgroundColor: theme.palette.primary.main,
    color: theme.palette.primary.contrastText,
    '&:hover': !disabled && {
      backgroundColor: theme.palette.primary.dark,
      transform: 'translateY(-1px)',
      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)'
    }
  }),

  ...(variant === 'outlined' && {
    backgroundColor: 'transparent',
    color: theme.palette.primary.main,
    border: `1px solid ${theme.palette.primary.main}`,
    '&:hover': !disabled && {
      backgroundColor: theme.palette.primary.main,
      color: theme.palette.primary.contrastText,
      transform: 'translateY(-1px)'
    }
  }),

  // Ripple effect container
  '&::before': {
    content: '""',
    position: 'absolute',
    top: '50%',
    left: '50%',
    width: 0,
    height: 0,
    borderRadius: '50%',
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    transform: 'translate(-50%, -50%)',
    transition: 'width 0.6s, height 0.6s'
  },

  '&:active::before': !disabled && {
    width: '300px',
    height: '300px'
  }
}));

/**
 * Floating Animation Component
 */
export const FloatingElement = ({ children, duration = 3, delay = 0 }) => {
  const floatAnimation = keyframes`
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
  `;

  return (
    <Box
      sx={{
        animation: `${floatAnimation} ${duration}s ease-in-out infinite`,
        animationDelay: `${delay}s`
      }}
    >
      {children}
    </Box>
  );
};

/**
 * Staggered Animation Container
 */
export const StaggeredAnimation = ({
  children,
  animation = 'slideIn',
  delay = 100,
  duration = 300
}) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), 50);
    return () => clearTimeout(timer);
  }, []);

  const getAnimation = (index) => {
    const animations = {
      slideIn: `${slideInAnimation} ${duration}ms ease-out ${index * delay}ms both`,
      fadeIn: `fadeIn ${duration}ms ease-out ${index * delay}ms both`,
      bounce: `${bounceAnimation} ${duration}ms ease-out ${index * delay}ms both`
    };
    return animations[animation] || animations.slideIn;
  };

  return (
    <>
      {React.Children.map(children, (child, index) => (
        <Box
          sx={{
            animation: isVisible ? getAnimation(index) : 'none',
            opacity: isVisible ? 1 : 0
          }}
        >
          {child}
        </Box>
      ))}
    </>
  );
};

/**
 * Loading State with Skeleton Animation
 */
export const SkeletonLoader = ({
  width = '100%',
  height = '20px',
  variant = 'rectangular',
  animation = 'pulse'
}) => {
  const skeletonPulse = keyframes`
    0% { opacity: 1; }
    50% { opacity: 0.4; }
    100% { opacity: 1; }
  `;

  const skeletonWave = keyframes`
    0% { transform: translateX(-100%); }
    50% { transform: translateX(100%); }
    100% { transform: translateX(100%); }
  `;

  return (
    <Box
      sx={{
        width,
        height,
        backgroundColor: 'grey.300',
        borderRadius: variant === 'circular' ? '50%' : DESIGN_TOKENS.layout.borderRadius.sm,
        animation: animation === 'pulse'
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
            background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)',
            animation: `${skeletonWave} 2s ease-in-out infinite`
          }
        })
      }}
    />
  );
};

/**
 * Success/Error Feedback Animation
 */
export const FeedbackAnimation = ({
  type = 'success',
  show = false,
  children,
  duration = 2000
}) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (show) {
      setIsVisible(true);
      const timer = setTimeout(() => setIsVisible(false), duration);
      return () => clearTimeout(timer);
    }
  }, [show, duration]);

  const getAnimation = () => {
    switch (type) {
      case 'success':
        return bounceAnimation;
      case 'error':
        return shakeAnimation;
      case 'pulse':
        return pulseAnimation;
      default:
        return bounceAnimation;
    }
  };

  return (
    <Zoom in={isVisible} timeout={300}>
      <Box
        sx={{
          animation: isVisible ? `${getAnimation()} 0.6s ease-in-out` : 'none'
        }}
      >
        {children}
      </Box>
    </Zoom>
  );
};

/**
 * Progress Indicator with Animation
 */
export const AnimatedProgress = ({
  value = 0,
  type = 'linear',
  showValue = false,
  color = 'primary'
}) => {
  const [animatedValue, setAnimatedValue] = useState(0);

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
            transition: 'all 0.8s ease-in-out'
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
            borderRadius: DESIGN_TOKENS.layout.borderRadius.sm
          }
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

/**
 * Touch Ripple Effect for Mobile
 */
export const TouchRipple = ({ children, ...props }) => {
  const [ripples, setRipples] = useState([]);

  const addRipple = (event) => {
    const rect = event.currentTarget.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;

    const newRipple = {
      x,
      y,
      size,
      id: Date.now()
    };

    setRipples(prev => [...prev, newRipple]);

    setTimeout(() => {
      setRipples(prev => prev.filter(ripple => ripple.id !== newRipple.id));
    }, 600);
  };

  return (
    <Box
      {...props}
      onTouchStart={addRipple}
      onClick={addRipple}
      sx={{
        position: 'relative',
        overflow: 'hidden',
        ...props.sx
      }}
    >
      {children}
      {ripples.map(ripple => (
        <Box
          key={ripple.id}
          sx={{
            position: 'absolute',
            left: ripple.x,
            top: ripple.y,
            width: ripple.size,
            height: ripple.size,
            borderRadius: '50%',
            backgroundColor: 'rgba(0, 0, 0, 0.2)',
            animation: `${rippleAnimation} 0.6s ease-out`,
            pointerEvents: 'none'
          }}
        />
      ))}
    </Box>
  );
};

export default {
  InteractiveCard,
  AnimatedButton,
  FloatingElement,
  StaggeredAnimation,
  SkeletonLoader,
  FeedbackAnimation,
  AnimatedProgress,
  TouchRipple
};

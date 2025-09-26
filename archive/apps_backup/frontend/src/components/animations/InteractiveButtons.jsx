/**
 * Enhanced Interactive Buttons
 * 
 * Button components with advanced micro-interactions:
 * - Smooth hover animations
 * - Loading states with spinners
 * - Success/error feedback
 * - Touch ripple effects
 * - Accessibility-first design
 */

import React, { useState, useEffect } from 'react';
import { 
  Button as MuiButton,
  IconButton as MuiIconButton,
  Box,
  CircularProgress,
  Fade,
  Zoom
} from '@mui/material';
import {
  Check as CheckIcon,
  Error as ErrorIcon
} from '@mui/icons-material';
import { TouchRipple, FeedbackAnimation } from './MicroInteractions.jsx';
import { DESIGN_TOKENS } from '../../theme/designTokens.js';

/**
 * Enhanced Button with Micro-interactions
 */
export const InteractiveButton = ({ 
  children,
  loading = false,
  success = false,
  error = false,
  variant = 'contained',
  color = 'primary',
  size = 'medium',
  startIcon,
  endIcon,
  onClick,
  disabled = false,
  ripple = true,
  hoverEffect = 'lift',
  loadingText = 'Loading...',
  successText = 'Success!',
  errorText = 'Error',
  resetDelay = 2000,
  ...props
}) => {
  const [internalSuccess, setInternalSuccess] = useState(false);
  const [internalError, setInternalError] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  // Auto-reset success/error states
  useEffect(() => {
    if (success || error) {
      const timer = setTimeout(() => {
        if (success) setInternalSuccess(false);
        if (error) setInternalError(false);
      }, resetDelay);
      return () => clearTimeout(timer);
    }
  }, [success, error, resetDelay]);

  // Update internal states
  useEffect(() => {
    if (success) setInternalSuccess(true);
    if (error) setInternalError(true);
  }, [success, error]);

  const getButtonContent = () => {
    if (loading) {
      return (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <CircularProgress 
            size={16} 
            color="inherit"
            sx={{ 
              animation: 'spin 1s linear infinite'
            }}
          />
          {loadingText}
        </Box>
      );
    }

    if (internalSuccess) {
      return (
        <FeedbackAnimation type="success" show={true}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CheckIcon sx={{ fontSize: 16 }} />
            {successText}
          </Box>
        </FeedbackAnimation>
      );
    }

    if (internalError) {
      return (
        <FeedbackAnimation type="error" show={true}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <ErrorIcon sx={{ fontSize: 16 }} />
            {errorText}
          </Box>
        </FeedbackAnimation>
      );
    }

    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        {startIcon}
        {children}
        {endIcon}
      </Box>
    );
  };

  const getHoverStyles = () => {
    if (disabled || loading) return {};
    
    const hoverStyles = {
      lift: {
        transform: 'translateY(-2px)',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)'
      },
      glow: {
        boxShadow: `0 0 0 2px ${color === 'primary' ? '#58a6ff20' : '#f85149aa'}`
      },
      scale: {
        transform: 'scale(1.05)'
      }
    };
    
    return hoverStyles[hoverEffect] || hoverStyles.lift;
  };

  const ButtonComponent = ripple ? TouchRipple : Box;

  return (
    <ButtonComponent>
      <MuiButton
        variant={variant}
        color={internalSuccess ? 'success' : internalError ? 'error' : color}
        size={size}
        disabled={disabled || loading}
        onClick={onClick}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        sx={{
          minHeight: size === 'small' ? '36px' : size === 'large' ? '52px' : '44px',
          borderRadius: DESIGN_TOKENS.layout.borderRadius.md,
          textTransform: 'none',
          fontWeight: 500,
          transition: 'all 0.2s ease-in-out',
          position: 'relative',
          overflow: 'hidden',
          
          ...(isHovered && getHoverStyles()),
          
          '&:focus-visible': {
            outline: `2px solid ${color === 'primary' ? '#58a6ff' : '#f85149'}`,
            outlineOffset: '2px'
          },
          
          // Touch feedback for mobile
          '@media (hover: none)': {
            '&:active': {
              transform: 'scale(0.98)',
              transition: 'transform 0.1s ease-out'
            }
          },
          
          ...props.sx
        }}
        {...props}
      >
        <Fade in={true} timeout={200}>
          <Box>{getButtonContent()}</Box>
        </Fade>
      </MuiButton>
    </ButtonComponent>
  );
};

/**
 * Enhanced Icon Button with Micro-interactions
 */
export const InteractiveIconButton = ({
  children,
  size = 'medium',
  color = 'primary',
  disabled = false,
  loading = false,
  success = false,
  error = false,
  onClick,
  hoverEffect = 'scale',
  ripple = true,
  tooltip,
  ...props
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);

  useEffect(() => {
    if (success || error) {
      setShowFeedback(true);
      const timer = setTimeout(() => setShowFeedback(false), 1500);
      return () => clearTimeout(timer);
    }
  }, [success, error]);

  const getSize = () => {
    const sizes = {
      small: { width: 36, height: 36 },
      medium: { width: 44, height: 44 },
      large: { width: 52, height: 52 }
    };
    return sizes[size] || sizes.medium;
  };

  const getHoverStyles = () => {
    if (disabled || loading) return {};
    
    const hoverStyles = {
      scale: { transform: 'scale(1.1)' },
      glow: { 
        boxShadow: `0 0 0 2px ${color === 'primary' ? '#58a6ff40' : '#f8514940'}`,
        backgroundColor: `${color === 'primary' ? '#58a6ff' : '#f85149'}10`
      },
      bounce: { 
        animation: 'bounce 0.6s ease-in-out',
        '@keyframes bounce': {
          '0%, 20%, 53%, 80%, 100%': { transform: 'translate3d(0,0,0)' },
          '40%, 43%': { transform: 'translate3d(0,-8px,0)' },
          '70%': { transform: 'translate3d(0,-4px,0)' },
          '90%': { transform: 'translate3d(0,-2px,0)' }
        }
      }
    };
    
    return hoverStyles[hoverEffect] || hoverStyles.scale;
  };

  const getIconContent = () => {
    if (loading) {
      return <CircularProgress size={16} color="inherit" />;
    }

    if (showFeedback && success) {
      return (
        <Zoom in={true} timeout={200}>
          <CheckIcon />
        </Zoom>
      );
    }

    if (showFeedback && error) {
      return (
        <Zoom in={true} timeout={200}>
          <ErrorIcon />
        </Zoom>
      );
    }

    return children;
  };

  const ButtonComponent = ripple ? TouchRipple : Box;

  return (
    <ButtonComponent>
      <MuiIconButton
        color={showFeedback && success ? 'success' : showFeedback && error ? 'error' : color}
        disabled={disabled || loading}
        onClick={onClick}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        title={tooltip}
        sx={{
          ...getSize(),
          borderRadius: DESIGN_TOKENS.layout.borderRadius.md,
          transition: 'all 0.2s ease-in-out',
          
          ...(isHovered && getHoverStyles()),
          
          '&:focus-visible': {
            outline: `2px solid ${color === 'primary' ? '#58a6ff' : '#f85149'}`,
            outlineOffset: '2px'
          },
          
          // Touch feedback for mobile
          '@media (hover: none)': {
            '&:active': {
              transform: 'scale(0.9)',
              transition: 'transform 0.1s ease-out'
            }
          },
          
          ...props.sx
        }}
        {...props}
      >
        <Fade in={true} timeout={200}>
          <Box>{getIconContent()}</Box>
        </Fade>
      </MuiIconButton>
    </ButtonComponent>
  );
};

/**
 * Floating Action Button with Enhanced Animations
 */
export const AnimatedFab = ({
  children,
  onClick,
  color = 'primary',
  size = 'medium',
  disabled = false,
  extended = false,
  text,
  icon,
  entrance = 'zoom',
  ...props
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), 100);
    return () => clearTimeout(timer);
  }, []);

  const getEntranceAnimation = () => {
    const animations = {
      zoom: { timeout: 200 },
      slide: { timeout: 300, direction: 'up' },
      fade: { timeout: 400 }
    };
    return animations[entrance] || animations.zoom;
  };

  const AnimationComponent = entrance === 'zoom' ? Zoom : entrance === 'slide' ? Slide : Fade;
  const animationProps = getEntranceAnimation();

  return (
    <AnimationComponent in={isVisible} {...animationProps}>
      <TouchRipple>
        <MuiButton
          variant="contained"
          color={color}
          disabled={disabled}
          onClick={onClick}
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
          sx={{
            position: 'fixed',
            bottom: 24,
            right: 24,
            borderRadius: extended ? DESIGN_TOKENS.layout.borderRadius.lg : '50%',
            minWidth: extended ? 'auto' : size === 'small' ? 40 : size === 'large' ? 64 : 56,
            width: extended ? 'auto' : size === 'small' ? 40 : size === 'large' ? 64 : 56,
            height: size === 'small' ? 40 : size === 'large' ? 64 : 56,
            zIndex: 1000,
            transition: 'all 0.3s ease-in-out',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
            
            ...(isHovered && {
              transform: 'scale(1.1) translateY(-2px)',
              boxShadow: '0 8px 24px rgba(0, 0, 0, 0.2)'
            }),
            
            '&:active': {
              transform: 'scale(0.95)',
              transition: 'transform 0.1s ease-out'
            },
            
            ...props.sx
          }}
          {...props}
        >
          {extended ? (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, px: 2 }}>
              {icon}
              {text}
            </Box>
          ) : (
            children || icon
          )}
        </MuiButton>
      </TouchRipple>
    </AnimationComponent>
  );
};

export default {
  InteractiveButton,
  InteractiveIconButton,
  AnimatedFab
};
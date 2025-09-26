/**
 * Mobile Responsive Hooks
 * 
 * Custom hooks for enhanced mobile and tablet interactions
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { useTheme, useMediaQuery } from '@mui/material';

/**
 * Enhanced Responsive Hook
 * Provides detailed device and orientation information
 */
export const useEnhancedResponsive = () => {
  const theme = useTheme();
  
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isTablet = useMediaQuery(theme.breakpoints.between('md', 'lg'));
  const isDesktop = useMediaQuery(theme.breakpoints.up('lg'));
  const isLandscape = useMediaQuery('(orientation: landscape)');
  const isPortrait = useMediaQuery('(orientation: portrait)');
  
  // Device type detection
  const deviceType = isMobile ? 'mobile' : isTablet ? 'tablet' : 'desktop';
  
  // Touch capability detection
  const isTouchDevice = useMediaQuery('(hover: none)');
  
  return {
    isMobile,
    isTablet,
    isDesktop,
    isLandscape,
    isPortrait,
    isTouchDevice,
    deviceType,
    
    // Responsive values
    getValue: (config) => {
      if (typeof config === 'object') {
        if (isMobile && config.mobile !== undefined) return config.mobile;
        if (isTablet && config.tablet !== undefined) return config.tablet;
        if (isDesktop && config.desktop !== undefined) return config.desktop;
        return config.default || config.mobile || config.tablet || config.desktop;
      }
      return config;
    }
  };
};

/**
 * Swipe Gesture Hook
 * Detects swipe gestures for mobile interactions
 */
export const useSwipeGesture = (options = {}) => {
  const {
    onSwipeLeft,
    onSwipeRight,
    onSwipeUp,
    onSwipeDown,
    threshold = 50,
    preventDefault = false
  } = options;
  
  const [touchStart, setTouchStart] = useState(null);
  const [touchEnd, setTouchEnd] = useState(null);
  
  const handleTouchStart = useCallback((e) => {
    if (preventDefault) e.preventDefault();
    setTouchEnd(null);
    setTouchStart({
      x: e.targetTouches[0].clientX,
      y: e.targetTouches[0].clientY
    });
  }, [preventDefault]);
  
  const handleTouchMove = useCallback((e) => {
    if (preventDefault) e.preventDefault();
    setTouchEnd({
      x: e.targetTouches[0].clientX,
      y: e.targetTouches[0].clientY
    });
  }, [preventDefault]);
  
  const handleTouchEnd = useCallback((e) => {
    if (!touchStart || !touchEnd) return;
    
    const deltaX = touchStart.x - touchEnd.x;
    const deltaY = touchStart.y - touchEnd.y;
    
    const isHorizontalSwipe = Math.abs(deltaX) > Math.abs(deltaY);
    const isVerticalSwipe = Math.abs(deltaY) > Math.abs(deltaX);
    
    if (isHorizontalSwipe && Math.abs(deltaX) > threshold) {
      if (deltaX > 0) {
        onSwipeLeft?.();
      } else {
        onSwipeRight?.();
      }
    }
    
    if (isVerticalSwipe && Math.abs(deltaY) > threshold) {
      if (deltaY > 0) {
        onSwipeUp?.();
      } else {
        onSwipeDown?.();
      }
    }
  }, [touchStart, touchEnd, threshold, onSwipeLeft, onSwipeRight, onSwipeUp, onSwipeDown]);
  
  return {
    onTouchStart: handleTouchStart,
    onTouchMove: handleTouchMove,
    onTouchEnd: handleTouchEnd
  };
};

/**
 * Mobile Drawer Hook
 * Manages mobile drawer state with enhanced UX
 */
export const useMobileDrawer = (initialOpen = false) => {
  const [isOpen, setIsOpen] = useState(initialOpen);
  const { isMobile } = useEnhancedResponsive();
  
  const open = useCallback(() => {
    setIsOpen(true);
  }, []);
  
  const close = useCallback(() => {
    setIsOpen(false);
  }, []);
  
  const toggle = useCallback(() => {
    setIsOpen(prev => !prev);
  }, []);
  
  // Auto-close on desktop
  useEffect(() => {
    if (!isMobile && isOpen) {
      setIsOpen(false);
    }
  }, [isMobile, isOpen]);
  
  return {
    isOpen,
    open,
    close,
    toggle,
    drawerProps: {
      open: isOpen,
      onClose: close
    }
  };
};

/**
 * Touch-friendly Button Hook
 * Provides enhanced touch target configuration
 */
export const useTouchFriendlyButton = (baseProps = {}) => {
  const { isMobile, isTablet, isTouchDevice } = useEnhancedResponsive();
  
  const enhancedProps = {
    ...baseProps,
    size: isMobile || isTablet ? 'large' : baseProps.size || 'medium',
    sx: {
      minHeight: isTouchDevice ? '48px' : '40px',
      minWidth: isTouchDevice ? '48px' : 'auto',
      ...baseProps.sx
    }
  };
  
  return enhancedProps;
};

/**
 * Responsive Grid Hook
 * Provides adaptive grid configurations
 */
export const useResponsiveGrid = (config = {}) => {
  const { deviceType, isPortrait } = useEnhancedResponsive();
  
  const defaultConfigs = {
    mobile: {
      columns: 1,
      spacing: 2,
      direction: 'column'
    },
    tablet: {
      columns: isPortrait ? 2 : 3,
      spacing: 3,
      direction: 'row'
    },
    desktop: {
      columns: 4,
      spacing: 4,
      direction: 'row'
    }
  };
  
  const currentConfig = {
    ...defaultConfigs[deviceType],
    ...config[deviceType]
  };
  
  return {
    ...currentConfig,
    deviceType
  };
};

/**
 * Mobile-First Spacing Hook
 * Provides responsive spacing values
 */
export const useMobileSpacing = () => {
  const { getValue } = useEnhancedResponsive();
  
  const getSpacing = useCallback((config) => {
    if (typeof config === 'number') return config;
    
    return getValue({
      mobile: config.xs || config.mobile || 1,
      tablet: config.sm || config.tablet || 2,
      desktop: config.md || config.desktop || 3
    });
  }, [getValue]);
  
  return { getSpacing };
};

/**
 * Adaptive Typography Hook
 * Provides responsive typography scaling
 */
export const useAdaptiveTypography = () => {
  const { deviceType } = useEnhancedResponsive();
  
  const getVariant = useCallback((baseVariant) => {
    const variants = {
      mobile: {
        h1: 'h2',
        h2: 'h3',
        h3: 'h4',
        h4: 'h5',
        h5: 'h6',
        h6: 'subtitle1'
      },
      tablet: {
        h1: 'h1',
        h2: 'h2',
        h3: 'h3',
        h4: 'h4',
        h5: 'h5',
        h6: 'h6'
      },
      desktop: {
        h1: 'h1',
        h2: 'h2',
        h3: 'h3',
        h4: 'h4',
        h5: 'h5',
        h6: 'h6'
      }
    };
    
    return variants[deviceType][baseVariant] || baseVariant;
  }, [deviceType]);
  
  return { getVariant };
};

/**
 * Orientation Change Hook
 * Handles orientation changes with debouncing
 */
export const useOrientationChange = (callback, delay = 300) => {
  const { isLandscape, isPortrait } = useEnhancedResponsive();
  const timeoutRef = useRef(null);
  
  useEffect(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    
    timeoutRef.current = setTimeout(() => {
      callback({ isLandscape, isPortrait });
    }, delay);
    
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [isLandscape, isPortrait, callback, delay]);
  
  return { isLandscape, isPortrait };
};

export {
  useEnhancedResponsive as default
};
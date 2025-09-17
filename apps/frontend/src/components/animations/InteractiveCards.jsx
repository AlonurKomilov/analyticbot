/**
 * Enhanced Interactive Cards
 * 
 * Card components with advanced micro-interactions:
 * - Smooth hover effects and animations
 * - Loading states with skeleton animations
 * - Expand/collapse animations
 * - Interactive states and feedback
 * - Touch-friendly interactions
 */

import React, { useState, useEffect } from 'react';
import { 
  Card as MuiCard,
  CardContent,
  CardHeader,
  CardActions,
  Box,
  Collapse,
  IconButton,
  Typography,
  Skeleton,
  Fade,
  Grow,
  useTheme
} from '@mui/material';
import {
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
  MoreVert as MoreIcon
} from '@mui/icons-material';
import { InteractiveCard, SkeletonLoader, StaggeredAnimation } from './MicroInteractions.jsx';
import { DESIGN_TOKENS } from '../../theme/designTokens.js';

/**
 * Enhanced Card with Hover Effects
 */
export const AnimatedCard = ({
  children,
  loading = false,
  interactive = true,
  hoverEffect = 'lift',
  elevation = 1,
  onClick,
  onHover,
  entrance = 'fade',
  delay = 0,
  ...props
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const theme = useTheme();

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), delay);
    return () => clearTimeout(timer);
  }, [delay]);

  const handleMouseEnter = () => {
    setIsHovered(true);
    onHover?.(true);
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
    onHover?.(false);
  };

  const getEntranceAnimation = () => {
    const animations = {
      fade: <Fade in={isVisible} timeout={400}>{getCardContent()}</Fade>,
      grow: <Grow in={isVisible} timeout={400}>{getCardContent()}</Grow>,
      none: getCardContent()
    };
    return animations[entrance] || animations.fade;
  };

  const getCardContent = () => (
    <InteractiveCard
      interactive={interactive}
      hoverEffect={hoverEffect}
      onClick={onClick}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      sx={{
        minHeight: loading ? 200 : 'auto',
        position: 'relative',
        overflow: 'hidden',
        transition: 'all 0.3s ease-in-out',
        boxShadow: elevation === 0 ? 'none' : `0 ${elevation * 2}px ${elevation * 4}px rgba(0, 0, 0, 0.1)`,
        
        ...(isHovered && interactive && {
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: '2px',
            background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
            opacity: 0.8
          }
        }),
        
        ...props.sx
      }}
      {...props}
    >
      {loading ? <CardSkeleton /> : children}
    </InteractiveCard>
  );

  return getEntranceAnimation();
};

/**
 * Card Skeleton Loading Component
 */
const CardSkeleton = () => (
  <Box sx={{ p: { xs: 2, md: 3 } }}>
    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
      <SkeletonLoader variant="circular" width={40} height={40} />
      <Box sx={{ ml: 2, flex: 1 }}>
        <SkeletonLoader width="60%" height={20} />
        <SkeletonLoader width="40%" height={16} sx={{ mt: 0.5 }} />
      </Box>
    </Box>
    <SkeletonLoader width="100%" height={16} sx={{ mb: 1 }} />
    <SkeletonLoader width="80%" height={16} sx={{ mb: 1 }} />
    <SkeletonLoader width="90%" height={16} />
  </Box>
);

/**
 * Expandable Card with Smooth Animations
 */
export const ExpandableCard = ({
  title,
  subtitle,
  children,
  headerActions,
  defaultExpanded = false,
  loading = false,
  onExpand,
  expandIcon = <ExpandIcon />,
  collapseIcon = <CollapseIcon />,
  ...props
}) => {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const [isAnimating, setIsAnimating] = useState(false);

  const handleExpandClick = () => {
    setIsAnimating(true);
    setExpanded(!expanded);
    onExpand?.(!expanded);
    
    // Reset animation state after transition
    setTimeout(() => setIsAnimating(false), 300);
  };

  return (
    <AnimatedCard 
      interactive={false}
      loading={loading}
      {...props}
    >
      <CardHeader
        title={title}
        subheader={subtitle}
        action={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {headerActions}
            <IconButton
              onClick={handleExpandClick}
              disabled={loading}
              sx={{
                transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
                transition: 'transform 0.3s ease-in-out',
                minWidth: '44px',
                minHeight: '44px',
                
                '&:hover': {
                  backgroundColor: 'action.hover',
                  transform: expanded ? 'rotate(180deg) scale(1.1)' : 'rotate(0deg) scale(1.1)'
                }
              }}
            >
              {expanded ? collapseIcon : expandIcon}
            </IconButton>
          </Box>
        }
        sx={{
          '& .MuiCardHeader-title': {
            fontSize: { xs: '1.125rem', md: '1.25rem' },
            fontWeight: 600,
            transition: 'color 0.2s ease-in-out'
          },
          '& .MuiCardHeader-subheader': {
            fontSize: '0.875rem',
            opacity: isAnimating ? 0.6 : 1,
            transition: 'opacity 0.2s ease-in-out'
          }
        }}
      />
      
      <Collapse 
        in={expanded} 
        timeout={300}
        unmountOnExit
      >
        <CardContent sx={{ pt: 0 }}>
          <Fade in={expanded} timeout={400}>
            <Box>{children}</Box>
          </Fade>
        </CardContent>
      </Collapse>
    </AnimatedCard>
  );
};

/**
 * Metric Card with Number Animation
 */
export const AnimatedMetricCard = ({
  title,
  value,
  previousValue,
  unit = '',
  trend = 'neutral',
  icon,
  loading = false,
  animationDuration = 1000,
  formatValue = (val) => val,
  ...props
}) => {
  const [displayValue, setDisplayValue] = useState(previousValue || 0);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (loading) return;
    
    setIsAnimating(true);
    const startValue = previousValue || 0;
    const endValue = value || 0;
    const startTime = Date.now();
    
    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / animationDuration, 1);
      
      // Easing function for smooth animation
      const easeOutCubic = 1 - Math.pow(1 - progress, 3);
      const currentValue = startValue + (endValue - startValue) * easeOutCubic;
      
      setDisplayValue(currentValue);
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        setIsAnimating(false);
      }
    };
    
    requestAnimationFrame(animate);
  }, [value, previousValue, animationDuration, loading]);

  const getTrendColor = () => {
    const colors = {
      positive: 'success.main',
      negative: 'error.main',
      neutral: 'text.primary'
    };
    return colors[trend] || colors.neutral;
  };

  return (
    <AnimatedCard
      interactive={true}
      hoverEffect="glow"
      loading={loading}
      {...props}
    >
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6" color="text.secondary">
            {title}
          </Typography>
          {icon && (
            <Box sx={{ 
              color: getTrendColor(),
              transform: isAnimating ? 'scale(1.1)' : 'scale(1)',
              transition: 'transform 0.2s ease-in-out'
            }}>
              {icon}
            </Box>
          )}
        </Box>
        
        <Typography 
          variant="h4" 
          component="div"
          sx={{ 
            color: getTrendColor(),
            fontWeight: 700,
            mb: 1,
            transform: isAnimating ? 'scale(1.05)' : 'scale(1)',
            transition: 'transform 0.3s ease-in-out'
          }}
        >
          {loading ? (
            <SkeletonLoader width="80%" height={40} />
          ) : (
            `${formatValue(displayValue)}${unit}`
          )}
        </Typography>
        
        {previousValue !== undefined && !loading && (
          <Typography 
            variant="body2" 
            color="text.secondary"
            sx={{ 
              opacity: isAnimating ? 0.6 : 1,
              transition: 'opacity 0.2s ease-in-out'
            }}
          >
            Previous: {formatValue(previousValue)}{unit}
          </Typography>
        )}
      </CardContent>
    </AnimatedCard>
  );
};

/**
 * Interactive Dashboard Card
 */
export const DashboardCard = ({
  title,
  subtitle,
  children,
  actions,
  loading = false,
  error = false,
  empty = false,
  emptyMessage = 'No data available',
  refreshable = false,
  onRefresh,
  ...props
}) => {
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    if (!onRefresh) return;
    
    setIsRefreshing(true);
    try {
      await onRefresh();
    } finally {
      setTimeout(() => setIsRefreshing(false), 500);
    }
  };

  const getCardContent = () => {
    if (loading || isRefreshing) {
      return <CardSkeleton />;
    }
    
    if (error) {
      return (
        <Box sx={{ 
          p: 3, 
          textAlign: 'center',
          color: 'error.main'
        }}>
          <Typography variant="h6">Error loading data</Typography>
          {refreshable && (
            <Typography 
              variant="body2" 
              sx={{ 
                mt: 1, 
                cursor: 'pointer',
                '&:hover': { textDecoration: 'underline' }
              }}
              onClick={handleRefresh}
            >
              Click to retry
            </Typography>
          )}
        </Box>
      );
    }
    
    if (empty) {
      return (
        <Box sx={{ 
          p: 3, 
          textAlign: 'center',
          color: 'text.secondary'
        }}>
          <Typography variant="body1">{emptyMessage}</Typography>
        </Box>
      );
    }
    
    return (
      <CardContent>
        <StaggeredAnimation>
          {children}
        </StaggeredAnimation>
      </CardContent>
    );
  };

  return (
    <AnimatedCard
      interactive={true}
      hoverEffect="lift"
      {...props}
    >
      {(title || subtitle || actions) && (
        <CardHeader
          title={title}
          subheader={subtitle}
          action={actions}
          sx={{
            '& .MuiCardHeader-title': {
              fontSize: '1.25rem',
              fontWeight: 600
            }
          }}
        />
      )}
      
      {getCardContent()}
    </AnimatedCard>
  );
};

export default {
  AnimatedCard,
  ExpandableCard,
  AnimatedMetricCard,
  DashboardCard
};
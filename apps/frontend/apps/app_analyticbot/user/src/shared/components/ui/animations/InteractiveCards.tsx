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

import React, { useState, useEffect, ReactNode } from 'react';
import {
  Box,
  CardContent,
  CardHeader,
  Collapse,
  IconButton,
  Typography,
  Fade,
  Grow,
  CardProps
} from '@mui/material';
import {
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon
} from '@mui/icons-material';
import { InteractiveCard, SkeletonLoader, StaggeredAnimation } from './MicroInteractions';

type HoverEffect = 'lift' | 'glow' | 'scale';
type EntranceEffect = 'fade' | 'grow' | 'none';
type Trend = 'positive' | 'negative' | 'neutral';

interface AnimatedCardProps extends Omit<CardProps, 'onClick'> {
  children: ReactNode;
  loading?: boolean;
  interactive?: boolean;
  hoverEffect?: HoverEffect;
  elevation?: number;
  onClick?: () => void;
  onHover?: (isHovered: boolean) => void;
  entrance?: EntranceEffect;
  delay?: number;
}

interface ExpandableCardProps extends Omit<AnimatedCardProps, 'children' | 'title'> {
  title: ReactNode;
  subtitle?: ReactNode;
  children: ReactNode;
  headerActions?: ReactNode;
  defaultExpanded?: boolean;
  onExpand?: (expanded: boolean) => void;
  expandIcon?: ReactNode;
  collapseIcon?: ReactNode;
}

interface AnimatedMetricCardProps extends Omit<CardProps, 'title'> {
  title: string;
  value: number;
  previousValue?: number;
  unit?: string;
  trend?: Trend;
  icon?: ReactNode;
  loading?: boolean;
  animationDuration?: number;
  formatValue?: (value: number) => string | number;
}

interface DashboardCardProps extends Omit<CardProps, 'title'> {
  title?: ReactNode;
  subtitle?: ReactNode;
  children: ReactNode;
  actions?: ReactNode;
  loading?: boolean;
  error?: boolean;
  empty?: boolean;
  emptyMessage?: string;
  refreshable?: boolean;
  onRefresh?: () => Promise<void>;
}

/**
 * Enhanced Card with Hover Effects
 */
export const AnimatedCard: React.FC<AnimatedCardProps> = ({
  children,
  loading = false,
  interactive = true,
  hoverEffect = 'lift',
  onClick,
  onHover,
  entrance = 'fade',
  delay = 0
}) => {
  const [isVisible, setIsVisible] = useState<boolean>(false);

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), delay);
    return () => clearTimeout(timer);
  }, [delay]);

  const handleMouseEnter = (): void => {
    onHover?.(true);
  };

  const handleMouseLeave = (): void => {
    onHover?.(false);
  };

  const getCardContent = (): React.ReactElement => (
    <InteractiveCard
      interactive={interactive as any}
      hoverEffect={hoverEffect as any}
      onClick={onClick}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      sx={{
        p: { xs: 2, md: 3 },
        height: '100%',
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      {loading ? <CardSkeleton /> : children}
    </InteractiveCard>
  );

  const getEntranceAnimation = (): React.ReactElement => {
    const cardContent = getCardContent();
    const animations: Record<EntranceEffect, React.ReactElement> = {
      fade: <Fade in={isVisible} timeout={400}><Box>{cardContent}</Box></Fade>,
      grow: <Grow in={isVisible} timeout={400}><Box>{cardContent}</Box></Grow>,
      none: <>{cardContent}</>
    };
    return animations[entrance] || animations.fade;
  };

  return <>{getEntranceAnimation()}</>;
};

/**
 * Card Skeleton Loading Component
 */
const CardSkeleton: React.FC = () => (
  <Box sx={{ p: { xs: 2, md: 3 } }}>
    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
      <SkeletonLoader variant="circular" width="40px" height="40px" />
      <Box sx={{ ml: 2, flex: 1 }}>
        <SkeletonLoader width="60%" height="20px" />
        <Box sx={{ mt: 0.5 }}>
          <SkeletonLoader width="40%" height="16px" />
        </Box>
      </Box>
    </Box>
    <Box sx={{ mb: 1 }}>
      <SkeletonLoader width="100%" height="16px" />
    </Box>
    <Box sx={{ mb: 1 }}>
      <SkeletonLoader width="80%" height="16px" />
    </Box>
    <SkeletonLoader width="90%" height="16px" />
  </Box>
);

/**
 * Expandable Card with Smooth Animations
 */
export const ExpandableCard: React.FC<ExpandableCardProps> = ({
  title,
  subtitle,
  children,
  headerActions,
  defaultExpanded = false,
  loading = false,
  onExpand,
  expandIcon = <ExpandIcon />,
  collapseIcon = <CollapseIcon />
}) => {
  const [expanded, setExpanded] = useState<boolean>(defaultExpanded);
  const [isAnimating, setIsAnimating] = useState<boolean>(false);

  const handleExpandClick = (): void => {
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
export const AnimatedMetricCard: React.FC<AnimatedMetricCardProps> = ({
  title,
  value,
  previousValue,
  unit = '',
  trend = 'neutral',
  icon,
  loading = false,
  animationDuration = 1000,
  formatValue = (val) => val
}) => {
  const [displayValue, setDisplayValue] = useState<number>(previousValue || 0);
  const [isAnimating, setIsAnimating] = useState<boolean>(false);

  useEffect(() => {
    if (loading) return;

    setIsAnimating(true);
    const startValue = previousValue || 0;
    const endValue = value || 0;
    const startTime = Date.now();

    const animate = (): void => {
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

  const getTrendColor = (): string => {
    const colors: Record<Trend, string> = {
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
export const DashboardCard: React.FC<DashboardCardProps> = ({
  title,
  subtitle,
  children,
  actions,
  loading = false,
  error = false,
  empty = false,
  emptyMessage = 'No data available',
  refreshable = false,
  onRefresh
}) => {
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);

  const handleRefresh = async (): Promise<void> => {
    if (!onRefresh) return;

    setIsRefreshing(true);
    try {
      await onRefresh();
    } finally {
      setTimeout(() => setIsRefreshing(false), 500);
    }
  };

  const getCardContent = (): ReactNode => {
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

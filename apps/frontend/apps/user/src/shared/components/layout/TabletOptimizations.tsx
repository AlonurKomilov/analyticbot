/**
 * Tablet-Optimized Components
 *
 * Enhanced components specifically optimized for tablet experience (768-1024px):
 * - Better space utilization
 * - Touch-friendly interactions
 * - Adaptive layouts that work well in both portrait and landscape
 */

import React, { ReactNode, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Grid,
  useTheme,
  useMediaQuery,
  IconButton,
  Collapse,
  Chip,
  Typography,
  CardProps
} from '@mui/material';
import {
  ExpandMore as ExpandIcon,
  Fullscreen as FullscreenIcon
} from '@mui/icons-material';
import { DESIGN_TOKENS } from '@theme/designTokens';

// ============================================================================
// Type Definitions
// ============================================================================

export interface TabletDashboardLayoutProps {
  header?: ReactNode;
  primaryContent: ReactNode;
  secondaryContent: ReactNode;
  quickActions?: ReactNode;
  fullScreenMode?: boolean;
  onFullScreenToggle?: () => void;
}

export interface TabletCollapsibleCardProps extends Omit<CardProps, 'title'> {
  title: ReactNode;
  subtitle?: ReactNode;
  children: ReactNode;
  defaultExpanded?: boolean;
  showFullscreen?: boolean;
  onFullscreen?: () => void;
  headerActions?: ReactNode;
}

export interface AnalyticsWidget {
  component: ReactNode;
}

export interface TabletAnalyticsGridProps {
  widgets?: ReactNode[];
  spacing?: number;
}

export interface ButtonConfig {
  component: ReactNode;
}

export interface TabletButtonGroupProps {
  buttons?: ReactNode[];
  orientation?: 'horizontal' | 'vertical';
  fullWidth?: boolean;
  spacing?: 'sm' | 'md' | 'lg';
}

export interface TabletSplitViewProps {
  leftContent: ReactNode;
  rightContent: ReactNode;
  defaultSplit?: number;
  minLeftWidth?: number;
  minRightWidth?: number;
}

export interface StatusItem {
  icon?: ReactNode;
  label?: string;
  value: string | number;
  color?: string;
  status?: 'default' | 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success';
  variant?: 'filled' | 'outlined';
}

export interface TabletStatusBarProps {
  statusItems?: StatusItem[];
  showLabels?: boolean;
  compact?: boolean;
}

// ============================================================================
// Components
// ============================================================================

/**
 * Tablet-Optimized Dashboard Layout
 * Adaptive layout that works well in both portrait and landscape tablet modes
 */
export const TabletDashboardLayout: React.FC<TabletDashboardLayoutProps> = ({
  header,
  primaryContent,
  secondaryContent,
  quickActions
}) => {
  const theme = useTheme();
  const isTablet = useMediaQuery(theme.breakpoints.between('md', 'lg'));
  const isPortrait = useMediaQuery('(orientation: portrait)');

  // In tablet portrait mode, stack vertically
  // In tablet landscape mode, use side-by-side layout
  const useVerticalLayout = isTablet && isPortrait;

  return (
    <Box
      sx={{
        minHeight: '100vh',
        bgcolor: 'background.default',
        p: { xs: 2, md: 3 }
      }}
    >
      {/* Header */}
      {header && (
        <Box sx={{ mb: 3 }}>
          {header}
        </Box>
      )}

      {/* Main Content Grid */}
      <Grid
        container
        spacing={{ xs: 2, md: 3, lg: 4 }}
        sx={{ mb: 3 }}
      >
        {/* Primary Content */}
        <Grid
          item
          xs={12}
          md={useVerticalLayout ? 12 : 8}
          order={{ xs: 1, md: 1 }}
        >
          {primaryContent}
        </Grid>

        {/* Secondary Content */}
        <Grid
          item
          xs={12}
          md={useVerticalLayout ? 12 : 4}
          order={{ xs: 2, md: 2 }}
        >
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: { xs: 2, md: 3 } }}>
            {secondaryContent}
            {quickActions && (
              <Box>
                {quickActions}
              </Box>
            )}
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

/**
 * Collapsible Tablet Card
 * Card component optimized for tablet with collapsible content
 */
export const TabletCollapsibleCard: React.FC<TabletCollapsibleCardProps> = ({
  title,
  subtitle,
  children,
  defaultExpanded = true,
  showFullscreen = false,
  onFullscreen,
  headerActions,
  ...props
}) => {
  const [expanded, setExpanded] = useState<boolean>(defaultExpanded);
  const theme = useTheme();

  return (
    <Card
      elevation={1}
      sx={{
        borderRadius: DESIGN_TOKENS.layout.borderRadius.md,
        border: `1px solid ${theme.palette.divider}`,
        ...props.sx
      }}
      {...props}
    >
      <CardHeader
        title={title}
        subheader={subtitle}
        action={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {headerActions}
            {showFullscreen && (
              <IconButton
                onClick={onFullscreen}
                size="small"
                sx={{
                  minWidth: '44px',
                  minHeight: '44px'
                }}
              >
                <FullscreenIcon />
              </IconButton>
            )}
            <IconButton
              onClick={() => setExpanded(!expanded)}
              size="small"
              sx={{
                minWidth: '44px',
                minHeight: '44px',
                transform: expanded ? 'rotate(0deg)' : 'rotate(180deg)',
                transition: 'transform 0.2s ease-in-out'
              }}
            >
              <ExpandIcon />
            </IconButton>
          </Box>
        }
        sx={{
          '& .MuiCardHeader-title': {
            fontSize: { xs: '1.125rem', md: '1.25rem' },
            fontWeight: 600
          },
          '& .MuiCardHeader-subheader': {
            fontSize: '0.875rem',
            mt: 0.5
          },
          pb: 1
        }}
      />

      <Collapse in={expanded} timeout="auto" unmountOnExit>
        <CardContent sx={{ pt: 0 }}>
          {children}
        </CardContent>
      </Collapse>
    </Card>
  );
};

/**
 * Tablet-Optimized Analytics Grid
 * Grid layout optimized for analytics widgets on tablets
 */
export const TabletAnalyticsGrid: React.FC<TabletAnalyticsGridProps> = ({
  widgets = [],
  spacing = 3
}) => {
  const theme = useTheme();
  const isTablet = useMediaQuery(theme.breakpoints.between('md', 'lg'));
  const isLandscape = useMediaQuery('(orientation: landscape)');

  // Different grid layouts based on orientation
  const getGridCols = () => {
    if (!isTablet) return { xs: 12, sm: 6, md: 4, lg: 3 };

    // Tablet-specific layouts
    if (isLandscape) {
      return { xs: 12, md: 4 }; // 3 columns in landscape
    } else {
      return { xs: 12, md: 6 }; // 2 columns in portrait
    }
  };

  const gridCols = getGridCols();

  return (
    <Grid container spacing={spacing}>
      {widgets.map((widget, index) => (
        <Grid item {...gridCols} key={index}>
          {widget}
        </Grid>
      ))}
    </Grid>
  );
};

/**
 * Tablet Touch-Optimized Button Group
 * Button group with enhanced touch targets for tablet
 */
export const TabletButtonGroup: React.FC<TabletButtonGroupProps> = ({
  buttons = [],
  orientation = 'horizontal',
  fullWidth = false,
  spacing = 'sm'
}) => {
  const theme = useTheme();
  const isTablet = useMediaQuery(theme.breakpoints.between('md', 'lg'));
  const spacingMap: Record<'sm' | 'md' | 'lg', number> = { sm: 2, md: 3, lg: 4 };
  const spacingValue = spacingMap[spacing] || 3;

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: orientation === 'horizontal' ? 'row' : 'column',
        gap: spacingValue,
        width: fullWidth ? '100%' : 'auto',
        flexWrap: orientation === 'horizontal' && isTablet ? 'wrap' : 'nowrap'
      }}
    >
      {buttons.map((button, index) => {
        if (!React.isValidElement(button)) {
          return <Box key={index}>{button}</Box>;
        }

        return (
          <Box
            key={index}
            sx={{
              flex: fullWidth && orientation === 'horizontal' ? 1 : 'none',
              minWidth: isTablet ? '120px' : 'auto'
            }}
          >
            {React.cloneElement(button as React.ReactElement<any>, {
              ...((button.props as any) || {}),
              size: isTablet ? 'large' : (button.props as any)?.size || 'medium',
              sx: {
                minHeight: '48px', // Enhanced touch target
                ...((button.props as any)?.sx || {})
              }
            })}
          </Box>
        );
      })}
    </Box>
  );
};

/**
 * Tablet Split View Component
 * Split view that adapts to tablet orientations
 */
export const TabletSplitView: React.FC<TabletSplitViewProps> = ({
  leftContent,
  rightContent,
  defaultSplit = 50,
  minLeftWidth = 300,
  minRightWidth = 300
}) => {
  const [splitRatio] = useState<number>(defaultSplit);
  const theme = useTheme();
  const isTablet = useMediaQuery(theme.breakpoints.between('md', 'lg'));
  const isLandscape = useMediaQuery('(orientation: landscape)');

  // Force vertical split on tablet portrait
  const forceVertical = isTablet && !isLandscape;

  if (forceVertical) {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', gap: 2 }}>
        <Box sx={{ flex: '0 0 auto', minHeight: '300px' }}>
          {leftContent}
        </Box>
        <Box sx={{ flex: 1, minHeight: '300px' }}>
          {rightContent}
        </Box>
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex', height: '100%', gap: 2 }}>
      <Box sx={{ flex: `0 0 ${splitRatio}%`, minWidth: `${minLeftWidth}px` }}>
        {leftContent}
      </Box>
      <Box sx={{ flex: 1, minWidth: `${minRightWidth}px` }}>
        {rightContent}
      </Box>
    </Box>
  );
};

/**
 * Tablet-Optimized Status Bar
 * Status indicators optimized for tablet viewing
 */
export const TabletStatusBar: React.FC<TabletStatusBarProps> = ({
  statusItems = [],
  showLabels = true,
  compact = false
}) => {
  const theme = useTheme();
  const isTablet = useMediaQuery(theme.breakpoints.between('md', 'lg'));

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: { xs: 1, md: 2 },
        p: { xs: 1, md: 1.5 },
        bgcolor: 'background.paper',
        borderRadius: DESIGN_TOKENS.layout.borderRadius.md,
        border: `1px solid ${theme.palette.divider}`,
        flexWrap: 'wrap'
      }}
    >
      {statusItems.map((item, index) => (
        <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {item.icon && (
            <Box sx={{ color: item.color || 'text.secondary' }}>
              {item.icon}
            </Box>
          )}

          {!compact && showLabels && (
            <Typography variant="body2" color="text.secondary">
              {item.label}
            </Typography>
          )}

          <Chip
            label={item.value}
            color={item.status || 'default'}
            size={isTablet ? 'medium' : 'small'}
            variant={item.variant || 'filled'}
          />

          {index < statusItems.length - 1 && (
            <Box
              sx={{
                width: '1px',
                height: '20px',
                bgcolor: 'divider',
                mx: 1
              }}
            />
          )}
        </Box>
      ))}
    </Box>
  );
};

export default {
  TabletDashboardLayout,
  TabletCollapsibleCard,
  TabletAnalyticsGrid,
  TabletButtonGroup,
  TabletSplitView,
  TabletStatusBar
};

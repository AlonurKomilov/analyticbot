/**
 * Mobile Responsive Enhancements
 *
 * Enhanced mobile responsive utilities and components for:
 * - Improved tablet experience (768-1024px)
 * - Touch-optimized interactions
 * - Swipe gestures for analytics tabs
 * - Better mobile content organization
 */

import React, { useState, useRef, ReactNode } from 'react';
import {
  Box,
  Drawer,
  IconButton,
  useTheme,
  useMediaQuery,
  Divider,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Chip
} from '@mui/material';
import {
  Close as CloseIcon,
  Dashboard as DashboardIcon,
  Analytics as AnalyticsIcon,
  Schedule as ScheduleIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';
import { DESIGN_TOKENS } from '../../theme/designTokens.js';

interface NavigationItem {
  label: string;
  path: string;
  icon: ReactNode;
  badge?: string | null;
}

interface MobileNavigationDrawerProps {
  open: boolean;
  onClose: () => void;
  navigationItems?: NavigationItem[];
  currentPath?: string;
  showChannelStatus?: boolean;
  channelCount?: number;
}

interface Tab {
  label: string;
  badge?: string | number;
}

interface SwipeableTabNavigationProps {
  tabs?: Tab[];
  activeTab?: number;
  onTabChange: (index: number) => void;
  children: ReactNode;
  enableSwipe?: boolean;
}

interface MobileCardStackProps {
  children: ReactNode;
  spacing?: 'sm' | 'md' | 'lg';
}

interface ResponsiveGridProps {
  children: ReactNode;
  mobileColumns?: number;
  tabletColumns?: number;
  desktopColumns?: number;
  spacing?: 'sm' | 'md' | 'lg';
}

/**
 * Enhanced Mobile Navigation Drawer
 * Better mobile navigation with improved touch targets and organization
 */
export const MobileNavigationDrawer: React.FC<MobileNavigationDrawerProps> = ({
  open,
  onClose,
  navigationItems = [],
  currentPath = '',
  showChannelStatus = false,
  channelCount = 0
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const defaultNavItems: NavigationItem[] = [
    {
      label: 'Dashboard',
      path: '/dashboard',
      icon: <DashboardIcon />,
      badge: channelCount > 0 ? `${channelCount} channels` : null
    },
    {
      label: 'Analytics',
      path: '/analytics',
      icon: <AnalyticsIcon />,
      badge: null
    },
    {
      label: 'Scheduled Posts',
      path: '/posts',
      icon: <ScheduleIcon />,
      badge: null
    },
    {
      label: 'Settings',
      path: '/settings',
      icon: <SettingsIcon />,
      badge: null
    }
  ];

  const items = navigationItems.length > 0 ? navigationItems : defaultNavItems;

  return (
    <Drawer
      anchor="left"
      open={open}
      onClose={onClose}
      sx={{
        '& .MuiDrawer-paper': {
          width: isMobile ? '280px' : '320px',
          bgcolor: 'background.paper',
          borderRight: `1px solid ${theme.palette.divider}`,
        }
      }}
    >
      {/* Header */}
      <Box
        sx={{
          p: DESIGN_TOKENS.layout.container.padding.md,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          minHeight: '64px',
          bgcolor: 'primary.50',
          borderBottom: `1px solid ${theme.palette.divider}`
        }}
      >
        <Box sx={{ fontSize: '1.125rem', fontWeight: 600, color: 'primary.main' }}>
          Analytics Bot
        </Box>
        <IconButton
          onClick={onClose}
          size="small"
          sx={{
            minWidth: '44px',
            minHeight: '44px',
            color: 'primary.main'
          }}
        >
          <CloseIcon />
        </IconButton>
      </Box>

      {/* Navigation Items */}
      <List sx={{ flex: 1, py: 2 }}>
        {items.map((item, index) => (
          <ListItem key={index} disablePadding sx={{ mb: 1 }}>
            <ListItemButton
              selected={currentPath === item.path}
              onClick={() => {
                // Handle navigation
                onClose();
              }}
              sx={{
                mx: 2,
                borderRadius: DESIGN_TOKENS.layout.borderRadius.md,
                minHeight: '52px', // Enhanced touch target
                '&.Mui-selected': {
                  bgcolor: 'primary.50',
                  '&:hover': {
                    bgcolor: 'primary.100',
                  }
                },
                '&:hover': {
                  bgcolor: 'action.hover',
                }
              }}
            >
              <ListItemIcon sx={{ minWidth: '40px', color: 'inherit' }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText
                primary={item.label}
                sx={{ '& .MuiListItemText-primary': { fontWeight: 500 } }}
              />
              {item.badge && (
                <Chip
                  label={item.badge}
                  size="small"
                  color="primary"
                  variant="outlined"
                />
              )}
            </ListItemButton>
          </ListItem>
        ))}
      </List>

      {showChannelStatus && (
        <>
          <Divider />
          <Box sx={{ p: 3, bgcolor: 'grey.50' }}>
            <Box sx={{ fontSize: '0.875rem', color: 'text.secondary', mb: 1 }}>
              Status
            </Box>
            <Chip
              label={`${channelCount} Connected Channels`}
              color={channelCount > 0 ? 'success' : 'default'}
              size="small"
            />
          </Box>
        </>
      )}
    </Drawer>
  );
};

/**
 * Swipeable Tab Navigation
 * Enhanced tab navigation with swipe gestures for mobile
 */
export const SwipeableTabNavigation: React.FC<SwipeableTabNavigationProps> = ({
  tabs = [],
  activeTab = 0,
  onTabChange,
  children,
  enableSwipe = true
}) => {
  const [startX, setStartX] = useState<number | null>(null);
  const [startY, setStartY] = useState<number | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // Touch handlers for swipe gestures
  const handleTouchStart = (e: React.TouchEvent<HTMLDivElement>): void => {
    if (!enableSwipe || !isMobile) return;

    const touch = e.touches[0];
    setStartX(touch.clientX);
    setStartY(touch.clientY);
  };

  const handleTouchEnd = (e: React.TouchEvent<HTMLDivElement>): void => {
    if (!enableSwipe || !isMobile || startX === null || startY === null) return;

    const touch = e.changedTouches[0];
    const deltaX = touch.clientX - startX;
    const deltaY = touch.clientY - startY;

    // Only process horizontal swipes (ignore vertical scrolling)
    if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
      if (deltaX > 0 && activeTab > 0) {
        // Swipe right - previous tab
        onTabChange(activeTab - 1);
      } else if (deltaX < 0 && activeTab < tabs.length - 1) {
        // Swipe left - next tab
        onTabChange(activeTab + 1);
      }
    }

    setStartX(null);
    setStartY(null);
  };

  return (
    <Box
      ref={containerRef}
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
      sx={{
        width: '100%',
        overflow: 'hidden',
        position: 'relative'
      }}
    >
      {/* Tab Headers */}
      <Box
        sx={{
          display: 'flex',
          overflowX: 'auto',
          borderBottom: `1px solid ${theme.palette.divider}`,
          bgcolor: 'background.paper',
          '&::-webkit-scrollbar': {
            height: '2px'
          },
          '&::-webkit-scrollbar-thumb': {
            bgcolor: 'primary.main',
            borderRadius: '2px'
          }
        }}
      >
        {tabs.map((tab, index) => (
          <Box
            key={index}
            onClick={() => onTabChange(index)}
            sx={{
              minWidth: isMobile ? '120px' : 'auto',
              px: 3,
              py: 2,
              cursor: 'pointer',
              borderBottom: activeTab === index ? `2px solid ${theme.palette.primary.main}` : '2px solid transparent',
              color: activeTab === index ? 'primary.main' : 'text.secondary',
              fontWeight: activeTab === index ? 600 : 400,
              fontSize: '0.875rem',
              textAlign: 'center',
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                bgcolor: 'action.hover',
                color: 'primary.main'
              },
              // Enhanced touch targets on mobile
              minHeight: isMobile ? '48px' : '40px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            {tab.label}
            {tab.badge && (
              <Chip
                label={tab.badge}
                size="small"
                color="primary"
                sx={{ ml: 1, height: '20px', fontSize: '0.75rem' }}
              />
            )}
          </Box>
        ))}
      </Box>

      {/* Tab Content */}
      <Box sx={{ p: { xs: 2, md: 3 } }}>
        {children}
      </Box>

      {/* Swipe Indicator (Mobile) */}
      {isMobile && enableSwipe && (
        <Box
          sx={{
            position: 'absolute',
            bottom: 8,
            left: '50%',
            transform: 'translateX(-50%)',
            display: 'flex',
            gap: 1,
            zIndex: 1
          }}
        >
          {tabs.map((_, index) => (
            <Box
              key={index}
              sx={{
                width: '6px',
                height: '6px',
                borderRadius: '50%',
                bgcolor: activeTab === index ? 'primary.main' : 'action.disabled',
                transition: 'background-color 0.2s ease-in-out'
              }}
            />
          ))}
        </Box>
      )}
    </Box>
  );
};

/**
 * Mobile-Optimized Card Stack
 * Stacked cards with better spacing for mobile
 */
export const MobileCardStack: React.FC<MobileCardStackProps> = ({ children, spacing = 'md' }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const spacingMap: Record<'sm' | 'md' | 'lg', number> = { sm: 2, md: 3, lg: 4 };
  const spacingValue = spacingMap[spacing] || 3;

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        gap: isMobile ? spacingValue : 4,
        px: isMobile ? 2 : 0,
        py: isMobile ? 1 : 0
      }}
    >
      {children}
    </Box>
  );
};

/**
 * Responsive Grid with Mobile Optimization
 */
export const ResponsiveGrid: React.FC<ResponsiveGridProps> = ({
  children,
  mobileColumns = 1,
  tabletColumns = 2,
  desktopColumns = 3,
  spacing = 'md'
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isTablet = useMediaQuery(theme.breakpoints.between('md', 'lg'));

  const columns = isMobile ? mobileColumns : isTablet ? tabletColumns : desktopColumns;
  const spacingMap: Record<'sm' | 'md' | 'lg', number> = { sm: 2, md: 3, lg: 4 };
  const spacingValue = spacingMap[spacing] || 3;

  return (
    <Box
      sx={{
        display: 'grid',
        gridTemplateColumns: `repeat(${columns}, 1fr)`,
        gap: spacingValue,
        width: '100%'
      }}
    >
      {children}
    </Box>
  );
};

export default {
  MobileNavigationDrawer,
  SwipeableTabNavigation,
  MobileCardStack,
  ResponsiveGrid
};

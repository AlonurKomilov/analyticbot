/**
 * Mobile-Responsive Enhanced Dashboard
 *
 * Mobile-first dashboard implementation with:
 * - Improved tablet experience (768-1024px)
 * - Touch-optimized interactions
 * - Swipe gestures for analytics tabs
 * - Adaptive layouts for different orientations
 * - Enhanced mobile navigation
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Alert,
  Chip,
  IconButton,
  Tooltip,
  useTheme,
  useMediaQuery,
  Fab
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  TrendingUp as TrendingIcon,
  Speed as SpeedIcon,
  Menu as MenuIcon
} from '@mui/icons-material';
import { useChannelStore, usePostStore, useUIStore } from '@/stores';
import { TouchTargetProvider } from '../common/TouchTargetCompliance.jsx';

// Enhanced layout components
import EnhancedSection from '../layout/EnhancedSection';
import EnhancedCard from '../layout/EnhancedCard.jsx';

// Mobile responsive components
import {
  MobileNavigationDrawer,
  SwipeableTabNavigation,
  MobileCardStack,
  ResponsiveGrid
} from '../layout/MobileResponsiveEnhancements.jsx';

// Tablet optimizations
import {
  TabletDashboardLayout,
  TabletCollapsibleCard,
  TabletStatusBar
} from '../layout/TabletOptimizations.jsx';

// Existing components
import { AnalyticsDashboard } from '../dashboard/AnalyticsDashboard';
import SystemStatusWidget from '../dashboard/SystemStatusWidget.jsx';
import AIServicesGrid from '../dashboard/AIServicesGrid';
import AddChannel from '../AddChannel.jsx';
import ScheduledPostsList from '../ScheduledPostsList.jsx';

interface MobileTab {
  label: string;
  badge: string | number | null;
}

interface NavigationItem {
  label: string;
  path: string;
  icon: React.ReactNode;
  badge: string | number | null;
}

interface StatusItem {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  status: 'success' | 'warning' | 'error' | 'info' | 'default' | 'primary' | 'secondary';
}

interface DataSourceStatus {
  label: string;
  color: 'success' | 'warning' | 'error' | 'info' | 'default' | 'primary' | 'secondary';
}

const MobileResponsiveDashboard: React.FC = () => {
  const { channels, addChannel, isLoading: isLoadingChannels } = useChannelStore();
  const loadChannels = useChannelStore.getState().fetchChannels || (() => Promise.resolve());
  const removeChannel = useChannelStore.getState().deleteChannel || (() => Promise.resolve());
  const { scheduledPosts } = usePostStore();
  const { dataSource } = useUIStore();
  const globalLoading = { isLoading: false };

  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isTablet = useMediaQuery(theme.breakpoints.between('md', 'lg'));

  // Mobile navigation state
  const [mobileMenuOpen, setMobileMenuOpen] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<number>(0);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  const isLoadingData = globalLoading.isLoading || isLoadingChannels;

  useEffect(() => {
    loadChannels();
  }, [loadChannels]);

  const handleRefresh = async (): Promise<void> => {
    await loadChannels();
    setLastRefresh(new Date());
  };

  const getDataSourceStatus = (): DataSourceStatus => {
    return {
      label: dataSource === 'api' ? 'Real API' : 'Demo Mode',
      color: dataSource === 'api' ? 'success' : 'warning'
    };
  };

  // Mobile tabs configuration
  const mobileTabs: MobileTab[] = [
    { label: 'Overview', badge: null },
    { label: 'Analytics', badge: 'New' },
    { label: 'Posts', badge: scheduledPosts?.length || 0 },
    { label: 'Channels', badge: channels?.length || 0 }
  ];

  // Navigation items for mobile drawer
  const navigationItems: NavigationItem[] = [
    {
      label: 'Dashboard',
      path: '/dashboard',
      icon: <TrendingIcon />,
      badge: null
    },
    {
      label: 'Analytics',
      path: '/analytics',
      icon: <TrendingIcon />,
      badge: null
    }
  ];

  // Loading state
  if (isLoadingData) {
    return (
      <TouchTargetProvider>
        <Box sx={{ p: { xs: 2, md: 3 } }}>
          <EnhancedSection
            title="Analytics Dashboard"
            subtitle="Loading your analytics data..."
            level={1}
          >
            <></>
          </EnhancedSection>
          <MobileCardStack>
            <EnhancedCard loading title="Analytics Overview" />
            <EnhancedCard loading title="Quick Actions" />
          </MobileCardStack>
        </Box>
      </TouchTargetProvider>
    );
  }

  // Mobile view with swipeable tabs
  if (isMobile) {
    return (
      <TouchTargetProvider>
        <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
          {/* Mobile Header */}
          <Box
            sx={{
              position: 'sticky',
              top: 0,
              zIndex: 1000,
              bgcolor: 'background.paper',
              borderBottom: `1px solid ${theme.palette.divider}`,
              p: 2
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <IconButton
                  onClick={() => setMobileMenuOpen(true)}
                  size="large"
                  sx={{ minWidth: '48px', minHeight: '48px' }}
                >
                  <MenuIcon />
                </IconButton>
                <Box>
                  <Typography variant="h6" fontWeight={600}>
                    Analytics
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {lastRefresh.toLocaleTimeString()}
                  </Typography>
                </Box>
              </Box>

              <Box sx={{ display: 'flex', gap: 1 }}>
                <Chip
                  icon={<SpeedIcon sx={{ fontSize: 16 }} />}
                  label={getDataSourceStatus().label}
                  color={getDataSourceStatus().color}
                  size="small"
                />
                <IconButton
                  onClick={handleRefresh}
                  size="large"
                  disabled={isLoadingData}
                  sx={{ minWidth: '48px', minHeight: '48px' }}
                >
                  <RefreshIcon />
                </IconButton>
              </Box>
            </Box>
          </Box>

          {/* System Status */}
          <Box sx={{ px: 2, py: 1 }}>
            <SystemStatusWidget dataSource={dataSource} />
          </Box>

          {/* Swipeable Tab Content */}
          <SwipeableTabNavigation
            tabs={mobileTabs as any}
            activeTab={activeTab}
            onTabChange={setActiveTab}
            enableSwipe={true}
          >
            {activeTab === 0 && (
              <MobileCardStack>
                <AIServicesGrid />
                <AnalyticsDashboard />
              </MobileCardStack>
            )}

            {activeTab === 1 && (
              <MobileCardStack>
                <AnalyticsDashboard />
              </MobileCardStack>
            )}

            {activeTab === 2 && (
              <MobileCardStack>
                <ScheduledPostsList {...{ posts: scheduledPosts } as any} />
              </MobileCardStack>
            )}

            {activeTab === 3 && (
              <MobileCardStack>
                <AddChannel {...{ channels, onAdd: addChannel, onRemove: removeChannel } as any} />
              </MobileCardStack>
            )}
          </SwipeableTabNavigation>

          {/* Mobile Navigation Drawer */}
          <MobileNavigationDrawer
            open={mobileMenuOpen}
            onClose={() => setMobileMenuOpen(false)}
            navigationItems={navigationItems as any}
            showChannelStatus={true}
            channelCount={channels?.length || 0}
          />

          {/* Floating Action Button */}
          <Fab
            color="primary"
            sx={{
              position: 'fixed',
              bottom: 24,
              right: 24,
              zIndex: 1000
            }}
            onClick={handleRefresh}
          >
            <RefreshIcon />
          </Fab>
        </Box>
      </TouchTargetProvider>
    );
  }

  // Tablet view with enhanced layout
  if (isTablet) {
    const statusItems: StatusItem[] = [
      {
        icon: <SpeedIcon />,
        label: 'Data Source',
        value: getDataSourceStatus().label,
        status: getDataSourceStatus().color
      },
      {
        icon: <TrendingIcon />,
        label: 'Channels',
        value: channels?.length || 0,
        status: 'primary'
      },
      {
        icon: <RefreshIcon />,
        label: 'Last Update',
        value: lastRefresh.toLocaleTimeString(),
        status: 'default'
      }
    ];

    return (
      <TouchTargetProvider>
        <TabletDashboardLayout
          header={
            <Box>
              <EnhancedSection
                title="Analytics Dashboard"
                subtitle="Monitor your social media performance and insights"
                level={1}
                actions={
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Tooltip title="Dashboard Settings">
                      <IconButton size="large">
                        <SettingsIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                }
              >
                <></>
              </EnhancedSection>
              <TabletStatusBar statusItems={statusItems} />
            </Box>
          }

          primaryContent={
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              <TabletCollapsibleCard
                title="AI-Powered Tools"
                subtitle="Intelligent content optimization"
                defaultExpanded={true}
              >
                <AIServicesGrid />
              </TabletCollapsibleCard>

              <TabletCollapsibleCard
                title="Analytics Overview"
                subtitle="Performance metrics and insights"
                defaultExpanded={true}
              >
                <AnalyticsDashboard />
              </TabletCollapsibleCard>
            </Box>
          }

          secondaryContent={
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              <TabletCollapsibleCard
                title="Scheduled Posts"
                subtitle={`${scheduledPosts?.length || 0} posts in queue`}
                defaultExpanded={true}
              >
                <ScheduledPostsList {...{ posts: scheduledPosts } as any} />
              </TabletCollapsibleCard>

              <TabletCollapsibleCard
                title="Channel Management"
                subtitle={`${channels?.length || 0} channels connected`}
                defaultExpanded={true}
              >
                <AddChannel {...{ channels, onAdd: addChannel, onRemove: removeChannel } as any} />
              </TabletCollapsibleCard>
            </Box>
          }

          quickActions={
            <Alert
              severity="info"
              sx={{
                bgcolor: 'primary.50',
                border: '1px solid',
                borderColor: 'primary.200'
              }}
            >
              <Typography variant="body2">
                <strong>Pro Tip:</strong> Use swipe gestures in mobile view to navigate between sections.
              </Typography>
            </Alert>
          }
        />
      </TouchTargetProvider>
    );
  }

  // Desktop view (fallback to enhanced dashboard)
  return (
    <TouchTargetProvider>
      <Box sx={{ p: 3 }}>
        <EnhancedSection
          title="Analytics Dashboard"
          subtitle="Full desktop experience"
          level={1}
        >
          <></>
        </EnhancedSection>
        <ResponsiveGrid
          mobileColumns={1}
          tabletColumns={2}
          desktopColumns={3}
          spacing="lg"
        >
          <AIServicesGrid />
          <AnalyticsDashboard />
          <Box>
            <ScheduledPostsList {...{ posts: scheduledPosts } as any} />
            <Box sx={{ mt: 3 }}>
              <AddChannel {...{ channels, onAdd: addChannel, onRemove: removeChannel } as any} />
            </Box>
          </Box>
        </ResponsiveGrid>
      </Box>
    </TouchTargetProvider>
  );
};

export default MobileResponsiveDashboard;

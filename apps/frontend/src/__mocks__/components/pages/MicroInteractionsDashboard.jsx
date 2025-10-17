/**
 * Micro-Interactions Enhanced Dashboard
 *
 * Dashboard with comprehensive micro-interactions:
 * - Smooth page transitions
 * - Interactive cards and buttons
 * - Loading animations
 * - Hover effects and feedback
 * - Touch-optimized interactions
 * - Staggered content animations
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Alert,
  Chip,
  Tooltip,
  useTheme,
  useMediaQuery,
  Grid
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  TrendingUp as TrendingIcon,
  Speed as SpeedIcon,
  Analytics as AnalyticsIcon,
  Schedule as ScheduleIcon,
  Devices as DevicesIcon
} from '@mui/icons-material';
import { useAppStore } from '../../store/appStore.js';
import { TouchTargetProvider } from '../common/TouchTargetCompliance.jsx';

// Enhanced layout components
import EnhancedSection from '../layout/EnhancedSection.jsx';

// Micro-interaction components
import {
  StaggeredAnimation,
  FloatingElement,
  FeedbackAnimation
} from '../animations/MicroInteractions.jsx';
import {
  InteractiveButton,
  InteractiveIconButton,
  AnimatedFab
} from '../animations/InteractiveButtons.jsx';
import {
  AnimatedCard,
  ExpandableCard,
  AnimatedMetricCard,
  DashboardCard
} from '../animations/InteractiveCards.jsx';

// Mobile responsive components (fallback for mobile/tablet)
import MobileResponsiveDashboard from './MobileResponsiveDashboard.jsx';

// Existing components
import { AnalyticsDashboard } from '../dashboard/AnalyticsDashboard';
import SystemStatusWidget from '../dashboard/SystemStatusWidget.jsx';
import AIServicesGrid from '../dashboard/AIServicesGrid.jsx';
import AddChannel from '../AddChannel.jsx';
import ScheduledPostsList from '../ScheduledPostsList.jsx';

const MicroInteractionsDashboard = () => {
  const {
    isGlobalLoading,
    isLoading,
    fetchData,
    scheduledPosts,
    channels,
    addChannel,
    removeChannel,
    dataSource
  } = useAppStore();

  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isTablet = useMediaQuery(theme.breakpoints.between('md', 'lg'));

  // State for micro-interactions
  const [lastRefresh, setLastRefresh] = useState(new Date());
  const [refreshing, setRefreshing] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [expandedSections, setExpandedSections] = useState({
    analytics: true,
    aiServices: true,
    posts: true,
    channels: true
  });

  const isLoadingData = isGlobalLoading() || isLoading('fetchData');

  // Use mobile-responsive dashboard for smaller screens
  if (isMobile || isTablet) {
    return <MobileResponsiveDashboard />;
  }

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await fetchData();
      setLastRefresh(new Date());
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 2000);
    } finally {
      setTimeout(() => setRefreshing(false), 800);
    }
  };

  const getDataSourceStatus = () => {
    return {
      label: dataSource === 'api' ? 'Real API' : 'Demo Mode',
      color: dataSource === 'api' ? 'success' : 'warning'
    };
  };

  const handleSectionToggle = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  // Mock analytics data for animated metrics
  const analyticsMetrics = [
    {
      title: 'Total Views',
      value: 156789,
      previousValue: 142356,
      unit: '',
      trend: 'positive',
      icon: <TrendingIcon />,
      formatValue: (val) => Math.round(val).toLocaleString()
    },
    {
      title: 'Engagement Rate',
      value: 8.7,
      previousValue: 7.2,
      unit: '%',
      trend: 'positive',
      icon: <AnalyticsIcon />,
      formatValue: (val) => val.toFixed(1)
    },
    {
      title: 'Active Channels',
      value: channels?.length || 0,
      previousValue: (channels?.length || 0) - 1,
      unit: '',
      trend: 'positive',
      icon: <DevicesIcon />,
      formatValue: (val) => Math.round(val)
    },
    {
      title: 'Scheduled Posts',
      value: scheduledPosts?.length || 0,
      previousValue: (scheduledPosts?.length || 0) + 2,
      unit: '',
      trend: 'neutral',
      icon: <ScheduleIcon />,
      formatValue: (val) => Math.round(val)
    }
  ];

  // Loading state with staggered animations
  if (isLoadingData && !refreshing) {
    return (
      <TouchTargetProvider>
        <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', p: 4 }}>
          <StaggeredAnimation delay={150}>
            <Box sx={{ mb: 4 }}>
              <EnhancedSection
                title="Analytics Dashboard"
                subtitle="Loading your analytics data..."
                level={1}
              />
            </Box>

            <Grid container spacing={4}>
              {[1, 2, 3, 4].map((i) => (
                <Grid item xs={12} sm={6} md={3} key={i}>
                  <AnimatedCard loading />
                </Grid>
              ))}
            </Grid>

            <Box sx={{ mt: 4 }}>
              <Grid container spacing={4}>
                <Grid item xs={12} md={8}>
                  <AnimatedCard loading sx={{ height: 400 }} />
                </Grid>
                <Grid item xs={12} md={4}>
                  <AnimatedCard loading sx={{ height: 400 }} />
                </Grid>
              </Grid>
            </Box>
          </StaggeredAnimation>
        </Box>
      </TouchTargetProvider>
    );
  }

  return (
    <TouchTargetProvider>
      <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', p: 4 }}>
        {/* Header Section with Micro-interactions */}
        <StaggeredAnimation>
          <Box sx={{ mb: 4 }}>
            <EnhancedSection
              title="Analytics Dashboard"
              subtitle="Monitor your social media performance with enhanced interactions"
              description="Experience smooth animations and responsive feedback throughout your dashboard"
              level={1}
              emphasis
              actions={
                <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                  <FeedbackAnimation type="success" show={showSuccess}>
                    <Chip
                      icon={<SpeedIcon sx={{ fontSize: 16 }} />}
                      label={getDataSourceStatus().label}
                      color={getDataSourceStatus().color}
                      size="small"
                      sx={{
                        transition: 'all 0.2s ease-in-out',
                        '&:hover': {
                          transform: 'scale(1.05)'
                        }
                      }}
                    />
                  </FeedbackAnimation>

                  <Tooltip title={`Last updated: ${lastRefresh.toLocaleTimeString()}`}>
                    <div>
                      <InteractiveIconButton
                        onClick={handleRefresh}
                        loading={refreshing}
                        success={showSuccess}
                        hoverEffect="bounce"
                        tooltip="Refresh data"
                      >
                        <RefreshIcon />
                      </InteractiveIconButton>
                    </div>
                  </Tooltip>

                  <Tooltip title="Dashboard Settings">
                    <div>
                      <InteractiveIconButton hoverEffect="glow">
                        <SettingsIcon />
                      </InteractiveIconButton>
                    </div>
                  </Tooltip>
                </Box>
              }
            />
          </Box>

          {/* System Status with Floating Animation */}
          <Box sx={{ mb: 4 }}>
            <FloatingElement duration={4} delay={0.5}>
              <SystemStatusWidget dataSource={dataSource} />
            </FloatingElement>
          </Box>
        </StaggeredAnimation>

        {/* Analytics Metrics Grid */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
            Key Metrics
          </Typography>
          <Grid container spacing={3}>
            <StaggeredAnimation delay={100}>
              {analyticsMetrics.map((metric, index) => (
                <Grid item xs={12} sm={6} md={3} key={index}>
                  <AnimatedMetricCard
                    {...metric}
                    loading={isLoadingData}
                    delay={index * 100}
                    entrance="grow"
                  />
                </Grid>
              ))}
            </StaggeredAnimation>
          </Grid>
        </Box>

        {/* Main Content Grid */}
        <Grid container spacing={4}>
          {/* Primary Content Area */}
          <Grid item xs={12} md={8}>
            <StaggeredAnimation delay={200}>
              {/* AI Services Section */}
              <Box sx={{ mb: 4 }}>
                <ExpandableCard
                  title="AI-Powered Tools"
                  subtitle="Intelligent content optimization and analytics"
                  defaultExpanded={expandedSections.aiServices}
                  onExpand={(expanded) => handleSectionToggle('aiServices')}
                  entrance="fade"
                  delay={300}
                >
                  <AIServicesGrid />
                </ExpandableCard>
              </Box>

              {/* Main Analytics Section */}
              <ExpandableCard
                title="Analytics Overview"
                subtitle="Performance metrics and detailed insights"
                defaultExpanded={expandedSections.analytics}
                onExpand={(expanded) => handleSectionToggle('analytics')}
                headerActions={
                  <InteractiveIconButton
                    hoverEffect="scale"
                    tooltip="View detailed analytics"
                  >
                    <TrendingIcon />
                  </InteractiveIconButton>
                }
                entrance="fade"
                delay={400}
              >
                <AnalyticsDashboard />
              </ExpandableCard>
            </StaggeredAnimation>
          </Grid>

          {/* Secondary Content Area */}
          <Grid item xs={12} md={4}>
            <StaggeredAnimation delay={300}>
              {/* Scheduled Posts */}
              <Box sx={{ mb: 4 }}>
                <DashboardCard
                  title="Scheduled Posts"
                  subtitle={`${scheduledPosts?.length || 0} posts in queue`}
                  loading={isLoadingData}
                  empty={!scheduledPosts?.length}
                  emptyMessage="No scheduled posts"
                  refreshable={true}
                  onRefresh={fetchData}
                  entrance="grow"
                  delay={500}
                >
                  <ScheduledPostsList posts={scheduledPosts} />
                </DashboardCard>
              </Box>

              {/* Channel Management */}
              <DashboardCard
                title="Channel Management"
                subtitle={`${channels?.length || 0} channels connected`}
                loading={isLoadingData}
                empty={!channels?.length}
                emptyMessage="No channels connected"
                actions={
                  <InteractiveButton
                    size="small"
                    variant="outlined"
                    startIcon={<DevicesIcon />}
                    hoverEffect="glow"
                  >
                    Add Channel
                  </InteractiveButton>
                }
                entrance="grow"
                delay={600}
              >
                <AddChannel
                  channels={channels}
                  onAdd={addChannel}
                  onRemove={removeChannel}
                />
              </DashboardCard>
            </StaggeredAnimation>
          </Grid>
        </Grid>

        {/* Quick Tips */}
        <Box sx={{ mt: 4 }}>
          <FloatingElement duration={5} delay={1}>
            <Alert
              severity="info"
              sx={{
                bgcolor: 'primary.50',
                border: '1px solid',
                borderColor: 'primary.200',
                borderRadius: 2,
                transition: 'all 0.2s ease-in-out',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
                }
              }}
            >
              <Typography variant="body2">
                <strong>💡 Pro Tip:</strong> Hover over cards and buttons to see interactive effects.
                All animations are optimized for smooth 60fps performance!
              </Typography>
            </Alert>
          </FloatingElement>
        </Box>

        {/* Floating Action Button */}
        <AnimatedFab
          onClick={handleRefresh}
          icon={<RefreshIcon />}
          text="Refresh"
          extended={false}
          entrance="zoom"
          color="primary"
          size="medium"
        />
      </Box>
    </TouchTargetProvider>
  );
};

export default MicroInteractionsDashboard;

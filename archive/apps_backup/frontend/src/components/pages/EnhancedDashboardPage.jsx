/**
 * Enhanced Dashboard Page with Micro-Interactions
 * 
 * Improved visual hierarchy with:
 * - Better content organization and spacing
 * - Clear primary/secondary content areas  
 * - Reduced cognitive load through better grouping
 * - Enhanced visual flow and emphasis
 * - Responsive layout optimization
 * - Smooth micro-interactions and animations
 * - Interactive feedback systems
 * - Loading states with skeleton animations
 */

import React, { useEffect, useState } from 'react';
import { Box, Typography, Alert, Tooltip, useTheme, useMediaQuery, Fade } from '@mui/material';
import { IconButton } from '../common/TouchTargetCompliance.jsx';
import ErrorBoundary from '../common/ErrorBoundary.jsx';
import { StatusChip } from '../common';
import { 
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  TrendingUp as TrendingIcon,
  Speed as SpeedIcon
} from '@mui/icons-material';
import { useAppStore } from '../../store/appStore.js';
import { TouchTargetProvider } from '../common/TouchTargetCompliance.jsx';

// Enhanced layout components
import EnhancedDashboardLayout from '../layout/EnhancedDashboardLayout.jsx';
import EnhancedSection from '../layout/EnhancedSection.jsx';
import EnhancedCard from '../layout/EnhancedCard.jsx';

// Micro-interaction components
import { 
  StaggeredAnimation, 
  FloatingElement,
  FeedbackAnimation
} from '../animations/MicroInteractions.jsx';
import { 
  InteractiveButton, 
  InteractiveIconButton 
} from '../animations/InteractiveButtons.jsx';
import { 
  AnimatedCard, 
  DashboardCard 
} from '../animations/InteractiveCards.jsx';

// Mobile responsive dashboard
import MobileResponsiveDashboard from './MobileResponsiveDashboard.jsx';

// Existing components
import { AnalyticsDashboard } from '../dashboard/AnalyticsDashboard';
import SystemStatusWidget from '../dashboard/SystemStatusWidget.jsx';
import AIServicesGrid from '../dashboard/AIServicesGrid.jsx';
import AddChannel from '../AddChannel.jsx';
import ScheduledPostsList from '../ScheduledPostsList.jsx';
import ChannelSelector from '../ChannelSelector.jsx';

const EnhancedDashboardPage = () => {
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
  
  const [lastRefresh, setLastRefresh] = useState(new Date());
  const [refreshing, setRefreshing] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [pageLoaded, setPageLoaded] = useState(false);
  const [selectedChannel, setSelectedChannel] = useState(null);
  const isLoadingData = isGlobalLoading() || isLoading('fetchData');
  
  useEffect(() => {
    fetchData();
    // Trigger page load animation
    setTimeout(() => setPageLoaded(true), 100);
  }, [fetchData]);

  // Use mobile-responsive dashboard for mobile and tablet
  if (isMobile || isTablet) {
    return <MobileResponsiveDashboard />;
  }

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
      label: dataSource === 'real' ? 'Live Data' : 'Demo Mode',
      color: dataSource === 'real' ? 'success' : 'warning'
    };
  };

  // Loading state with micro-interactions
  if (isLoadingData && !refreshing) {
    return (
      <TouchTargetProvider>
        <EnhancedDashboardLayout
          header={
            <StaggeredAnimation delay={150}>
              <EnhancedSection 
                title="Analytics Dashboard" 
                subtitle="Loading your analytics data..."
                level={1}
              />
            </StaggeredAnimation>
          }
          primaryContent={
            <StaggeredAnimation delay={300}>
              <DashboardCard loading title="Analytics Overview" />
            </StaggeredAnimation>
          }
          secondaryContent={
            <StaggeredAnimation delay={450}>
              <DashboardCard loading title="Quick Actions" />
            </StaggeredAnimation>
          }
        />
      </TouchTargetProvider>
    );
  }

  return (
    <TouchTargetProvider>
      <Box sx={{ minHeight: '100vh', position: 'relative', overflow: 'hidden' }}>
        <ErrorBoundary>
          <Box 
            sx={{ 
              height: '100%', 
              overflow: 'visible',
              opacity: pageLoaded ? 1 : 0,
              transition: 'opacity 0.8s ease-in-out',
              transform: pageLoaded ? 'translateY(0)' : 'translateY(20px)',
              transitionProperty: 'opacity, transform'
            }}
          >
            <EnhancedDashboardLayout
          // Header Section with Micro-interactions
          header={
            <StaggeredAnimation delay={150}>
              <EnhancedSection
                title="Analytics Dashboard"
                subtitle="Monitor your social media performance with enhanced interactions"
                description="Real-time analytics with smooth animations and responsive feedback"
                level={1}
                emphasis
                actions={
                  <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
                    {/* Channel Selector - Primary Action */}
                    <Box sx={{ minWidth: 300 }}>
                      <ChannelSelector
                        onChannelChange={setSelectedChannel}
                        size="small"
                        showCreateButton={true}
                        showRefreshButton={false}
                      />
                    </Box>
                    
                    <FeedbackAnimation type="success" show={showSuccess}>
                      <StatusChip
                        icon={<SpeedIcon sx={{ fontSize: 16 }} />}
                        label={getDataSourceStatus().label}
                        variant={getDataSourceStatus().color}
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
            </StaggeredAnimation>
          }

          // System Status - Prominent but not overwhelming
          systemStatus={
            <FloatingElement duration={4} delay={0.5}>
              <SystemStatusWidget dataSource={dataSource} />
            </FloatingElement>
          }

        // Primary Content Area (60% width)
        primaryContent={
          <>
            {/* AI Services - Quick Access */}
            <EnhancedSection
              title="AI-Powered Tools"
              subtitle="Intelligent content optimization and analytics"
              level={2}
              info="AI services to enhance your content strategy and performance"
            >
              <AIServicesGrid />
            </EnhancedSection>

            {/* Main Analytics - Primary focus */}
            <EnhancedSection
              title="Analytics Overview"
              subtitle="Performance metrics and insights"
              level={2}
              emphasis
              actions={
                <Tooltip title="View detailed analytics">
                  <IconButton size="small">
                    <TrendingIcon />
                  </IconButton>
                </Tooltip>
              }
            >
              <AnalyticsDashboard 
                selectedChannel={selectedChannel}
                channelId={selectedChannel?.id}
              />
            </EnhancedSection>
          </>
        }

        // Secondary Content Area (40% width) - Sidebar
        secondaryContent={
          <>
            {/* Scheduled Posts - Important but secondary */}
            <EnhancedSection
              title="Scheduled Posts"
              subtitle={`${scheduledPosts?.length || 0} posts in queue`}
              level={3}
            >
              <ScheduledPostsList posts={scheduledPosts} />
            </EnhancedSection>

            {/* Channel Management - Utility */}
            <EnhancedSection
              title="Channel Management"
              subtitle={`${channels?.length || 0} channels connected`}
              level={3}
            >
              <AddChannel 
                channels={channels} 
                onAdd={addChannel} 
                onRemove={removeChannel} 
              />
            </EnhancedSection>
          </>
        }

        // Quick Actions - Most accessible in sidebar
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
              <strong>Pro Tip:</strong> Use AI content optimization to improve engagement rates by up to 40%.
            </Typography>
          </Alert>
        }
            />
          </Box>
        </ErrorBoundary>
      </Box>
    </TouchTargetProvider>
  );
};

export default EnhancedDashboardPage;
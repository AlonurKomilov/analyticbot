/**
 * DashboardPage - Main dashboard overview page
 *
 * Enhanced with improved visual hierarchy:
 * - Uses new EnhancedDashboardLayout for better organization
 * - Improved content grouping and spacing
 * - Clearer visual emphasis and flow
 * - Maintained backward compatibility
 */

import React, { useEffect } from 'react';
import { useChannelStore, usePostStore, useUIStore } from '@/stores';
import { TouchTargetProvider } from '../common/TouchTargetCompliance.jsx';

// Import the enhanced dashboard component
import EnhancedDashboardPage from './EnhancedDashboardPage.jsx';

// Legacy imports for backward compatibility
import { Container, Stack } from '@mui/material';
import { PageContainer, SectionHeader } from '../common/StandardComponents.jsx';
import { AnalyticsDashboard } from '../dashboard/AnalyticsDashboard';
import SystemStatusWidget from '../dashboard/SystemStatusWidget.jsx';
import AIServicesGrid from '../dashboard/AIServicesGrid.jsx';
import AddChannel from '../AddChannel.jsx';
import ScheduledPostsList from '../ScheduledPostsList.jsx';
import { DESIGN_TOKENS } from '../../theme/designTokens.js';

const AppSkeleton = () => (
  <Stack spacing={DESIGN_TOKENS.layout.grid.gap.md}>
    {/* Loading skeleton implementation */}
    <div>Loading dashboard...</div>
  </Stack>
);

const DashboardPage = () => {
  // Enhanced version with improved visual hierarchy
  return <EnhancedDashboardPage />;
};

// Legacy implementation (preserved for backward compatibility)
const LegacyDashboardPage = () => {
  const { channels, loadChannels, addChannel, removeChannel, isLoading: isLoadingChannels } = useChannelStore();
  const { scheduledPosts } = usePostStore();
  const { dataSource, globalLoading } = useUIStore();

  const isLoadingData = globalLoading.isLoading || isLoadingChannels;

  useEffect(() => {
    loadChannels();
  }, [loadChannels]);

  if (isLoadingData) {
    return (
      <TouchTargetProvider>
        <PageContainer>
          <AppSkeleton />
        </PageContainer>
      </TouchTargetProvider>
    );
  }

  return (
    <TouchTargetProvider>
      <PageContainer>
        <SectionHeader level={1}>
          Analytics Dashboard
        </SectionHeader>

        <Stack spacing={4}>
          {/* System Status Section */}
          <SystemStatusWidget dataSource={dataSource} />

          {/* AI Services Section */}
          <AIServicesGrid />

          {/* Main Analytics Dashboard */}
          <Stack spacing={3}>
            <SectionHeader level={2}>Analytics Overview</SectionHeader>
            <AnalyticsDashboard />
          </Stack>

          {/* Sidebar Content */}
          <Stack spacing={3}>
            <ScheduledPostsList posts={scheduledPosts} />
            <AddChannel
              channels={channels}
              onAdd={addChannel}
              removeChannel={removeChannel}
            />
          </Stack>
        </Stack>
      </PageContainer>
    </TouchTargetProvider>
  );
};

export default DashboardPage;

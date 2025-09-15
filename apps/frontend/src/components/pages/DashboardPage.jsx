/**
 * DashboardPage - Main dashboard overview page
 * 
 * Simplified dashboard focusing on system overview and quick navigation.
 * Extracted from the monolithic MainDashboard component.
 */

import React, { useEffect } from 'react';
import { Container, Stack } from '@mui/material';
import { useAppStore } from '../../store/appStore.js';
import { TouchTargetProvider } from '../common/TouchTargetCompliance.jsx';
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
  
  const isLoadingData = isGlobalLoading() || isLoading('fetchData');
  
  useEffect(() => {
    fetchData();
  }, [fetchData]);

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
              onRemove={removeChannel} 
            />
          </Stack>
        </Stack>
      </PageContainer>
    </TouchTargetProvider>
  );
};

export default DashboardPage;
/**
 * AnalyticsPage - Dedicated analytics page
 *
 * Full-featured analytics dashboard without distractions.
 * Extracted from the tab interface in MainDashboard.
 */

import React, { useEffect } from 'react';
import { TouchTargetProvider } from '../common/TouchTargetCompliance.jsx';
import { PageContainer, SectionHeader } from '../common/StandardComponents.jsx';
import { AnalyticsDashboard } from '../dashboard/AnalyticsDashboard';
import { useChannelStore } from '@/stores';

const AnalyticsPage = () => {
  const { loadChannels } = useChannelStore();

  useEffect(() => {
    loadChannels();
  }, [loadChannels]);

  return (
    <TouchTargetProvider>
      <PageContainer maxWidth="2xl">
        <SectionHeader level={1}>
          Advanced Analytics
        </SectionHeader>

        <AnalyticsDashboard />
      </PageContainer>
    </TouchTargetProvider>
  );
};

export default AnalyticsPage;

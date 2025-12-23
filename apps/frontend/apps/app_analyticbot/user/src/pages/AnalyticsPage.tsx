/**
 * AnalyticsPage - Dedicated analytics page
 *
 * Full-featured analytics dashboard without distractions.
 * Extracted from the tab interface in MainDashboard.
 */

import React, { useEffect } from 'react';
import { TouchTargetProvider } from '@shared/components/ui';
import { PageContainer, SectionHeader } from '@shared/components/ui';
import { AnalyticsDashboard } from '@features/dashboard';
import { useChannelStore } from '@store';

const AnalyticsPage: React.FC = () => {
  const fetchChannels = useChannelStore((state) => state.fetchChannels);

  useEffect(() => {
    fetchChannels();
  }, [fetchChannels]);

  return (
    <TouchTargetProvider>
      <PageContainer maxWidth="xl">
        <SectionHeader level={1}>
          Advanced Analytics
        </SectionHeader>

        <AnalyticsDashboard />
      </PageContainer>
    </TouchTargetProvider>
  );
};

export default AnalyticsPage;

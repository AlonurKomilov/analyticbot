/**
 * SystemStatusWidget - System status display component
 *
 * Extracted from MainDashboard.jsx to provide focused system status display
 * with data source switching capabilities.
 */

import React from 'react';
import { Box, Stack } from '@mui/material';
import { StandardCard, SectionHeader, StandardStatusChip } from '@shared/components/ui';
import { GlobalDataSourceSwitch } from '@shared/components/navigation';
import { DESIGN_TOKENS } from '@/theme/designTokens';

interface StatusItem {
  label: string;
  status: 'success' | 'info' | 'warning' | 'error';
}

interface SystemStatusWidgetProps {
  dataSource?: string;
}

const SystemStatusWidget: React.FC<SystemStatusWidgetProps> = () => {
  const statusItems: StatusItem[] = [
    { label: 'Analytics Active', status: 'success' },
    { label: 'AI Services Running', status: 'success' },
    { label: 'Real-time Monitoring', status: 'info' },
    { label: 'Security Enabled', status: 'success' },
    { label: 'Performance Optimized', status: 'warning' }
  ];

  return (
    <StandardCard
      variant="elevated"
      sx={{
        background: DESIGN_TOKENS.charts.gradient.primary,
        border: '1px solid',
        borderColor: 'divider'
      }}
    >
      <SectionHeader level={3}>System Status</SectionHeader>

      <Box sx={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        mb: 2
      }}>
        <GlobalDataSourceSwitch size="medium" />
      </Box>

      <Stack
        direction="row"
        spacing={1}
        sx={{
          flexWrap: 'wrap',
          gap: 1
        }}
      >
        {statusItems.map((item) => (
          <StandardStatusChip
            key={item.label}
            label={item.label}
            status={item.status}
            size="small"
          />
        ))}
      </Stack>
    </StandardCard>
  );
};

export default SystemStatusWidget;

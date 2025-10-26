/**
 * Content Optimizer Page Component
 * Main page for AI-powered content optimization
 * UI ONLY - all business logic in service layer
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Tabs,
  Tab,
  Card
} from '@mui/material';

import { useContentOptimizer } from '@/hooks/useContentOptimizer';
import { ContentOptimizerHeader } from './ContentOptimizerHeader';
import { ContentOptimizerStats } from './ContentOptimizerStats';
import { RecentActivity } from './RecentActivity';
import { OptimizationSettings } from './OptimizationSettings';
import { OptimizationSchedule } from './OptimizationSchedule';

interface TabPanelProps {
  children: React.ReactNode;
  value: number;
  index: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div hidden={value !== index}>
    {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
  </div>
);

export const ContentOptimizerPage: React.FC = () => {
  const [currentTab, setCurrentTab] = useState(0);
  const [autoOptimization, setAutoOptimization] = useState(false);

  const { stats, isOptimizing, loadStats, optimizeContent, error } = useContentOptimizer();

  // Load stats on mount
  useEffect(() => {
    loadStats();
  }, [loadStats]);

  const handleOptimize = async () => {
    // Example content - in real app this would come from a form
    const sampleContent = 'This is sample content to optimize';
    await optimizeContent(sampleContent);
  };

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  return (
    <Box sx={{ p: { xs: 2, md: 4 }, maxWidth: '100%' }}>
      {/* Header with title and status */}
      <ContentOptimizerHeader
        status={stats.status}
        onOptimize={handleOptimize}
        isOptimizing={isOptimizing}
      />

      {/* Statistics Cards */}
      <ContentOptimizerStats
        totalOptimized={stats.totalOptimized}
        todayOptimized={stats.todayOptimized}
        avgImprovement={stats.avgImprovement}
        onOptimize={handleOptimize}
        isOptimizing={isOptimizing}
      />

      {/* Tabbed Content */}
      <Card
        elevation={0}
        sx={{
          borderRadius: 3,
          overflow: 'hidden',
          boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
          mt: 5
        }}
      >
        <Box sx={{
          background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
          p: 2
        }}>
          <Tabs
            value={currentTab}
            onChange={handleTabChange}
            sx={{
              '& .MuiTabs-indicator': {
                backgroundColor: 'primary.main',
                height: 3,
                borderRadius: 2
              },
              '& .MuiTab-root': {
                fontWeight: 600,
                fontSize: '1rem',
                textTransform: 'none',
                minHeight: 64,
                '&.Mui-selected': {
                  color: 'primary.main'
                }
              }
            }}
          >
            <Tab label="Recent Activity" iconPosition="start" sx={{ px: 3 }} />
            <Tab label="Settings" iconPosition="start" sx={{ px: 3 }} />
            <Tab label="Schedule" iconPosition="start" sx={{ px: 3 }} />
          </Tabs>
        </Box>

        <TabPanel value={currentTab} index={0}>
          <RecentActivity isOptimizing={isOptimizing} />
        </TabPanel>

        <TabPanel value={currentTab} index={1}>
          <OptimizationSettings
            autoOptimization={autoOptimization}
            onAutoOptimizationChange={setAutoOptimization}
          />
        </TabPanel>

        <TabPanel value={currentTab} index={2}>
          <OptimizationSchedule />
        </TabPanel>
      </Card>

      {/* Error Display */}
      {error && (
        <Box sx={{ mt: 2 }}>
          <Typography color="error" variant="body2">
            {error}
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default ContentOptimizerPage;

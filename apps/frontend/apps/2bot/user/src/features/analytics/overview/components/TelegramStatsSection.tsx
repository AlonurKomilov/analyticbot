/**
 * TelegramStatsSection Component
 * Displays audience insights from Telegram Stats API
 */

import React from 'react';
import { Box, Grid, Typography, Skeleton, Alert } from '@mui/material';
import { Language, Public } from '@mui/icons-material';
import { DemographicsCard } from './DemographicsCard';
import { TrafficSourcesCard } from './TrafficSourcesCard';
import type { TelegramStats } from '../types';

export interface TelegramStatsSectionProps {
  telegramStats: TelegramStats | null;
  isLoading: boolean;
}

const TelegramStatsNotAvailable: React.FC<{ message?: string }> = ({
  message = 'Telegram Statistics require at least 500 subscribers'
}) => (
  <Alert severity="info" sx={{ mb: 3 }}>
    <Typography variant="body2">
      {message}
    </Typography>
  </Alert>
);

export const TelegramStatsSection: React.FC<TelegramStatsSectionProps> = ({
  telegramStats,
  isLoading,
}) => {
  return (
    <Box sx={{ mb: 4 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <Typography variant="h6">
          Audience Insights
        </Typography>
        {isLoading && (
          <Skeleton width={100} height={24} />
        )}
      </Box>

      {telegramStats && !telegramStats.is_available ? (
        <TelegramStatsNotAvailable
          message={telegramStats.error_message || 'Telegram Statistics require at least 500 subscribers'}
        />
      ) : telegramStats && telegramStats.is_available ? (
        <Grid container spacing={3}>
          {/* Languages */}
          <Grid item xs={12} md={4}>
            <DemographicsCard
              title="Languages"
              icon={<Language fontSize="small" />}
              data={(telegramStats.languages || []).map((l) => ({
                name: l.language_name,
                percentage: l.percentage
              }))}
              emptyMessage="No language data available"
            />
          </Grid>

          {/* Countries */}
          <Grid item xs={12} md={4}>
            <DemographicsCard
              title="Countries"
              icon={<Public fontSize="small" />}
              data={(telegramStats.countries || []).map((c) => ({
                name: c.country_name,
                percentage: c.percentage
              }))}
              emptyMessage="No country data available"
            />
          </Grid>

          {/* Traffic Sources */}
          <Grid item xs={12} md={4}>
            <TrafficSourcesCard
              data={telegramStats.traffic_sources || []}
            />
          </Grid>
        </Grid>
      ) : !isLoading ? (
        <TelegramStatsNotAvailable
          message="Unable to load Telegram Statistics"
        />
      ) : null}
    </Box>
  );
};

export default TelegramStatsSection;

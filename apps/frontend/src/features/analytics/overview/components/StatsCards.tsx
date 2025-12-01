/**
 * StatsCards Components
 * Statistics display cards for posts, engagement, and reach
 */

import React from 'react';
import { Box, Paper, Typography, Divider } from '@mui/material';
import { formatNumber, formatPercentage } from './utils';
import type { ChannelOverviewData } from '../types';

interface StatRowProps {
  label: string;
  value: string | number;
}

const StatRow: React.FC<StatRowProps> = ({ label, value }) => (
  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
    <Typography variant="body2" color="text.secondary">{label}</Typography>
    <Typography variant="body2" fontWeight="medium">{value}</Typography>
  </Box>
);

export interface PostsStatsCardProps {
  posts: ChannelOverviewData['posts'];
}

export const PostsStatsCard: React.FC<PostsStatsCardProps> = ({ posts }) => (
  <Paper sx={{ p: 2 }}>
    <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
      Posts Statistics
    </Typography>
    <Divider sx={{ mb: 2 }} />
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
      <StatRow label="Today" value={posts.today} />
      <StatRow label="This Week" value={posts.week} />
      <StatRow label="This Month" value={posts.month} />
      <StatRow label="All Time" value={formatNumber(posts.total)} />
    </Box>
  </Paper>
);

export interface EngagementStatsCardProps {
  engagement: ChannelOverviewData['engagement'];
}

export const EngagementStatsCard: React.FC<EngagementStatsCardProps> = ({ engagement }) => (
  <Paper sx={{ p: 2 }}>
    <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
      Engagement Breakdown
    </Typography>
    <Divider sx={{ mb: 2 }} />
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
      <StatRow label="Total Reactions" value={formatNumber(engagement.total_reactions)} />
      <StatRow label="Total Forwards" value={formatNumber(engagement.total_forwards)} />
      <StatRow label="Total Comments" value={formatNumber(engagement.total_comments)} />
      <StatRow label="ER (24h)" value={formatPercentage(engagement.err_24h)} />
    </Box>
  </Paper>
);

export interface ReachStatsCardProps {
  reach: ChannelOverviewData['reach'];
}

export const ReachStatsCard: React.FC<ReachStatsCardProps> = ({ reach }) => (
  <Paper sx={{ p: 2 }}>
    <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
      Reach Statistics
    </Typography>
    <Divider sx={{ mb: 2 }} />
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
      <StatRow label="Reach (12h)" value={formatNumber(reach.reach_12h)} />
      <StatRow label="Reach (24h)" value={formatNumber(reach.reach_24h)} />
      <StatRow label="Reach (48h)" value={formatNumber(reach.reach_48h)} />
      <StatRow label="Avg Ad Reach" value={formatNumber(reach.avg_ad_reach)} />
    </Box>
  </Paper>
);

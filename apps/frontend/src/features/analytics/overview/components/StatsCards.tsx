/**
 * StatsCards Components
 * Statistics display cards for posts, engagement, and reach with user-friendly explanations
 */

import React from 'react';
import { Box, Paper, Typography, Divider, Tooltip, Chip } from '@mui/material';
import { HelpOutline, TrendingUp, TrendingDown, Remove } from '@mui/icons-material';
import { 
  formatNumber, 
  formatPercentage,
  getEngagementRatePerformance,
  getPostingFrequencyPerformance,
} from './utils';
import type { ChannelOverviewData } from '../types';

interface StatRowProps {
  label: string;
  value: string | number;
  tooltip?: string;
  highlight?: boolean;
  trend?: 'up' | 'down' | 'neutral';
}

const StatRow: React.FC<StatRowProps> = ({ label, value, tooltip, highlight, trend }) => (
  <Box sx={{ 
    display: 'flex', 
    justifyContent: 'space-between', 
    alignItems: 'center',
    py: 0.5,
    px: 1,
    borderRadius: 1,
    bgcolor: highlight ? 'action.hover' : 'transparent',
  }}>
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
      <Typography variant="body2" color="text.secondary">{label}</Typography>
      {tooltip && (
        <Tooltip title={tooltip} arrow placement="top">
          <HelpOutline sx={{ fontSize: 12, opacity: 0.5, cursor: 'help' }} />
        </Tooltip>
      )}
    </Box>
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
      {trend === 'up' && <TrendingUp sx={{ fontSize: 14, color: 'success.main' }} />}
      {trend === 'down' && <TrendingDown sx={{ fontSize: 14, color: 'error.main' }} />}
      {trend === 'neutral' && <Remove sx={{ fontSize: 14, color: 'text.secondary' }} />}
      <Typography variant="body2" fontWeight={highlight ? 'bold' : 'medium'}>
        {typeof value === 'number' ? formatNumber(value) : value}
      </Typography>
    </Box>
  </Box>
);

export interface PostsStatsCardProps {
  posts: ChannelOverviewData['posts'];
}

export const PostsStatsCard: React.FC<PostsStatsCardProps> = ({ posts }) => {
  const frequency = getPostingFrequencyPerformance(posts.avg_per_day);
  
  return (
    <Paper sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
        <Typography variant="subtitle1" fontWeight="bold">
          📝 Posts Statistics
        </Typography>
        <Chip
          size="small"
          label={`${frequency.emoji} ${frequency.label}`}
          sx={{
            height: 22,
            fontSize: '0.7rem',
            bgcolor: `${frequency.color}15`,
            color: frequency.color,
          }}
        />
      </Box>
      <Divider sx={{ mb: 2 }} />
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
        <StatRow 
          label="Today" 
          value={posts.today} 
          tooltip="Posts published today"
          highlight={posts.today > 0}
        />
        <StatRow 
          label="This Week" 
          value={posts.week} 
          tooltip="Posts in the last 7 days"
        />
        <StatRow 
          label="This Month" 
          value={posts.month} 
          tooltip="Posts in the last 30 days"
        />
        <Divider sx={{ my: 0.5 }} />
        <StatRow 
          label="All Time" 
          value={formatNumber(posts.total)} 
          highlight
        />
        <Box sx={{ mt: 1, px: 1 }}>
          <Typography variant="caption" color="text.secondary">
            Average: <strong>{posts.avg_per_day.toFixed(1)}</strong> posts/day
          </Typography>
        </Box>
      </Box>
    </Paper>
  );
};

export interface EngagementStatsCardProps {
  engagement: ChannelOverviewData['engagement'];
}

export const EngagementStatsCard: React.FC<EngagementStatsCardProps> = ({ engagement }) => {
  const performance = getEngagementRatePerformance(engagement.engagement_rate);
  const totalEngagement = engagement.total_reactions + engagement.total_forwards + engagement.total_comments;
  
  // Calculate percentages for the breakdown bar
  const reactionsPercent = totalEngagement > 0 ? (engagement.total_reactions / totalEngagement) * 100 : 0;
  const forwardsPercent = totalEngagement > 0 ? (engagement.total_forwards / totalEngagement) * 100 : 0;
  
  return (
    <Paper sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
        <Typography variant="subtitle1" fontWeight="bold">
          💬 Engagement Breakdown
        </Typography>
        <Tooltip title={performance.description} arrow>
          <Chip
            size="small"
            label={`${performance.emoji} ${performance.label}`}
            sx={{
              height: 22,
              fontSize: '0.7rem',
              bgcolor: `${performance.color}15`,
              color: performance.color,
              cursor: 'help',
            }}
          />
        </Tooltip>
      </Box>
      <Divider sx={{ mb: 2 }} />
      
      {/* Visual breakdown bar */}
      <Box sx={{ mb: 2, px: 1 }}>
        <Box sx={{ display: 'flex', height: 8, borderRadius: 1, overflow: 'hidden', bgcolor: 'action.hover' }}>
          <Box sx={{ width: `${reactionsPercent}%`, bgcolor: '#f44336' }} />
          <Box sx={{ width: `${forwardsPercent}%`, bgcolor: '#2196f3' }} />
          <Box sx={{ flex: 1, bgcolor: '#4caf50' }} />
        </Box>
        <Box sx={{ display: 'flex', gap: 2, mt: 0.5 }}>
          <Typography variant="caption" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#f44336' }} />
            Reactions
          </Typography>
          <Typography variant="caption" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#2196f3' }} />
            Forwards
          </Typography>
          <Typography variant="caption" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#4caf50' }} />
            Comments
          </Typography>
        </Box>
      </Box>
      
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
        <StatRow 
          label="Total Reactions" 
          value={formatNumber(engagement.total_reactions)}
          tooltip="👍 Emoji reactions on posts (likes, hearts, etc.)"
        />
        <StatRow 
          label="Total Forwards" 
          value={formatNumber(engagement.total_forwards)}
          tooltip="📤 Times your posts were shared to other chats"
        />
        <StatRow 
          label="Total Comments" 
          value={formatNumber(engagement.total_comments)}
          tooltip="💬 Comments and replies on posts"
        />
        <Divider sx={{ my: 0.5 }} />
        <StatRow 
          label="ER (24h)" 
          value={formatPercentage(engagement.err_24h)}
          tooltip="Engagement rate for posts in the last 24 hours"
          highlight
        />
      </Box>
    </Paper>
  );
};

export interface ReachStatsCardProps {
  reach: ChannelOverviewData['reach'];
}

export const ReachStatsCard: React.FC<ReachStatsCardProps> = ({ reach }) => {
  // Determine if reach is improving
  const reachTrend = reach.reach_24h > reach.reach_12h * 1.5 ? 'up' : 
                     reach.reach_24h < reach.reach_12h ? 'down' : 'neutral';
  
  return (
    <Paper sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
        <Typography variant="subtitle1" fontWeight="bold">
          📡 Reach Statistics
        </Typography>
      </Box>
      <Divider sx={{ mb: 2 }} />
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
        <StatRow 
          label="Last 12 hours" 
          value={formatNumber(reach.reach_12h)}
          tooltip="Views on posts from the last 12 hours"
        />
        <StatRow 
          label="Last 24 hours" 
          value={formatNumber(reach.reach_24h)}
          tooltip="Views on posts from the last 24 hours"
          trend={reachTrend}
        />
        <StatRow 
          label="Last 48 hours" 
          value={formatNumber(reach.reach_48h)}
          tooltip="Views on posts from the last 48 hours"
        />
        <Divider sx={{ my: 0.5 }} />
        <StatRow 
          label="Avg Ad Reach" 
          value={formatNumber(reach.avg_ad_reach)}
          tooltip="Estimated reach for sponsored content (~70% of organic reach)"
          highlight
        />
      </Box>
      
      {/* Tip for low reach */}
      {reach.avg_post_reach < 10 && (
        <Box sx={{ mt: 2, p: 1, bgcolor: 'warning.main', borderRadius: 1, opacity: 0.1 }}>
          <Typography variant="caption" color="warning.dark">
            💡 Tip: Post during peak hours (evening) to increase reach
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

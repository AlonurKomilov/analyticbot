import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  CircularProgress,
  Card,
  CardContent,
  alpha,
  useTheme,
} from '@mui/material';
import {
  People as PeopleIcon,
  LiveTv as ChannelsIcon,
  Analytics as AnalyticsIcon,
  MonitorHeart as HealthIcon,
  TrendingUp as TrendingIcon,
  Storage as StorageIcon,
} from '@mui/icons-material';
import { apiClient } from '@api/client';
import { API_ENDPOINTS } from '@config/api';

interface SystemStats {
  total_users: number;
  total_channels: number;
  total_posts: number;
  system_health: string;
  active_users_today: number;
  storage_used_gb: number;
}

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color: string;
  subtitle?: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, color, subtitle }) => {
  const theme = useTheme();
  return (
    <Card
      sx={{
        height: '100%',
        border: `1px solid ${theme.palette.divider}`,
        transition: 'transform 0.2s',
        '&:hover': { transform: 'translateY(-4px)' },
      }}
    >
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
          <Box
            sx={{
              p: 1.5,
              borderRadius: 2,
              bgcolor: alpha(color, 0.15),
              color: color,
            }}
          >
            {icon}
          </Box>
          <Box sx={{ flex: 1 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h4" fontWeight={700}>
              {value}
            </Typography>
            {subtitle && (
              <Typography variant="caption" color="text.secondary">
                {subtitle}
              </Typography>
            )}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

const DashboardPage: React.FC = () => {
  const theme = useTheme();
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await apiClient.get(API_ENDPOINTS.ADMIN.STATS);
        setStats(response.data);
      } catch (error) {
        console.error('Failed to fetch stats:', error);
        // Set default stats on error
        setStats({
          total_users: 0,
          total_channels: 0,
          total_posts: 0,
          system_health: 'Unknown',
          active_users_today: 0,
          storage_used_gb: 0,
        });
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Admin Dashboard
        </Typography>
        <Typography color="text.secondary">
          System overview and management
        </Typography>
      </Box>

      {/* Stats Grid */}
      <Grid container spacing={3}>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <StatCard
            title="Total Users"
            value={stats?.total_users || 0}
            icon={<PeopleIcon />}
            color={theme.palette.primary.main}
            subtitle="Registered accounts"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <StatCard
            title="Total Channels"
            value={stats?.total_channels || 0}
            icon={<ChannelsIcon />}
            color={theme.palette.success.main}
            subtitle="Connected channels"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <StatCard
            title="Total Posts"
            value={stats?.total_posts || 0}
            icon={<AnalyticsIcon />}
            color={theme.palette.info.main}
            subtitle="Tracked content"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <StatCard
            title="System Health"
            value={stats?.system_health || 'Unknown'}
            icon={<HealthIcon />}
            color={stats?.system_health === 'Healthy' ? theme.palette.success.main : theme.palette.warning.main}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <StatCard
            title="Active Today"
            value={stats?.active_users_today || 0}
            icon={<TrendingIcon />}
            color={theme.palette.secondary.main}
            subtitle="Users online today"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <StatCard
            title="Storage Used"
            value={`${(stats?.storage_used_gb || 0).toFixed(1)} GB`}
            icon={<StorageIcon />}
            color={theme.palette.warning.main}
            subtitle="Database storage"
          />
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Paper sx={{ mt: 4, p: 3, border: `1px solid ${theme.palette.divider}` }}>
        <Typography variant="h6" fontWeight={600} gutterBottom>
          Quick Actions
        </Typography>
        <Typography color="text.secondary">
          Use the sidebar navigation to manage users, channels, bots, and system settings.
        </Typography>
      </Paper>
    </Box>
  );
};

export default DashboardPage;

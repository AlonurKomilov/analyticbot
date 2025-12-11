import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid2 as Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  alpha,
  useTheme,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from '@mui/material';
import {
  People as PeopleIcon,
  LiveTv as ChannelsIcon,
  Analytics as AnalyticsIcon,
  MonitorHeart as HealthIcon,
  TrendingUp as TrendingIcon,
  Storage as StorageIcon,
  SmartToy as BotIcon,
  Memory as MemoryIcon,
  Speed as SpeedIcon,
  CheckCircle as ActiveIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from 'recharts';
import { apiClient } from '@api/client';
import { API_ENDPOINTS } from '@config/api';
import { DashboardSkeleton } from '../components/Skeletons';

interface SystemStats {
  total_users: number;
  total_channels: number;
  total_posts: number;
  total_views: number;
  active_channels: number;
  system_health: string;
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
          total_views: 0,
          active_channels: 0,
          system_health: 'Unknown',
        });
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) {
    return <DashboardSkeleton />;
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
            title="Active Channels"
            value={stats?.active_channels || 0}
            icon={<TrendingIcon />}
            color={theme.palette.secondary.main}
            subtitle="Currently active"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <StatCard
            title="Total Views"
            value={(stats?.total_views || 0).toLocaleString()}
            icon={<StorageIcon />}
            color={theme.palette.warning.main}
            subtitle="Tracked views"
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

      {/* Charts & Info Section */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        {/* Channel Status Distribution */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Paper sx={{ p: 3, border: `1px solid ${theme.palette.divider}`, height: '100%' }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Channel Status Distribution
            </Typography>
            <Box sx={{ width: '100%', height: 200, display: 'flex', justifyContent: 'center' }}>
              <ResponsiveContainer>
                <PieChart>
                  <Pie
                    data={[
                      { name: 'Active', value: stats?.active_channels || 0 },
                      { name: 'Inactive', value: Math.max(0, (stats?.total_channels || 0) - (stats?.active_channels || 0)) },
                    ]}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={70}
                    fill="#8884d8"
                    paddingAngle={5}
                    dataKey="value"
                    label={({ name, value }) => `${name}: ${value}`}
                  >
                    <Cell fill={theme.palette.success.main} />
                    <Cell fill={theme.palette.error.main} />
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'center', gap: 3, mt: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box sx={{ width: 12, height: 12, borderRadius: '50%', bgcolor: 'success.main' }} />
                <Typography variant="body2">Active ({stats?.active_channels || 0})</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box sx={{ width: 12, height: 12, borderRadius: '50%', bgcolor: 'error.main' }} />
                <Typography variant="body2">Inactive ({Math.max(0, (stats?.total_channels || 0) - (stats?.active_channels || 0))})</Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>

        {/* User Distribution Bar Chart */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Paper sx={{ p: 3, border: `1px solid ${theme.palette.divider}`, height: '100%' }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Resource Overview
            </Typography>
            <Box sx={{ width: '100%', height: 200 }}>
              <ResponsiveContainer>
                <BarChart
                  data={[
                    { name: 'Users', value: stats?.total_users || 0, fill: theme.palette.primary.main },
                    { name: 'Channels', value: stats?.total_channels || 0, fill: theme.palette.success.main },
                    { name: 'Active', value: stats?.active_channels || 0, fill: theme.palette.info.main },
                  ]}
                  layout="vertical"
                  margin={{ left: 60, right: 20, top: 10, bottom: 10 }}
                >
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                  <XAxis type="number" />
                  <YAxis type="category" dataKey="name" width={60} />
                  <Tooltip />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                    {[
                      { name: 'Users', fill: theme.palette.primary.main },
                      { name: 'Channels', fill: theme.palette.success.main },
                      { name: 'Active', fill: theme.palette.info.main },
                    ].map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>

        {/* System Status Panel */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Paper sx={{ p: 3, border: `1px solid ${theme.palette.divider}`, height: '100%' }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              System Status
            </Typography>
            <List dense>
              <ListItem>
                <ListItemIcon>
                  {stats?.system_health === 'Healthy' ? (
                    <ActiveIcon color="success" />
                  ) : stats?.system_health === 'Warning' ? (
                    <WarningIcon color="warning" />
                  ) : (
                    <ErrorIcon color="error" />
                  )}
                </ListItemIcon>
                <ListItemText 
                  primary="System Health" 
                  secondary={
                    <Chip 
                      size="small" 
                      label={stats?.system_health || 'Unknown'}
                      color={stats?.system_health === 'Healthy' ? 'success' : stats?.system_health === 'Warning' ? 'warning' : 'error'}
                    />
                  }
                />
              </ListItem>
              <Divider />
              <ListItem>
                <ListItemIcon>
                  <BotIcon color="primary" />
                </ListItemIcon>
                <ListItemText 
                  primary="Bot Workers" 
                  secondary="Status available in Bot Management"
                />
              </ListItem>
              <Divider />
              <ListItem>
                <ListItemIcon>
                  <MemoryIcon color="info" />
                </ListItemIcon>
                <ListItemText 
                  primary="Total Posts Tracked" 
                  secondary={(stats?.total_posts || 0).toLocaleString()}
                />
              </ListItem>
              <Divider />
              <ListItem>
                <ListItemIcon>
                  <SpeedIcon color="warning" />
                </ListItemIcon>
                <ListItemText 
                  primary="Total Views Collected" 
                  secondary={(stats?.total_views || 0).toLocaleString()}
                />
              </ListItem>
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardPage;

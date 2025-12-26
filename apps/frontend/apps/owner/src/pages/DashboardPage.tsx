import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Chip,
  alpha,
  useTheme,
  Alert,
} from '@mui/material';
import {
  People,
  Storage,
  Speed,
  TrendingUp,
  Memory,
  Dns,
  CheckCircle,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { ownerApi } from '@api/ownerApi';

interface SystemStats {
  users: {
    total: number;
    active: number;
    new_today: number;
    new_this_week: number;
  };
  activity: {
    daily_active: number;
    weekly_active: number;
    monthly_active: number;
  };
  system: {
    database_size: string;
    uptime: string;
    cpu_usage: number;
    memory_usage: number;
    total_channels: number;
    total_bots: number;
  };
}

const StatCard: React.FC<{
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactElement;
  color: string;
  trend?: { value: number; label: string };
}> = ({ title, value, subtitle, icon, color, trend }) => {
  const theme = useTheme();
  
  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
          <Box>
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
            {trend && (
              <Chip
                size="small"
                icon={<TrendingUp sx={{ fontSize: 14 }} />}
                label={`${trend.value > 0 ? '+' : ''}${trend.value}% ${trend.label}`}
                sx={{
                  mt: 1,
                  bgcolor: alpha(theme.palette.success.main, 0.1),
                  color: 'success.main',
                }}
              />
            )}
          </Box>
          <Box
            sx={{
              p: 1.5,
              borderRadius: 2,
              bgcolor: alpha(color, 0.1),
              color: color,
            }}
          >
            {React.cloneElement(icon as React.ReactElement<{ sx?: object }>, { sx: { fontSize: 28 } })}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

const DashboardPage: React.FC = () => {
  const theme = useTheme();
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [health, setHealth] = useState<{ 
    database?: { status: string }; 
    redis?: { status: string }; 
    api?: { status: string };
    user_bots?: { status: string };
    user_mtproto?: { status: string };
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setFetchError(null);
        // Fetch stats and health in parallel
        const [statsResponse, healthResponse] = await Promise.all([
          ownerApi.getSystemStats().catch((err) => {
            console.error('Failed to load stats:', err);
            return null;
          }),
          ownerApi.getSystemHealth().catch((err) => {
            console.error('Failed to load health:', err);
            return null;
          }),
        ]);
        
        if (statsResponse) {
          setStats(statsResponse.data);
        }
        if (healthResponse) {
          setHealth(healthResponse.data);
        }
        if (!statsResponse && !healthResponse) {
          setFetchError('Failed to load dashboard data');
        }
      } catch (err: any) {
        console.error('Failed to load dashboard data:', err);
        setFetchError(err.response?.data?.detail || 'Failed to load data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: '100%', overflow: 'hidden' }}>
      {fetchError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {fetchError}
        </Alert>
      )}
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Platform Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Overview of your entire platform
      </Typography>

      {/* Platform Stats */}
      <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
        Platform Overview
      </Typography>
      <Grid container spacing={2} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} lg={3}>
          <StatCard
            title="Total Users"
            value={stats?.users?.total?.toLocaleString() || '0'}
            subtitle={`${stats?.users?.active?.toLocaleString() || '0'} active`}
            icon={<People />}
            color={theme.palette.primary.main}
            trend={{ value: 12, label: 'this month' }}
          />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <StatCard
            title="Channels"
            value={stats?.system?.total_channels?.toLocaleString() || '0'}
            icon={<Dns />}
            color={theme.palette.info.main}
          />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <StatCard
            title="Database Size"
            value={stats?.system?.database_size || '0 GB'}
            icon={<Storage />}
            color={theme.palette.warning.main}
          />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <StatCard
            title="Uptime"
            value={stats?.system?.uptime || '0%'}
            icon={<Speed />}
            color={theme.palette.success.main}
          />
        </Grid>
      </Grid>

      {/* Activity Stats */}
      <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
        Activity Overview
      </Typography>
      <Grid container spacing={2} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} lg={3}>
          <StatCard
            title="Daily Active"
            value={stats?.activity?.daily_active?.toLocaleString() || '0'}
            icon={<TrendingUp />}
            color={theme.palette.primary.main}
          />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <StatCard
            title="Weekly Active"
            value={stats?.activity?.weekly_active?.toLocaleString() || '0'}
            icon={<TrendingUp />}
            color={theme.palette.secondary.main}
          />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <StatCard
            title="Monthly Active"
            value={stats?.activity?.monthly_active?.toLocaleString() || '0'}
            icon={<TrendingUp />}
            color={theme.palette.success.main}
          />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <StatCard
            title="CPU Usage"
            value={`${stats?.system?.cpu_usage || 0}%`}
            icon={<Memory />}
            color={
              (stats?.system?.cpu_usage || 0) > 80
                ? theme.palette.error.main
                : theme.palette.info.main
            }
          />
        </Grid>
      </Grid>

      {/* System Health */}
      <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
        System Health
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                Services Status
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                {[
                  { name: 'API Server', status: health?.api?.status || 'unknown' },
                  { name: 'Database', status: health?.database?.status || 'unknown' },
                  { name: 'Redis Cache', status: health?.redis?.status || 'unknown' },
                  { name: 'User Bots', status: health?.user_bots?.status || 'unknown' },
                  { name: 'MTProto Service', status: health?.user_mtproto?.status || 'unknown' },
                ].map((service) => {
                  const isHealthy = service.status === 'healthy';
                  const isUnknown = service.status === 'unknown';
                  const chipColor = isHealthy ? 'success' : isUnknown ? 'default' : 'error';
                  const bgColor = isHealthy 
                    ? alpha(theme.palette.success.main, 0.05) 
                    : isUnknown 
                    ? alpha(theme.palette.grey[500], 0.05)
                    : alpha(theme.palette.error.main, 0.05);
                  
                  return (
                    <Box
                      key={service.name}
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        p: 1.5,
                        borderRadius: 1,
                        bgcolor: bgColor,
                      }}
                    >
                      <Typography variant="body2">{service.name}</Typography>
                      <Chip
                        size="small"
                        icon={isHealthy ? <CheckCircle /> : <ErrorIcon />}
                        label={service.status}
                        color={chipColor}
                        sx={{ textTransform: 'capitalize' }}
                      />
                    </Box>
                  );
                })}
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                Quick Actions
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                {[
                  { name: 'View All Users', path: '/users' },
                  { name: 'System Health', path: '/system/health' },
                  { name: 'Database Backup', path: '/database' },
                  { name: 'View Audit Logs', path: '/audit' },
                  { name: 'Infrastructure Overview', path: '/infrastructure' },
                  { name: 'System Settings', path: '/settings' },
                ].map((action) => (
                  <Box
                    key={action.name}
                    component="a"
                    href={action.path}
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      p: 1.5,
                      borderRadius: 1,
                      bgcolor: alpha(theme.palette.primary.main, 0.05),
                      color: 'text.primary',
                      textDecoration: 'none',
                      '&:hover': {
                        bgcolor: alpha(theme.palette.primary.main, 0.1),
                      },
                    }}
                  >
                    <Typography variant="body2">{action.name}</Typography>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardPage;

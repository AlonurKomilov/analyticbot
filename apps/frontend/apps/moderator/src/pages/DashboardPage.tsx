import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Paper,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Button,
} from '@mui/material';
import {
  LibraryBooks as CatalogIcon,
  Category as CategoryIcon,
  Star as StarIcon,
  Verified as VerifiedIcon,
  TrendingUp as TrendingIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '@api/client';
import { API_ENDPOINTS } from '@config/api';
import { ROUTES } from '@config/routes';
import { PageSkeleton } from '../components/Skeletons';

interface CatalogStats {
  total_channels: number;
  featured_channels: number;
  verified_channels: number;
  active_channels: number;
  inactive_channels: number;
  total_categories: number;
}

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<CatalogStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await apiClient.get(API_ENDPOINTS.CATALOG.STATS);
        setStats(response.data);
      } catch (err: any) {
        setError(err.message || 'Failed to load stats');
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) {
    return <PageSkeleton />;
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Moderator Dashboard
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Welcome to the Public Catalog management panel
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => navigate(ROUTES.CATALOG)}
        >
          Add Channel
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Stats Cards */}
      {stats && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: 'primary.main', color: 'white' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CatalogIcon />
                  <Typography variant="h4" fontWeight={700}>
                    {stats.total_channels}
                  </Typography>
                </Box>
                <Typography variant="body2" sx={{ opacity: 0.9, mt: 1 }}>
                  Total Channels
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: 'warning.main', color: 'white' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <StarIcon />
                  <Typography variant="h4" fontWeight={700}>
                    {stats.featured_channels}
                  </Typography>
                </Box>
                <Typography variant="body2" sx={{ opacity: 0.9, mt: 1 }}>
                  Featured
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: 'success.main', color: 'white' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <VerifiedIcon />
                  <Typography variant="h4" fontWeight={700}>
                    {stats.verified_channels}
                  </Typography>
                </Box>
                <Typography variant="body2" sx={{ opacity: 0.9, mt: 1 }}>
                  Verified
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: 'info.main', color: 'white' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CategoryIcon />
                  <Typography variant="h4" fontWeight={700}>
                    {stats.total_categories}
                  </Typography>
                </Box>
                <Typography variant="body2" sx={{ opacity: 0.9, mt: 1 }}>
                  Categories
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Quick Actions */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Quick Actions
            </Typography>
            <List>
              <ListItem
                button
                onClick={() => navigate(ROUTES.CATALOG)}
                sx={{ borderRadius: 1 }}
              >
                <ListItemIcon>
                  <CatalogIcon color="primary" />
                </ListItemIcon>
                <ListItemText
                  primary="Manage Channels"
                  secondary="Add, edit, or remove channels from catalog"
                />
              </ListItem>
              <ListItem
                button
                onClick={() => navigate(ROUTES.CATEGORIES)}
                sx={{ borderRadius: 1 }}
              >
                <ListItemIcon>
                  <CategoryIcon color="primary" />
                </ListItemIcon>
                <ListItemText
                  primary="Manage Categories"
                  secondary="Create and organize channel categories"
                />
              </ListItem>
              <ListItem
                button
                onClick={() => navigate(ROUTES.FEATURED)}
                sx={{ borderRadius: 1 }}
              >
                <ListItemIcon>
                  <StarIcon color="warning" />
                </ListItemIcon>
                <ListItemText
                  primary="Featured Channels"
                  secondary="Manage homepage featured channels"
                />
              </ListItem>
            </List>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Catalog Status
            </Typography>
            <List>
              <ListItem>
                <ListItemIcon>
                  <TrendingIcon color="success" />
                </ListItemIcon>
                <ListItemText
                  primary="Active Channels"
                  secondary={`${stats?.active_channels || 0} channels visible to public`}
                />
                <Chip label={stats?.active_channels || 0} color="success" size="small" />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <TrendingIcon color="error" sx={{ transform: 'rotate(180deg)' }} />
                </ListItemIcon>
                <ListItemText
                  primary="Inactive Channels"
                  secondary={`${stats?.inactive_channels || 0} channels hidden`}
                />
                <Chip label={stats?.inactive_channels || 0} color="default" size="small" />
              </ListItem>
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardPage;

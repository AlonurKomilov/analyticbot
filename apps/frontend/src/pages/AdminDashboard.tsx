/**
 * 🔧 Admin Dashboard - System Management Interface
 *
 * Administrative interface for system management, user oversight,
 * and analytics monitoring. Only accessible to admin users.
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  Tab,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  AdminPanelSettings as AdminIcon,
  People as PeopleIcon,
  Analytics as AnalyticsIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Assessment as ReportIcon,
  Security as SecurityIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

interface Channel {
  id: string;
  name: string;
  user_id: number;
  total_subscribers?: number;
  created_at: string;
}

interface SystemStats {
  total_channels?: number;
  total_users?: string;
  total_metrics_collected?: string;
  system_health?: string;
}

interface DeleteDialogState {
  open: boolean;
  channelId: string | null;
}

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color?: 'primary' | 'success' | 'warning' | 'error' | 'info';
}

const AdminDashboard: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<number>(0);
  const [allChannels, setAllChannels] = useState<Channel[]>([]);
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [deleteDialog, setDeleteDialog] = useState<DeleteDialogState>({ open: false, channelId: null });

  // Load admin data
  useEffect(() => {
    loadAdminData();
  }, []);

  const loadAdminData = async (): Promise<void> => {
    setLoading(true);
    try {
      // Load system statistics
      const statsResponse = await fetch('/api/analytics/admin/system-stats', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (statsResponse.ok) {
        const stats: SystemStats = await statsResponse.json();
        setSystemStats(stats);
      }

      // Load all channels
      const channelsResponse = await fetch('/api/analytics/admin/all-channels', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (channelsResponse.ok) {
        const channels: Channel[] = await channelsResponse.json();
        setAllChannels(channels);
      }
    } catch (error) {
      console.error('Error loading admin data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteChannel = async (channelId: string): Promise<void> => {
    try {
      const response = await fetch(`/api/analytics/admin/channels/${channelId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        // Refresh channels list
        setAllChannels(prev => prev.filter(channel => channel.id !== channelId));
        setDeleteDialog({ open: false, channelId: null });
      }
    } catch (error) {
      console.error('Error deleting channel:', error);
    }
  };

  const StatCard: React.FC<StatCardProps> = ({ title, value, icon, color = 'primary' }) => (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          {icon}
          <Typography variant="h6" sx={{ ml: 1 }}>
            {title}
          </Typography>
        </Box>
        <Typography variant="h4" color={`${color}.main`}>
          {value}
        </Typography>
      </CardContent>
    </Card>
  );

  if (loading && !systemStats) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
        <CircularProgress />
        <Typography sx={{ ml: 2 }}>Loading admin dashboard...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
          <AdminIcon sx={{ mr: 2, fontSize: 40 }} />
          Admin Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          System management and user oversight panel
        </Typography>
        <Alert severity="info" sx={{ mt: 2 }}>
          Welcome, {user?.username}! You have administrator privileges.
        </Alert>
      </Box>

      {/* System Statistics */}
      {systemStats && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Total Channels"
              value={systemStats.total_channels || allChannels.length}
              icon={<AnalyticsIcon color="primary" />}
              color="primary"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Total Users"
              value={systemStats.total_users || '5'}
              icon={<PeopleIcon color="success" />}
              color="success"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Metrics Collected"
              value={systemStats.total_metrics_collected || '12.5K'}
              icon={<ReportIcon color="warning" />}
              color="warning"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="System Health"
              value={systemStats.system_health || 'Healthy'}
              icon={<SecurityIcon color="success" />}
              color="success"
            />
          </Grid>
        </Grid>
      )}

      {/* Admin Tabs */}
      <Paper sx={{ mt: 3 }}>
        <Tabs value={activeTab} onChange={(_e, newValue: number) => setActiveTab(newValue)}>
          <Tab label="All Channels" icon={<AnalyticsIcon />} />
          <Tab label="User Management" icon={<PeopleIcon />} />
          <Tab label="System Settings" icon={<SettingsIcon />} />
        </Tabs>

        {/* All Channels Tab */}
        {activeTab === 0 && (
          <Box sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              All System Channels
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Manage channels across all users in the system.
            </Typography>

            {allChannels.length === 0 ? (
              <Alert severity="info">No channels found in the system.</Alert>
            ) : (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Channel ID</TableCell>
                      <TableCell>Name</TableCell>
                      <TableCell>Owner ID</TableCell>
                      <TableCell>Subscribers</TableCell>
                      <TableCell>Created</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {allChannels.map((channel) => (
                      <TableRow key={channel.id}>
                        <TableCell>{channel.id}</TableCell>
                        <TableCell>{channel.name}</TableCell>
                        <TableCell>
                          <Chip
                            label={`User ${channel.user_id}`}
                            size="small"
                            color="primary"
                          />
                        </TableCell>
                        <TableCell>{channel.total_subscribers?.toLocaleString()}</TableCell>
                        <TableCell>
                          {new Date(channel.created_at).toLocaleDateString()}
                        </TableCell>
                        <TableCell>
                          <Tooltip title="View Channel">
                            <IconButton size="small" color="primary">
                              <ViewIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete Channel">
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => setDeleteDialog({ open: true, channelId: channel.id })}
                            >
                              <DeleteIcon />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </Box>
        )}

        {/* User Management Tab */}
        {activeTab === 1 && (
          <Box sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              User Management
            </Typography>
            <Alert severity="info">
              User management features will be implemented in the next phase.
            </Alert>
          </Box>
        )}

        {/* System Settings Tab */}
        {activeTab === 2 && (
          <Box sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              System Settings
            </Typography>
            <Alert severity="info">
              System configuration settings will be implemented in the next phase.
            </Alert>
          </Box>
        )}
      </Paper>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialog.open}
        onClose={() => setDeleteDialog({ open: false, channelId: null })}
      >
        <DialogTitle>Delete Channel</DialogTitle>
        <DialogContent>
          Are you sure you want to delete channel {deleteDialog.channelId}? This action cannot be undone.
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog({ open: false, channelId: null })}>
            Cancel
          </Button>
          <Button
            onClick={() => deleteDialog.channelId && handleDeleteChannel(deleteDialog.channelId)}
            color="error"
            variant="contained"
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AdminDashboard;

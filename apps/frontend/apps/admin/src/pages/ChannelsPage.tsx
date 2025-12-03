import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  CircularProgress,
  TextField,
  InputAdornment,
  Tooltip,
  TablePagination,
} from '@mui/material';
import {
  Search as SearchIcon,
  Visibility as ViewIcon,
  Delete as DeleteIcon,
  Sync as SyncIcon,
} from '@mui/icons-material';
import { apiClient } from '@api/client';
import { API_ENDPOINTS } from '@config/api';
import { format } from 'date-fns';

interface Channel {
  id: number;
  name: string;
  username: string;
  user_id: number;
  total_subscribers: number;
  status: string;
  created_at: string;
  last_sync: string | null;
}

const ChannelsPage: React.FC = () => {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  useEffect(() => {
    const fetchChannels = async () => {
      try {
        const response = await apiClient.get(API_ENDPOINTS.ADMIN.CHANNELS);
        setChannels(response.data.channels || response.data || []);
      } catch (error) {
        console.error('Failed to fetch channels:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchChannels();
  }, []);

  const filteredChannels = channels.filter(
    (channel) =>
      channel.name?.toLowerCase().includes(search.toLowerCase()) ||
      channel.username?.toLowerCase().includes(search.toLowerCase())
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'suspended': return 'error';
      case 'syncing': return 'info';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Channel Management
        </Typography>
        <Typography color="text.secondary">
          Manage all connected Telegram channels
        </Typography>
      </Box>

      {/* Search */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <TextField
          placeholder="Search channels..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          size="small"
          sx={{ minWidth: 300 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon color="action" />
              </InputAdornment>
            ),
          }}
        />
      </Paper>

      {/* Channels Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Username</TableCell>
              <TableCell>Owner ID</TableCell>
              <TableCell>Subscribers</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Last Sync</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredChannels
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((channel) => (
                <TableRow key={channel.id} hover>
                  <TableCell>{channel.id}</TableCell>
                  <TableCell sx={{ fontWeight: 500 }}>{channel.name || '-'}</TableCell>
                  <TableCell>@{channel.username || '-'}</TableCell>
                  <TableCell>{channel.user_id}</TableCell>
                  <TableCell>
                    {channel.total_subscribers?.toLocaleString() || 0}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={channel.status || 'active'}
                      size="small"
                      color={getStatusColor(channel.status) as any}
                    />
                  </TableCell>
                  <TableCell>
                    {channel.created_at
                      ? format(new Date(channel.created_at), 'MMM d, yyyy')
                      : '-'}
                  </TableCell>
                  <TableCell>
                    {channel.last_sync
                      ? format(new Date(channel.last_sync), 'MMM d, HH:mm')
                      : 'Never'}
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title="View Details">
                      <IconButton size="small">
                        <ViewIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Force Sync">
                      <IconButton size="small" color="info">
                        <SyncIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete Channel">
                      <IconButton size="small" color="error">
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
        <TablePagination
          component="div"
          count={filteredChannels.length}
          page={page}
          onPageChange={(_, newPage) => setPage(newPage)}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
        />
      </TableContainer>
    </Box>
  );
};

export default ChannelsPage;

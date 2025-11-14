/**
 * Storage Channel Manager Component
 *
 * UI for connecting and managing user-owned Telegram channels for file storage.
 * Displays connected channels, allows adding new channels, and shows storage stats.
 */

import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  TextField,
  Typography,
  Alert,
  CircularProgress,
  Stack,
  Divider,
} from '@mui/material';
import {
  Add as AddIcon,
  CloudUpload as CloudIcon,
  Delete as DeleteIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Storage as StorageIcon,
  Telegram as TelegramIcon,
} from '@mui/icons-material';
import { useTelegramStorageStore, selectTotalStorageUsedFormatted } from '@/store/slices/storage/useTelegramStorageStore';

export const StorageChannelManager: React.FC = () => {
  const {
    channels: channelsFromStore,
    isLoadingChannels,
    isValidating,
    error,
    fetchChannels,
    validateChannel,
    connectChannel,
    disconnectChannel,
    clearError,
  } = useTelegramStorageStore();

  // Ensure channels is always an array (defensive programming)
  const channels = Array.isArray(channelsFromStore) ? channelsFromStore : [];

  const totalStorageUsed = useTelegramStorageStore(selectTotalStorageUsedFormatted);

  const [dialogOpen, setDialogOpen] = useState(false);
  const [channelId, setChannelId] = useState('');
  const [channelUsername, setChannelUsername] = useState('');
  const [validationResult, setValidationResult] = useState<any>(null);
  const [validationError, setValidationError] = useState<string | null>(null);

  useEffect(() => {
    fetchChannels();
  }, [fetchChannels]);

  const handleOpenDialog = () => {
    setDialogOpen(true);
    setChannelId('');
    setChannelUsername('');
    setValidationResult(null);
    setValidationError(null);
    clearError();
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setValidationResult(null);
    setValidationError(null);
  };

  const handleValidate = async () => {
    if (!channelId) {
      setValidationError('Please enter a channel ID');
      return;
    }

    const numericChannelId = parseInt(channelId);
    if (isNaN(numericChannelId)) {
      setValidationError('Channel ID must be a number (e.g., -1001234567890)');
      return;
    }

    try {
      setValidationError(null);
      const result = await validateChannel(numericChannelId, channelUsername || undefined);
      setValidationResult(result);
    } catch (err: any) {
      setValidationError(err.message);
      setValidationResult(null);
    }
  };

  const handleConnect = async () => {
    if (!channelId || !validationResult) return;

    try {
      await connectChannel(parseInt(channelId), channelUsername || undefined);
      handleCloseDialog();
    } catch (err: any) {
      setValidationError(err.message);
    }
  };

  const handleDisconnect = async (channelDbId: number) => {
    if (confirm('Are you sure you want to disconnect this channel?')) {
      try {
        await disconnectChannel(channelDbId);
      } catch (err) {
        console.error('Failed to disconnect channel:', err);
      }
    }
  };

  return (
    <Box>
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h5" gutterBottom>
            <StorageIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Storage Channels
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Connect your Telegram channels for zero-cost file storage
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleOpenDialog}
          disabled={isLoadingChannels}
        >
          Add Channel
        </Button>
      </Stack>

      {/* Storage Stats */}
      {channels.length > 0 && (
        <Card sx={{ mb: 3, bgcolor: 'primary.50' }}>
          <CardContent>
            <Stack direction="row" spacing={4} alignItems="center">
              <Box>
                <Typography variant="h4" color="primary">
                  {channels.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Connected Channels
                </Typography>
              </Box>
              <Divider orientation="vertical" flexItem />
              <Box>
                <Typography variant="h4" color="primary">
                  {totalStorageUsed}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Storage Used
                </Typography>
              </Box>
              <Divider orientation="vertical" flexItem />
              <Box flex={1}>
                <Alert severity="success" icon={<CloudIcon />}>
                  All files stored in your Telegram channels - <strong>zero server costs!</strong>
                </Alert>
              </Box>
            </Stack>
          </CardContent>
        </Card>
      )}

      {/* Error Display */}
      {error && (
        <Alert severity="error" onClose={clearError} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Channels List */}
      {isLoadingChannels ? (
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      ) : channels.length === 0 ? (
        <Card>
          <CardContent>
            <Box textAlign="center" py={4}>
              <TelegramIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                No Storage Channels Connected
              </Typography>
              <Typography variant="body2" color="text.secondary" mb={3}>
                Connect your private Telegram channel to start uploading files
              </Typography>
              <Button variant="contained" startIcon={<AddIcon />} onClick={handleOpenDialog}>
                Connect Your First Channel
              </Button>
            </Box>
          </CardContent>
        </Card>
      ) : (
        <List>
          {channels.map((channel) => (
            <Card key={channel.id} sx={{ mb: 2 }}>
              <ListItem>
                <ListItemText
                  primary={
                    <Stack direction="row" spacing={1} alignItems="center">
                      <Typography variant="h6">{channel.channel_title}</Typography>
                      {channel.is_active && <Chip label="Active" color="success" size="small" />}
                      {channel.is_bot_admin && (
                        <Chip label="Bot Admin" color="primary" size="small" variant="outlined" />
                      )}
                    </Stack>
                  }
                  secondary={
                    <Box mt={1}>
                      <Typography variant="body2" color="text.secondary">
                        Channel ID: {channel.channel_id}
                        {channel.channel_username && ` • @${channel.channel_username}`}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Connected: {new Date(channel.created_at).toLocaleDateString()}
                        {channel.last_validated_at &&
                          ` • Last validated: ${new Date(channel.last_validated_at).toLocaleDateString()}`}
                      </Typography>
                    </Box>
                  }
                />
                <ListItemSecondaryAction>
                  <IconButton
                    edge="end"
                    aria-label="disconnect"
                    onClick={() => handleDisconnect(channel.id)}
                    color="error"
                  >
                    <DeleteIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            </Card>
          ))}
        </List>
      )}

      {/* Add Channel Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          <TelegramIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Connect Storage Channel
        </DialogTitle>
        <DialogContent>
          <Stack spacing={3} mt={2}>
            <Alert severity="info">
              <Typography variant="body2">
                <strong>Setup Instructions:</strong>
                <ol style={{ marginTop: 8, marginBottom: 0, paddingLeft: 20 }}>
                  <li>Create a private Telegram channel</li>
                  <li>Add the bot as admin with "Post Messages" permission</li>
                  <li>Get the channel ID (starts with -100)</li>
                  <li>Enter the details below and validate</li>
                </ol>
              </Typography>
            </Alert>

            <TextField
              label="Channel ID"
              placeholder="-1001234567890"
              value={channelId}
              onChange={(e) => setChannelId(e.target.value)}
              fullWidth
              required
              helperText="Numeric channel ID (e.g., -1001234567890)"
              error={!!validationError && !validationResult}
            />

            <TextField
              label="Channel Username (Optional)"
              placeholder="my_storage_channel"
              value={channelUsername}
              onChange={(e) => setChannelUsername(e.target.value)}
              fullWidth
              helperText="Username without @ (if channel is public)"
            />

            <Button
              variant="outlined"
              onClick={handleValidate}
              disabled={!channelId || isValidating}
              startIcon={isValidating ? <CircularProgress size={20} /> : null}
            >
              {isValidating ? 'Validating...' : 'Validate Channel'}
            </Button>

            {/* Validation Result */}
            {validationResult && (
              <Alert severity="success" icon={<CheckIcon />}>
                <Typography variant="body2">
                  <strong>✓ Channel Validated Successfully</strong>
                </Typography>
                <Typography variant="body2" sx={{ mt: 1 }}>
                  Channel: <strong>{validationResult.channel_title}</strong>
                  <br />
                  Members: {validationResult.member_count}
                  <br />
                  Bot has admin access: {validationResult.bot_is_admin ? 'Yes' : 'No'}
                </Typography>
              </Alert>
            )}

            {validationError && (
              <Alert severity="error" icon={<ErrorIcon />}>
                {validationError}
              </Alert>
            )}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={handleConnect}
            variant="contained"
            disabled={!validationResult || isValidating}
          >
            Connect Channel
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

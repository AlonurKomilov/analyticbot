/**
 * User Bot Dashboard Component
 * Display bot status, controls, and statistics
 */

import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Grid,
  IconButton,
  Paper,
  TextField,
  Typography,
  Alert,
} from '@mui/material';
import {
  SmartToy,
  Delete,
  Settings,
  Refresh,
  CheckCircle,
  Error,
  Warning,
  HourglassEmpty,
  Send,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useUserBotStore } from '@/store';
import { BotStatus } from '@/types';
import toast from 'react-hot-toast';
import { format } from 'date-fns';

export const UserBotDashboard: React.FC = () => {
  const navigate = useNavigate();
  const {
    bot,
    fetchBotStatus,
    removeBot,
    updateRateLimits,
    verifyBot,
    isLoading,
    isRemoving,
    isUpdating,
    isVerifying,
    error,
    clearError,
  } = useUserBotStore();

  const [showRemoveDialog, setShowRemoveDialog] = useState(false);
  const [showRateLimitDialog, setShowRateLimitDialog] = useState(false);
  const [showTestMessageDialog, setShowTestMessageDialog] = useState(false);
  const [testMessage, setTestMessage] = useState('Hello! This is a test message from your bot.');
  const [testChatId, setTestChatId] = useState('');
  const [rateLimitRps, setRateLimitRps] = useState('');
  const [maxConcurrent, setMaxConcurrent] = useState('');

  // Fetch bot status only once on mount
  useEffect(() => {
    const loadBotStatus = async () => {
      // Skip if already loading or if we already have data
      if (isLoading || bot) {
        return;
      }

      try {
        const result = await fetchBotStatus();
        if (result) {
          toast.success('✅ Bot status loaded');
        }
      } catch (err) {
        // Error already handled in store, just log
        console.error('Failed to load bot status:', err);
      }
    };
    loadBotStatus();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Empty dependency array - only run once on mount

  useEffect(() => {
    if (bot) {
      setRateLimitRps(bot.max_requests_per_second.toString());
      setMaxConcurrent(bot.max_concurrent_requests.toString());
    }
  }, [bot]);

  const handleRefresh = async () => {
    try {
      await fetchBotStatus();
      toast.success('✅ Bot status updated');
    } catch (err) {
      toast.error('Failed to refresh bot status');
    }
  };

  const handleRemoveBot = async () => {
    try {
      await removeBot();
      toast.success('Bot removed successfully');
      setShowRemoveDialog(false);
      navigate('/bot/setup');
    } catch (err) {
      toast.error('Failed to remove bot');
    }
  };

  const handleUpdateRateLimits = async () => {
    try {
      const rps = parseFloat(rateLimitRps);
      const concurrent = parseInt(maxConcurrent);

      if (isNaN(rps) || rps <= 0) {
        toast.error('RPS must be a positive number');
        return;
      }

      if (isNaN(concurrent) || concurrent <= 0) {
        toast.error('Max concurrent must be a positive integer');
        return;
      }

      await updateRateLimits({
        max_requests_per_second: rps,
        max_concurrent_requests: concurrent,
      });
      toast.success('Rate limits updated successfully');
      setShowRateLimitDialog(false);
    } catch (err) {
      toast.error('Failed to update rate limits');
    }
  };

  const handleSendTestMessage = async () => {
    if (!testChatId.trim()) {
      toast.error('Please enter your Telegram chat ID');
      return;
    }

    const chatId = parseInt(testChatId, 10);
    if (isNaN(chatId)) {
      toast.error('Invalid chat ID. Please enter a valid number.');
      return;
    }

    try {
      await verifyBot({
        send_test_message: true,
        test_chat_id: chatId,
        test_message: testMessage,
      });

      toast.success('✅ Test message sent successfully! Check your Telegram.');
      setShowTestMessageDialog(false);
      setTestChatId(''); // Clear for next time
    } catch (err: any) {
      const errorMsg = err?.response?.data?.detail || err?.message || 'Failed to send test message';
      toast.error(`❌ ${errorMsg}`);
    }
  };

  const getStatusIcon = (status: BotStatus) => {
    switch (status) {
      case BotStatus.ACTIVE:
        return <CheckCircle color="success" />;
      case BotStatus.SUSPENDED:
        return <Error color="error" />;
      case BotStatus.RATE_LIMITED:
        return <Warning color="warning" />;
      case BotStatus.PENDING:
        return <HourglassEmpty color="info" />;
      default:
        return <Error color="error" />;
    }
  };

  const getStatusColor = (status: BotStatus): 'success' | 'error' | 'warning' | 'info' | 'default' => {
    switch (status) {
      case BotStatus.ACTIVE:
        return 'success';
      case BotStatus.SUSPENDED:
        return 'error';
      case BotStatus.RATE_LIMITED:
        return 'warning';
      case BotStatus.PENDING:
        return 'info';
      default:
        return 'default';
    }
  };

  if (isLoading && !bot) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (!bot && !isLoading) {
    return (
      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <SmartToy sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h5" gutterBottom>
          No Bot Configured
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          You haven't set up a bot yet. Create one to get started!
        </Typography>
        <Button variant="contained" onClick={() => navigate('/bot/setup')}>
          Setup Bot
        </Button>
      </Paper>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          My Bot Dashboard
        </Typography>
        <Box>
          <IconButton onClick={handleRefresh} disabled={isLoading}>
            <Refresh />
          </IconButton>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={clearError}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Bot Status Card */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <SmartToy sx={{ mr: 1, fontSize: 32 }} />
                <Typography variant="h6">Bot Information</Typography>
              </Box>

              <Box mb={2}>
                <Typography variant="body2" color="text.secondary">
                  Username
                </Typography>
                <Typography variant="body1" fontWeight="bold">
                  @{bot?.bot_username || 'Unknown'}
                </Typography>
              </Box>

              <Box mb={2}>
                <Typography variant="body2" color="text.secondary">
                  Bot ID
                </Typography>
                <Typography variant="body1">{bot?.bot_id || 'N/A'}</Typography>
              </Box>

              <Box mb={2}>
                <Typography variant="body2" color="text.secondary">
                  Status
                </Typography>
                <Box display="flex" alignItems="center" mt={1}>
                  {bot && getStatusIcon(bot.status)}
                  <Chip
                    label={bot?.status.toUpperCase()}
                    color={bot ? getStatusColor(bot.status) : 'default'}
                    size="small"
                    sx={{ ml: 1 }}
                  />
                  {bot?.is_verified && (
                    <Chip label="VERIFIED" color="success" size="small" sx={{ ml: 1 }} />
                  )}
                </Box>
              </Box>

              {bot?.suspension_reason && (
                <Alert severity="warning" sx={{ mt: 2 }}>
                  <Typography variant="body2" fontWeight="bold">
                    Suspension Reason:
                  </Typography>
                  <Typography variant="body2">{bot.suspension_reason}</Typography>
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Statistics Card */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Settings sx={{ mr: 1, fontSize: 32 }} />
                <Typography variant="h6">Configuration & Stats</Typography>
              </Box>

              <Box mb={2}>
                <Typography variant="body2" color="text.secondary">
                  Rate Limit (RPS)
                </Typography>
                <Typography variant="h5">{bot?.max_requests_per_second}</Typography>
              </Box>

              <Box mb={2}>
                <Typography variant="body2" color="text.secondary">
                  Max Concurrent Requests
                </Typography>
                <Typography variant="h5">{bot?.max_concurrent_requests}</Typography>
              </Box>

              <Box mb={2}>
                <Typography variant="body2" color="text.secondary">
                  Total Requests
                </Typography>
                <Typography variant="h5">{bot?.total_requests.toLocaleString()}</Typography>
              </Box>

              <Box>
                <Typography variant="body2" color="text.secondary">
                  Last Used
                </Typography>
                <Typography variant="body1">
                  {bot?.last_used_at
                    ? format(new Date(bot.last_used_at), 'PPpp')
                    : 'Never'}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Timeline Card */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" mb={2}>
                Timeline
              </Typography>

              <Box display="flex" justifyContent="space-between" mb={2}>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Created
                  </Typography>
                  <Typography variant="body1">
                    {bot?.created_at && format(new Date(bot.created_at), 'PPpp')}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Last Updated
                  </Typography>
                  <Typography variant="body1">
                    {bot?.updated_at && format(new Date(bot.updated_at), 'PPpp')}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Actions Card */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" mb={2}>
                Actions
              </Typography>
              <Box display="flex" gap={2} flexWrap="wrap">
                <Button
                  variant="contained"
                  startIcon={<Send />}
                  onClick={() => setShowTestMessageDialog(true)}
                  color="primary"
                >
                  Send Test Message
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Settings />}
                  onClick={() => setShowRateLimitDialog(true)}
                  disabled={isUpdating}
                >
                  Update Rate Limits
                </Button>
                <Button
                  variant="outlined"
                  color="error"
                  startIcon={<Delete />}
                  onClick={() => setShowRemoveDialog(true)}
                  disabled={isRemoving}
                >
                  Remove Bot
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Remove Bot Dialog */}
      <Dialog open={showRemoveDialog} onClose={() => setShowRemoveDialog(false)}>
        <DialogTitle>Remove Bot?</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to remove your bot? This action cannot be undone. All bot data
            and configurations will be permanently deleted.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowRemoveDialog(false)}>Cancel</Button>
          <Button onClick={handleRemoveBot} color="error" disabled={isRemoving}>
            {isRemoving ? 'Removing...' : 'Remove Bot'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Update Rate Limits Dialog */}
      <Dialog open={showRateLimitDialog} onClose={() => setShowRateLimitDialog(false)}>
        <DialogTitle>Update Rate Limits</DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ mb: 2 }}>
            Configure the rate limiting settings for your bot.
          </DialogContentText>
          <TextField
            fullWidth
            label="Requests Per Second (RPS)"
            value={rateLimitRps}
            onChange={(e) => setRateLimitRps(e.target.value)}
            type="number"
            sx={{ mb: 2 }}
            helperText="Maximum requests per second"
          />
          <TextField
            fullWidth
            label="Max Concurrent Requests"
            value={maxConcurrent}
            onChange={(e) => setMaxConcurrent(e.target.value)}
            type="number"
            helperText="Maximum concurrent requests"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowRateLimitDialog(false)}>Cancel</Button>
          <Button onClick={handleUpdateRateLimits} variant="contained" disabled={isUpdating}>
            {isUpdating ? 'Updating...' : 'Update'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Send Test Message Dialog */}
      <Dialog open={showTestMessageDialog} onClose={() => setShowTestMessageDialog(false)}>
        <DialogTitle>Send Test Message</DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ mb: 2 }}>
            Send a test message to verify your bot is working correctly.
          </DialogContentText>
          <TextField
            fullWidth
            label="Your Telegram Chat ID"
            value={testChatId}
            onChange={(e) => setTestChatId(e.target.value)}
            type="number"
            sx={{ mb: 2 }}
            helperText="Get your chat ID by messaging @userinfobot on Telegram"
            required
          />
          <TextField
            fullWidth
            label="Test Message"
            value={testMessage}
            onChange={(e) => setTestMessage(e.target.value)}
            multiline
            rows={3}
            helperText="Message to send from your bot"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowTestMessageDialog(false)} disabled={isVerifying}>
            Cancel
          </Button>
          <Button
            onClick={handleSendTestMessage}
            variant="contained"
            startIcon={isVerifying ? <CircularProgress size={20} /> : <Send />}
            disabled={isVerifying}
          >
            {isVerifying ? 'Sending...' : 'Send Message'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

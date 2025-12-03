/**
 * User Bot Dashboard Component
 * Display bot status, controls, and statistics
 *
 * Refactored: Components and hooks extracted for better maintainability
 */

import React from 'react';
import {
  Box,
  Button,
  CircularProgress,
  Grid,
  IconButton,
  Paper,
  Typography,
  Alert,
} from '@mui/material';
import { SmartToy, Refresh } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  RemoveBotDialog,
  RateLimitDialog,
  TestMessageDialog,
} from '../dialogs';
import { useBotDashboard } from './hooks';
import { BotInfoCard } from './BotInfoCard';
import { BotStatsCard } from './BotStatsCard';
import { BotTimelineCard } from './BotTimelineCard';
import { BotActionsCard } from './BotActionsCard';
import { convertChannelToChatId } from './utils';

export const UserBotDashboard: React.FC = () => {
  const navigate = useNavigate();
  const {
    bot,
    channels,
    error,
    clearError,
    isLoading,
    isLoadingChannels,
    isRemoving,
    isUpdating,
    isVerifying,
    fetchBotStatus,
    removeBot,
    updateRateLimits,
    verifyBot,
    dialogs,
    openDialog,
    closeDialog,
    testMessageState,
    setTestMessageState,
    rateLimitState,
    setRateLimitState,
  } = useBotDashboard();

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
      closeDialog('showRemoveDialog');
      navigate('/bot/setup');
    } catch (err) {
      toast.error('Failed to remove bot');
    }
  };

  const handleUpdateRateLimits = async () => {
    try {
      const rps = parseFloat(rateLimitState.rateLimitRps);
      const concurrent = parseInt(rateLimitState.maxConcurrent);

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
      closeDialog('showRateLimitDialog');
    } catch (err) {
      toast.error('Failed to update rate limits');
    }
  };

  const handleSendTestMessage = async () => {
    let chatId: number;
    const { useManualInput, manualChatId, selectedChannelId, testMessage } = testMessageState;

    if (useManualInput) {
      if (!manualChatId.trim()) {
        toast.error('Please enter your Telegram chat ID');
        return;
      }
      const parsedId = parseInt(manualChatId, 10);
      if (isNaN(parsedId)) {
        toast.error('Invalid chat ID. Please enter a valid number.');
        return;
      }
      chatId = parsedId;
    } else {
      if (!selectedChannelId) {
        toast.error('Please select a channel');
        return;
      }
      const selectedChannel = channels.find(ch => ch.id === selectedChannelId);
      if (!selectedChannel) {
        toast.error('Selected channel not found');
        return;
      }

      const convertedId = convertChannelToChatId(selectedChannel.telegramId);
      if (convertedId === null) {
        toast.error('Invalid channel ID format');
        return;
      }
      chatId = convertedId;
    }

    try {
      await verifyBot({
        send_test_message: true,
        test_chat_id: chatId,
        test_message: testMessage,
      });

      toast.success('✅ Test message sent successfully! Check your Telegram.');
      closeDialog('showTestMessageDialog');
      setTestMessageState(prev => ({
        ...prev,
        selectedChannelId: '',
        manualChatId: '',
      }));
    } catch (err: any) {
      const errorMsg = err?.response?.data?.detail || err?.message || 'Failed to send test message';
      toast.error(`❌ ${errorMsg}`);
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
        <Grid item xs={12} md={6}>
          {bot && <BotInfoCard bot={bot} />}
        </Grid>

        <Grid item xs={12} md={6}>
          {bot && <BotStatsCard bot={bot} />}
        </Grid>

        <Grid item xs={12}>
          {bot && <BotTimelineCard bot={bot} />}
        </Grid>

        <Grid item xs={12}>
          <BotActionsCard
            onSendTestMessage={() => openDialog('showTestMessageDialog')}
            onUpdateRateLimits={() => openDialog('showRateLimitDialog')}
            onRemoveBot={() => openDialog('showRemoveDialog')}
            isUpdating={isUpdating}
            isRemoving={isRemoving}
          />
        </Grid>
      </Grid>

      {/* Dialogs */}
      <RemoveBotDialog
        open={dialogs.showRemoveDialog}
        onClose={() => closeDialog('showRemoveDialog')}
        onConfirm={handleRemoveBot}
        isRemoving={isRemoving}
      />

      <RateLimitDialog
        open={dialogs.showRateLimitDialog}
        onClose={() => closeDialog('showRateLimitDialog')}
        onConfirm={handleUpdateRateLimits}
        rateLimitRps={rateLimitState.rateLimitRps}
        setRateLimitRps={(v) => setRateLimitState(prev => ({ ...prev, rateLimitRps: v }))}
        maxConcurrent={rateLimitState.maxConcurrent}
        setMaxConcurrent={(v) => setRateLimitState(prev => ({ ...prev, maxConcurrent: v }))}
        isUpdating={isUpdating}
      />

      <TestMessageDialog
        open={dialogs.showTestMessageDialog}
        onClose={() => closeDialog('showTestMessageDialog')}
        onSend={handleSendTestMessage}
        channels={channels}
        isLoadingChannels={isLoadingChannels}
        selectedChannelId={testMessageState.selectedChannelId}
        setSelectedChannelId={(v) => setTestMessageState(prev => ({ ...prev, selectedChannelId: v }))}
        manualChatId={testMessageState.manualChatId}
        setManualChatId={(v) => setTestMessageState(prev => ({ ...prev, manualChatId: v }))}
        useManualInput={testMessageState.useManualInput}
        setUseManualInput={(v) => setTestMessageState(prev => ({ ...prev, useManualInput: v }))}
        testMessage={testMessageState.testMessage}
        setTestMessage={(v) => setTestMessageState(prev => ({ ...prev, testMessage: v }))}
        isVerifying={isVerifying}
      />
    </Box>
  );
};

export default UserBotDashboard;

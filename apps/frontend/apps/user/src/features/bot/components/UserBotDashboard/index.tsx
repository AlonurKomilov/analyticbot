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
import { useBotDashboard, useBotServices } from './hooks';
import { BotInfoCard } from './BotInfoCard';
import { BotStatsCard } from './BotStatsCard';
import { BotTimelineCard } from './BotTimelineCard';
import { BotActionsCard } from './BotActionsCard';
import { ActiveServicesCard } from './ActiveServicesCard';
import { AvailableUpgradesCard } from './AvailableUpgradesCard';
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

  // Fetch user's active services and available upgrades
  const {
    activeServices,
    availableServices,
    activeServiceKeys,
    isLoading: isLoadingServices,
    refetch: refetchServices,
  } = useBotServices();

  const handleRefresh = async () => {
    try {
      await Promise.all([fetchBotStatus(), refetchServices()]);
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
    console.log('[UserBotDashboard] handleSendTestMessage called - checking for Telegram ID');
    try {
      // Try to send test message directly (will use user's telegram_id if available)
      const response = await verifyBot({
        send_test_message: true,
        // Don't provide test_chat_id - backend will use user's telegram_id automatically
      });

      // Check if the operation was successful
      if (response.success) {
        toast.success('✅ Test message sent! Check your Telegram messages.');
        // Refresh bot status to update total_requests count
        await fetchBotStatus();
      } else {
        // Backend returned success=false with a message
        toast.error(`❌ ${response.message}`);
      }
    } catch (err: any) {
      console.error('[UserBotDashboard] Send test message failed:', err);
      const errorMsg = err?.response?.data?.detail || err?.message || '';
      
      // Check if error is because user doesn't have telegram_id
      if (errorMsg.includes('logged in with email') || errorMsg.includes('Telegram ID not found')) {
        // User logged in via email - show manual input dialog
        console.log('[UserBotDashboard] User has no telegram_id, opening manual dialog');
        toast((t) => (
          <div>
            <strong>⚠️ Telegram ID Not Found</strong>
            <br />
            <span style={{ fontSize: '0.9em' }}>
              We couldn't find your Telegram ID because you logged in with email.
              <br />
              Please enter your Telegram ID manually to send test messages.
            </span>
          </div>
        ), {
          duration: 6000,
          style: {
            background: '#1976d2',
            color: 'white',
          },
        });
        // Force manual input mode for email users
        setTestMessageState(prev => ({ ...prev, useManualInput: true }));
        openDialog('showTestMessageDialog');
      } else {
        // Other error - show error message
        toast.error(`❌ ${errorMsg}`);
      }
    }
  };

  const handleSendTestMessageWithChatId = async () => {
    const { manualChatId, testMessage } = testMessageState;

    // Validate Telegram ID input
    if (!manualChatId.trim()) {
      toast.error('Please enter your Telegram ID');
      return;
    }
    
    const chatId = parseInt(manualChatId, 10);
    if (isNaN(chatId)) {
      toast.error('Invalid Telegram ID. Please enter a valid number.');
      return;
    }

    try {
      const response = await verifyBot({
        send_test_message: true,
        test_chat_id: chatId,
        test_message: testMessage,
      });

      // Check if the operation was successful
      if (response.success) {
        toast.success('✅ Test message sent successfully! Check your Telegram.');
        closeDialog('showTestMessageDialog');
        setTestMessageState(prev => ({
          ...prev,
          manualChatId: '',
        }));
        // Refresh bot status to update total_requests count
        await fetchBotStatus();
      } else {
        // Backend returned success=false with a message
        toast.error(`❌ ${response.message}`);
      }
    } catch (err: any) {
      const errorMsg = err?.response?.data?.detail || err?.message || 'Failed to send test message';
      toast.error(`❌ ${errorMsg}`);
    }
  };

  const handleVerifyBot = async () => {
    console.log('[UserBotDashboard] handleVerifyBot called');
    try {
      console.log('[UserBotDashboard] Calling verifyBot API...');
      await verifyBot({
        send_test_message: false,
      });
      console.log('[UserBotDashboard] Verify successful');
      toast.success('✅ Bot verified successfully!');
      await fetchBotStatus();
    } catch (err: any) {
      console.error('[UserBotDashboard] Verify failed:', err);
      const errorMsg = err?.response?.data?.detail || err?.message || 'Failed to verify bot';
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
        {/* Bot Info & Stats Row */}
        <Grid item xs={12} md={6}>
          {bot && <BotInfoCard bot={bot} onVerify={handleVerifyBot} isVerifying={isVerifying} />}
        </Grid>

        <Grid item xs={12} md={6}>
          {bot && <BotStatsCard bot={bot} />}
        </Grid>

        {/* Active Power-Ups Section */}
        <Grid item xs={12}>
          <ActiveServicesCard
            services={activeServices}
            isLoading={isLoadingServices}
          />
        </Grid>

        {/* Available Upgrades Section */}
        <Grid item xs={12}>
          <AvailableUpgradesCard
            services={availableServices}
            activeServiceKeys={activeServiceKeys}
            isLoading={isLoadingServices}
          />
        </Grid>

        {/* Timeline */}
        <Grid item xs={12}>
          {bot && <BotTimelineCard bot={bot} />}
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12}>
          {/* Important: Start Bot First Info */}
          {bot && !bot.is_verified && (
            <Alert severity="info" sx={{ mb: 2 }}>
              <strong>Before sending test messages:</strong> You must start your bot first!
              <br />
              1. Open Telegram and search for <strong>@{bot.bot_username}</strong>
              <br />
              2. Click the <strong>START</strong> button to begin a conversation
              <br />
              3. Then come back here and click "Send Test Message"
            </Alert>
          )}
          
          <BotActionsCard
            onSendTestMessage={handleSendTestMessage}
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
        onSend={handleSendTestMessageWithChatId}
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

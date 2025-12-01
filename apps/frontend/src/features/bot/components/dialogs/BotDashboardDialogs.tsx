/**
 * User Bot Dashboard Dialogs
 * Extracted dialog components for better maintainability
 */
import React from 'react';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  CircularProgress,
  Alert,
} from '@mui/material';
import { Send } from '@mui/icons-material';
import type { Channel } from '@/types';

// ============================================================================
// Remove Bot Dialog
// ============================================================================

interface RemoveBotDialogProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  isRemoving: boolean;
}

export const RemoveBotDialog: React.FC<RemoveBotDialogProps> = ({
  open,
  onClose,
  onConfirm,
  isRemoving,
}) => {
  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>Remove Bot?</DialogTitle>
      <DialogContent>
        <DialogContentText>
          Are you sure you want to remove your bot? This action cannot be undone. All bot data
          and configurations will be permanently deleted.
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={onConfirm} color="error" disabled={isRemoving}>
          {isRemoving ? 'Removing...' : 'Remove Bot'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

// ============================================================================
// Rate Limit Dialog
// ============================================================================

interface RateLimitDialogProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  rateLimitRps: string;
  setRateLimitRps: (value: string) => void;
  maxConcurrent: string;
  setMaxConcurrent: (value: string) => void;
  isUpdating: boolean;
}

export const RateLimitDialog: React.FC<RateLimitDialogProps> = ({
  open,
  onClose,
  onConfirm,
  rateLimitRps,
  setRateLimitRps,
  maxConcurrent,
  setMaxConcurrent,
  isUpdating,
}) => {
  return (
    <Dialog open={open} onClose={onClose}>
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
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={onConfirm} variant="contained" disabled={isUpdating}>
          {isUpdating ? 'Updating...' : 'Update'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

// ============================================================================
// Test Message Dialog
// ============================================================================

interface TestMessageDialogProps {
  open: boolean;
  onClose: () => void;
  onSend: () => void;
  channels: Channel[];
  isLoadingChannels: boolean;
  selectedChannelId: string;
  setSelectedChannelId: (value: string) => void;
  manualChatId: string;
  setManualChatId: (value: string) => void;
  useManualInput: boolean;
  setUseManualInput: (value: boolean) => void;
  testMessage: string;
  setTestMessage: (value: string) => void;
  isVerifying: boolean;
}

export const TestMessageDialog: React.FC<TestMessageDialogProps> = ({
  open,
  onClose,
  onSend,
  channels,
  isLoadingChannels,
  selectedChannelId,
  setSelectedChannelId,
  manualChatId,
  setManualChatId,
  useManualInput,
  setUseManualInput,
  testMessage,
  setTestMessage,
  isVerifying,
}) => {
  const canSend = !isVerifying && 
    ((!useManualInput && selectedChannelId) || (useManualInput && manualChatId));

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Send Test Message</DialogTitle>
      <DialogContent>
        <DialogContentText sx={{ mb: 2 }}>
          Send a test message to verify your bot is working correctly.
        </DialogContentText>

        {/* Channel Selector or Manual Input Toggle */}
        <Box sx={{ mb: 2 }}>
          <Button
            size="small"
            onClick={() => setUseManualInput(!useManualInput)}
            sx={{ mb: 1 }}
          >
            {useManualInput ? '📋 Use Channel Selector' : '✏️ Enter Chat ID Manually'}
          </Button>
        </Box>

        {!useManualInput ? (
          // Channel Selector Mode
          <>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel id="channel-select-label">Select Channel</InputLabel>
              <Select
                labelId="channel-select-label"
                value={selectedChannelId}
                onChange={(e) => setSelectedChannelId(e.target.value)}
                label="Select Channel"
                disabled={isLoadingChannels}
              >
                {isLoadingChannels ? (
                  <MenuItem disabled>
                    <CircularProgress size={20} sx={{ mr: 1 }} />
                    Loading channels...
                  </MenuItem>
                ) : channels.length === 0 ? (
                  <MenuItem disabled>
                    No channels found. Add channels in the Channels page first.
                  </MenuItem>
                ) : channels.filter(ch => ch.isActive).length === 0 ? (
                  <MenuItem disabled>
                    No active channels found. Please activate a channel first.
                  </MenuItem>
                ) : (
                  channels
                    .filter(ch => ch.isActive)
                    .map((channel) => (
                      <MenuItem key={channel.id} value={channel.id}>
                        {channel.username ? `@${channel.username}` : channel.name}
                        {channel.subscriberCount > 0 && ` (${channel.subscriberCount.toLocaleString()} subscribers)`}
                      </MenuItem>
                    ))
                )}
              </Select>
            </FormControl>
            {channels.length === 0 && !isLoadingChannels && (
              <Alert severity="info" sx={{ mb: 2 }}>
                No channels found. You can either add channels in the Channels page or use manual input below.
              </Alert>
            )}
          </>
        ) : (
          // Manual Input Mode
          <TextField
            fullWidth
            label="Your Telegram Chat ID"
            value={manualChatId}
            onChange={(e) => setManualChatId(e.target.value)}
            type="number"
            sx={{ mb: 2 }}
            helperText="Get your chat ID by messaging @userinfobot on Telegram"
            required
          />
        )}

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
        <Button onClick={onClose} disabled={isVerifying}>
          Cancel
        </Button>
        <Button
          onClick={onSend}
          variant="contained"
          startIcon={isVerifying ? <CircularProgress size={20} /> : <Send />}
          disabled={!canSend}
        >
          {isVerifying ? 'Sending...' : 'Send Message'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

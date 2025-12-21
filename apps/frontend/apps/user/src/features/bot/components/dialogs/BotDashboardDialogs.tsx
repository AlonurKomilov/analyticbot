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
  const canSend = !isVerifying && manualChatId;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Send Test Message</DialogTitle>
      <DialogContent>
        <DialogContentText sx={{ mb: 2 }}>
          <strong>📱 Enter Your Telegram ID</strong>
          <br />
          To test your bot, please follow these steps:
          <br />
          1. Open Telegram and message <strong>@userinfobot</strong>
          <br />
          2. Copy your Telegram ID (the number shown)
          <br />
          3. Paste it in the field below
          <br />
          4. Make sure you've started a chat with your bot first!
        </DialogContentText>

        {/* Manual Telegram ID Input */}
        <TextField
          fullWidth
          label="Your Telegram ID"
          value={manualChatId}
          onChange={(e) => setManualChatId(e.target.value)}
          type="number"
          sx={{ mb: 2 }}
          helperText="Get your Telegram ID by messaging @userinfobot on Telegram"
          required
          error={!manualChatId}
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

/**
 * MTProto Account Info Card Component
 * Shows user's MTProto configuration details and management actions
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Chip,
  Divider,
  Switch,
  FormControlLabel,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Stack,
  Tooltip,
  IconButton,
} from '@mui/material';
import {
  AccountCircle,
  Phone as PhoneIcon,
  Key as KeyIcon,
  Delete as DeleteIcon,
  PowerSettingsNew as DisconnectIcon,
  CheckCircle,
  Cancel,
  Visibility,
  VisibilityOff,
  ContentCopy,
  Settings as SettingsIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { apiClient } from '@/api/client';

interface MTProtoStatus {
  configured: boolean;
  verified: boolean;
  phone: string | null;
  api_id: number | null;
  connected: boolean;
  actively_connected?: boolean;
  last_used: string | null;
  can_read_history: boolean;
  mtproto_enabled?: boolean;
}

interface AccountInfoCardProps {
  onStatusChange?: () => void;
}

export const AccountInfoCard: React.FC<AccountInfoCardProps> = ({ onStatusChange }) => {
  const [status, setStatus] = useState<MTProtoStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Action states
  const [isToggling, setIsToggling] = useState(false);
  const [isDisconnecting, setIsDisconnecting] = useState(false);
  const [isRemoving, setIsRemoving] = useState(false);
  
  // UI states
  const [showPhone, setShowPhone] = useState(false);
  const [removeDialogOpen, setRemoveDialogOpen] = useState(false);

  const fetchStatus = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get<MTProtoStatus>('/user-mtproto/status');
      setStatus(response);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch MTProto status');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleToggle = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const enabled = event.target.checked;
    try {
      setIsToggling(true);
      setError(null);
      await apiClient.post('/user-mtproto/toggle', { enabled });
      setSuccess(enabled ? 'MTProto enabled successfully!' : 'MTProto disabled');
      await fetchStatus();
      onStatusChange?.();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to toggle MTProto');
    } finally {
      setIsToggling(false);
    }
  };

  const handleDisconnect = async () => {
    try {
      setIsDisconnecting(true);
      setError(null);
      await apiClient.post('/user-mtproto/disconnect', {});
      setSuccess('MTProto disconnected. Session file preserved.');
      await fetchStatus();
      onStatusChange?.();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to disconnect');
    } finally {
      setIsDisconnecting(false);
    }
  };

  const handleRemove = async () => {
    try {
      setIsRemoving(true);
      setError(null);
      await apiClient.delete('/user-mtproto/remove');
      setSuccess('MTProto configuration removed completely');
      setRemoveDialogOpen(false);
      await fetchStatus();
      onStatusChange?.();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to remove configuration');
    } finally {
      setIsRemoving(false);
    }
  };

  const maskPhone = (phone: string | null): string => {
    if (!phone) return 'Not set';
    if (showPhone) return phone;
    // Show first 4 and last 2 digits
    if (phone.length > 6) {
      return phone.slice(0, 4) + '****' + phone.slice(-2);
    }
    return '****';
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setSuccess('Copied to clipboard!');
    setTimeout(() => setSuccess(null), 2000);
  };

  if (loading) {
    return (
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="center" py={3}>
            <CircularProgress size={24} />
            <Typography sx={{ ml: 2 }}>Loading account info...</Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (!status?.configured) {
    return (
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <SettingsIcon color="action" />
            <Typography variant="h6">MTProto Configuration</Typography>
          </Box>
          <Alert severity="info">
            MTProto is not configured yet. Go to MTProto Setup to connect your Telegram account.
          </Alert>
          <Button
            variant="contained"
            href="/mtproto-setup"
            sx={{ mt: 2 }}
          >
            Configure MTProto
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box display="flex" alignItems="center" gap={1} mb={2}>
          <AccountCircle color="primary" />
          <Typography variant="h6">MTProto Account</Typography>
          <Box flexGrow={1} />
          {/* Global Enable/Disable Toggle */}
          <FormControlLabel
            control={
              <Switch
                checked={status.mtproto_enabled ?? false}
                onChange={handleToggle}
                disabled={isToggling}
                color="success"
              />
            }
            label={
              <Typography variant="body2" color={status.mtproto_enabled ? 'success.main' : 'text.secondary'}>
                {status.mtproto_enabled ? 'Enabled' : 'Disabled'}
              </Typography>
            }
          />
        </Box>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Your Telegram MTProto configuration and management
        </Typography>
        <Divider sx={{ my: 2 }} />

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
            {success}
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* Phone Number */}
          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">Phone Number</Typography>
              <Box display="flex" alignItems="center" gap={1} mt={1}>
                <PhoneIcon fontSize="small" color="action" />
                <Typography variant="body1" fontFamily="monospace">
                  {maskPhone(status.phone)}
                </Typography>
                <Tooltip title={showPhone ? 'Hide' : 'Show'}>
                  <IconButton size="small" onClick={() => setShowPhone(!showPhone)}>
                    {showPhone ? <VisibilityOff fontSize="small" /> : <Visibility fontSize="small" />}
                  </IconButton>
                </Tooltip>
                {status.phone && (
                  <Tooltip title="Copy">
                    <IconButton size="small" onClick={() => copyToClipboard(status.phone!)}>
                      <ContentCopy fontSize="small" />
                    </IconButton>
                  </Tooltip>
                )}
              </Box>
            </Box>
          </Grid>

          {/* API ID */}
          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">API ID</Typography>
              <Box display="flex" alignItems="center" gap={1} mt={1}>
                <KeyIcon fontSize="small" color="action" />
                <Typography variant="body1" fontFamily="monospace">
                  {status.api_id || 'System Default'}
                </Typography>
              </Box>
            </Box>
          </Grid>

          {/* Verification Status */}
          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">Verification</Typography>
              <Box display="flex" alignItems="center" gap={1} mt={1}>
                {status.verified ? (
                  <>
                    <CheckCircle color="success" fontSize="small" />
                    <Chip label="Verified" size="small" color="success" />
                  </>
                ) : (
                  <>
                    <Cancel color="error" fontSize="small" />
                    <Chip label="Not Verified" size="small" color="error" />
                  </>
                )}
              </Box>
            </Box>
          </Grid>

          {/* Can Read History */}
          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">Permissions</Typography>
              <Box display="flex" alignItems="center" gap={1} mt={1}>
                <Chip
                  label={status.can_read_history ? 'Can read history' : 'Limited access'}
                  size="small"
                  color={status.can_read_history ? 'success' : 'default'}
                  variant={status.can_read_history ? 'filled' : 'outlined'}
                />
              </Box>
            </Box>
          </Grid>
        </Grid>

        {/* Last Used Info */}
        {status.last_used && (
          <Box mt={2}>
            <Typography variant="caption" color="text.secondary">
              Last activity: {new Date(status.last_used).toLocaleString()}
            </Typography>
          </Box>
        )}

        <Divider sx={{ my: 2 }} />

        {/* Action Buttons */}
        <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap>
          <Button
            variant="outlined"
            color="warning"
            size="small"
            startIcon={isDisconnecting ? <CircularProgress size={16} /> : <DisconnectIcon />}
            onClick={handleDisconnect}
            disabled={isDisconnecting || !status.connected}
          >
            {isDisconnecting ? 'Disconnecting...' : 'Disconnect Session'}
          </Button>

          <Button
            variant="outlined"
            color="error"
            size="small"
            startIcon={<DeleteIcon />}
            onClick={() => setRemoveDialogOpen(true)}
            disabled={isRemoving}
          >
            Remove MTProto
          </Button>

          <Button
            variant="text"
            size="small"
            href="/mtproto-setup"
          >
            Go to Setup Page
          </Button>
        </Stack>

        {/* Warning about removing */}
        <Alert severity="warning" icon={<WarningIcon />} sx={{ mt: 2 }}>
          <Typography variant="caption">
            <strong>Disconnect:</strong> Closes active connection but keeps your session. 
            <strong> Remove:</strong> Permanently deletes all MTProto data including session.
          </Typography>
        </Alert>
      </CardContent>

      {/* Remove Confirmation Dialog */}
      <Dialog open={removeDialogOpen} onClose={() => setRemoveDialogOpen(false)}>
        <DialogTitle>Remove MTProto Configuration?</DialogTitle>
        <DialogContent>
          <DialogContentText>
            This will permanently remove your MTProto configuration including:
            <ul>
              <li>Phone number and API credentials</li>
              <li>Session file (you'll need to verify again)</li>
              <li>Per-channel MTProto settings</li>
            </ul>
            Your collected posts and analytics data will NOT be deleted.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRemoveDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleRemove}
            color="error"
            variant="contained"
            disabled={isRemoving}
            startIcon={isRemoving ? <CircularProgress size={16} /> : <DeleteIcon />}
          >
            {isRemoving ? 'Removing...' : 'Remove Configuration'}
          </Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
};

export default AccountInfoCard;

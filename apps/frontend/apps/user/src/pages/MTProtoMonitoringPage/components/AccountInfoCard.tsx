/**
 * MTProto Account Info Card Component
 * Shows user's MTProto configuration details and management actions with modern design
 */
import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Chip,
  Switch,
  FormControlLabel,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Tooltip,
  IconButton,
  Paper,
  Avatar,
  alpha,
} from '@mui/material';
import {
  AccountCircle,
  Phone as PhoneIcon,
  Key as KeyIcon,
  Delete as DeleteIcon,
  PowerSettingsNew as DisconnectIcon,
  CheckCircle,
  Visibility,
  VisibilityOff,
  ContentCopy,
  Settings as SettingsIcon,
  Warning as WarningIcon,
  Security as SecurityIcon,
} from '@mui/icons-material';
import { apiClient } from '@/api/client';
import { checkMTProtoConnection } from '@/features/mtproto-setup/api';

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
  onTestConnection?: () => void;
  onBrowsePowerUps?: () => void;
  onOpenSettings?: () => void;
  isTestingConnection?: boolean;
}

interface StatItemProps {
  icon: React.ReactNode;
  label: string;
  value: React.ReactNode;
  color?: string;
  actions?: React.ReactNode;
}

const StatItem: React.FC<StatItemProps> = ({ icon, label, value, color = '#8b5cf6', actions }) => (
  <Box display="flex" alignItems="center" gap={1.5}>
    <Box
      sx={{
        width: 40,
        height: 40,
        borderRadius: 1.5,
        bgcolor: alpha(color, 0.15),
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: color,
      }}
    >
      {icon}
    </Box>
    <Box flex={1}>
      <Typography variant="caption" color="text.secondary" textTransform="uppercase" letterSpacing={0.5} fontSize="0.65rem">
        {label}
      </Typography>
      <Box display="flex" alignItems="center" gap={0.5}>
        {value}
        {actions}
      </Box>
    </Box>
  </Box>
);

export const AccountInfoCard: React.FC<AccountInfoCardProps> = ({ 
  onStatusChange,
}) => {
  const { t } = useTranslation(['mtproto', 'common', 'errors']);
  const [status, setStatus] = useState<MTProtoStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Action states
  const [isToggling, setIsToggling] = useState(false);
  const [isDisconnecting, setIsDisconnecting] = useState(false);
  const [isRemoving, setIsRemoving] = useState(false);
  const [isCheckingStatus, setIsCheckingStatus] = useState(false);

  // UI states
  const [showPhone, setShowPhone] = useState(false);
  const [removeDialogOpen, setRemoveDialogOpen] = useState(false);
  const [reconnectDialogOpen, setReconnectDialogOpen] = useState(false);

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
  const handleCheckStatus = async () => {
    try {
      setIsCheckingStatus(true);
      setError(null);
      const response = await checkMTProtoConnection();
      setSuccess(response.message || 'Connection status: Active and healthy!');
      await fetchStatus();
      setTimeout(() => setSuccess(null), 5000);
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Failed to check connection status';
      setError(errorMsg);
      
      // If session expired, show reconnect option
      if (errorMsg.includes('session') || errorMsg.includes('expired') || errorMsg.includes('invalid')) {
        setReconnectDialogOpen(true);
      }
    } finally {
      setIsCheckingStatus(false);
    }
  };

  const handleReconnect = () => {
    // Close dialog and navigate to MTProto setup page to re-verify
    setReconnectDialogOpen(false);
    // Use React Router navigation instead of window.location
    window.location.href = '/workers/mtproto';
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
      <Card 
        sx={{ 
          mb: 3,
          background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.08) 0%, rgba(168, 85, 247, 0.08) 100%)',
          border: '1px solid rgba(139, 92, 246, 0.2)',
        }}
      >
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="center" py={3}>
            <CircularProgress size={24} sx={{ color: '#8b5cf6' }} />
            <Typography sx={{ ml: 2 }}>{t('mtproto:accountInfo.loading')}</Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (!status?.configured) {
    return (
      <Card 
        sx={{ 
          mb: 3,
          background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.08) 0%, rgba(168, 85, 247, 0.08) 100%)',
          border: '1px solid rgba(139, 92, 246, 0.2)',
        }}
      >
        <CardContent>
          <Box display="flex" alignItems="center" gap={2} mb={2}>
            <Avatar
              sx={{
                width: 48,
                height: 48,
                bgcolor: alpha('#8b5cf6', 0.2),
                color: '#8b5cf6',
              }}
            >
              <SettingsIcon sx={{ fontSize: 28 }} />
            </Avatar>
            <Box>
              <Typography variant="h6" fontWeight={600}>{t('mtproto:status.configuration')}</Typography>
              <Typography variant="caption" color="text.secondary">
                {t('mtproto:setup.needAccount')}
              </Typography>
            </Box>
          </Box>
          <Button
            variant="contained"
            href="/mtproto-setup"
            sx={{
              background: 'linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #7c3aed 0%, #9333ea 100%)',
              },
            }}
          >
            {t('mtproto:setup.title')}
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card 
      sx={{ 
        mb: 3,
        background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.08) 0%, rgba(168, 85, 247, 0.08) 100%)',
        border: '1px solid rgba(139, 92, 246, 0.2)',
      }}
    >
      <CardContent>
        {/* Header */}
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Box display="flex" alignItems="center" gap={2}>
            <Avatar
              sx={{
                width: 48,
                height: 48,
                bgcolor: alpha('#8b5cf6', 0.2),
                color: '#8b5cf6',
              }}
            >
              <AccountCircle sx={{ fontSize: 28 }} />
            </Avatar>
            <Box>
              <Typography variant="h6" fontWeight={600}>{t('mtproto:status.account')}</Typography>
              <Typography variant="caption" color="text.secondary">
                {t('mtproto:description')}
              </Typography>
            </Box>
          </Box>
          {/* Global Enable/Disable Toggle */}
          <FormControlLabel
            control={
              <Switch
                checked={status.mtproto_enabled ?? false}
                onChange={handleToggle}
                disabled={isToggling}
                sx={{
                  '& .MuiSwitch-switchBase.Mui-checked': {
                    color: '#10b981',
                  },
                  '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                    backgroundColor: '#10b981',
                  },
                }}
              />
            }
            label={
              <Chip 
                label={status.mtproto_enabled ? t('common:enabled') : t('common:disabled')}
                size="small"
                sx={{
                  height: 24,
                  bgcolor: status.mtproto_enabled ? 'rgba(16, 185, 129, 0.2)' : 'rgba(107, 114, 128, 0.2)',
                  color: status.mtproto_enabled ? '#10b981' : '#6b7280',
                }}
              />
            }
          />
        </Box>

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

        {/* Account Info Stats */}
        <Paper
          sx={{
            p: 2,
            background: 'rgba(0, 0, 0, 0.2)',
            borderRadius: 2,
            mb: 2,
          }}
        >
          <Grid container spacing={2}>
            {/* Phone Number */}
            <Grid item xs={6} sm={3}>
              <StatItem
                icon={<PhoneIcon sx={{ fontSize: 20 }} />}
                label={t('mtproto:accountInfo.phoneNumber')}
                value={
                  <Typography variant="subtitle2" fontWeight={600} fontFamily="monospace">
                    {maskPhone(status.phone)}
                  </Typography>
                }
                color="#8b5cf6"
                actions={
                  <Box display="flex" gap={0.5}>
                    <IconButton size="small" onClick={() => setShowPhone(!showPhone)} sx={{ p: 0.5 }}>
                      {showPhone ? <VisibilityOff sx={{ fontSize: 14, color: 'text.secondary' }} /> : <Visibility sx={{ fontSize: 14, color: 'text.secondary' }} />}
                    </IconButton>
                    {status.phone && (
                      <IconButton size="small" onClick={() => copyToClipboard(status.phone!)} sx={{ p: 0.5 }}>
                        <ContentCopy sx={{ fontSize: 14, color: 'text.secondary' }} />
                      </IconButton>
                    )}
                  </Box>
                }
              />
            </Grid>

            {/* API ID */}
            <Grid item xs={6} sm={3}>
              <StatItem
                icon={<KeyIcon sx={{ fontSize: 20 }} />}
                label={t('mtproto:accountInfo.apiId')}
                value={
                  <Typography variant="subtitle2" fontWeight={600} fontFamily="monospace">
                    {status.api_id || 'System Default'}
                  </Typography>
                }
                color="#f59e0b"
              />
            </Grid>

            {/* Verification Status */}
            <Grid item xs={6} sm={3}>
              <StatItem
                icon={<CheckCircle sx={{ fontSize: 20 }} />}
                label={t('common:status')}
                value={
                  <Chip
                    label={status.verified ? t('mtproto:status.verified') : t('errors:notVerified')}
                    size="small"
                    sx={{
                      height: 20,
                      fontSize: '0.65rem',
                      bgcolor: status.verified ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                      color: status.verified ? '#10b981' : '#ef4444',
                    }}
                  />
                }
                color={status.verified ? '#10b981' : '#ef4444'}
              />
            </Grid>

            {/* Can Read History */}
            <Grid item xs={6} sm={3}>
              <StatItem
                icon={<SecurityIcon sx={{ fontSize: 20 }} />}
                label={t('common:permissions')}
                value={
                  <Chip
                    label={status.can_read_history ? t('common:readHistory') : t('common:limitedAccess')}
                    size="small"
                    sx={{
                      height: 20,
                      fontSize: '0.65rem',
                      bgcolor: status.can_read_history ? 'rgba(16, 185, 129, 0.2)' : 'rgba(107, 114, 128, 0.2)',
                      color: status.can_read_history ? '#10b981' : '#6b7280',
                    }}
                  />
                }
                color={status.can_read_history ? '#10b981' : '#6b7280'}
              />
            </Grid>
          </Grid>

          {/* Last Used Info */}
          {status.last_used && (
            <Typography variant="caption" color="text.secondary" display="block" mt={1.5}>
              Last activity: {new Date(status.last_used).toLocaleString()}
            </Typography>
          )}
        </Paper>

        {/* Quick Actions */}
        <Box display="flex" gap={1.5} flexWrap="wrap" alignItems="center">
          {/* Check Status Button - Primary Action */}
          <Tooltip title="Check your MTProto connection and verify session health">
            <Button
              variant="contained"
              size="small"
              startIcon={isCheckingStatus ? <CircularProgress size={14} /> : <CheckCircle />}
              onClick={handleCheckStatus}
              disabled={isCheckingStatus}
              sx={{
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
                },
                '&:disabled': {
                  background: 'rgba(107, 114, 128, 0.3)',
                },
              }}
            >
              {isCheckingStatus ? 'Checking...' : 'Check Status'}
            </Button>
          </Tooltip>

          {/* Disconnect Session Button */}
          <Tooltip title={t('mtproto:accountInfo.disconnectDesc', 'Close active connection but keep session')}>
            <Button
              variant="outlined"
              size="small"
              startIcon={isDisconnecting ? <CircularProgress size={14} /> : <DisconnectIcon />}
              onClick={handleDisconnect}
              disabled={isDisconnecting || !status.connected}
              sx={{
                borderColor: 'rgba(107, 114, 128, 0.5)',
                color: 'text.secondary',
                '&:hover': {
                  borderColor: 'rgba(107, 114, 128, 0.8)',
                  bgcolor: 'rgba(107, 114, 128, 0.1)',
                },
              }}
            >
              {t('mtproto:accountInfo.disconnectSession', 'Disconnect Session')}
            </Button>
          </Tooltip>

          {/* Remove MTProto Button */}
          <Tooltip title={t('mtproto:quickActions.removeDesc', 'Permanently delete your MTProto configuration')}>
            <Button
              variant="outlined"
              size="small"
              color="error"
              startIcon={isRemoving ? <CircularProgress size={14} /> : <DeleteIcon />}
              onClick={() => setRemoveDialogOpen(true)}
              disabled={isRemoving}
              sx={{
                borderColor: 'rgba(239, 68, 68, 0.5)',
                '&:hover': {
                  borderColor: 'rgba(239, 68, 68, 0.8)',
                  bgcolor: 'rgba(239, 68, 68, 0.1)',
                },
              }}
            >
              {t('mtproto:quickActions.remove', 'Remove MTProto')}
            </Button>
          </Tooltip>

          {/* MTProto Setup Link */}
          <Button
            variant="text"
            size="small"
            href="/mtproto-setup"
            sx={{ color: '#8b5cf6' }}
          >
            {t('mtproto:setup.title')}
          </Button>
        </Box>

        {/* Warning Alert */}
        <Alert 
          severity="warning" 
          icon={<WarningIcon sx={{ fontSize: 18 }} />} 
          sx={{ 
            mt: 2,
            bgcolor: 'rgba(245, 158, 11, 0.1)',
            border: '1px solid rgba(245, 158, 11, 0.2)',
            '& .MuiAlert-icon': { color: '#f59e0b' },
          }}
        >
          <Typography variant="caption">
            <strong>Disconnect:</strong> Closes active connection but keeps your session.{' '}
            <strong>Remove:</strong> <span style={{ color: '#ef4444' }}>Permanently deletes all MTProto data including session.</span>
          </Typography>
        </Alert>
      </CardContent>

      {/* Remove Confirmation Dialog */}
      <Dialog open={removeDialogOpen} onClose={() => setRemoveDialogOpen(false)}>
        <DialogTitle>{t('common:confirmRemove')}</DialogTitle>
        <DialogContent>
          <DialogContentText>
            {t('common:removeWarning')}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRemoveDialogOpen(false)}>{t('common:cancel')}</Button>
          <Button
            onClick={handleRemove}
            color="error"
            variant="contained"
            disabled={isRemoving}
            startIcon={isRemoving ? <CircularProgress size={16} /> : <DeleteIcon />}
          >
            {isRemoving ? t('common:removing') : t('common:removeConfig')}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Reconnect Dialog - Shows when session expired */}
      <Dialog open={reconnectDialogOpen} onClose={() => setReconnectDialogOpen(false)}>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <WarningIcon color="warning" />
          Session Expired
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            Your MTProto session has expired or become invalid. You need to reconnect to resume data collection.
          </DialogContentText>
          <Alert severity="info" sx={{ mt: 2 }}>
            <strong>What happens when you reconnect:</strong>
            <ul style={{ margin: '8px 0 0 0', paddingLeft: '20px' }}>
              <li>You'll receive a new verification code on Telegram</li>
              <li>Enter the code to re-authenticate</li>
              <li>Your data collection will resume automatically</li>
              <li>All your settings and channel configurations will be preserved</li>
            </ul>
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setReconnectDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleReconnect}
            variant="contained"
            color="primary"
            sx={{
              background: 'linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #7c3aed 0%, #9333ea 100%)',
              },
            }}
          >
            Reconnect Now
          </Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
};

export default AccountInfoCard;

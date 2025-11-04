/**
 * MTProto Status Card Component
 * Displays current MTProto configuration status with GLOBAL TOGGLE
 */

import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Button,
  Stack,
  CircularProgress,
  Alert,
  Switch,
  FormControlLabel,
  Divider,
} from '@mui/material';
import {
  CheckCircle,
  Cancel,
  PhoneAndroid,
  AccountCircle,
  CloudDone,
  CloudOff,
  SignalCellularAlt as MTProtoOnIcon,
  SignalCellularOff as MTProtoOffIcon,
} from '@mui/icons-material';
import { useMTProtoStore } from '../hooks';
import { logger } from '@/utils/logger';
import { toggleGlobalMTProto, connectMTProto } from '../api';

export const MTProtoStatusCard: React.FC = () => {
  const { status, isLoading, isDisconnecting, isRemoving, error, disconnect, remove, fetchStatus } = useMTProtoStore();

  // Global MTProto enable/disable state
  const [globalEnabled, setGlobalEnabled] = useState<boolean>(true);
  const [isToggling, setIsToggling] = useState(false);
  const [toggleError, setToggleError] = useState<string | null>(null);
  const [toggleSuccess, setToggleSuccess] = useState<string | null>(null);

  // Connect state
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectError, setConnectError] = useState<string | null>(null);
  const [connectSuccess, setConnectSuccess] = useState<string | null>(null);

  // Load global setting when status loads
  React.useEffect(() => {
    if (status?.mtproto_enabled !== undefined) {
      setGlobalEnabled(status.mtproto_enabled);
    }
  }, [status?.mtproto_enabled]);

  const handleGlobalToggle = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = event.target.checked;
    setIsToggling(true);
    setToggleError(null);
    setToggleSuccess(null);

    try {
      // Call API to toggle global MTProto setting (backend expects POST)
      await toggleGlobalMTProto(newValue);
      setGlobalEnabled(newValue);
      setToggleSuccess(
        newValue
          ? 'MTProto enabled globally for all channels'
          : 'MTProto disabled globally - per-channel settings still apply'
      );

      logger.log(`Global MTProto toggled: ${newValue}`);
      
      // Refetch status to update connection state
      await fetchStatus();
    } catch (err: any) {
      logger.error('Failed to toggle global MTProto:', err);
      setToggleError(err.message || 'Failed to toggle MTProto');
      // Revert on error
      setGlobalEnabled(!newValue);
    } finally {
      setIsToggling(false);
    }
  };

  const handleConnect = async () => {
    setIsConnecting(true);
    setConnectError(null);
    setConnectSuccess(null);

    try {
      await connectMTProto();
      setConnectSuccess('MTProto client connected successfully!');
      logger.log('MTProto client connected manually');
      
      // Refetch status to show active connection
      await fetchStatus();
    } catch (err: any) {
      logger.error('Failed to connect MTProto:', err);
      setConnectError(err.message || 'Failed to connect MTProto client');
    } finally {
      setIsConnecting(false);
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="center" py={3}>
            <CircularProgress />
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent>
          <Alert severity="error">
            Failed to load MTProto status: {error}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (!status) {
    return null;
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          MTProto Configuration Status
        </Typography>

        {/* GLOBAL MTPROTO TOGGLE - PROMINENT AND CLEAR */}
        {status.configured && status.verified && (
          <Box sx={{ my: 3, p: 2, bgcolor: globalEnabled ? 'success.lighter' : 'grey.100', borderRadius: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {globalEnabled ? (
                  <MTProtoOnIcon sx={{ fontSize: 32, color: 'success.main' }} />
                ) : (
                  <MTProtoOffIcon sx={{ fontSize: 32, color: 'text.disabled' }} />
                )}
                <Box>
                  <Typography variant="subtitle1" fontWeight={600}>
                    MTProto Feature Control
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {globalEnabled
                      ? 'Feature enabled - can read channel history'
                      : 'Feature disabled - bot API only'
                    }
                  </Typography>
                </Box>
              </Box>
              <FormControlLabel
                control={
                  <Switch
                    checked={globalEnabled}
                    onChange={handleGlobalToggle}
                    disabled={isToggling}
                    color="primary"
                    size="medium"
                  />
                }
                label=""
                sx={{ m: 0 }}
              />
            </Box>

            {/* Persistent inline feedback */}
            {toggleError && (
              <Alert severity="error" sx={{ mt: 1 }} onClose={() => setToggleError(null)}>
                {toggleError}
              </Alert>
            )}
            {toggleSuccess && (
              <Alert severity="success" sx={{ mt: 1 }} onClose={() => setToggleSuccess(null)}>
                {toggleSuccess}
              </Alert>
            )}
          </Box>
        )}

        <Divider sx={{ my: 2 }} />

        <Stack spacing={2} mt={2}>
          {/* Configuration Status */}
          <Box display="flex" alignItems="center" gap={1}>
            {status.configured ? (
              <CheckCircle color="success" />
            ) : (
              <Cancel color="error" />
            )}
            <Typography>
              <strong>Configured:</strong> {status.configured ? 'Yes' : 'No'}
            </Typography>
          </Box>

          {/* Verification Status */}
          <Box display="flex" alignItems="center" gap={1}>
            {status.verified ? (
              <CheckCircle color="success" />
            ) : (
              <Cancel color="error" />
            )}
            <Typography>
              <strong>Verified:</strong> {status.verified ? 'Yes' : 'No'}
            </Typography>
          </Box>

          {/* Phone Number */}
          {status.phone && (
            <Box display="flex" alignItems="center" gap={1}>
              <PhoneAndroid color="action" />
              <Typography>
                <strong>Phone:</strong> {status.phone}
              </Typography>
            </Box>
          )}

          {/* API ID */}
          {status.api_id && (
            <Box display="flex" alignItems="center" gap={1}>
              <AccountCircle color="action" />
              <Typography>
                <strong>API ID:</strong> {status.api_id}
              </Typography>
            </Box>
          )}

          {/* Connection Status - Session State */}
          <Box display="flex" alignItems="center" gap={1}>
            {status.connected ? (
              <CloudDone color="success" />
            ) : (
              <CloudOff color="disabled" />
            )}
            <Typography>
              <strong>Session Status:</strong> {status.connected ? 'Ready' : 'Not Ready'}
            </Typography>
          </Box>
          {status.connected && (
            <Box sx={{ ml: 4 }}>
              <Typography variant="caption" color="success.main" sx={{ display: 'block' }}>
                ✅ Session is ready - will auto-connect when reading channel history
              </Typography>
              <Button
                variant="outlined"
                color="primary"
                size="small"
                onClick={handleConnect}
                disabled={isConnecting}
                sx={{ mt: 1 }}
              >
                {isConnecting ? 'Connecting...' : 'Connect Now'}
              </Button>
              
              {/* Connect feedback */}
              {connectSuccess && (
                <Alert severity="success" sx={{ mt: 1, py: 0.5 }} onClose={() => setConnectSuccess(null)}>
                  {connectSuccess}
                </Alert>
              )}
              {connectError && (
                <Alert severity="error" sx={{ mt: 1, py: 0.5 }} onClose={() => setConnectError(null)}>
                  {connectError}
                </Alert>
              )}
            </Box>
          )}

          {/* Last Used */}
          {status.last_used && (
            <Typography variant="body2" color="text.secondary">
              <strong>Last used:</strong>{' '}
              {new Date(status.last_used).toLocaleString()}
            </Typography>
          )}

          {/* Can Read History Badge */}
          <Box>
            <Chip
              label={status.can_read_history ? 'Can read channel history' : 'Cannot read channel history'}
              color={status.can_read_history ? 'success' : 'default'}
              size="small"
            />
          </Box>

          {/* Actions */}
          {status.configured && (
            <Stack direction="row" spacing={1} mt={2}>
              <Button
                variant="outlined"
                color="warning"
                size="small"
                onClick={() => disconnect()}
                disabled={isDisconnecting}
              >
                {isDisconnecting ? 'Disconnecting...' : 'Disconnect'}
              </Button>
              <Button
                variant="outlined"
                color="error"
                size="small"
                onClick={() => {
                  if (window.confirm('Are you sure you want to remove all MTProto configuration?')) {
                    remove();
                  }
                }}
                disabled={isRemoving}
              >
                {isRemoving ? 'Removing...' : 'Remove Configuration'}
              </Button>
            </Stack>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
};

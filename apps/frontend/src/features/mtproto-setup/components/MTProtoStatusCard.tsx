/**
 * MTProto Status Card Component
 * Displays current MTProto configuration status with GLOBAL TOGGLE
 */

import React, { useState, useEffect } from 'react';
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
import { uiLogger, logger } from '@/utils/logger';
import { toggleGlobalMTProto, connectMTProto } from '../api';

export const MTProtoStatusCard: React.FC = () => {
  const { status, isLoading, isDisconnecting, isRemoving, error, disconnect, remove, fetchStatus } = useMTProtoStore();

  // Debug: Log the status to see what we're receiving
  useEffect(() => {
    uiLogger.debug('MTProto Status Debug', {
      connected: status?.connected,
      actively_connected: status?.actively_connected,
      mtproto_enabled: status?.mtproto_enabled,
      has_mtproto_enabled_field: 'mtproto_enabled' in (status || {}),
      should_show_button: status?.connected && !status?.actively_connected,
      full_status: status
    });
  }, [status]);

  // Global toggle state - track if user is actively toggling
  // ✅ FIXED: Default to false if status not loaded yet (fail-secure)
  const [globalEnabled, setGlobalEnabled] = useState(status?.mtproto_enabled ?? false);
  const [isUserToggling, setIsUserToggling] = useState(false); // Prevent race conditions

  // Sync toggle state when status changes (but NOT during user toggle action)
  useEffect(() => {
    // Don't override if user is actively toggling
    if (isUserToggling) {
      uiLogger.debug('Skipping sync - user is toggling');
      return;
    }

    uiLogger.debug('Toggle Sync Effect', {
      status_mtproto_enabled: status?.mtproto_enabled,
      current_globalEnabled: globalEnabled,
      will_update: status?.mtproto_enabled !== undefined && !isUserToggling
    });

    if (status?.mtproto_enabled !== undefined) {
      uiLogger.debug('Syncing globalEnabled', { value: status.mtproto_enabled });
      setGlobalEnabled(status.mtproto_enabled);
    }
  }, [status?.mtproto_enabled, isUserToggling]);

  const [isToggling, setIsToggling] = useState(false);
  const [toggleError, setToggleError] = useState<string | null>(null);
  const [toggleSuccess, setToggleSuccess] = useState<string | null>(null);
  const [hasAutoConnected, setHasAutoConnected] = useState(false); // Track if we already auto-connected

  // 🚀 AUTO-CONNECT ON PAGE LOAD: Connect if MTProto is enabled but not actively connected
  useEffect(() => {
    const autoConnect = async () => {
      // Only auto-connect once per page load
      if (hasAutoConnected) {
        uiLogger.debug('Already attempted auto-connect');
        return;
      }

      // Check if MTProto is enabled, session is ready, but not actively connected
      if (status?.mtproto_enabled && status?.connected && !status?.actively_connected) {
        uiLogger.debug('Auto-connecting on page load');
        setHasAutoConnected(true); // Mark as attempted

        try {
          await connectMTProto();
          uiLogger.debug('Auto-connect on load succeeded');
          // Refresh status to show active connection
          await fetchStatus();
        } catch (err: any) {
          uiLogger.warn('Auto-connect on load failed', { error: err });
          // Don't show error to user - connection will happen automatically when needed
        }
      }
    };

    autoConnect();
  }, [status?.mtproto_enabled, status?.connected, status?.actively_connected, hasAutoConnected]);

  const handleGlobalToggle = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = event.target.checked;
    uiLogger.debug('MTProto toggle clicked', { from: globalEnabled, to: newValue });

    // Mark that user is actively toggling - prevent race conditions
    setIsUserToggling(true);

    // Immediately update UI for responsive feedback
    setGlobalEnabled(newValue);
    setIsToggling(true);
    setToggleError(null);
    setToggleSuccess(null);

    try {
      // Call API to toggle global MTProto setting (backend expects POST)
      uiLogger.debug('Sending toggle request', { enabled: newValue });
      await toggleGlobalMTProto(newValue);
      uiLogger.debug('Toggle API succeeded');

      // 🚀 AUTO-CONNECT: When enabling MTProto, automatically connect the session
      if (newValue) {
        uiLogger.debug('Auto-connecting MTProto session');
        try {
          await connectMTProto();
          uiLogger.debug('Auto-connect succeeded');
          setToggleSuccess('MTProto enabled and connected automatically!');
        } catch (connectErr: any) {
          uiLogger.warn('Auto-connect failed', { error: connectErr });
          // Don't fail the whole operation if connect fails - session will connect lazily
          setToggleSuccess('MTProto enabled globally (will connect automatically when needed)');
        }
      } else {
        setToggleSuccess('MTProto disabled globally - per-channel settings still apply');
      }

      logger.log(`Global MTProto toggled: ${newValue}`);

      // Refetch status to update connection state
      uiLogger.debug('Refetching status');
      await fetchStatus();
      uiLogger.debug('Status refetched');

      // Wait a bit to ensure backend has processed and returned new state
      await new Promise(resolve => setTimeout(resolve, 300));

    } catch (err: any) {
      logger.error('Failed to toggle global MTProto:', err);
      setToggleError(err.message || 'Failed to toggle MTProto');
      // Revert on error
      setGlobalEnabled(!newValue);
    } finally {
      setIsToggling(false);
      // Re-enable sync after toggle completes
      setIsUserToggling(false);
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
                    key={`mtproto-toggle-${globalEnabled}`}
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
            {status.actively_connected ? (
              <CloudDone color="success" />
            ) : status.connected ? (
              <CloudDone color="info" />
            ) : (
              <CloudOff color="disabled" />
            )}
            <Typography>
              <strong>Session Status:</strong>{' '}
              {status.actively_connected
                ? 'Connected'
                : status.connected
                ? 'Ready'
                : 'Not Ready'}
            </Typography>
          </Box>

          {/* Status-specific message and actions */}
          {status.actively_connected && (
            <Typography variant="caption" color="success.main" sx={{ ml: 4, display: 'block' }}>
              ✅ Active connection - reading channel history in real-time
            </Typography>
          )}

          {status.connected && !status.actively_connected && (
            <Box sx={{ ml: 4 }}>
              <Typography variant="caption" color="info.main" sx={{ display: 'block' }}>
                🔌 Session ready - connecting automatically...
              </Typography>
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

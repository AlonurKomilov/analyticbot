/**
 * Channel MTProto Toggle Component
 *
 * Per-channel MTProto enable/disable switch with status indicator
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Switch,
  FormControlLabel,
  Tooltip,
  CircularProgress,
  Typography,
  Alert
} from '@mui/material';
import {
  SignalCellularAlt as MTProtoIcon,
  SignalCellularOff as MTProtoOffIcon
} from '@mui/icons-material';
import { getChannelMTProtoSetting, toggleChannelMTProto } from '@/features/mtproto-setup/api';
import { logger } from '@/utils/logger';

interface ChannelMTProtoToggleProps {
  channelId: string | number;
  channelName: string;
  /**
   * If true, shows compact inline switch. If false, shows full card layout
   */
  compact?: boolean;
}

export const ChannelMTProtoToggle: React.FC<ChannelMTProtoToggleProps> = ({
  channelId,
  channelName,
  compact = false
}) => {
  const [enabled, setEnabled] = useState<boolean>(true); // Default to enabled
  const [isLoading, setIsLoading] = useState(false);
  const [isToggling, setIsToggling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Load current setting on mount
  useEffect(() => {
    loadSetting();
  }, [channelId]);

  const loadSetting = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const numericChannelId = typeof channelId === 'string' ? parseInt(channelId, 10) : channelId;
      const result = await getChannelMTProtoSetting(numericChannelId);
      setEnabled(result.mtproto_enabled);
    } catch (err: any) {
      // 404 means no per-channel setting exists yet - use global default (enabled)
      if (err.status === 404) {
        logger.log(`No per-channel setting for ${channelId}, using global default (enabled)`);
        setEnabled(true);
      } else {
        logger.error(`Failed to load MTProto setting for channel ${channelId}:`, err);
        // Default to enabled on error (fail-open for better UX)
        setEnabled(true);
        setError('Failed to load MTProto status');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggle = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = event.target.checked;
    setIsToggling(true);
    setError(null);

    try {
      const numericChannelId = typeof channelId === 'string' ? parseInt(channelId, 10) : channelId;
      await toggleChannelMTProto(numericChannelId, newValue);
      setEnabled(newValue);
      setSuccessMessage(
        newValue
          ? `MTProto enabled for ${channelName}`
          : `MTProto disabled for ${channelName}`
      );
    } catch (err: any) {
      logger.error(`Failed to toggle MTProto for channel ${channelId}:`, err);
      setError(err.message || 'Failed to toggle MTProto');
      // Revert on error
      setEnabled(!newValue);
    } finally {
      setIsToggling(false);
    }
  };

  if (compact) {
    // Compact inline version for channel cards with PERSISTENT inline feedback
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {isLoading ? (
            <CircularProgress size={20} />
          ) : (
            <Tooltip
              title={
                enabled
                  ? 'MTProto enabled - full history access'
                  : 'MTProto disabled - bot-only access'
              }
            >
              <FormControlLabel
                control={
                  <Switch
                    checked={enabled ?? true}
                    onChange={handleToggle}
                    disabled={isToggling || isLoading}
                    size="small"
                    color="primary"
                  />
                }
                label={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    {enabled ? (
                      <MTProtoIcon sx={{ fontSize: 16, color: 'success.main' }} />
                    ) : (
                      <MTProtoOffIcon sx={{ fontSize: 16, color: 'text.disabled' }} />
                    )}
                    <Typography variant="caption" color="text.secondary">
                      MTProto
                    </Typography>
                  </Box>
                }
                sx={{ m: 0 }}
              />
            </Tooltip>
          )}
        </Box>

        {/* PERSISTENT inline feedback instead of closing toasts */}
        {error && (
          <Alert severity="error" sx={{ py: 0.5, px: 1 }} onClose={() => setError(null)}>
            <Typography variant="caption">{error}</Typography>
          </Alert>
        )}
        {successMessage && (
          <Alert severity="success" sx={{ py: 0.5, px: 1 }} onClose={() => setSuccessMessage(null)}>
            <Typography variant="caption">{successMessage}</Typography>
          </Alert>
        )}
      </Box>
    );
  }

  // Full card layout (for settings pages)
  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {enabled ? (
            <MTProtoIcon sx={{ color: 'success.main' }} />
          ) : (
            <MTProtoOffIcon sx={{ color: 'text.disabled' }} />
          )}
          <Box>
            <Typography variant="subtitle1" fontWeight={600}>
              MTProto Access
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {enabled
                ? 'Full channel history access enabled'
                : 'Disabled - only bot-accessible data'
              }
            </Typography>
          </Box>
        </Box>

        {isLoading ? (
          <CircularProgress size={24} />
        ) : (
          <Switch
            checked={enabled ?? true}
            onChange={handleToggle}
            disabled={isToggling || isLoading}
            color="primary"
          />
        )}
      </Box>

      {error && (
        <Alert severity="error" sx={{ mt: 1 }}>
          {error}
        </Alert>
      )}

      {successMessage && (
        <Alert severity="success" sx={{ mt: 1 }}>
          {successMessage}
        </Alert>
      )}
    </Box>
  );
};

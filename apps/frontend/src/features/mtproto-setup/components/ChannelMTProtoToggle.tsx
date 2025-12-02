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
import { getChannelMTProtoSetting, toggleChannelMTProto, getMTProtoStatus } from '@/features/mtproto-setup/api';
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
  const [enabled, setEnabled] = useState<boolean | null>(null); // null = not loaded yet
  const [globalEnabled, setGlobalEnabled] = useState<boolean>(false); // Global MTProto setting
  const [isLoading, setIsLoading] = useState(false);
  const [isToggling, setIsToggling] = useState(false);
  const [isUserToggling, setIsUserToggling] = useState(false); // Prevent race conditions
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Load current setting on mount and when channelId changes
  // BUT block during user toggle to prevent race conditions
  useEffect(() => {
    if (isUserToggling) {
      console.log(`⏸️ Channel ${channelId}: Skipping reload - user is toggling`);
      return;
    }
    console.log(`🔄 Channel ${channelId}: Loading setting...`);
    loadSetting();
  }, [channelId, isUserToggling]);

  const loadSetting = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // FIRST: Get global MTProto setting (the source of truth for defaults)
      const status = await getMTProtoStatus();
      const globalSetting = status.mtproto_enabled ?? false;
      setGlobalEnabled(globalSetting);

      console.log('🌐 Global MTProto setting:', globalSetting);

      // SECOND: Try to get per-channel override
      const numericChannelId = typeof channelId === 'string' ? parseInt(channelId, 10) : channelId;
      const result = await getChannelMTProtoSetting(numericChannelId);
      
      if (result !== null) {
        // Has per-channel override
        console.log(`📌 Channel ${channelId} has override:`, result.mtproto_enabled);
        setEnabled(result.mtproto_enabled);
      } else {
        // No per-channel setting, inherit from global
        console.log(`📌 Channel ${channelId} inherits global:`, globalSetting);
        setEnabled(globalSetting);
      }
    } catch (err: any) {
      logger.error(`Failed to load MTProto setting for channel ${channelId}:`, err);
      // On error, default to false (fail-secure, not fail-open)
      setEnabled(false);
      setGlobalEnabled(false);
      setError('Failed to load MTProto status');
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggle = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = event.target.checked;

    console.log(`🎚️ Channel ${channelId} toggle clicked:`, { from: enabled, to: newValue });

    // 🔒 LOCK: Prevent race conditions
    setIsUserToggling(true);
    setIsToggling(true);
    setError(null);

    // ⚡ INSTANT: Update UI immediately (optimistic)
    setEnabled(newValue);

    try {
      console.log(`📤 Sending channel toggle request for ${channelId}:`, { enabled: newValue });
      const numericChannelId = typeof channelId === 'string' ? parseInt(channelId, 10) : channelId;
      await toggleChannelMTProto(numericChannelId, newValue);
      console.log(`✅ Channel toggle API succeeded for ${channelId}`);

      setSuccessMessage(
        newValue
          ? `MTProto enabled for ${channelName}`
          : `MTProto disabled for ${channelName}`
      );

      // ⏱️ WAIT: Let backend fully process (prevent stale data)
      await new Promise(resolve => setTimeout(resolve, 300));

    } catch (err: any) {
      console.error(`❌ Channel toggle failed for ${channelId}:`, err);
      logger.error(`Failed to toggle MTProto for channel ${channelId}:`, err);
      setError(err.message || 'Failed to toggle MTProto');
      // Revert on error
      setEnabled(!newValue);
    } finally {
      setIsToggling(false);
      // 🔓 UNLOCK: Allow future updates
      setIsUserToggling(false);
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
                    key={`channel-${channelId}-toggle-${enabled}`}
                    checked={enabled ?? globalEnabled}
                    onChange={handleToggle}
                    disabled={isToggling || isLoading || enabled === null}
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
            key={`channel-${channelId}-toggle-${enabled}`}
            checked={enabled ?? globalEnabled}
            onChange={handleToggle}
            disabled={isToggling || isLoading || enabled === null}
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

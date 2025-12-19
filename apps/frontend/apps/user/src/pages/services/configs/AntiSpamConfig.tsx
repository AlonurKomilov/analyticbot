/**
 * Anti-Spam Service Configuration
 */

import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Switch,
  FormControlLabel,
  FormGroup,
  Slider,
  Alert,
  Button,
  CircularProgress,
  Divider,
  alpha,
  Card,
  CardContent,
} from '@mui/material';
import {
  Security as SecurityIcon,
  Save as SaveIcon,
  Speed as SpeedIcon,
  Link as LinkIcon,
  Forward as ForwardIcon,
  SmartToy as BotIcon,
} from '@mui/icons-material';
import { apiClient } from '@/api/client';

interface AntiSpamSettings {
  anti_spam_enabled: boolean;
  anti_link_enabled: boolean;
  anti_forward_enabled: boolean;
  spam_action: string;
  spam_sensitivity: number;
  flood_control_enabled: boolean;
  flood_messages_limit: number;
  flood_time_window: number;
}

interface Props {
  chatId: number;
}

export const AntiSpamConfig: React.FC<Props> = ({ chatId }) => {
  const [settings, setSettings] = useState<AntiSpamSettings>({
    anti_spam_enabled: false,
    anti_link_enabled: false,
    anti_forward_enabled: false,
    spam_action: 'delete',
    spam_sensitivity: 5,
    flood_control_enabled: false,
    flood_messages_limit: 5,
    flood_time_window: 60,
  });
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isNewConfig, setIsNewConfig] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const fetchSettings = async () => {
      setIsLoading(true);
      try {
        const response = await apiClient.get(`/user-bot/service/settings/${chatId}`) as AntiSpamSettings;
        if (response) {
          setSettings(prev => ({
            ...prev,
            anti_spam_enabled: response.anti_spam_enabled ?? false,
            anti_link_enabled: response.anti_link_enabled ?? false,
            anti_forward_enabled: response.anti_forward_enabled ?? false,
            spam_action: response.spam_action ?? 'delete',
            spam_sensitivity: response.spam_sensitivity ?? 5,
            flood_control_enabled: response.flood_control_enabled ?? false,
            flood_messages_limit: response.flood_messages_limit ?? 5,
            flood_time_window: response.flood_time_window ?? 60,
          }));
        }
      } catch (err: any) {
        // 404 means settings don't exist yet - this is normal for new chats
        if (err.message?.includes('not found') || err.status === 404) {
          setIsNewConfig(true);
        } else {
          setError(err.message || 'Failed to load settings');
        }
      } finally {
        setIsLoading(false);
      }
    };

    if (chatId) {
      fetchSettings();
    }
  }, [chatId]);

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);
    setSuccess(false);
    try {
      await apiClient.post(`/user-bot/service/settings/${chatId}`, settings);
      setSuccess(true);
      setIsNewConfig(false);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err: any) {
      setError(err.message || 'Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" py={4}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 3 }}>Settings saved successfully!</Alert>}
      {isNewConfig && !success && (
        <Alert severity="info" sx={{ mb: 3 }}>
          This chat hasn't been configured yet. Customize your settings and save to get started!
        </Alert>
      )}

      {/* Main Anti-Spam Toggle */}
      <Card sx={{ mb: 3, bgcolor: alpha('#667eea', 0.05), border: '1px solid', borderColor: alpha('#667eea', 0.2) }}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box display="flex" alignItems="center" gap={2}>
              <SecurityIcon sx={{ color: '#667eea', fontSize: 40 }} />
              <Box>
                <Typography variant="h6">Anti-Spam Protection</Typography>
                <Typography variant="body2" color="text.secondary">
                  Enable AI-powered spam detection to automatically filter unwanted messages
                </Typography>
              </Box>
            </Box>
            <Switch
              checked={settings.anti_spam_enabled}
              onChange={(e) => setSettings(prev => ({ ...prev, anti_spam_enabled: e.target.checked }))}
              color="primary"
              size="medium"
            />
          </Box>
        </CardContent>
      </Card>

      {settings.anti_spam_enabled && (
        <>
          {/* Sensitivity */}
          <Box mb={4}>
            <Typography variant="subtitle1" mb={2}>
              <SpeedIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Detection Sensitivity
            </Typography>
            <Box px={2}>
              <Slider
                value={settings.spam_sensitivity}
                onChange={(_, value) => setSettings(prev => ({ ...prev, spam_sensitivity: value as number }))}
                min={1}
                max={10}
                step={1}
                marks={[
                  { value: 1, label: 'Low' },
                  { value: 5, label: 'Medium' },
                  { value: 10, label: 'High' },
                ]}
                valueLabelDisplay="auto"
              />
            </Box>
            <Typography variant="caption" color="text.secondary">
              Higher sensitivity catches more spam but may have more false positives
            </Typography>
          </Box>

          <Divider sx={{ my: 3 }} />

          {/* Additional Filters */}
          <Typography variant="subtitle1" mb={2}>Additional Filters</Typography>
          
          <FormGroup>
            {/* Anti-Link */}
            <Box sx={{ p: 2, borderRadius: 2, bgcolor: 'background.default', mb: 2 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.anti_link_enabled}
                    onChange={(e) => setSettings(prev => ({ ...prev, anti_link_enabled: e.target.checked }))}
                  />
                }
                label={
                  <Box>
                    <Box display="flex" alignItems="center" gap={1}>
                      <LinkIcon fontSize="small" />
                      <Typography>Block External Links</Typography>
                    </Box>
                    <Typography variant="caption" color="text.secondary">
                      Automatically remove messages containing links from non-admins
                    </Typography>
                  </Box>
                }
                sx={{ alignItems: 'flex-start', m: 0 }}
              />
            </Box>

            {/* Anti-Forward */}
            <Box sx={{ p: 2, borderRadius: 2, bgcolor: 'background.default', mb: 2 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.anti_forward_enabled}
                    onChange={(e) => setSettings(prev => ({ ...prev, anti_forward_enabled: e.target.checked }))}
                  />
                }
                label={
                  <Box>
                    <Box display="flex" alignItems="center" gap={1}>
                      <ForwardIcon fontSize="small" />
                      <Typography>Block Forwarded Messages</Typography>
                    </Box>
                    <Typography variant="caption" color="text.secondary">
                      Remove forwarded messages from other chats/channels
                    </Typography>
                  </Box>
                }
                sx={{ alignItems: 'flex-start', m: 0 }}
              />
            </Box>

            {/* Flood Control */}
            <Box sx={{ p: 2, borderRadius: 2, bgcolor: 'background.default' }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.flood_control_enabled}
                    onChange={(e) => setSettings(prev => ({ ...prev, flood_control_enabled: e.target.checked }))}
                  />
                }
                label={
                  <Box>
                    <Box display="flex" alignItems="center" gap={1}>
                      <BotIcon fontSize="small" />
                      <Typography>Flood Protection</Typography>
                    </Box>
                    <Typography variant="caption" color="text.secondary">
                      Limit rapid message sending to prevent spam floods
                    </Typography>
                  </Box>
                }
                sx={{ alignItems: 'flex-start', m: 0 }}
              />
              
              {settings.flood_control_enabled && (
                <Box mt={2} ml={4}>
                  <Typography variant="body2" mb={1}>
                    Max <strong>{settings.flood_messages_limit}</strong> messages per <strong>{settings.flood_time_window}</strong> seconds
                  </Typography>
                  <Box display="flex" gap={2}>
                    <Box flex={1}>
                      <Typography variant="caption">Messages</Typography>
                      <Slider
                        value={settings.flood_messages_limit}
                        onChange={(_, value) => setSettings(prev => ({ ...prev, flood_messages_limit: value as number }))}
                        min={3}
                        max={20}
                        step={1}
                        size="small"
                      />
                    </Box>
                    <Box flex={1}>
                      <Typography variant="caption">Time Window (sec)</Typography>
                      <Slider
                        value={settings.flood_time_window}
                        onChange={(_, value) => setSettings(prev => ({ ...prev, flood_time_window: value as number }))}
                        min={10}
                        max={300}
                        step={10}
                        size="small"
                      />
                    </Box>
                  </Box>
                </Box>
              )}
            </Box>
          </FormGroup>
        </>
      )}

      {/* Save Button */}
      <Box mt={4} display="flex" justifyContent="flex-end">
        <Button
          variant="contained"
          startIcon={isSaving ? <CircularProgress size={20} color="inherit" /> : <SaveIcon />}
          onClick={handleSave}
          disabled={isSaving}
          size="large"
        >
          {isSaving ? 'Saving...' : 'Save Settings'}
        </Button>
      </Box>
    </Box>
  );
};

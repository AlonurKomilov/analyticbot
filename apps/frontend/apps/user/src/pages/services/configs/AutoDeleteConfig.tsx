/**
 * Auto-Delete Join/Leave Messages Configuration
 */

import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Switch,
  Alert,
  Button,
  CircularProgress,
  Divider,
  alpha,
  Card,
  CardContent,
  Slider,
} from '@mui/material';
import {
  Save as SaveIcon,
  PersonAdd as JoinIcon,
  PersonRemove as LeaveIcon,
  Timer as TimerIcon,
} from '@mui/icons-material';
import { apiClient } from '@/api/client';

interface AutoDeleteSettings {
  clean_join_messages: boolean;
  clean_leave_messages: boolean;
  delete_delay_seconds: number;
}

interface Props {
  chatId: number;
}

export const AutoDeleteConfig: React.FC<Props> = ({ chatId }) => {
  const [settings, setSettings] = useState<AutoDeleteSettings>({
    clean_join_messages: false,
    clean_leave_messages: false,
    delete_delay_seconds: 5,
  });
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const fetchSettings = async () => {
      setIsLoading(true);
      try {
        const response = await apiClient.get(`/bot/moderation/${chatId}/settings`) as AutoDeleteSettings;
        if (response) {
          setSettings(prev => ({
            ...prev,
            clean_join_messages: response.clean_join_messages ?? false,
            clean_leave_messages: response.clean_leave_messages ?? false,
            delete_delay_seconds: response.delete_delay_seconds ?? 5,
          }));
        }
      } catch (err: any) {
        setError(err.message || 'Failed to load settings');
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
      await apiClient.patch(`/bot/moderation/${chatId}/settings`, settings);
      setSuccess(true);
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

  const isEnabled = settings.clean_join_messages || settings.clean_leave_messages;

  return (
    <Box>
      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 3 }}>Settings saved successfully!</Alert>}

      {/* Clean Join Messages */}
      <Card sx={{ mb: 3, bgcolor: alpha('#10b981', 0.05), border: '1px solid', borderColor: alpha('#10b981', 0.2) }}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box display="flex" alignItems="center" gap={2}>
              <Box
                sx={{
                  width: 50,
                  height: 50,
                  borderRadius: 2,
                  bgcolor: alpha('#10b981', 0.2),
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <JoinIcon sx={{ color: '#10b981', fontSize: 28 }} />
              </Box>
              <Box>
                <Typography variant="h6">Auto-Delete Join Messages</Typography>
                <Typography variant="body2" color="text.secondary">
                  Automatically remove "User has joined the group" messages
                </Typography>
              </Box>
            </Box>
            <Switch
              checked={settings.clean_join_messages}
              onChange={(e) => setSettings(prev => ({ ...prev, clean_join_messages: e.target.checked }))}
              color="success"
              size="medium"
            />
          </Box>
        </CardContent>
      </Card>

      {/* Clean Leave Messages */}
      <Card sx={{ mb: 3, bgcolor: alpha('#f59e0b', 0.05), border: '1px solid', borderColor: alpha('#f59e0b', 0.2) }}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box display="flex" alignItems="center" gap={2}>
              <Box
                sx={{
                  width: 50,
                  height: 50,
                  borderRadius: 2,
                  bgcolor: alpha('#f59e0b', 0.2),
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <LeaveIcon sx={{ color: '#f59e0b', fontSize: 28 }} />
              </Box>
              <Box>
                <Typography variant="h6">Auto-Delete Leave Messages</Typography>
                <Typography variant="body2" color="text.secondary">
                  Automatically remove "User has left the group" messages
                </Typography>
              </Box>
            </Box>
            <Switch
              checked={settings.clean_leave_messages}
              onChange={(e) => setSettings(prev => ({ ...prev, clean_leave_messages: e.target.checked }))}
              color="warning"
              size="medium"
            />
          </Box>
        </CardContent>
      </Card>

      {/* Delete Delay */}
      {isEnabled && (
        <>
          <Divider sx={{ my: 3 }} />
          
          <Box mb={4}>
            <Typography variant="subtitle1" mb={2}>
              <TimerIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Deletion Delay
            </Typography>
            <Typography variant="body2" color="text.secondary" mb={2}>
              How long to wait before deleting the message (allows members to briefly see join/leave notifications)
            </Typography>
            
            <Box px={2}>
              <Slider
                value={settings.delete_delay_seconds}
                onChange={(_, value) => setSettings(prev => ({ ...prev, delete_delay_seconds: value as number }))}
                min={0}
                max={30}
                step={1}
                marks={[
                  { value: 0, label: 'Instant' },
                  { value: 5, label: '5s' },
                  { value: 15, label: '15s' },
                  { value: 30, label: '30s' },
                ]}
                valueLabelDisplay="auto"
                valueLabelFormat={(value) => `${value}s`}
              />
            </Box>
            
            <Alert severity="info" sx={{ mt: 2 }}>
              {settings.delete_delay_seconds === 0
                ? 'Messages will be deleted immediately upon detection.'
                : `Messages will be deleted after ${settings.delete_delay_seconds} seconds.`
              }
            </Alert>
          </Box>
        </>
      )}

      {/* Preview */}
      <Box
        sx={{
          p: 3,
          borderRadius: 2,
          bgcolor: 'background.default',
          border: '1px dashed',
          borderColor: 'divider',
          mb: 3,
        }}
      >
        <Typography variant="subtitle2" color="text.secondary" mb={2}>
          Preview - This is how system messages look:
        </Typography>
        <Box
          sx={{
            p: 2,
            borderRadius: 1,
            bgcolor: alpha('#3b82f6', 0.1),
            color: 'text.secondary',
            fontStyle: 'italic',
            textDecoration: settings.clean_join_messages ? 'line-through' : 'none',
            opacity: settings.clean_join_messages ? 0.5 : 1,
          }}
        >
          👤 John Doe joined the group
        </Box>
        <Box
          sx={{
            p: 2,
            borderRadius: 1,
            bgcolor: alpha('#ef4444', 0.1),
            color: 'text.secondary',
            fontStyle: 'italic',
            mt: 1,
            textDecoration: settings.clean_leave_messages ? 'line-through' : 'none',
            opacity: settings.clean_leave_messages ? 0.5 : 1,
          }}
        >
          👤 Jane Smith left the group
        </Box>
      </Box>

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

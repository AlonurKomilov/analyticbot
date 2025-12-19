/**
 * Settings Tab Component
 * Configure moderation feature toggles
 */

import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Paper,
  Typography,
  Switch,
  FormControlLabel,
  Grid,
  Divider,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Save as SaveIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import toast from 'react-hot-toast';

import { useModerationStore } from '@/store';
import type { ChatSettingsUpdate, ModerationAction } from '@/types';

interface SettingsTabProps {
  chatId: number;
}

export const SettingsTab: React.FC<SettingsTabProps> = ({ chatId }) => {
  const { t } = useTranslation(['moderation', 'common']);
  const {
    settings,
    isSaving,
    updateSettings,
    deleteSettings,
  } = useModerationStore();

  const [localSettings, setLocalSettings] = useState<ChatSettingsUpdate>({});
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    if (settings) {
      setLocalSettings({
        clean_join_messages: settings.clean_join_messages,
        clean_leave_messages: settings.clean_leave_messages,
        banned_words_enabled: settings.banned_words_enabled,
        anti_spam_enabled: settings.anti_spam_enabled,
        anti_link_enabled: settings.anti_link_enabled,
        anti_forward_enabled: settings.anti_forward_enabled,
        welcome_enabled: settings.welcome_enabled,
        invite_tracking_enabled: settings.invite_tracking_enabled,
        captcha_enabled: settings.captcha_enabled,
        slow_mode_enabled: settings.slow_mode_enabled,
        night_mode_enabled: settings.night_mode_enabled,
        spam_action: settings.spam_action,
        max_warnings: settings.max_warnings,
        warning_action: settings.warning_action,
        mute_duration_minutes: settings.mute_duration_minutes,
        flood_limit: settings.flood_limit,
        flood_interval_seconds: settings.flood_interval_seconds,
        night_mode_start_hour: settings.night_mode_start_hour,
        night_mode_end_hour: settings.night_mode_end_hour,
        night_mode_timezone: settings.night_mode_timezone,
      });
      setHasChanges(false);
    } else {
      // Default values for new settings
      setLocalSettings({
        clean_join_messages: false,
        clean_leave_messages: false,
        banned_words_enabled: false,
        anti_spam_enabled: false,
        anti_link_enabled: false,
        anti_forward_enabled: false,
        welcome_enabled: false,
        invite_tracking_enabled: false,
        captcha_enabled: false,
        slow_mode_enabled: false,
        night_mode_enabled: false,
        spam_action: 'delete',
        max_warnings: 3,
        warning_action: 'mute',
        mute_duration_minutes: 60,
        flood_limit: 5,
        flood_interval_seconds: 10,
        night_mode_start_hour: 22,
        night_mode_end_hour: 8,
        night_mode_timezone: 'UTC',
      });
    }
  }, [settings]);

  const handleToggle = (key: keyof ChatSettingsUpdate) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setLocalSettings((prev: ChatSettingsUpdate) => ({
      ...prev,
      [key]: event.target.checked,
    }));
    setHasChanges(true);
  };

  const handleChange = (key: keyof ChatSettingsUpdate) => (
    event: React.ChangeEvent<HTMLInputElement | { value: unknown }>
  ) => {
    const value = event.target.value;
    setLocalSettings((prev: ChatSettingsUpdate) => ({
      ...prev,
      [key]: typeof value === 'string' && !isNaN(Number(value)) ? Number(value) : value,
    }));
    setHasChanges(true);
  };

  const handleSave = async () => {
    try {
      await updateSettings(chatId, localSettings);
      setHasChanges(false);
      toast.success(t('settings.saveSuccess'));
    } catch (err) {
      toast.error(t('settings.saveError'));
    }
  };

  const handleDelete = async () => {
    if (window.confirm(t('common:confirmDelete'))) {
      try {
        await deleteSettings(chatId);
        toast.success(t('common:deleteSuccess'));
      } catch (err) {
        toast.error(t('common:deleteError'));
      }
    }
  };

  return (
    <Box>
      <Alert severity="info" sx={{ mb: 3 }}>
        {t('settings.optInNotice')}
      </Alert>

      {/* Basic Features */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          {t('settings.title')}
        </Typography>
        <Divider sx={{ mb: 2 }} />

        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={localSettings.clean_join_messages || false}
                  onChange={handleToggle('clean_join_messages')}
                  color="primary"
                />
              }
              label={
                <Box>
                  <Typography variant="body1">{t('settings.cleanJoinMessages.title')}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {t('settings.cleanJoinMessages.description')}
                  </Typography>
                </Box>
              }
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={localSettings.clean_leave_messages || false}
                  onChange={handleToggle('clean_leave_messages')}
                  color="primary"
                />
              }
              label={
                <Box>
                  <Typography variant="body1">{t('settings.cleanLeaveMessages.title')}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {t('settings.cleanLeaveMessages.description')}
                  </Typography>
                </Box>
              }
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={localSettings.welcome_enabled || false}
                  onChange={handleToggle('welcome_enabled')}
                  color="primary"
                />
              }
              label={
                <Box>
                  <Typography variant="body1">{t('settings.welcomeMessages.title')}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {t('settings.welcomeMessages.description')}
                  </Typography>
                </Box>
              }
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={localSettings.invite_tracking_enabled || false}
                  onChange={handleToggle('invite_tracking_enabled')}
                  color="primary"
                />
              }
              label={
                <Box>
                  <Typography variant="body1">{t('settings.inviteTracking.title')}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {t('settings.inviteTracking.description')}
                  </Typography>
                </Box>
              }
            />
          </Grid>
        </Grid>
      </Paper>

      {/* Content Protection */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          {t('common:contentProtection')}
        </Typography>
        <Divider sx={{ mb: 2 }} />

        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={localSettings.banned_words_enabled || false}
                  onChange={handleToggle('banned_words_enabled')}
                  color="primary"
                />
              }
              label={
                <Box>
                  <Typography variant="body1">Banned Words Filter</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Delete messages containing banned words
                  </Typography>
                </Box>
              }
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={localSettings.anti_link_enabled || false}
                  onChange={handleToggle('anti_link_enabled')}
                  color="primary"
                />
              }
              label={
                <Box>
                  <Typography variant="body1">Anti-Link Protection</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Delete messages containing links
                  </Typography>
                </Box>
              }
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={localSettings.anti_forward_enabled || false}
                  onChange={handleToggle('anti_forward_enabled')}
                  color="primary"
                />
              }
              label={
                <Box>
                  <Typography variant="body1">Anti-Forward Protection</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Delete forwarded messages
                  </Typography>
                </Box>
              }
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={localSettings.anti_spam_enabled || false}
                  onChange={handleToggle('anti_spam_enabled')}
                  color="primary"
                />
              }
              label={
                <Box>
                  <Typography variant="body1">Anti-Spam Protection</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Detect and handle spam messages
                  </Typography>
                </Box>
              }
            />
          </Grid>
        </Grid>
      </Paper>

      {/* Advanced Settings */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6">Advanced Settings</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth size="small">
                <InputLabel>Spam Action</InputLabel>
                <Select
                  value={localSettings.spam_action || 'delete'}
                  label="Spam Action"
                  onChange={(e) => {
                    setLocalSettings((prev: ChatSettingsUpdate) => ({
                      ...prev,
                      spam_action: e.target.value as ModerationAction,
                    }));
                    setHasChanges(true);
                  }}
                >
                  <MenuItem value="delete">Delete Message</MenuItem>
                  <MenuItem value="warn">Warn User</MenuItem>
                  <MenuItem value="mute">Mute User</MenuItem>
                  <MenuItem value="kick">Kick User</MenuItem>
                  <MenuItem value="ban">Ban User</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                size="small"
                type="number"
                label="Max Warnings"
                value={localSettings.max_warnings || 3}
                onChange={handleChange('max_warnings')}
                inputProps={{ min: 1, max: 10 }}
                helperText="Number of warnings before action"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth size="small">
                <InputLabel>Warning Action</InputLabel>
                <Select
                  value={localSettings.warning_action || 'mute'}
                  label="Warning Action"
                  onChange={(e) => {
                    setLocalSettings((prev: ChatSettingsUpdate) => ({
                      ...prev,
                      warning_action: e.target.value as ModerationAction,
                    }));
                    setHasChanges(true);
                  }}
                >
                  <MenuItem value="mute">Mute User</MenuItem>
                  <MenuItem value="kick">Kick User</MenuItem>
                  <MenuItem value="ban">Ban User</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                size="small"
                type="number"
                label="Mute Duration (minutes)"
                value={localSettings.mute_duration_minutes || 60}
                onChange={handleChange('mute_duration_minutes')}
                inputProps={{ min: 1, max: 10080 }}
                helperText="How long to mute users (max 7 days)"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                size="small"
                type="number"
                label="Flood Limit"
                value={localSettings.flood_limit || 5}
                onChange={handleChange('flood_limit')}
                inputProps={{ min: 2, max: 20 }}
                helperText="Max messages before flood detection"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                size="small"
                type="number"
                label="Flood Interval (seconds)"
                value={localSettings.flood_interval_seconds || 10}
                onChange={handleChange('flood_interval_seconds')}
                inputProps={{ min: 5, max: 60 }}
                helperText="Time window for flood detection"
              />
            </Grid>
          </Grid>
        </AccordionDetails>
      </Accordion>

      {/* Night Mode */}
      <Accordion sx={{ mt: 2 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography variant="h6">Night Mode</Typography>
            <Switch
              checked={localSettings.night_mode_enabled || false}
              onChange={handleToggle('night_mode_enabled')}
              onClick={(e) => e.stopPropagation()}
            />
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                size="small"
                type="number"
                label="Start Hour (0-23)"
                value={localSettings.night_mode_start_hour || 22}
                onChange={handleChange('night_mode_start_hour')}
                inputProps={{ min: 0, max: 23 }}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                size="small"
                type="number"
                label="End Hour (0-23)"
                value={localSettings.night_mode_end_hour || 8}
                onChange={handleChange('night_mode_end_hour')}
                inputProps={{ min: 0, max: 23 }}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                size="small"
                label="Timezone"
                value={localSettings.night_mode_timezone || 'UTC'}
                onChange={handleChange('night_mode_timezone')}
                placeholder="UTC, Europe/London, etc."
              />
            </Grid>
          </Grid>
        </AccordionDetails>
      </Accordion>

      {/* Action Buttons */}
      <Box sx={{ mt: 3, display: 'flex', gap: 2, justifyContent: 'space-between' }}>
        <Button
          variant="outlined"
          color="error"
          startIcon={<DeleteIcon />}
          onClick={handleDelete}
          disabled={!settings || isSaving}
        >
          {t('common:deleteSettings')}
        </Button>

        <Button
          variant="contained"
          startIcon={isSaving ? <CircularProgress size={20} /> : <SaveIcon />}
          onClick={handleSave}
          disabled={!hasChanges || isSaving}
        >
          {t('settings.saveButton')}
        </Button>
      </Box>
    </Box>
  );
};

export default SettingsTab;

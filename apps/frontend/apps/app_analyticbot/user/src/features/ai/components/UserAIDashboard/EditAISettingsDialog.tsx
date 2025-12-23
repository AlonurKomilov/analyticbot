/**
 * Edit AI Settings Dialog
 * Allows users to configure their AI preferences and behavior
 */

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  FormLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Box,
  Typography,
  Slider,
  Divider,
  Alert,
  CircularProgress,
} from '@mui/material';
import { Settings as SettingsIcon } from '@mui/icons-material';
import toast from 'react-hot-toast';
import { UserAIAPI } from '../../api';
import type { AISettings } from '../../types';

interface EditAISettingsDialogProps {
  open: boolean;
  onClose: () => void;
  currentSettings: AISettings | null;
  onSettingsUpdated?: () => void;
}

export const EditAISettingsDialog: React.FC<EditAISettingsDialogProps> = ({
  open,
  onClose,
  currentSettings,
  onSettingsUpdated,
}) => {
  const [isSaving, setIsSaving] = useState(false);
  const [settings, setSettings] = useState<Partial<AISettings>>({
    temperature: 0.7,
    language: 'en',
    response_style: 'balanced',
    include_recommendations: true,
    include_explanations: true,
    auto_insights_enabled: false,
    auto_insights_frequency: 'weekly',
  });

  // Load current settings when dialog opens
  useEffect(() => {
    if (currentSettings) {
      setSettings({
        temperature: currentSettings.temperature ?? 0.7,
        language: currentSettings.language ?? 'en',
        response_style: currentSettings.response_style ?? 'balanced',
        include_recommendations: currentSettings.include_recommendations ?? true,
        include_explanations: currentSettings.include_explanations ?? true,
        auto_insights_enabled: currentSettings.auto_insights_enabled ?? false,
        auto_insights_frequency: currentSettings.auto_insights_frequency ?? 'weekly',
      });
    }
  }, [currentSettings, open]);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await UserAIAPI.updateSettings(settings);
      toast.success('✅ AI settings updated successfully');
      onSettingsUpdated?.();
      onClose();
    } catch (error: any) {
      console.error('Failed to update AI settings:', error);
      toast.error(error.response?.data?.detail || 'Failed to update settings');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <SettingsIcon />
          <Typography variant="h6">AI Settings</Typography>
        </Box>
      </DialogTitle>

      <DialogContent dividers>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {/* Temperature */}
          <Box>
            <FormLabel>
              <Typography variant="subtitle2" gutterBottom>
                Temperature: {settings.temperature}
              </Typography>
            </FormLabel>
            <Typography variant="caption" color="text.secondary" paragraph>
              Controls randomness. Lower values make output more focused and deterministic.
            </Typography>
            <Slider
              value={settings.temperature ?? 0.7}
              onChange={(_, value) => setSettings({ ...settings, temperature: value as number })}
              min={0}
              max={1}
              step={0.1}
              marks={[
                { value: 0, label: '0' },
                { value: 0.5, label: '0.5' },
                { value: 1, label: '1' },
              ]}
              valueLabelDisplay="auto"
            />
          </Box>

          <Divider />

          {/* Language */}
          <FormControl fullWidth>
            <FormLabel>
              <Typography variant="subtitle2" gutterBottom>
                Response Language
              </Typography>
            </FormLabel>
            <Select
              value={settings.language ?? 'en'}
              onChange={(e) => setSettings({ ...settings, language: e.target.value })}
              size="small"
            >
              <MenuItem value="en">English</MenuItem>
              <MenuItem value="ru">Russian</MenuItem>
              <MenuItem value="uz">Uzbek</MenuItem>
              <MenuItem value="es">Spanish</MenuItem>
              <MenuItem value="fr">French</MenuItem>
            </Select>
          </FormControl>

          {/* Response Style */}
          <FormControl fullWidth>
            <FormLabel>
              <Typography variant="subtitle2" gutterBottom>
                Response Style
              </Typography>
            </FormLabel>
            <Select
              value={settings.response_style ?? 'balanced'}
              onChange={(e) => setSettings({ ...settings, response_style: e.target.value })}
              size="small"
            >
              <MenuItem value="concise">Concise - Brief and to the point</MenuItem>
              <MenuItem value="balanced">Balanced - Detailed but focused</MenuItem>
              <MenuItem value="detailed">Detailed - Comprehensive explanations</MenuItem>
            </Select>
          </FormControl>

          <Divider />

          {/* Toggles */}
          <Box>
            <FormControlLabel
              control={
                <Switch
                  checked={settings.include_recommendations ?? true}
                  onChange={(e) =>
                    setSettings({ ...settings, include_recommendations: e.target.checked })
                  }
                />
              }
              label={
                <Box>
                  <Typography variant="body2">Include Recommendations</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Add actionable suggestions to AI responses
                  </Typography>
                </Box>
              }
            />
          </Box>

          <Box>
            <FormControlLabel
              control={
                <Switch
                  checked={settings.include_explanations ?? true}
                  onChange={(e) =>
                    setSettings({ ...settings, include_explanations: e.target.checked })
                  }
                />
              }
              label={
                <Box>
                  <Typography variant="body2">Include Explanations</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Provide reasoning behind AI insights
                  </Typography>
                </Box>
              }
            />
          </Box>

          <Divider />

          {/* Auto Insights */}
          <Box>
            <FormControlLabel
              control={
                <Switch
                  checked={settings.auto_insights_enabled ?? false}
                  onChange={(e) =>
                    setSettings({ ...settings, auto_insights_enabled: e.target.checked })
                  }
                />
              }
              label={
                <Box>
                  <Typography variant="body2">Auto-Insights</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Automatically generate periodic analytics insights
                  </Typography>
                </Box>
              }
            />
          </Box>

          {settings.auto_insights_enabled && (
            <FormControl fullWidth>
              <FormLabel>
                <Typography variant="subtitle2" gutterBottom>
                  Insights Frequency
                </Typography>
              </FormLabel>
              <Select
                value={settings.auto_insights_frequency ?? 'weekly'}
                onChange={(e) =>
                  setSettings({ ...settings, auto_insights_frequency: e.target.value })
                }
                size="small"
              >
                <MenuItem value="daily">Daily</MenuItem>
                <MenuItem value="weekly">Weekly</MenuItem>
                <MenuItem value="monthly">Monthly</MenuItem>
              </Select>
            </FormControl>
          )}

          <Alert severity="info" sx={{ mt: 1 }}>
            Settings apply to all AI features including analytics, content suggestions, and auto-replies.
          </Alert>
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} disabled={isSaving}>
          Cancel
        </Button>
        <Button
          onClick={handleSave}
          variant="contained"
          disabled={isSaving}
          startIcon={isSaving && <CircularProgress size={16} />}
        >
          {isSaving ? 'Saving...' : 'Save Settings'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default EditAISettingsDialog;

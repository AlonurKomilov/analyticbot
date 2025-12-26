/**
 * AI Settings Page
 * Dedicated page for managing AI configuration and preferences
 */

import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  Switch,
  FormControlLabel,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Divider,
  Slider,
} from '@mui/material';
import {
  Psychology as AIIcon,
  ArrowBack as BackIcon,
  Save as SaveIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useFullAIDashboard } from '@features/ai/hooks';

export const AISettingsPage: React.FC = () => {
  const navigate = useNavigate();
  const { settings, updateSettings, isLoading } = useFullAIDashboard();

  const [localSettings, setLocalSettings] = useState({
    temperature: settings?.temperature ?? 0.7,
    language: settings?.language ?? 'en',
    response_style: settings?.response_style ?? 'balanced',
    include_recommendations: settings?.include_recommendations ?? true,
    include_explanations: settings?.include_explanations ?? true,
    auto_insights_enabled: settings?.auto_insights_enabled ?? false,
    auto_insights_frequency: settings?.auto_insights_frequency ?? 'daily',
  });

  const [isSaving, setIsSaving] = useState(false);

  React.useEffect(() => {
    if (settings) {
      setLocalSettings({
        temperature: settings.temperature ?? 0.7,
        language: settings.language ?? 'en',
        response_style: settings.response_style ?? 'balanced',
        include_recommendations: settings.include_recommendations ?? true,
        include_explanations: settings.include_explanations ?? true,
        auto_insights_enabled: settings.auto_insights_enabled ?? false,
        auto_insights_frequency: settings.auto_insights_frequency ?? 'daily',
      });
    }
  }, [settings]);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await updateSettings(localSettings);
      toast.success('✅ AI settings saved successfully');
      setTimeout(() => navigate('/workers/ai'), 500);
    } catch (error) {
      toast.error('Failed to save settings');
      console.error('Failed to save AI settings:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleBack = () => {
    navigate('/workers/ai');
  };

  return (
    <Box sx={{ maxWidth: 1000, mx: 'auto', py: 4, px: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2 }}>
        <IconButton onClick={handleBack} sx={{ mr: 1 }}>
          <BackIcon />
        </IconButton>
        <Box
          sx={{
            width: 48,
            height: 48,
            borderRadius: 2,
            background: 'linear-gradient(135deg, #9C27B0 0%, #673AB7 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <AIIcon sx={{ color: 'white', fontSize: 28 }} />
        </Box>
        <Box>
          <Typography variant="h4" component="h1" fontWeight={700}>
            AI Settings
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Configure your AI assistant preferences and behavior
          </Typography>
        </Box>
      </Box>

      <Paper sx={{ p: 4 }}>
        <Grid container spacing={4}>
          {/* Model Settings */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom fontWeight={600}>
              Model Settings
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Configure AI model behavior and response characteristics
            </Typography>
          </Grid>

          {/* Temperature */}
          <Grid item xs={12}>
            <Typography variant="body2" gutterBottom fontWeight={500}>
              Temperature (Creativity)
            </Typography>
            <Box sx={{ px: 2 }}>
              <Slider
                value={localSettings.temperature}
                onChange={(_, value) =>
                  setLocalSettings({ ...localSettings, temperature: value as number })
                }
                min={0}
                max={1}
                step={0.1}
                marks={[
                  { value: 0, label: 'Precise' },
                  { value: 0.5, label: 'Balanced' },
                  { value: 1, label: 'Creative' },
                ]}
                valueLabelDisplay="auto"
                sx={{
                  '& .MuiSlider-thumb': {
                    background: 'linear-gradient(135deg, #9C27B0 0%, #673AB7 100%)',
                  },
                  '& .MuiSlider-track': {
                    background: 'linear-gradient(135deg, #9C27B0 0%, #673AB7 100%)',
                  },
                }}
              />
            </Box>
            <Typography variant="caption" color="text.secondary">
              Lower values make responses more focused and deterministic, higher values make them
              more creative
            </Typography>
          </Grid>

          {/* Language */}
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Language</InputLabel>
              <Select
                value={localSettings.language}
                label="Language"
                onChange={(e) =>
                  setLocalSettings({ ...localSettings, language: e.target.value })
                }
              >
                <MenuItem value="en">English</MenuItem>
                <MenuItem value="es">Spanish</MenuItem>
                <MenuItem value="fr">French</MenuItem>
                <MenuItem value="de">German</MenuItem>
                <MenuItem value="ru">Russian</MenuItem>
                <MenuItem value="zh">Chinese</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          {/* Response Style */}
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Response Style</InputLabel>
              <Select
                value={localSettings.response_style}
                label="Response Style"
                onChange={(e) =>
                  setLocalSettings({ ...localSettings, response_style: e.target.value })
                }
              >
                <MenuItem value="concise">Concise</MenuItem>
                <MenuItem value="balanced">Balanced</MenuItem>
                <MenuItem value="detailed">Detailed</MenuItem>
                <MenuItem value="technical">Technical</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <Divider />
          </Grid>

          {/* Features */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom fontWeight={600}>
              Features
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Enable or disable specific AI capabilities
            </Typography>
          </Grid>

          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={localSettings.include_recommendations}
                  onChange={(e) =>
                    setLocalSettings({
                      ...localSettings,
                      include_recommendations: e.target.checked,
                    })
                  }
                  sx={{
                    '& .MuiSwitch-switchBase.Mui-checked': {
                      color: '#9C27B0',
                    },
                    '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                      backgroundColor: '#9C27B0',
                    },
                  }}
                />
              }
              label={
                <Box>
                  <Typography variant="body2" fontWeight={500}>
                    Include Recommendations
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Get actionable suggestions in AI responses
                  </Typography>
                </Box>
              }
            />
          </Grid>

          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={localSettings.include_explanations}
                  onChange={(e) =>
                    setLocalSettings({
                      ...localSettings,
                      include_explanations: e.target.checked,
                    })
                  }
                  sx={{
                    '& .MuiSwitch-switchBase.Mui-checked': {
                      color: '#9C27B0',
                    },
                    '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                      backgroundColor: '#9C27B0',
                    },
                  }}
                />
              }
              label={
                <Box>
                  <Typography variant="body2" fontWeight={500}>
                    Include Explanations
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Get detailed explanations for insights and recommendations
                  </Typography>
                </Box>
              }
            />
          </Grid>

          <Grid item xs={12}>
            <Divider />
          </Grid>

          {/* Auto Insights */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom fontWeight={600}>
              Auto-Insights
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Automatically receive AI-generated insights about your channels
            </Typography>
          </Grid>

          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={localSettings.auto_insights_enabled}
                  onChange={(e) =>
                    setLocalSettings({
                      ...localSettings,
                      auto_insights_enabled: e.target.checked,
                    })
                  }
                  sx={{
                    '& .MuiSwitch-switchBase.Mui-checked': {
                      color: '#9C27B0',
                    },
                    '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                      backgroundColor: '#9C27B0',
                    },
                  }}
                />
              }
              label={
                <Box>
                  <Typography variant="body2" fontWeight={500}>
                    Enable Auto-Insights
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Receive automatic AI insights and recommendations
                  </Typography>
                </Box>
              }
            />
          </Grid>

          {localSettings.auto_insights_enabled && (
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Frequency</InputLabel>
                <Select
                  value={localSettings.auto_insights_frequency}
                  label="Frequency"
                  onChange={(e) =>
                    setLocalSettings({
                      ...localSettings,
                      auto_insights_frequency: e.target.value,
                    })
                  }
                >
                  <MenuItem value="hourly">Hourly</MenuItem>
                  <MenuItem value="daily">Daily</MenuItem>
                  <MenuItem value="weekly">Weekly</MenuItem>
                  <MenuItem value="monthly">Monthly</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          )}

          {/* Actions */}
          <Grid item xs={12}>
            <Divider sx={{ my: 2 }} />
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
              <Button variant="outlined" onClick={handleBack} disabled={isSaving}>
                Cancel
              </Button>
              <Button
                variant="contained"
                startIcon={<SaveIcon />}
                onClick={handleSave}
                disabled={isSaving || isLoading}
                sx={{
                  background: 'linear-gradient(135deg, #9C27B0 0%, #673AB7 100%)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #7B1FA2 0%, #512DA8 100%)',
                  },
                }}
              >
                {isSaving ? 'Saving...' : 'Save Settings'}
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default AISettingsPage;

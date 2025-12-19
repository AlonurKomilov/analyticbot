/**
 * AI Content Moderation Service Configuration
 * 
 * Service: ai_content_moderation
 * Price: 175 credits/month
 * Daily Quota: 500 moderations
 * 
 * Allows users to configure:
 * - Content categories to detect (spam, hate, adult, etc.)
 * - Sensitivity thresholds
 * - Auto-moderation actions
 * - Appeal and review workflows
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
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Stack,
  Grid,
  LinearProgress,
  Paper,
} from '@mui/material';
import {
  Shield as ShieldIcon,
  Save as SaveIcon,
  Speed as SpeedIcon,
  Psychology as AIIcon,
  Warning as WarningIcon,
  Block as BlockIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as HideIcon,
  Gavel as ActionIcon,
  Report as ReportIcon,
} from '@mui/icons-material';
import { apiClient } from '@/api/client';

interface ContentModerationSettings {
  enabled: boolean;
  detect_spam: boolean;
  detect_hate_speech: boolean;
  detect_adult_content: boolean;
  detect_violence: boolean;
  detect_harassment: boolean;
  detect_misinformation: boolean;
  sensitivity: number;
  auto_action: 'none' | 'flag' | 'hide' | 'delete';
  notify_admins: boolean;
  allow_appeals: boolean;
  appeal_window_hours: number;
  log_all_decisions: boolean;
  whitelist_admins: boolean;
  custom_rules_enabled: boolean;
}

interface ModerationStats {
  moderations_today: number;
  moderations_month: number;
  daily_limit: number;
  flagged_today: number;
  auto_removed_today: number;
  false_positive_rate: number;
  categories_breakdown: {
    spam: number;
    hate: number;
    adult: number;
    violence: number;
    other: number;
  };
}

const CONTENT_CATEGORIES = [
  { key: 'detect_spam', label: 'Spam', description: 'Promotional, repetitive content', icon: '📧', color: '#F59E0B' },
  { key: 'detect_hate_speech', label: 'Hate Speech', description: 'Discriminatory language', icon: '🚫', color: '#EF4444' },
  { key: 'detect_adult_content', label: 'Adult Content', description: 'NSFW, explicit material', icon: '🔞', color: '#EC4899' },
  { key: 'detect_violence', label: 'Violence', description: 'Violent or graphic content', icon: '⚠️', color: '#DC2626' },
  { key: 'detect_harassment', label: 'Harassment', description: 'Bullying, threats', icon: '😠', color: '#F97316' },
  { key: 'detect_misinformation', label: 'Misinformation', description: 'False or misleading info', icon: '❌', color: '#8B5CF6' },
];

const AUTO_ACTIONS = [
  { value: 'none', label: 'No Action', description: 'Only log detections', icon: <VisibilityIcon /> },
  { value: 'flag', label: 'Flag for Review', description: 'Mark for human review', icon: <ReportIcon /> },
  { value: 'hide', label: 'Hide Content', description: 'Hide but don\'t delete', icon: <HideIcon /> },
  { value: 'delete', label: 'Auto-Delete', description: 'Immediately remove', icon: <BlockIcon /> },
];

export const ContentModerationConfig: React.FC = () => {
  const [settings, setSettings] = useState<ContentModerationSettings>({
    enabled: true,
    detect_spam: true,
    detect_hate_speech: true,
    detect_adult_content: true,
    detect_violence: true,
    detect_harassment: true,
    detect_misinformation: false,
    sensitivity: 70,
    auto_action: 'flag',
    notify_admins: true,
    allow_appeals: true,
    appeal_window_hours: 24,
    log_all_decisions: true,
    whitelist_admins: true,
    custom_rules_enabled: false,
  });

  const [stats, setStats] = useState<ModerationStats>({
    moderations_today: 0,
    moderations_month: 0,
    daily_limit: 500,
    flagged_today: 0,
    auto_removed_today: 0,
    false_positive_rate: 2.5,
    categories_breakdown: {
      spam: 45,
      hate: 15,
      adult: 10,
      violence: 5,
      other: 25,
    },
  });

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        const savedSettings = localStorage.getItem('ai_content_moderation_settings');
        if (savedSettings) {
          setSettings(prev => ({ ...prev, ...JSON.parse(savedSettings) }));
        }

        try {
          const response = await apiClient.get('/ai/content-moderation/stats') as Record<string, any>;
          if (response) {
            setStats(prev => ({
              ...prev,
              moderations_today: response.today || 0,
              moderations_month: response.month || 0,
              flagged_today: response.flagged || 0,
              auto_removed_today: response.removed || 0,
              false_positive_rate: response.false_positive_rate || 2.5,
            }));
          }
        } catch {
          // Stats not available
        }
      } catch (err: any) {
        setError(err.message || 'Failed to load settings');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);
    setSuccess(false);
    try {
      localStorage.setItem('ai_content_moderation_settings', JSON.stringify(settings));
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

  const dailyUsagePercent = (stats.moderations_today / stats.daily_limit) * 100;

  return (
    <Box>
      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 3 }}>Settings saved successfully!</Alert>}

      {/* Service Header */}
      <Card sx={{ mb: 3, bgcolor: alpha('#EF4444', 0.05), border: '1px solid', borderColor: alpha('#EF4444', 0.2) }}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box display="flex" alignItems="center" gap={2}>
              <ShieldIcon sx={{ color: '#EF4444', fontSize: 40 }} />
              <Box>
                <Typography variant="h6">AI Content Moderation</Typography>
                <Typography variant="body2" color="text.secondary">
                  Automatically detect and moderate harmful content using AI
                </Typography>
              </Box>
            </Box>
            <Stack direction="row" spacing={1}>
              <Chip 
                icon={<AIIcon />}
                label="AI Powered" 
                size="small"
                sx={{ bgcolor: alpha('#EF4444', 0.1), color: '#EF4444' }}
              />
            </Stack>
          </Box>
        </CardContent>
      </Card>

      {/* Moderation Stats */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="subtitle1" mb={2}>
            <SpeedIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Today's Moderation Activity
          </Typography>

          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Box>
                <Box display="flex" justifyContent="space-between" mb={0.5}>
                  <Typography variant="body2">Daily Usage</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {stats.moderations_today} / {stats.daily_limit}
                  </Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={Math.min(dailyUsagePercent, 100)} 
                  sx={{ 
                    height: 8, 
                    borderRadius: 1,
                    bgcolor: alpha('#EF4444', 0.1),
                    '& .MuiLinearProgress-bar': { bgcolor: '#EF4444' }
                  }}
                />
              </Box>
            </Grid>
            <Grid item xs={12} md={2}>
              <Paper sx={{ p: 2, bgcolor: alpha('#F59E0B', 0.05), textAlign: 'center' }}>
                <Typography variant="caption" color="text.secondary">Flagged</Typography>
                <Typography variant="h5" color="#F59E0B">{stats.flagged_today}</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={2}>
              <Paper sx={{ p: 2, bgcolor: alpha('#EF4444', 0.05), textAlign: 'center' }}>
                <Typography variant="caption" color="text.secondary">Removed</Typography>
                <Typography variant="h5" color="#EF4444">{stats.auto_removed_today}</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={2}>
              <Paper sx={{ p: 2, bgcolor: alpha('#22C55E', 0.05), textAlign: 'center' }}>
                <Typography variant="caption" color="text.secondary">Accuracy</Typography>
                <Typography variant="h5" color="#22C55E">{(100 - stats.false_positive_rate).toFixed(1)}%</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={2}>
              <Paper sx={{ p: 2, bgcolor: 'background.default', textAlign: 'center' }}>
                <Typography variant="caption" color="text.secondary">This Month</Typography>
                <Typography variant="h5">{stats.moderations_month}</Typography>
              </Paper>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Content Categories */}
      <Typography variant="subtitle1" mb={2}>
        <WarningIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Content Categories to Detect
      </Typography>

      <Grid container spacing={2} mb={3}>
        {CONTENT_CATEGORIES.map(cat => (
          <Grid item xs={12} sm={6} md={4} key={cat.key}>
            <Paper 
              sx={{ 
                p: 2, 
                cursor: 'pointer',
                border: '2px solid',
                borderColor: settings[cat.key as keyof typeof settings] ? cat.color : 'transparent',
                bgcolor: settings[cat.key as keyof typeof settings] ? alpha(cat.color, 0.05) : 'background.default',
                transition: 'all 0.2s ease',
                '&:hover': { borderColor: alpha(cat.color, 0.5) },
              }}
              onClick={() => setSettings(prev => ({ 
                ...prev, 
                [cat.key]: !prev[cat.key as keyof typeof settings] 
              }))}
            >
              <Box display="flex" alignItems="center" gap={2}>
                <Typography variant="h5">{cat.icon}</Typography>
                <Box flex={1}>
                  <Typography variant="subtitle2">{cat.label}</Typography>
                  <Typography variant="caption" color="text.secondary">{cat.description}</Typography>
                </Box>
                <Switch 
                  checked={settings[cat.key as keyof typeof settings] as boolean} 
                  size="small"
                />
              </Box>
            </Paper>
          </Grid>
        ))}
      </Grid>

      <Divider sx={{ my: 3 }} />

      {/* Sensitivity */}
      <Typography variant="subtitle1" mb={2}>
        Detection Sensitivity
      </Typography>

      <Box mb={3}>
        <Box display="flex" justifyContent="space-between" mb={1}>
          <Typography variant="body2">
            Sensitivity Level: <strong>{settings.sensitivity}%</strong>
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {settings.sensitivity < 40 ? 'Low (fewer false positives)' : 
             settings.sensitivity > 70 ? 'High (catch more violations)' : 'Balanced'}
          </Typography>
        </Box>
        <Slider
          value={settings.sensitivity}
          onChange={(_, value) => setSettings(prev => ({ ...prev, sensitivity: value as number }))}
          min={10}
          max={100}
          step={5}
          marks={[
            { value: 10, label: 'Low' },
            { value: 50, label: 'Medium' },
            { value: 100, label: 'High' },
          ]}
          valueLabelDisplay="auto"
          sx={{ 
            '& .MuiSlider-thumb': { bgcolor: '#EF4444' }, 
            '& .MuiSlider-track': { bgcolor: '#EF4444' } 
          }}
        />
        <Alert severity="info" sx={{ mt: 2 }}>
          Higher sensitivity catches more violations but may have more false positives.
          Lower sensitivity is more accurate but may miss some content.
        </Alert>
      </Box>

      <Divider sx={{ my: 3 }} />

      {/* Auto-Action Settings */}
      <Typography variant="subtitle1" mb={2}>
        <ActionIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Automatic Action
      </Typography>

      <Stack spacing={2} mb={3}>
        {AUTO_ACTIONS.map(action => (
          <Paper
            key={action.value}
            sx={{
              p: 2,
              cursor: 'pointer',
              border: '2px solid',
              borderColor: settings.auto_action === action.value ? '#EF4444' : 'transparent',
              bgcolor: settings.auto_action === action.value ? alpha('#EF4444', 0.05) : 'background.default',
              transition: 'all 0.2s ease',
            }}
            onClick={() => setSettings(prev => ({ ...prev, auto_action: action.value as any }))}
          >
            <Box display="flex" alignItems="center" gap={2}>
              <Box sx={{ color: settings.auto_action === action.value ? '#EF4444' : 'text.secondary' }}>
                {action.icon}
              </Box>
              <Box flex={1}>
                <Typography variant="subtitle2">{action.label}</Typography>
                <Typography variant="caption" color="text.secondary">{action.description}</Typography>
              </Box>
              {settings.auto_action === action.value && (
                <Chip label="Active" size="small" sx={{ bgcolor: '#EF4444', color: 'white' }} />
              )}
            </Box>
          </Paper>
        ))}
      </Stack>

      <FormGroup>
        <Box sx={{ p: 2, borderRadius: 2, bgcolor: 'background.default', mb: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={settings.notify_admins}
                onChange={(e) => setSettings(prev => ({ ...prev, notify_admins: e.target.checked }))}
              />
            }
            label={
              <Box>
                <Typography>Notify Admins</Typography>
                <Typography variant="caption" color="text.secondary">
                  Send notifications to admins when content is flagged
                </Typography>
              </Box>
            }
            sx={{ alignItems: 'flex-start', m: 0 }}
          />
        </Box>
      </FormGroup>

      <Divider sx={{ my: 3 }} />

      {/* Appeals Settings */}
      <Typography variant="subtitle1" mb={2}>
        Appeals & Review
      </Typography>

      <FormGroup>
        <Box sx={{ p: 2, borderRadius: 2, bgcolor: 'background.default', mb: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={settings.allow_appeals}
                onChange={(e) => setSettings(prev => ({ ...prev, allow_appeals: e.target.checked }))}
              />
            }
            label={
              <Box>
                <Typography>Allow Appeals</Typography>
                <Typography variant="caption" color="text.secondary">
                  Let users appeal moderation decisions
                </Typography>
              </Box>
            }
            sx={{ alignItems: 'flex-start', m: 0 }}
          />
        </Box>
      </FormGroup>

      {settings.allow_appeals && (
        <FormControl fullWidth sx={{ mb: 3 }}>
          <InputLabel>Appeal Window</InputLabel>
          <Select
            value={settings.appeal_window_hours}
            label="Appeal Window"
            onChange={(e) => setSettings(prev => ({ ...prev, appeal_window_hours: e.target.value as number }))}
          >
            {[6, 12, 24, 48, 72].map(hours => (
              <MenuItem key={hours} value={hours}>
                {hours} hours
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      )}

      <FormGroup>
        <Box sx={{ p: 2, borderRadius: 2, bgcolor: 'background.default', mb: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={settings.whitelist_admins}
                onChange={(e) => setSettings(prev => ({ ...prev, whitelist_admins: e.target.checked }))}
              />
            }
            label={
              <Box>
                <Typography>Whitelist Admins</Typography>
                <Typography variant="caption" color="text.secondary">
                  Skip moderation for admin messages
                </Typography>
              </Box>
            }
            sx={{ alignItems: 'flex-start', m: 0 }}
          />
        </Box>

        <Box sx={{ p: 2, borderRadius: 2, bgcolor: 'background.default' }}>
          <FormControlLabel
            control={
              <Switch
                checked={settings.log_all_decisions}
                onChange={(e) => setSettings(prev => ({ ...prev, log_all_decisions: e.target.checked }))}
              />
            }
            label={
              <Box>
                <Typography>Log All Decisions</Typography>
                <Typography variant="caption" color="text.secondary">
                  Keep a detailed log of all moderation decisions for audit
                </Typography>
              </Box>
            }
            sx={{ alignItems: 'flex-start', m: 0 }}
          />
        </Box>
      </FormGroup>

      {/* Save Button */}
      <Box mt={4} display="flex" justifyContent="flex-end">
        <Button
          variant="contained"
          startIcon={isSaving ? <CircularProgress size={20} color="inherit" /> : <SaveIcon />}
          onClick={handleSave}
          disabled={isSaving}
          size="large"
          sx={{ bgcolor: '#EF4444', '&:hover': { bgcolor: '#DC2626' } }}
        >
          {isSaving ? 'Saving...' : 'Save Settings'}
        </Button>
      </Box>
    </Box>
  );
};

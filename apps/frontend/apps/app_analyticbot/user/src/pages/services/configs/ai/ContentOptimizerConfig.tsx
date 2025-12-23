/**
 * AI Content Optimizer Service Configuration
 * 
 * Service: ai_content_optimizer
 * Price: 125 credits/month
 * Daily Quota: 50 optimizations
 * 
 * Allows users to configure:
 * - Optimization goals (engagement, reach, clarity)
 * - Tone preferences
 * - Content length targets
 * - Auto-suggestions settings
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
  AutoFixHigh as OptimizeIcon,
  Save as SaveIcon,
  TrendingUp as EngagementIcon,
  Visibility as ReachIcon,
  TextFields as ClarityIcon,
  Speed as SpeedIcon,
  Tune as TuneIcon,
  Psychology as AIIcon,
} from '@mui/icons-material';
import { apiClient } from '@/api/client';

interface ContentOptimizerSettings {
  enabled: boolean;
  optimization_goal: 'engagement' | 'reach' | 'clarity' | 'balanced';
  tone: 'professional' | 'casual' | 'friendly' | 'authoritative' | 'humorous';
  target_length: 'short' | 'medium' | 'long' | 'auto';
  auto_suggest: boolean;
  suggest_hashtags: boolean;
  suggest_emojis: boolean;
  suggest_cta: boolean;
  language: string;
  creativity_level: number;
  preserve_voice: boolean;
}

interface UsageStats {
  optimizations_today: number;
  optimizations_month: number;
  daily_limit: number;
  monthly_limit: number;
  avg_improvement: number;
}

const OPTIMIZATION_GOALS = [
  { value: 'engagement', label: 'Maximize Engagement', description: 'Optimize for likes, comments, shares', icon: <EngagementIcon /> },
  { value: 'reach', label: 'Maximize Reach', description: 'Optimize for views and impressions', icon: <ReachIcon /> },
  { value: 'clarity', label: 'Improve Clarity', description: 'Make content clearer and easier to read', icon: <ClarityIcon /> },
  { value: 'balanced', label: 'Balanced', description: 'Balance all optimization factors', icon: <TuneIcon /> },
];

const TONE_OPTIONS = [
  { value: 'professional', label: 'Professional', emoji: '👔' },
  { value: 'casual', label: 'Casual', emoji: '😊' },
  { value: 'friendly', label: 'Friendly', emoji: '🤗' },
  { value: 'authoritative', label: 'Authoritative', emoji: '📢' },
  { value: 'humorous', label: 'Humorous', emoji: '😄' },
];

const LENGTH_OPTIONS = [
  { value: 'short', label: 'Short', description: '< 100 characters' },
  { value: 'medium', label: 'Medium', description: '100-280 characters' },
  { value: 'long', label: 'Long', description: '280+ characters' },
  { value: 'auto', label: 'Auto', description: 'AI decides based on content' },
];

export const ContentOptimizerConfig: React.FC = () => {
  const [settings, setSettings] = useState<ContentOptimizerSettings>({
    enabled: true,
    optimization_goal: 'balanced',
    tone: 'professional',
    target_length: 'auto',
    auto_suggest: true,
    suggest_hashtags: true,
    suggest_emojis: false,
    suggest_cta: true,
    language: 'en',
    creativity_level: 50,
    preserve_voice: true,
  });

  const [usageStats, setUsageStats] = useState<UsageStats>({
    optimizations_today: 0,
    optimizations_month: 0,
    daily_limit: 50,
    monthly_limit: 1000,
    avg_improvement: 0,
  });

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        const savedSettings = localStorage.getItem('ai_content_optimizer_settings');
        if (savedSettings) {
          setSettings(prev => ({ ...prev, ...JSON.parse(savedSettings) }));
        }

        // Try to fetch usage stats
        try {
          const response = await apiClient.get('/ai/content-optimizer/stats') as Record<string, any>;
          if (response) {
            setUsageStats(prev => ({
              ...prev,
              optimizations_today: response.today || 0,
              optimizations_month: response.month || 0,
              avg_improvement: response.avg_improvement || 0,
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
      localStorage.setItem('ai_content_optimizer_settings', JSON.stringify(settings));
      
      // TODO: Save to backend when API is ready
      // await apiClient.patch('/ai/content-optimizer/settings', settings);
      
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

  const dailyUsagePercent = (usageStats.optimizations_today / usageStats.daily_limit) * 100;

  return (
    <Box>
      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 3 }}>Settings saved successfully!</Alert>}

      {/* Service Header */}
      <Card sx={{ mb: 3, bgcolor: alpha('#6366F1', 0.05), border: '1px solid', borderColor: alpha('#6366F1', 0.2) }}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box display="flex" alignItems="center" gap={2}>
              <OptimizeIcon sx={{ color: '#6366F1', fontSize: 40 }} />
              <Box>
                <Typography variant="h6">AI Content Optimizer</Typography>
                <Typography variant="body2" color="text.secondary">
                  Get AI-powered suggestions to improve your posts for better engagement
                </Typography>
              </Box>
            </Box>
            <Stack direction="row" spacing={1}>
              <Chip 
                icon={<AIIcon />}
                label="AI Powered" 
                size="small"
                sx={{ bgcolor: alpha('#6366F1', 0.1), color: '#6366F1' }}
              />
            </Stack>
          </Box>
        </CardContent>
      </Card>

      {/* Usage Stats */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="subtitle1" mb={2}>
            <SpeedIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Usage & Performance
          </Typography>

          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Box>
                <Box display="flex" justifyContent="space-between" mb={0.5}>
                  <Typography variant="body2">Daily Usage</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {usageStats.optimizations_today} / {usageStats.daily_limit}
                  </Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={Math.min(dailyUsagePercent, 100)} 
                  color={dailyUsagePercent > 80 ? 'warning' : 'primary'}
                  sx={{ height: 8, borderRadius: 1 }}
                />
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2, bgcolor: 'background.default', textAlign: 'center' }}>
                <Typography variant="caption" color="text.secondary">This Month</Typography>
                <Typography variant="h5">{usageStats.optimizations_month}</Typography>
                <Typography variant="caption" color="text.secondary">optimizations</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2, bgcolor: 'background.default', textAlign: 'center' }}>
                <Typography variant="caption" color="text.secondary">Avg. Improvement</Typography>
                <Typography variant="h5" color="success.main">+{usageStats.avg_improvement}%</Typography>
                <Typography variant="caption" color="text.secondary">engagement</Typography>
              </Paper>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Optimization Goal */}
      <Typography variant="subtitle1" mb={2}>
        <TuneIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Optimization Goal
      </Typography>

      <Grid container spacing={2} mb={3}>
        {OPTIMIZATION_GOALS.map(goal => (
          <Grid item xs={12} sm={6} md={3} key={goal.value}>
            <Card 
              sx={{ 
                p: 2, 
                cursor: 'pointer',
                height: '100%',
                border: '2px solid',
                borderColor: settings.optimization_goal === goal.value ? 'primary.main' : 'transparent',
                bgcolor: settings.optimization_goal === goal.value ? alpha('#6366F1', 0.05) : 'background.default',
                transition: 'all 0.2s ease',
                '&:hover': {
                  borderColor: alpha('#6366F1', 0.5),
                },
              }}
              onClick={() => setSettings(prev => ({ ...prev, optimization_goal: goal.value as any }))}
            >
              <Box textAlign="center">
                <Box sx={{ color: settings.optimization_goal === goal.value ? '#6366F1' : 'text.secondary', mb: 1 }}>
                  {goal.icon}
                </Box>
                <Typography variant="subtitle2">{goal.label}</Typography>
                <Typography variant="caption" color="text.secondary">
                  {goal.description}
                </Typography>
              </Box>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Divider sx={{ my: 3 }} />

      {/* Tone & Style */}
      <Typography variant="subtitle1" mb={2}>
        Tone & Style
      </Typography>

      <FormControl fullWidth sx={{ mb: 3 }}>
        <InputLabel>Content Tone</InputLabel>
        <Select
          value={settings.tone}
          label="Content Tone"
          onChange={(e) => setSettings(prev => ({ ...prev, tone: e.target.value as any }))}
        >
          {TONE_OPTIONS.map(option => (
            <MenuItem key={option.value} value={option.value}>
              {option.emoji} {option.label}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <FormControl fullWidth sx={{ mb: 3 }}>
        <InputLabel>Target Length</InputLabel>
        <Select
          value={settings.target_length}
          label="Target Length"
          onChange={(e) => setSettings(prev => ({ ...prev, target_length: e.target.value as any }))}
        >
          {LENGTH_OPTIONS.map(option => (
            <MenuItem key={option.value} value={option.value}>
              <Box>
                <Typography>{option.label}</Typography>
                <Typography variant="caption" color="text.secondary">{option.description}</Typography>
              </Box>
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <Box mb={3}>
        <Typography variant="body2" gutterBottom>
          Creativity Level: <strong>{settings.creativity_level}%</strong>
        </Typography>
        <Typography variant="caption" color="text.secondary" display="block" mb={2}>
          Higher = more creative suggestions, Lower = safer, more predictable
        </Typography>
        <Slider
          value={settings.creativity_level}
          onChange={(_, value) => setSettings(prev => ({ ...prev, creativity_level: value as number }))}
          min={0}
          max={100}
          step={10}
          marks={[
            { value: 0, label: 'Safe' },
            { value: 50, label: 'Balanced' },
            { value: 100, label: 'Creative' },
          ]}
          valueLabelDisplay="auto"
          valueLabelFormat={(value) => `${value}%`}
        />
      </Box>

      <Divider sx={{ my: 3 }} />

      {/* Auto-Suggest Features */}
      <Typography variant="subtitle1" mb={2}>
        Auto-Suggest Features
      </Typography>

      <FormGroup>
        <Box sx={{ p: 2, borderRadius: 2, bgcolor: 'background.default', mb: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={settings.auto_suggest}
                onChange={(e) => setSettings(prev => ({ ...prev, auto_suggest: e.target.checked }))}
              />
            }
            label={
              <Box>
                <Typography>Auto-Suggest Mode</Typography>
                <Typography variant="caption" color="text.secondary">
                  Automatically show optimization suggestions while typing
                </Typography>
              </Box>
            }
            sx={{ alignItems: 'flex-start', m: 0 }}
          />
        </Box>

        <Grid container spacing={2}>
          <Grid item xs={12} sm={4}>
            <Paper 
              sx={{ 
                p: 2, 
                cursor: 'pointer',
                border: '2px solid',
                borderColor: settings.suggest_hashtags ? 'primary.main' : 'transparent',
                bgcolor: settings.suggest_hashtags ? alpha('#6366F1', 0.05) : 'background.default',
              }}
              onClick={() => setSettings(prev => ({ ...prev, suggest_hashtags: !prev.suggest_hashtags }))}
            >
              <Box display="flex" alignItems="center" gap={1}>
                <Switch checked={settings.suggest_hashtags} size="small" />
                <Box>
                  <Typography variant="body2">#️⃣ Hashtags</Typography>
                  <Typography variant="caption" color="text.secondary">Suggest relevant hashtags</Typography>
                </Box>
              </Box>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Paper 
              sx={{ 
                p: 2, 
                cursor: 'pointer',
                border: '2px solid',
                borderColor: settings.suggest_emojis ? 'primary.main' : 'transparent',
                bgcolor: settings.suggest_emojis ? alpha('#6366F1', 0.05) : 'background.default',
              }}
              onClick={() => setSettings(prev => ({ ...prev, suggest_emojis: !prev.suggest_emojis }))}
            >
              <Box display="flex" alignItems="center" gap={1}>
                <Switch checked={settings.suggest_emojis} size="small" />
                <Box>
                  <Typography variant="body2">😀 Emojis</Typography>
                  <Typography variant="caption" color="text.secondary">Suggest emojis to add</Typography>
                </Box>
              </Box>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Paper 
              sx={{ 
                p: 2, 
                cursor: 'pointer',
                border: '2px solid',
                borderColor: settings.suggest_cta ? 'primary.main' : 'transparent',
                bgcolor: settings.suggest_cta ? alpha('#6366F1', 0.05) : 'background.default',
              }}
              onClick={() => setSettings(prev => ({ ...prev, suggest_cta: !prev.suggest_cta }))}
            >
              <Box display="flex" alignItems="center" gap={1}>
                <Switch checked={settings.suggest_cta} size="small" />
                <Box>
                  <Typography variant="body2">📢 Call-to-Action</Typography>
                  <Typography variant="caption" color="text.secondary">Suggest CTAs</Typography>
                </Box>
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </FormGroup>

      <Divider sx={{ my: 3 }} />

      {/* Advanced Settings */}
      <Typography variant="subtitle1" mb={2}>
        Advanced Settings
      </Typography>

      <FormGroup>
        <Box sx={{ p: 2, borderRadius: 2, bgcolor: 'background.default' }}>
          <FormControlLabel
            control={
              <Switch
                checked={settings.preserve_voice}
                onChange={(e) => setSettings(prev => ({ ...prev, preserve_voice: e.target.checked }))}
              />
            }
            label={
              <Box>
                <Typography>Preserve My Voice</Typography>
                <Typography variant="caption" color="text.secondary">
                  AI learns and maintains your unique writing style
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
          sx={{ bgcolor: '#6366F1', '&:hover': { bgcolor: '#4F46E5' } }}
        >
          {isSaving ? 'Saving...' : 'Save Settings'}
        </Button>
      </Box>
    </Box>
  );
};

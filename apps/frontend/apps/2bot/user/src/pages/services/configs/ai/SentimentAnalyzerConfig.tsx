/**
 * AI Sentiment Analyzer Service Configuration
 * 
 * Service: ai_sentiment_analyzer
 * Price: 100 credits/month
 * Daily Quota: 100 analyses
 * 
 * Allows users to configure:
 * - Analysis scope (comments, reactions, mentions)
 * - Alert thresholds for negative sentiment
 * - Reporting preferences
 * - Language detection settings
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
  SentimentSatisfied as SentimentIcon,
  Save as SaveIcon,
  NotificationsActive as AlertIcon,
  Analytics as AnalyticsIcon,
  Language as LanguageIcon,
  Speed as SpeedIcon,
  Psychology as AIIcon,
  TrendingUp as TrendingIcon,
  TrendingDown as TrendingDownIcon,
} from '@mui/icons-material';
import { apiClient } from '@/api/client';

interface SentimentAnalyzerSettings {
  enabled: boolean;
  analyze_comments: boolean;
  analyze_reactions: boolean;
  analyze_mentions: boolean;
  analyze_dms: boolean;
  alert_threshold: number;
  alert_on_negative_spike: boolean;
  alert_on_positive_spike: boolean;
  report_frequency: 'realtime' | 'hourly' | 'daily' | 'weekly';
  auto_detect_language: boolean;
  primary_language: string;
  track_keywords: boolean;
  aggregate_by_channel: boolean;
}

interface SentimentStats {
  analyses_today: number;
  analyses_month: number;
  daily_limit: number;
  avg_sentiment: number;
  positive_percent: number;
  neutral_percent: number;
  negative_percent: number;
}

const REPORT_FREQUENCIES = [
  { value: 'realtime', label: 'Real-time', description: 'Instant analysis as messages arrive' },
  { value: 'hourly', label: 'Hourly', description: 'Aggregated hourly reports' },
  { value: 'daily', label: 'Daily', description: 'Daily sentiment summary' },
  { value: 'weekly', label: 'Weekly', description: 'Weekly trend reports' },
];

const LANGUAGE_OPTIONS = [
  { value: 'en', label: 'English' },
  { value: 'ru', label: 'Russian' },
  { value: 'es', label: 'Spanish' },
  { value: 'de', label: 'German' },
  { value: 'fr', label: 'French' },
  { value: 'zh', label: 'Chinese' },
  { value: 'ar', label: 'Arabic' },
  { value: 'pt', label: 'Portuguese' },
];

export const SentimentAnalyzerConfig: React.FC = () => {
  const [settings, setSettings] = useState<SentimentAnalyzerSettings>({
    enabled: true,
    analyze_comments: true,
    analyze_reactions: true,
    analyze_mentions: true,
    analyze_dms: false,
    alert_threshold: 30,
    alert_on_negative_spike: true,
    alert_on_positive_spike: false,
    report_frequency: 'daily',
    auto_detect_language: true,
    primary_language: 'en',
    track_keywords: true,
    aggregate_by_channel: true,
  });

  const [stats, setStats] = useState<SentimentStats>({
    analyses_today: 0,
    analyses_month: 0,
    daily_limit: 100,
    avg_sentiment: 0.65,
    positive_percent: 45,
    neutral_percent: 40,
    negative_percent: 15,
  });

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        const savedSettings = localStorage.getItem('ai_sentiment_settings');
        if (savedSettings) {
          setSettings(prev => ({ ...prev, ...JSON.parse(savedSettings) }));
        }

        try {
          const response = await apiClient.get('/ai/sentiment/stats') as Record<string, any>;
          if (response) {
            setStats(prev => ({
              ...prev,
              analyses_today: response.today || 0,
              analyses_month: response.month || 0,
              avg_sentiment: response.avg_sentiment || 0.65,
              positive_percent: response.positive || 45,
              neutral_percent: response.neutral || 40,
              negative_percent: response.negative || 15,
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
      localStorage.setItem('ai_sentiment_settings', JSON.stringify(settings));
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

  const dailyUsagePercent = (stats.analyses_today / stats.daily_limit) * 100;
  const sentimentColor = stats.avg_sentiment > 0.6 ? 'success' : stats.avg_sentiment > 0.4 ? 'warning' : 'error';

  return (
    <Box>
      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 3 }}>Settings saved successfully!</Alert>}

      {/* Service Header */}
      <Card sx={{ mb: 3, bgcolor: alpha('#EC4899', 0.05), border: '1px solid', borderColor: alpha('#EC4899', 0.2) }}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box display="flex" alignItems="center" gap={2}>
              <SentimentIcon sx={{ color: '#EC4899', fontSize: 40 }} />
              <Box>
                <Typography variant="h6">AI Sentiment Analyzer</Typography>
                <Typography variant="body2" color="text.secondary">
                  Understand audience mood and reactions with AI-powered sentiment analysis
                </Typography>
              </Box>
            </Box>
            <Stack direction="row" spacing={1}>
              <Chip 
                icon={<AIIcon />}
                label="AI Powered" 
                size="small"
                sx={{ bgcolor: alpha('#EC4899', 0.1), color: '#EC4899' }}
              />
            </Stack>
          </Box>
        </CardContent>
      </Card>

      {/* Sentiment Overview */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="subtitle1" mb={2}>
            <AnalyticsIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Sentiment Overview
          </Typography>

          <Grid container spacing={3}>
            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, bgcolor: 'background.default', textAlign: 'center' }}>
                <Typography variant="caption" color="text.secondary">Average Sentiment</Typography>
                <Typography variant="h4" color={`${sentimentColor}.main`}>
                  {(stats.avg_sentiment * 100).toFixed(0)}%
                </Typography>
                <Chip 
                  size="small" 
                  label={stats.avg_sentiment > 0.6 ? 'Positive' : stats.avg_sentiment > 0.4 ? 'Mixed' : 'Negative'}
                  color={sentimentColor}
                />
              </Paper>
            </Grid>
            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, bgcolor: alpha('#22C55E', 0.05) }}>
                <Box display="flex" alignItems="center" gap={1}>
                  <TrendingIcon sx={{ color: '#22C55E' }} />
                  <Typography variant="body2">Positive</Typography>
                </Box>
                <Typography variant="h5" color="#22C55E">{stats.positive_percent}%</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, bgcolor: alpha('#F59E0B', 0.05) }}>
                <Typography variant="body2" color="text.secondary">Neutral</Typography>
                <Typography variant="h5" color="#F59E0B">{stats.neutral_percent}%</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, bgcolor: alpha('#EF4444', 0.05) }}>
                <Box display="flex" alignItems="center" gap={1}>
                  <TrendingDownIcon sx={{ color: '#EF4444' }} />
                  <Typography variant="body2">Negative</Typography>
                </Box>
                <Typography variant="h5" color="#EF4444">{stats.negative_percent}%</Typography>
              </Paper>
            </Grid>
          </Grid>

          <Box mt={3}>
            <Box display="flex" justifyContent="space-between" mb={0.5}>
              <Typography variant="body2">Daily Analysis Usage</Typography>
              <Typography variant="body2" color="text.secondary">
                {stats.analyses_today} / {stats.daily_limit}
              </Typography>
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={Math.min(dailyUsagePercent, 100)} 
              sx={{ 
                height: 8, 
                borderRadius: 1,
                bgcolor: alpha('#EC4899', 0.1),
                '& .MuiLinearProgress-bar': { bgcolor: '#EC4899' }
              }}
            />
          </Box>
        </CardContent>
      </Card>

      {/* Analysis Scope */}
      <Typography variant="subtitle1" mb={2}>
        <SpeedIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Analysis Scope
      </Typography>

      <Grid container spacing={2} mb={3}>
        {[
          { key: 'analyze_comments', label: 'Comments', description: 'Analyze comment sentiment' },
          { key: 'analyze_reactions', label: 'Reactions', description: 'Track reaction patterns' },
          { key: 'analyze_mentions', label: 'Mentions', description: 'Monitor @mentions' },
          { key: 'analyze_dms', label: 'Direct Messages', description: 'Analyze DM sentiment' },
        ].map(item => (
          <Grid item xs={12} sm={6} md={3} key={item.key}>
            <Paper 
              sx={{ 
                p: 2, 
                cursor: 'pointer',
                border: '2px solid',
                borderColor: settings[item.key as keyof typeof settings] ? '#EC4899' : 'transparent',
                bgcolor: settings[item.key as keyof typeof settings] ? alpha('#EC4899', 0.05) : 'background.default',
                transition: 'all 0.2s ease',
              }}
              onClick={() => setSettings(prev => ({ 
                ...prev, 
                [item.key]: !prev[item.key as keyof typeof settings] 
              }))}
            >
              <Box display="flex" alignItems="center" gap={1}>
                <Switch 
                  checked={settings[item.key as keyof typeof settings] as boolean} 
                  size="small"
                  sx={{ '& .Mui-checked': { color: '#EC4899' } }}
                />
                <Box>
                  <Typography variant="body2">{item.label}</Typography>
                  <Typography variant="caption" color="text.secondary">{item.description}</Typography>
                </Box>
              </Box>
            </Paper>
          </Grid>
        ))}
      </Grid>

      <Divider sx={{ my: 3 }} />

      {/* Alert Settings */}
      <Typography variant="subtitle1" mb={2}>
        <AlertIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Alert Settings
      </Typography>

      <Box mb={3}>
        <Typography variant="body2" gutterBottom>
          Negative Sentiment Alert Threshold: <strong>{settings.alert_threshold}%</strong>
        </Typography>
        <Typography variant="caption" color="text.secondary" display="block" mb={2}>
          Get alerted when negative sentiment exceeds this percentage
        </Typography>
        <Slider
          value={settings.alert_threshold}
          onChange={(_, value) => setSettings(prev => ({ ...prev, alert_threshold: value as number }))}
          min={10}
          max={50}
          step={5}
          marks={[
            { value: 10, label: '10%' },
            { value: 25, label: '25%' },
            { value: 50, label: '50%' },
          ]}
          valueLabelDisplay="auto"
          valueLabelFormat={(value) => `${value}%`}
          sx={{ '& .MuiSlider-thumb': { bgcolor: '#EC4899' }, '& .MuiSlider-track': { bgcolor: '#EC4899' } }}
        />
      </Box>

      <FormGroup>
        <Box sx={{ p: 2, borderRadius: 2, bgcolor: 'background.default', mb: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={settings.alert_on_negative_spike}
                onChange={(e) => setSettings(prev => ({ ...prev, alert_on_negative_spike: e.target.checked }))}
              />
            }
            label={
              <Box>
                <Typography>Alert on Negative Spike</Typography>
                <Typography variant="caption" color="text.secondary">
                  Notify when negative sentiment suddenly increases
                </Typography>
              </Box>
            }
            sx={{ alignItems: 'flex-start', m: 0 }}
          />
        </Box>

        <Box sx={{ p: 2, borderRadius: 2, bgcolor: 'background.default', mb: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={settings.alert_on_positive_spike}
                onChange={(e) => setSettings(prev => ({ ...prev, alert_on_positive_spike: e.target.checked }))}
              />
            }
            label={
              <Box>
                <Typography>Alert on Positive Spike</Typography>
                <Typography variant="caption" color="text.secondary">
                  Notify when positive sentiment suddenly increases (viral content)
                </Typography>
              </Box>
            }
            sx={{ alignItems: 'flex-start', m: 0 }}
          />
        </Box>
      </FormGroup>

      <Divider sx={{ my: 3 }} />

      {/* Reporting Settings */}
      <Typography variant="subtitle1" mb={2}>
        Report Frequency
      </Typography>

      <Stack spacing={2} mb={3}>
        {REPORT_FREQUENCIES.map(freq => (
          <Paper
            key={freq.value}
            sx={{
              p: 2,
              cursor: 'pointer',
              border: '2px solid',
              borderColor: settings.report_frequency === freq.value ? '#EC4899' : 'transparent',
              bgcolor: settings.report_frequency === freq.value ? alpha('#EC4899', 0.05) : 'background.default',
              transition: 'all 0.2s ease',
            }}
            onClick={() => setSettings(prev => ({ ...prev, report_frequency: freq.value as any }))}
          >
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography variant="subtitle2">{freq.label}</Typography>
                <Typography variant="caption" color="text.secondary">{freq.description}</Typography>
              </Box>
              {settings.report_frequency === freq.value && (
                <Chip label="Active" size="small" sx={{ bgcolor: '#EC4899', color: 'white' }} />
              )}
            </Box>
          </Paper>
        ))}
      </Stack>

      <Divider sx={{ my: 3 }} />

      {/* Language Settings */}
      <Typography variant="subtitle1" mb={2}>
        <LanguageIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Language Settings
      </Typography>

      <FormGroup>
        <Box sx={{ p: 2, borderRadius: 2, bgcolor: 'background.default', mb: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={settings.auto_detect_language}
                onChange={(e) => setSettings(prev => ({ ...prev, auto_detect_language: e.target.checked }))}
              />
            }
            label={
              <Box>
                <Typography>Auto-Detect Language</Typography>
                <Typography variant="caption" color="text.secondary">
                  Automatically detect and analyze content in multiple languages
                </Typography>
              </Box>
            }
            sx={{ alignItems: 'flex-start', m: 0 }}
          />
        </Box>
      </FormGroup>

      {!settings.auto_detect_language && (
        <FormControl fullWidth sx={{ mb: 3 }}>
          <InputLabel>Primary Language</InputLabel>
          <Select
            value={settings.primary_language}
            label="Primary Language"
            onChange={(e) => setSettings(prev => ({ ...prev, primary_language: e.target.value }))}
          >
            {LANGUAGE_OPTIONS.map(option => (
              <MenuItem key={option.value} value={option.value}>
                {option.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      )}

      {/* Save Button */}
      <Box mt={4} display="flex" justifyContent="flex-end">
        <Button
          variant="contained"
          startIcon={isSaving ? <CircularProgress size={20} color="inherit" /> : <SaveIcon />}
          onClick={handleSave}
          disabled={isSaving}
          size="large"
          sx={{ bgcolor: '#EC4899', '&:hover': { bgcolor: '#DB2777' } }}
        >
          {isSaving ? 'Saving...' : 'Save Settings'}
        </Button>
      </Box>
    </Box>
  );
};

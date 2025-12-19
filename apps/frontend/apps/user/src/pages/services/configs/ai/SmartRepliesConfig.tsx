/**
 * AI Smart Replies Service Configuration
 * 
 * Service: ai_smart_replies
 * Price: 150 credits/month
 * Daily Quota: 200 replies
 * 
 * Allows users to configure:
 * - Reply tone and style
 * - Response templates
 * - Auto-reply triggers
 * - Context awareness settings
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
  Chip,
  Stack,
  Grid,
  LinearProgress,
  Paper,
  TextField,
} from '@mui/material';
import {
  QuickreplyRounded as ReplyIcon,
  Save as SaveIcon,
  Speed as SpeedIcon,
  Psychology as AIIcon,
  AutoAwesome as AutoIcon,
  Timer as TimerIcon,
  Tune as TuneIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { apiClient } from '@/api/client';

interface SmartRepliesSettings {
  enabled: boolean;
  reply_tone: 'professional' | 'friendly' | 'casual' | 'formal';
  response_speed: 'instant' | 'natural' | 'delayed';
  delay_seconds: number;
  context_messages: number;
  auto_reply_enabled: boolean;
  auto_reply_triggers: string[];
  include_greeting: boolean;
  include_signature: boolean;
  signature_text: string;
  max_length: number;
  use_emojis: boolean;
  learn_from_history: boolean;
}

interface UsageStats {
  replies_today: number;
  replies_month: number;
  daily_limit: number;
  monthly_limit: number;
  avg_response_time_ms: number;
  satisfaction_rate: number;
}

const TONE_OPTIONS = [
  { value: 'professional', label: 'Professional', description: 'Business-appropriate responses', emoji: '👔' },
  { value: 'friendly', label: 'Friendly', description: 'Warm and personable', emoji: '😊' },
  { value: 'casual', label: 'Casual', description: 'Relaxed and informal', emoji: '👋' },
  { value: 'formal', label: 'Formal', description: 'Strict and official', emoji: '📋' },
];

const SPEED_OPTIONS = [
  { value: 'instant', label: 'Instant', description: 'Reply immediately' },
  { value: 'natural', label: 'Natural', description: 'Simulate human typing delay' },
  { value: 'delayed', label: 'Delayed', description: 'Custom delay before reply' },
];

export const SmartRepliesConfig: React.FC = () => {
  const [settings, setSettings] = useState<SmartRepliesSettings>({
    enabled: true,
    reply_tone: 'friendly',
    response_speed: 'natural',
    delay_seconds: 3,
    context_messages: 5,
    auto_reply_enabled: false,
    auto_reply_triggers: ['hello', 'help', 'support'],
    include_greeting: true,
    include_signature: false,
    signature_text: '',
    max_length: 500,
    use_emojis: true,
    learn_from_history: true,
  });

  const [stats, setStats] = useState<UsageStats>({
    replies_today: 0,
    replies_month: 0,
    daily_limit: 200,
    monthly_limit: 4000,
    avg_response_time_ms: 1200,
    satisfaction_rate: 92,
  });

  const [newTrigger, setNewTrigger] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        const savedSettings = localStorage.getItem('ai_smart_replies_settings');
        if (savedSettings) {
          setSettings(prev => ({ ...prev, ...JSON.parse(savedSettings) }));
        }

        try {
          const response = await apiClient.get('/ai/smart-replies/stats') as Record<string, any>;
          if (response) {
            setStats(prev => ({
              ...prev,
              replies_today: response.today || 0,
              replies_month: response.month || 0,
              avg_response_time_ms: response.avg_response_time || 1200,
              satisfaction_rate: response.satisfaction || 92,
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
      localStorage.setItem('ai_smart_replies_settings', JSON.stringify(settings));
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err: any) {
      setError(err.message || 'Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddTrigger = () => {
    if (newTrigger.trim() && !settings.auto_reply_triggers.includes(newTrigger.trim().toLowerCase())) {
      setSettings(prev => ({
        ...prev,
        auto_reply_triggers: [...prev.auto_reply_triggers, newTrigger.trim().toLowerCase()],
      }));
      setNewTrigger('');
    }
  };

  const handleRemoveTrigger = (trigger: string) => {
    setSettings(prev => ({
      ...prev,
      auto_reply_triggers: prev.auto_reply_triggers.filter(t => t !== trigger),
    }));
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" py={4}>
        <CircularProgress />
      </Box>
    );
  }

  const dailyUsagePercent = (stats.replies_today / stats.daily_limit) * 100;

  return (
    <Box>
      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 3 }}>Settings saved successfully!</Alert>}

      {/* Service Header */}
      <Card sx={{ mb: 3, bgcolor: alpha('#14B8A6', 0.05), border: '1px solid', borderColor: alpha('#14B8A6', 0.2) }}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box display="flex" alignItems="center" gap={2}>
              <ReplyIcon sx={{ color: '#14B8A6', fontSize: 40 }} />
              <Box>
                <Typography variant="h6">AI Smart Replies</Typography>
                <Typography variant="body2" color="text.secondary">
                  Generate intelligent, context-aware reply suggestions powered by AI
                </Typography>
              </Box>
            </Box>
            <Stack direction="row" spacing={1}>
              <Chip 
                icon={<AIIcon />}
                label="AI Powered" 
                size="small"
                sx={{ bgcolor: alpha('#14B8A6', 0.1), color: '#14B8A6' }}
              />
            </Stack>
          </Box>
        </CardContent>
      </Card>

      {/* Usage & Performance Stats */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="subtitle1" mb={2}>
            <SpeedIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Usage & Performance
          </Typography>

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Box>
                <Box display="flex" justifyContent="space-between" mb={0.5}>
                  <Typography variant="body2">Daily Usage</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {stats.replies_today} / {stats.daily_limit}
                  </Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={Math.min(dailyUsagePercent, 100)} 
                  sx={{ 
                    height: 8, 
                    borderRadius: 1,
                    bgcolor: alpha('#14B8A6', 0.1),
                    '& .MuiLinearProgress-bar': { bgcolor: '#14B8A6' }
                  }}
                />
              </Box>
            </Grid>
            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, bgcolor: 'background.default', textAlign: 'center' }}>
                <Typography variant="caption" color="text.secondary">Avg Response</Typography>
                <Typography variant="h5">{(stats.avg_response_time_ms / 1000).toFixed(1)}s</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, bgcolor: 'background.default', textAlign: 'center' }}>
                <Typography variant="caption" color="text.secondary">Satisfaction</Typography>
                <Typography variant="h5" color="success.main">{stats.satisfaction_rate}%</Typography>
              </Paper>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Reply Tone */}
      <Typography variant="subtitle1" mb={2}>
        <TuneIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Reply Tone & Style
      </Typography>

      <Grid container spacing={2} mb={3}>
        {TONE_OPTIONS.map(tone => (
          <Grid item xs={12} sm={6} md={3} key={tone.value}>
            <Card 
              sx={{ 
                p: 2, 
                cursor: 'pointer',
                height: '100%',
                border: '2px solid',
                borderColor: settings.reply_tone === tone.value ? '#14B8A6' : 'transparent',
                bgcolor: settings.reply_tone === tone.value ? alpha('#14B8A6', 0.05) : 'background.default',
                transition: 'all 0.2s ease',
                '&:hover': { borderColor: alpha('#14B8A6', 0.5) },
              }}
              onClick={() => setSettings(prev => ({ ...prev, reply_tone: tone.value as any }))}
            >
              <Box textAlign="center">
                <Typography variant="h4" mb={1}>{tone.emoji}</Typography>
                <Typography variant="subtitle2">{tone.label}</Typography>
                <Typography variant="caption" color="text.secondary">{tone.description}</Typography>
              </Box>
            </Card>
          </Grid>
        ))}
      </Grid>

      <FormGroup>
        <Grid container spacing={2} mb={3}>
          <Grid item xs={12} sm={6}>
            <Paper 
              sx={{ 
                p: 2, 
                cursor: 'pointer',
                border: '2px solid',
                borderColor: settings.use_emojis ? '#14B8A6' : 'transparent',
                bgcolor: settings.use_emojis ? alpha('#14B8A6', 0.05) : 'background.default',
              }}
              onClick={() => setSettings(prev => ({ ...prev, use_emojis: !prev.use_emojis }))}
            >
              <Box display="flex" alignItems="center" gap={1}>
                <Switch checked={settings.use_emojis} size="small" />
                <Box>
                  <Typography variant="body2">😀 Include Emojis</Typography>
                  <Typography variant="caption" color="text.secondary">Add relevant emojis to replies</Typography>
                </Box>
              </Box>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Paper 
              sx={{ 
                p: 2, 
                cursor: 'pointer',
                border: '2px solid',
                borderColor: settings.include_greeting ? '#14B8A6' : 'transparent',
                bgcolor: settings.include_greeting ? alpha('#14B8A6', 0.05) : 'background.default',
              }}
              onClick={() => setSettings(prev => ({ ...prev, include_greeting: !prev.include_greeting }))}
            >
              <Box display="flex" alignItems="center" gap={1}>
                <Switch checked={settings.include_greeting} size="small" />
                <Box>
                  <Typography variant="body2">👋 Include Greeting</Typography>
                  <Typography variant="caption" color="text.secondary">Start replies with a greeting</Typography>
                </Box>
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </FormGroup>

      <Divider sx={{ my: 3 }} />

      {/* Response Timing */}
      <Typography variant="subtitle1" mb={2}>
        <TimerIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Response Timing
      </Typography>

      <Stack spacing={2} mb={3}>
        {SPEED_OPTIONS.map(speed => (
          <Paper
            key={speed.value}
            sx={{
              p: 2,
              cursor: 'pointer',
              border: '2px solid',
              borderColor: settings.response_speed === speed.value ? '#14B8A6' : 'transparent',
              bgcolor: settings.response_speed === speed.value ? alpha('#14B8A6', 0.05) : 'background.default',
              transition: 'all 0.2s ease',
            }}
            onClick={() => setSettings(prev => ({ ...prev, response_speed: speed.value as any }))}
          >
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography variant="subtitle2">{speed.label}</Typography>
                <Typography variant="caption" color="text.secondary">{speed.description}</Typography>
              </Box>
              {settings.response_speed === speed.value && (
                <Chip label="Active" size="small" sx={{ bgcolor: '#14B8A6', color: 'white' }} />
              )}
            </Box>
          </Paper>
        ))}
      </Stack>

      {settings.response_speed === 'delayed' && (
        <Box mb={3}>
          <Typography variant="body2" gutterBottom>
            Delay: <strong>{settings.delay_seconds} seconds</strong>
          </Typography>
          <Slider
            value={settings.delay_seconds}
            onChange={(_, value) => setSettings(prev => ({ ...prev, delay_seconds: value as number }))}
            min={1}
            max={30}
            step={1}
            marks={[
              { value: 1, label: '1s' },
              { value: 10, label: '10s' },
              { value: 30, label: '30s' },
            ]}
            valueLabelDisplay="auto"
            sx={{ '& .MuiSlider-thumb': { bgcolor: '#14B8A6' }, '& .MuiSlider-track': { bgcolor: '#14B8A6' } }}
          />
        </Box>
      )}

      <Divider sx={{ my: 3 }} />

      {/* Context Settings */}
      <Typography variant="subtitle1" mb={2}>
        Context Awareness
      </Typography>

      <Box mb={3}>
        <Typography variant="body2" gutterBottom>
          Messages to Consider: <strong>{settings.context_messages}</strong>
        </Typography>
        <Typography variant="caption" color="text.secondary" display="block" mb={2}>
          Number of previous messages to analyze for context
        </Typography>
        <Slider
          value={settings.context_messages}
          onChange={(_, value) => setSettings(prev => ({ ...prev, context_messages: value as number }))}
          min={1}
          max={20}
          step={1}
          marks={[
            { value: 1, label: '1' },
            { value: 5, label: '5' },
            { value: 10, label: '10' },
            { value: 20, label: '20' },
          ]}
          valueLabelDisplay="auto"
          sx={{ '& .MuiSlider-thumb': { bgcolor: '#14B8A6' }, '& .MuiSlider-track': { bgcolor: '#14B8A6' } }}
        />
      </Box>

      <FormGroup>
        <Box sx={{ p: 2, borderRadius: 2, bgcolor: 'background.default', mb: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={settings.learn_from_history}
                onChange={(e) => setSettings(prev => ({ ...prev, learn_from_history: e.target.checked }))}
              />
            }
            label={
              <Box>
                <Typography>Learn From Your Replies</Typography>
                <Typography variant="caption" color="text.secondary">
                  AI adapts to your communication style over time
                </Typography>
              </Box>
            }
            sx={{ alignItems: 'flex-start', m: 0 }}
          />
        </Box>
      </FormGroup>

      <Divider sx={{ my: 3 }} />

      {/* Auto-Reply Settings */}
      <Typography variant="subtitle1" mb={2}>
        <AutoIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Auto-Reply (Beta)
      </Typography>

      <FormGroup>
        <Box sx={{ p: 2, borderRadius: 2, bgcolor: 'background.default', mb: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={settings.auto_reply_enabled}
                onChange={(e) => setSettings(prev => ({ ...prev, auto_reply_enabled: e.target.checked }))}
              />
            }
            label={
              <Box>
                <Typography>Enable Auto-Reply</Typography>
                <Typography variant="caption" color="text.secondary">
                  Automatically send AI-generated replies for specific triggers
                </Typography>
              </Box>
            }
            sx={{ alignItems: 'flex-start', m: 0 }}
          />
        </Box>
      </FormGroup>

      {settings.auto_reply_enabled && (
        <Box mb={3}>
          <Typography variant="body2" mb={1}>Trigger Keywords</Typography>
          <Box display="flex" gap={1} flexWrap="wrap" mb={2}>
            {settings.auto_reply_triggers.map(trigger => (
              <Chip
                key={trigger}
                label={trigger}
                onDelete={() => handleRemoveTrigger(trigger)}
                sx={{ bgcolor: alpha('#14B8A6', 0.1) }}
              />
            ))}
          </Box>
          <Box display="flex" gap={1}>
            <TextField
              size="small"
              placeholder="Add trigger keyword..."
              value={newTrigger}
              onChange={(e) => setNewTrigger(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddTrigger()}
              sx={{ flex: 1 }}
            />
            <Button 
              variant="outlined" 
              onClick={handleAddTrigger}
              startIcon={<AddIcon />}
              sx={{ borderColor: '#14B8A6', color: '#14B8A6' }}
            >
              Add
            </Button>
          </Box>
        </Box>
      )}

      {/* Signature */}
      <FormGroup>
        <Box sx={{ p: 2, borderRadius: 2, bgcolor: 'background.default', mb: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={settings.include_signature}
                onChange={(e) => setSettings(prev => ({ ...prev, include_signature: e.target.checked }))}
              />
            }
            label={
              <Box>
                <Typography>Include Signature</Typography>
                <Typography variant="caption" color="text.secondary">
                  Add a custom signature at the end of replies
                </Typography>
              </Box>
            }
            sx={{ alignItems: 'flex-start', m: 0 }}
          />
        </Box>
      </FormGroup>

      {settings.include_signature && (
        <TextField
          fullWidth
          multiline
          rows={2}
          label="Signature Text"
          value={settings.signature_text}
          onChange={(e) => setSettings(prev => ({ ...prev, signature_text: e.target.value }))}
          placeholder="Best regards, Your Name"
          sx={{ mb: 3 }}
        />
      )}

      {/* Save Button */}
      <Box mt={4} display="flex" justifyContent="flex-end">
        <Button
          variant="contained"
          startIcon={isSaving ? <CircularProgress size={20} color="inherit" /> : <SaveIcon />}
          onClick={handleSave}
          disabled={isSaving}
          size="large"
          sx={{ bgcolor: '#14B8A6', '&:hover': { bgcolor: '#0D9488' } }}
        >
          {isSaving ? 'Saving...' : 'Save Settings'}
        </Button>
      </Box>
    </Box>
  );
};

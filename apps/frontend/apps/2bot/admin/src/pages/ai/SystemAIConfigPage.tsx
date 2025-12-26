/**
 * System AI Configuration Page
 * 
 * Configure System AI settings:
 * - Enable/disable AI
 * - Auto-scale settings
 * - Approval levels
 * - Resource limits
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid2 as Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CardHeader,
  Chip,
  alpha,
  useTheme,
  Divider,
  Button,
  TextField,
  FormControl,
  FormControlLabel,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  Slider,
  Skeleton,
  Alert,
  Snackbar,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Tooltip,
  IconButton,
} from '@mui/material';
import {
  Save as SaveIcon,
  Refresh as RefreshIcon,
  SmartToy as AIIcon,
  Security as SecurityIcon,
  Speed as PerformanceIcon,
  Memory as ResourceIcon,
  Notifications as AlertIcon,
  Info as InfoIcon,
} from '@mui/icons-material';

interface SystemAIConfig {
  // Core settings
  ai_enabled: boolean;
  auto_scale_enabled: boolean;
  dry_run_mode: boolean;
  
  // Approval settings
  approval_level: 'auto' | 'review' | 'approval';
  require_approval_for_scale: boolean;
  require_approval_for_config: boolean;
  require_approval_for_security: boolean;
  
  // Resource limits
  max_workers: number;
  memory_limit_mb: number;
  cpu_threshold_percent: number;
  memory_threshold_percent: number;
  
  // Scaling settings
  scale_up_threshold: number;
  scale_down_threshold: number;
  scale_cooldown_minutes: number;
  min_instances: number;
  max_instances: number;
  
  // Alert settings
  alert_on_scale: boolean;
  alert_on_error: boolean;
  alert_on_threshold: boolean;
  alert_channels: string[];
}

const defaultConfig: SystemAIConfig = {
  ai_enabled: true,
  auto_scale_enabled: true,
  dry_run_mode: false,
  
  approval_level: 'review',
  require_approval_for_scale: true,
  require_approval_for_config: true,
  require_approval_for_security: true,
  
  max_workers: 10,
  memory_limit_mb: 4096,
  cpu_threshold_percent: 80,
  memory_threshold_percent: 85,
  
  scale_up_threshold: 80,
  scale_down_threshold: 30,
  scale_cooldown_minutes: 5,
  min_instances: 1,
  max_instances: 10,
  
  alert_on_scale: true,
  alert_on_error: true,
  alert_on_threshold: true,
  alert_channels: ['telegram', 'email'],
};

const SystemAIConfigPage: React.FC = () => {
  const theme = useTheme();
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [config, setConfig] = useState<SystemAIConfig>(defaultConfig);
  const [originalConfig, setOriginalConfig] = useState<SystemAIConfig>(defaultConfig);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success',
  });

  const hasChanges = JSON.stringify(config) !== JSON.stringify(originalConfig);

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        setLoading(true);
        // TODO: Replace with actual API call
        await new Promise(resolve => setTimeout(resolve, 500));
        setConfig(defaultConfig);
        setOriginalConfig(defaultConfig);
      } catch (err) {
        setSnackbar({ open: true, message: 'Failed to load configuration', severity: 'error' });
      } finally {
        setLoading(false);
      }
    };
    
    fetchConfig();
  }, []);

  const handleSave = async () => {
    try {
      setSaving(true);
      // TODO: Replace with actual API call
      await new Promise(resolve => setTimeout(resolve, 500));
      setOriginalConfig(config);
      setSnackbar({ open: true, message: 'Configuration saved successfully', severity: 'success' });
    } catch (err) {
      setSnackbar({ open: true, message: 'Failed to save configuration', severity: 'error' });
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    setConfig(originalConfig);
  };

  const updateConfig = <K extends keyof SystemAIConfig>(key: K, value: SystemAIConfig[K]) => {
    setConfig(prev => ({ ...prev, [key]: value }));
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Skeleton variant="text" width={300} height={40} />
        {[1, 2, 3].map((i) => (
          <Skeleton key={i} variant="rounded" height={200} sx={{ mt: 3 }} />
        ))}
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box>
          <Typography variant="h4" component="h1" fontWeight={700} gutterBottom>
            System AI Configuration
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Configure AI behavior, limits, and automation settings
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          {hasChanges && (
            <Button variant="outlined" onClick={handleReset} disabled={saving}>
              Reset
            </Button>
          )}
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={handleSave}
            disabled={!hasChanges || saving}
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </Button>
        </Box>
      </Box>

      {hasChanges && (
        <Alert severity="info" sx={{ mb: 3 }}>
          You have unsaved changes. Don't forget to save before leaving.
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Core Settings */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ height: '100%', border: `1px solid ${theme.palette.divider}` }}>
            <CardHeader
              avatar={<AIIcon color="primary" />}
              title="Core Settings"
              subheader="Basic AI system configuration"
            />
            <Divider />
            <CardContent>
              <List disablePadding>
                <ListItem sx={{ px: 0 }}>
                  <ListItemText
                    primary="Enable System AI"
                    secondary="Turn on/off all AI automation features"
                  />
                  <ListItemSecondaryAction>
                    <Switch
                      checked={config.ai_enabled}
                      onChange={(e) => updateConfig('ai_enabled', e.target.checked)}
                    />
                  </ListItemSecondaryAction>
                </ListItem>
                
                <Divider sx={{ my: 1 }} />
                
                <ListItem sx={{ px: 0 }}>
                  <ListItemText
                    primary="Auto-scale Workers"
                    secondary="Automatically scale workers based on load"
                  />
                  <ListItemSecondaryAction>
                    <Switch
                      checked={config.auto_scale_enabled}
                      onChange={(e) => updateConfig('auto_scale_enabled', e.target.checked)}
                      disabled={!config.ai_enabled}
                    />
                  </ListItemSecondaryAction>
                </ListItem>
                
                <Divider sx={{ my: 1 }} />
                
                <ListItem sx={{ px: 0 }}>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        Dry Run Mode
                        <Tooltip title="Simulate actions without executing them">
                          <InfoIcon fontSize="small" color="action" />
                        </Tooltip>
                      </Box>
                    }
                    secondary="Test AI decisions without making changes"
                  />
                  <ListItemSecondaryAction>
                    <Switch
                      checked={config.dry_run_mode}
                      onChange={(e) => updateConfig('dry_run_mode', e.target.checked)}
                      disabled={!config.ai_enabled}
                    />
                  </ListItemSecondaryAction>
                </ListItem>
                
                <Divider sx={{ my: 1 }} />
                
                <ListItem sx={{ px: 0 }}>
                  <FormControl fullWidth>
                    <InputLabel>Approval Level</InputLabel>
                    <Select
                      value={config.approval_level}
                      label="Approval Level"
                      onChange={(e) => updateConfig('approval_level', e.target.value as SystemAIConfig['approval_level'])}
                      disabled={!config.ai_enabled}
                    >
                      <MenuItem value="auto">Auto (no approval needed)</MenuItem>
                      <MenuItem value="review">Review (notify admins)</MenuItem>
                      <MenuItem value="approval">Approval (require manual approval)</MenuItem>
                    </Select>
                  </FormControl>
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Security Settings */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ height: '100%', border: `1px solid ${theme.palette.divider}` }}>
            <CardHeader
              avatar={<SecurityIcon color="primary" />}
              title="Approval Requirements"
              subheader="When to require manual approval"
            />
            <Divider />
            <CardContent>
              <List disablePadding>
                <ListItem sx={{ px: 0 }}>
                  <ListItemText
                    primary="Scaling Decisions"
                    secondary="Require approval for scaling workers up/down"
                  />
                  <ListItemSecondaryAction>
                    <Switch
                      checked={config.require_approval_for_scale}
                      onChange={(e) => updateConfig('require_approval_for_scale', e.target.checked)}
                      disabled={!config.ai_enabled || config.approval_level === 'auto'}
                    />
                  </ListItemSecondaryAction>
                </ListItem>
                
                <Divider sx={{ my: 1 }} />
                
                <ListItem sx={{ px: 0 }}>
                  <ListItemText
                    primary="Configuration Changes"
                    secondary="Require approval for config modifications"
                  />
                  <ListItemSecondaryAction>
                    <Switch
                      checked={config.require_approval_for_config}
                      onChange={(e) => updateConfig('require_approval_for_config', e.target.checked)}
                      disabled={!config.ai_enabled || config.approval_level === 'auto'}
                    />
                  </ListItemSecondaryAction>
                </ListItem>
                
                <Divider sx={{ my: 1 }} />
                
                <ListItem sx={{ px: 0 }}>
                  <ListItemText
                    primary="Security Actions"
                    secondary="Require approval for security-related actions"
                  />
                  <ListItemSecondaryAction>
                    <Switch
                      checked={config.require_approval_for_security}
                      onChange={(e) => updateConfig('require_approval_for_security', e.target.checked)}
                      disabled={!config.ai_enabled || config.approval_level === 'auto'}
                    />
                  </ListItemSecondaryAction>
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Resource Limits */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ border: `1px solid ${theme.palette.divider}` }}>
            <CardHeader
              avatar={<ResourceIcon color="primary" />}
              title="Resource Limits"
              subheader="Maximum resource allocation"
            />
            <Divider />
            <CardContent>
              <Grid container spacing={3}>
                <Grid size={{ xs: 6 }}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Max Workers"
                    value={config.max_workers}
                    onChange={(e) => updateConfig('max_workers', Number(e.target.value))}
                    disabled={!config.ai_enabled}
                    inputProps={{ min: 1, max: 100 }}
                  />
                </Grid>
                <Grid size={{ xs: 6 }}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Memory Limit (MB)"
                    value={config.memory_limit_mb}
                    onChange={(e) => updateConfig('memory_limit_mb', Number(e.target.value))}
                    disabled={!config.ai_enabled}
                    inputProps={{ min: 512, max: 32768 }}
                  />
                </Grid>
                <Grid size={{ xs: 12 }}>
                  <Typography variant="body2" gutterBottom>
                    CPU Threshold: {config.cpu_threshold_percent}%
                  </Typography>
                  <Slider
                    value={config.cpu_threshold_percent}
                    onChange={(_, value) => updateConfig('cpu_threshold_percent', value as number)}
                    min={50}
                    max={95}
                    marks={[
                      { value: 50, label: '50%' },
                      { value: 80, label: '80%' },
                      { value: 95, label: '95%' },
                    ]}
                    disabled={!config.ai_enabled}
                  />
                </Grid>
                <Grid size={{ xs: 12 }}>
                  <Typography variant="body2" gutterBottom>
                    Memory Threshold: {config.memory_threshold_percent}%
                  </Typography>
                  <Slider
                    value={config.memory_threshold_percent}
                    onChange={(_, value) => updateConfig('memory_threshold_percent', value as number)}
                    min={50}
                    max={95}
                    marks={[
                      { value: 50, label: '50%' },
                      { value: 85, label: '85%' },
                      { value: 95, label: '95%' },
                    ]}
                    disabled={!config.ai_enabled}
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Scaling Settings */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ border: `1px solid ${theme.palette.divider}` }}>
            <CardHeader
              avatar={<PerformanceIcon color="primary" />}
              title="Scaling Settings"
              subheader="Auto-scaling behavior configuration"
            />
            <Divider />
            <CardContent>
              <Grid container spacing={3}>
                <Grid size={{ xs: 12 }}>
                  <Typography variant="body2" gutterBottom>
                    Scale Up Threshold: {config.scale_up_threshold}%
                  </Typography>
                  <Slider
                    value={config.scale_up_threshold}
                    onChange={(_, value) => updateConfig('scale_up_threshold', value as number)}
                    min={50}
                    max={95}
                    disabled={!config.ai_enabled || !config.auto_scale_enabled}
                  />
                </Grid>
                <Grid size={{ xs: 12 }}>
                  <Typography variant="body2" gutterBottom>
                    Scale Down Threshold: {config.scale_down_threshold}%
                  </Typography>
                  <Slider
                    value={config.scale_down_threshold}
                    onChange={(_, value) => updateConfig('scale_down_threshold', value as number)}
                    min={10}
                    max={50}
                    disabled={!config.ai_enabled || !config.auto_scale_enabled}
                  />
                </Grid>
                <Grid size={{ xs: 6 }}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Min Instances"
                    value={config.min_instances}
                    onChange={(e) => updateConfig('min_instances', Number(e.target.value))}
                    disabled={!config.ai_enabled || !config.auto_scale_enabled}
                    inputProps={{ min: 1, max: 10 }}
                  />
                </Grid>
                <Grid size={{ xs: 6 }}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Max Instances"
                    value={config.max_instances}
                    onChange={(e) => updateConfig('max_instances', Number(e.target.value))}
                    disabled={!config.ai_enabled || !config.auto_scale_enabled}
                    inputProps={{ min: 1, max: 50 }}
                  />
                </Grid>
                <Grid size={{ xs: 12 }}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Cooldown Period (minutes)"
                    value={config.scale_cooldown_minutes}
                    onChange={(e) => updateConfig('scale_cooldown_minutes', Number(e.target.value))}
                    disabled={!config.ai_enabled || !config.auto_scale_enabled}
                    inputProps={{ min: 1, max: 60 }}
                    helperText="Wait time between scaling actions"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Alert Settings */}
        <Grid size={{ xs: 12 }}>
          <Card sx={{ border: `1px solid ${theme.palette.divider}` }}>
            <CardHeader
              avatar={<AlertIcon color="primary" />}
              title="Alert Settings"
              subheader="Configure when and how to receive notifications"
            />
            <Divider />
            <CardContent>
              <Grid container spacing={3}>
                <Grid size={{ xs: 12, sm: 4 }}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={config.alert_on_scale}
                        onChange={(e) => updateConfig('alert_on_scale', e.target.checked)}
                        disabled={!config.ai_enabled}
                      />
                    }
                    label="Alert on Scaling Events"
                  />
                </Grid>
                <Grid size={{ xs: 12, sm: 4 }}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={config.alert_on_error}
                        onChange={(e) => updateConfig('alert_on_error', e.target.checked)}
                        disabled={!config.ai_enabled}
                      />
                    }
                    label="Alert on Errors"
                  />
                </Grid>
                <Grid size={{ xs: 12, sm: 4 }}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={config.alert_on_threshold}
                        onChange={(e) => updateConfig('alert_on_threshold', e.target.checked)}
                        disabled={!config.ai_enabled}
                      />
                    }
                    label="Alert on Threshold Breach"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
      >
        <Alert
          onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default SystemAIConfigPage;

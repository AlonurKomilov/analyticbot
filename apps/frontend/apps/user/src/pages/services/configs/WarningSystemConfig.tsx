/**
 * Warning System Configuration
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
  TextField,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Warning as WarningIcon,
  Save as SaveIcon,
  Gavel as BanIcon,
  RemoveCircle as MuteIcon,
  Delete as DeleteIcon,
  History as HistoryIcon,
  Person as PersonIcon,
  Clear as ClearIcon,
} from '@mui/icons-material';
import { apiClient } from '@/api/client';
import { format } from 'date-fns';

interface WarningSettings {
  warning_system_enabled: boolean;
  max_warnings: number;
  warning_expiry_days: number;
  action_on_max_warnings: string;
  mute_duration_minutes: number;
  ban_duration_days: number;
}

interface WarningRecord {
  id: number;
  user_id: number;
  user_name: string;
  reason: string;
  issued_by_name: string;
  warning_count: number;
  created_at: string;
}

interface Props {
  chatId: number;
}

export const WarningSystemConfig: React.FC<Props> = ({ chatId }) => {
  const [settings, setSettings] = useState<WarningSettings>({
    warning_system_enabled: false,
    max_warnings: 3,
    warning_expiry_days: 30,
    action_on_max_warnings: 'ban',
    mute_duration_minutes: 60,
    ban_duration_days: 7,
  });
  const [warnings, setWarnings] = useState<WarningRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isLoadingWarnings, setIsLoadingWarnings] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        const settingsResponse = await apiClient.get(`/bot/moderation/${chatId}/settings`) as WarningSettings;
        if (settingsResponse) {
          setSettings(prev => ({
            ...prev,
            warning_system_enabled: settingsResponse.warning_system_enabled ?? false,
            max_warnings: settingsResponse.max_warnings ?? 3,
            warning_expiry_days: settingsResponse.warning_expiry_days ?? 30,
            action_on_max_warnings: settingsResponse.action_on_max_warnings ?? 'ban',
            mute_duration_minutes: settingsResponse.mute_duration_minutes ?? 60,
            ban_duration_days: settingsResponse.ban_duration_days ?? 7,
          }));
        }

        // Fetch recent warnings
        if (settingsResponse?.warning_system_enabled) {
          await fetchWarnings();
        }
      } catch (err: any) {
        setError(err.message || 'Failed to load settings');
      } finally {
        setIsLoading(false);
      }
    };

    if (chatId) {
      fetchData();
    }
  }, [chatId]);

  const fetchWarnings = async () => {
    setIsLoadingWarnings(true);
    try {
      const response = await apiClient.get(`/bot/moderation/${chatId}/warnings`) as { warnings?: WarningRecord[] };
      if (response?.warnings) {
        setWarnings(response.warnings);
      }
    } catch {
      setWarnings([]);
    } finally {
      setIsLoadingWarnings(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);
    setSuccess(false);
    try {
      await apiClient.patch(`/bot/moderation/${chatId}/settings`, settings);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
      
      if (settings.warning_system_enabled) {
        await fetchWarnings();
      }
    } catch (err: any) {
      setError(err.message || 'Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  const handleClearWarning = async (warningId: number) => {
    try {
      await apiClient.delete(`/bot/moderation/${chatId}/warnings/${warningId}`);
      setWarnings(prev => prev.filter(w => w.id !== warningId));
    } catch (err: any) {
      setError(err.message || 'Failed to clear warning');
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

      {/* Main Toggle */}
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
                <WarningIcon sx={{ color: '#f59e0b', fontSize: 28 }} />
              </Box>
              <Box>
                <Typography variant="h6">Warning System</Typography>
                <Typography variant="body2" color="text.secondary">
                  Issue warnings to members who violate rules with automatic escalation
                </Typography>
              </Box>
            </Box>
            <Switch
              checked={settings.warning_system_enabled}
              onChange={(e) => setSettings(prev => ({ ...prev, warning_system_enabled: e.target.checked }))}
              color="warning"
              size="medium"
            />
          </Box>
        </CardContent>
      </Card>

      {settings.warning_system_enabled && (
        <>
          {/* Warning Threshold */}
          <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
            <Typography variant="subtitle1" mb={3}>Warning Rules</Typography>
            
            <Box mb={4}>
              <Typography variant="body2" mb={1}>
                Maximum warnings before action: <strong>{settings.max_warnings}</strong>
              </Typography>
              <Slider
                value={settings.max_warnings}
                onChange={(_, value) => setSettings(prev => ({ ...prev, max_warnings: value as number }))}
                min={1}
                max={10}
                step={1}
                marks={[
                  { value: 1, label: '1' },
                  { value: 3, label: '3' },
                  { value: 5, label: '5' },
                  { value: 10, label: '10' },
                ]}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box mb={4}>
              <Typography variant="body2" mb={1}>
                Warnings expire after: <strong>{settings.warning_expiry_days} days</strong>
              </Typography>
              <Slider
                value={settings.warning_expiry_days}
                onChange={(_, value) => setSettings(prev => ({ ...prev, warning_expiry_days: value as number }))}
                min={1}
                max={90}
                step={1}
                marks={[
                  { value: 7, label: '7d' },
                  { value: 30, label: '30d' },
                  { value: 60, label: '60d' },
                  { value: 90, label: '90d' },
                ]}
                valueLabelDisplay="auto"
              />
              <Typography variant="caption" color="text.secondary">
                Warnings older than this will no longer count towards the limit
              </Typography>
            </Box>
          </Paper>

          {/* Action on Max Warnings */}
          <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
            <Typography variant="subtitle1" mb={2}>Action After Max Warnings</Typography>
            
            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel>Action</InputLabel>
              <Select
                value={settings.action_on_max_warnings}
                label="Action"
                onChange={(e) => setSettings(prev => ({ ...prev, action_on_max_warnings: e.target.value }))}
              >
                <MenuItem value="mute">
                  <Box display="flex" alignItems="center" gap={1}>
                    <MuteIcon color="info" />
                    <Box>
                      <Typography>Mute User</Typography>
                      <Typography variant="caption" color="text.secondary">
                        Temporarily restrict user from sending messages
                      </Typography>
                    </Box>
                  </Box>
                </MenuItem>
                <MenuItem value="kick">
                  <Box display="flex" alignItems="center" gap={1}>
                    <DeleteIcon color="warning" />
                    <Box>
                      <Typography>Kick User</Typography>
                      <Typography variant="caption" color="text.secondary">
                        Remove user from chat (they can rejoin)
                      </Typography>
                    </Box>
                  </Box>
                </MenuItem>
                <MenuItem value="ban">
                  <Box display="flex" alignItems="center" gap={1}>
                    <BanIcon color="error" />
                    <Box>
                      <Typography>Ban User</Typography>
                      <Typography variant="caption" color="text.secondary">
                        Permanently remove and block user
                      </Typography>
                    </Box>
                  </Box>
                </MenuItem>
                <MenuItem value="temp_ban">
                  <Box display="flex" alignItems="center" gap={1}>
                    <BanIcon color="warning" />
                    <Box>
                      <Typography>Temporary Ban</Typography>
                      <Typography variant="caption" color="text.secondary">
                        Ban user for a specified duration
                      </Typography>
                    </Box>
                  </Box>
                </MenuItem>
              </Select>
            </FormControl>

            {settings.action_on_max_warnings === 'mute' && (
              <TextField
                type="number"
                label="Mute Duration (minutes)"
                value={settings.mute_duration_minutes}
                onChange={(e) => setSettings(prev => ({ ...prev, mute_duration_minutes: parseInt(e.target.value) || 60 }))}
                fullWidth
                InputProps={{ inputProps: { min: 1 } }}
                helperText="How long to mute the user"
              />
            )}

            {settings.action_on_max_warnings === 'temp_ban' && (
              <TextField
                type="number"
                label="Ban Duration (days)"
                value={settings.ban_duration_days}
                onChange={(e) => setSettings(prev => ({ ...prev, ban_duration_days: parseInt(e.target.value) || 7 }))}
                fullWidth
                InputProps={{ inputProps: { min: 1 } }}
                helperText="How long to ban the user"
              />
            )}
          </Paper>

          <Divider sx={{ my: 3 }} />

          {/* Recent Warnings */}
          <Box mb={4}>
            <Typography variant="h6" mb={2}>
              <HistoryIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Recent Warnings
            </Typography>

            {isLoadingWarnings ? (
              <Box display="flex" justifyContent="center" py={4}>
                <CircularProgress size={24} />
              </Box>
            ) : warnings.length === 0 ? (
              <Alert severity="info">
                No warnings issued yet.
              </Alert>
            ) : (
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>User</TableCell>
                      <TableCell>Reason</TableCell>
                      <TableCell>Issued By</TableCell>
                      <TableCell align="center">Count</TableCell>
                      <TableCell>Date</TableCell>
                      <TableCell align="right">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {warnings.slice(0, 20).map((warning) => (
                      <TableRow key={warning.id}>
                        <TableCell>
                          <Box display="flex" alignItems="center" gap={1}>
                            <PersonIcon fontSize="small" color="action" />
                            <Typography variant="body2">{warning.user_name}</Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" color="text.secondary">
                            {warning.reason || 'No reason specified'}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">{warning.issued_by_name}</Typography>
                        </TableCell>
                        <TableCell align="center">
                          <Chip
                            label={`${warning.warning_count}/${settings.max_warnings}`}
                            size="small"
                            color={warning.warning_count >= settings.max_warnings ? 'error' : 'warning'}
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="caption">
                            {format(new Date(warning.created_at), 'MMM d, HH:mm')}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Tooltip title="Clear Warning">
                            <IconButton
                              size="small"
                              onClick={() => handleClearWarning(warning.id)}
                              color="error"
                            >
                              <ClearIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </Box>
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

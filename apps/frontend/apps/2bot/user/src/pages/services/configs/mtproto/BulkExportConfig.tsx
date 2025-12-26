/**
 * MTProto Bulk Export Service Configuration
 * 
 * Service: mtproto_bulk_export
 * Price: 200 credits/month
 * 
 * Allows users to configure:
 * - Export format preferences (JSON, CSV, HTML)
 * - Data inclusion options (messages, media, members)
 * - Date range filtering
 * - Compression and delivery options
 */

import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Switch,
  FormControlLabel,
  FormGroup,
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
  Paper,
  Checkbox,
} from '@mui/material';
import {
  ImportExport as ExportIcon,
  Save as SaveIcon,
  Description as FormatIcon,
  DateRange as DateIcon,
  CloudDownload as DownloadIcon,
  Compress as CompressIcon,
  Email as EmailIcon,
  Storage as StorageIcon,
  Schedule as ScheduleIcon,
  CheckCircle as CheckIcon,
} from '@mui/icons-material';
import { apiClient } from '@/api/client';

interface BulkExportSettings {
  enabled: boolean;
  default_format: 'json' | 'csv' | 'html';
  include_messages: boolean;
  include_media_files: boolean;
  include_members: boolean;
  include_statistics: boolean;
  include_reactions: boolean;
  compress_output: boolean;
  compression_format: 'zip' | 'tar.gz';
  date_range_days: number | null;
  delivery_method: 'download' | 'email' | 'cloud';
  email_notification: boolean;
  chunk_size_mb: number;
  preserve_threads: boolean;
}

interface ExportHistory {
  id: string;
  created_at: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  format: string;
  channels_count: number;
  messages_count: number;
  file_size_mb: number | null;
  download_url: string | null;
}

const FORMAT_OPTIONS = [
  { 
    value: 'json', 
    label: 'JSON', 
    description: 'Full structured data, best for developers',
    icon: '{ }',
  },
  { 
    value: 'csv', 
    label: 'CSV', 
    description: 'Spreadsheet-compatible, good for analysis',
    icon: '📊',
  },
  { 
    value: 'html', 
    label: 'HTML', 
    description: 'Human-readable, viewable in browser',
    icon: '🌐',
  },
];

const DATE_RANGE_OPTIONS = [
  { value: null, label: 'All time' },
  { value: 7, label: 'Last 7 days' },
  { value: 30, label: 'Last 30 days' },
  { value: 90, label: 'Last 90 days' },
  { value: 180, label: 'Last 6 months' },
  { value: 365, label: 'Last year' },
];

const DELIVERY_OPTIONS = [
  { value: 'download', label: 'Direct Download', description: 'Download immediately when ready' },
  { value: 'email', label: 'Email Link', description: 'Receive download link via email' },
  { value: 'cloud', label: 'Cloud Storage', description: 'Export to connected cloud storage' },
];

export const BulkExportConfig: React.FC = () => {
  const [settings, setSettings] = useState<BulkExportSettings>({
    enabled: true,
    default_format: 'json',
    include_messages: true,
    include_media_files: false,
    include_members: true,
    include_statistics: true,
    include_reactions: true,
    compress_output: true,
    compression_format: 'zip',
    date_range_days: 30,
    delivery_method: 'download',
    email_notification: true,
    chunk_size_mb: 100,
    preserve_threads: true,
  });

  const [exportHistory, setExportHistory] = useState<ExportHistory[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        // Load saved settings
        const savedSettings = localStorage.getItem('mtproto_export_settings');
        if (savedSettings) {
          setSettings(prev => ({ ...prev, ...JSON.parse(savedSettings) }));
        }

        // Try to fetch export history
        try {
          const response = await apiClient.get('/user-mtproto/exports/history') as Record<string, any>;
          setExportHistory(response.exports || []);
        } catch {
          // History not available
          setExportHistory([]);
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
      localStorage.setItem('mtproto_export_settings', JSON.stringify(settings));
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err: any) {
      setError(err.message || 'Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  const handleStartExport = async () => {
    setIsExporting(true);
    setError(null);
    try {
      // This would trigger an export job
      await apiClient.post('/user-mtproto/exports/start', {
        format: settings.default_format,
        include_messages: settings.include_messages,
        include_media: settings.include_media_files,
        include_members: settings.include_members,
        date_range_days: settings.date_range_days,
        compress: settings.compress_output,
      });
      
      // Refresh history
      const response = await apiClient.get('/user-mtproto/exports/history') as Record<string, any>;
      setExportHistory(response.exports || []);
      
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err: any) {
      setError(err.message || 'Failed to start export');
    } finally {
      setIsExporting(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'processing': return 'info';
      case 'pending': return 'warning';
      case 'failed': return 'error';
      default: return 'default';
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
      {success && <Alert severity="success" sx={{ mb: 3 }}>Operation completed successfully!</Alert>}

      {/* Service Header */}
      <Card sx={{ mb: 3, bgcolor: alpha('#9C27B0', 0.05), border: '1px solid', borderColor: alpha('#9C27B0', 0.2) }}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box display="flex" alignItems="center" gap={2}>
              <ExportIcon sx={{ color: '#9C27B0', fontSize: 40 }} />
              <Box>
                <Typography variant="h6">MTProto Bulk Export</Typography>
                <Typography variant="body2" color="text.secondary">
                  Export all your channel data in bulk with customizable formats
                </Typography>
              </Box>
            </Box>
            <Chip 
              label="Premium Service" 
              sx={{ bgcolor: alpha('#9C27B0', 0.1), color: '#9C27B0' }}
              size="small"
            />
          </Box>
        </CardContent>
      </Card>

      {/* Quick Export Button */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box>
              <Typography variant="subtitle1">Quick Export</Typography>
              <Typography variant="body2" color="text.secondary">
                Start a new export with current settings
              </Typography>
            </Box>
            <Button
              variant="contained"
              startIcon={isExporting ? <CircularProgress size={20} color="inherit" /> : <DownloadIcon />}
              onClick={handleStartExport}
              disabled={isExporting}
              sx={{ bgcolor: '#9C27B0', '&:hover': { bgcolor: '#7B1FA2' } }}
            >
              {isExporting ? 'Starting...' : 'Start Export'}
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Export History */}
      {exportHistory.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="subtitle1" mb={2}>
              <ScheduleIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Recent Exports
            </Typography>
            
            <Stack spacing={1}>
              {exportHistory.slice(0, 5).map(exp => (
                <Paper key={exp.id} sx={{ p: 2, bgcolor: 'background.default' }}>
                  <Box display="flex" alignItems="center" justifyContent="space-between">
                    <Box>
                      <Typography variant="body2">
                        {new Date(exp.created_at).toLocaleString()} • {exp.format.toUpperCase()}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {exp.channels_count} channels • {exp.messages_count?.toLocaleString()} messages
                        {exp.file_size_mb && ` • ${exp.file_size_mb}MB`}
                      </Typography>
                    </Box>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Chip 
                        label={exp.status} 
                        size="small" 
                        color={getStatusColor(exp.status) as any}
                      />
                      {exp.status === 'completed' && exp.download_url && (
                        <Button 
                          size="small" 
                          startIcon={<DownloadIcon />}
                          href={exp.download_url}
                        >
                          Download
                        </Button>
                      )}
                    </Box>
                  </Box>
                </Paper>
              ))}
            </Stack>
          </CardContent>
        </Card>
      )}

      {/* Export Format */}
      <Typography variant="subtitle1" mb={2}>
        <FormatIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Export Format
      </Typography>

      <Grid container spacing={2} mb={3}>
        {FORMAT_OPTIONS.map(format => (
          <Grid item xs={12} sm={4} key={format.value}>
            <Card 
              sx={{ 
                p: 2, 
                cursor: 'pointer',
                border: '2px solid',
                borderColor: settings.default_format === format.value ? 'secondary.main' : 'transparent',
                bgcolor: settings.default_format === format.value ? alpha('#9C27B0', 0.05) : 'background.default',
                height: '100%',
                transition: 'all 0.2s ease',
                '&:hover': {
                  borderColor: alpha('#9C27B0', 0.5),
                },
              }}
              onClick={() => setSettings(prev => ({ ...prev, default_format: format.value as any }))}
            >
              <Box textAlign="center">
                <Typography variant="h4" mb={1}>{format.icon}</Typography>
                <Typography variant="subtitle1">{format.label}</Typography>
                <Typography variant="caption" color="text.secondary">
                  {format.description}
                </Typography>
              </Box>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Divider sx={{ my: 3 }} />

      {/* Data Inclusion */}
      <Typography variant="subtitle1" mb={2}>
        <StorageIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Data to Include
      </Typography>

      <Grid container spacing={2} mb={3}>
        {[
          { key: 'include_messages', label: 'Messages', description: 'All channel messages' },
          { key: 'include_media_files', label: 'Media Files', description: 'Photos, videos, documents' },
          { key: 'include_members', label: 'Member List', description: 'Channel participants' },
          { key: 'include_statistics', label: 'Statistics', description: 'View counts, forwards' },
          { key: 'include_reactions', label: 'Reactions', description: 'Emoji reactions data' },
        ].map(item => (
          <Grid item xs={12} sm={6} md={4} key={item.key}>
            <Paper 
              sx={{ 
                p: 2, 
                cursor: 'pointer',
                border: '2px solid',
                borderColor: settings[item.key as keyof typeof settings] ? 'secondary.main' : 'transparent',
                bgcolor: settings[item.key as keyof typeof settings] ? alpha('#9C27B0', 0.05) : 'background.default',
              }}
              onClick={() => setSettings(prev => ({ 
                ...prev, 
                [item.key]: !prev[item.key as keyof typeof settings] 
              }))}
            >
              <Box display="flex" alignItems="center" gap={2}>
                <Checkbox 
                  checked={settings[item.key as keyof typeof settings] as boolean}
                  sx={{ p: 0 }}
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

      {/* Date Range */}
      <Typography variant="subtitle1" mb={2}>
        <DateIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Date Range
      </Typography>

      <FormControl fullWidth sx={{ mb: 3 }}>
        <InputLabel>Export Date Range</InputLabel>
        <Select
          value={settings.date_range_days ?? 'null'}
          label="Export Date Range"
          onChange={(e) => setSettings(prev => ({ 
            ...prev, 
            date_range_days: e.target.value === 'null' ? null : e.target.value as number 
          }))}
        >
          {DATE_RANGE_OPTIONS.map(option => (
            <MenuItem key={option.value ?? 'null'} value={option.value ?? 'null'}>
              {option.label}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <Divider sx={{ my: 3 }} />

      {/* Compression Settings */}
      <Typography variant="subtitle1" mb={2}>
        <CompressIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Output Settings
      </Typography>

      <FormGroup>
        <Box sx={{ p: 2, borderRadius: 2, bgcolor: 'background.default', mb: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={settings.compress_output}
                onChange={(e) => setSettings(prev => ({ ...prev, compress_output: e.target.checked }))}
              />
            }
            label={
              <Box>
                <Typography>Compress Output</Typography>
                <Typography variant="caption" color="text.secondary">
                  Create a compressed archive of the export
                </Typography>
              </Box>
            }
            sx={{ alignItems: 'flex-start', m: 0 }}
          />
        </Box>

        {settings.compress_output && (
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Compression Format</InputLabel>
            <Select
              value={settings.compression_format}
              label="Compression Format"
              onChange={(e) => setSettings(prev => ({ ...prev, compression_format: e.target.value as any }))}
            >
              <MenuItem value="zip">ZIP (widely compatible)</MenuItem>
              <MenuItem value="tar.gz">TAR.GZ (better compression)</MenuItem>
            </Select>
          </FormControl>
        )}

        <Box sx={{ p: 2, borderRadius: 2, bgcolor: 'background.default', mb: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={settings.preserve_threads}
                onChange={(e) => setSettings(prev => ({ ...prev, preserve_threads: e.target.checked }))}
              />
            }
            label={
              <Box>
                <Typography>Preserve Thread Structure</Typography>
                <Typography variant="caption" color="text.secondary">
                  Keep reply chains and thread relationships in export
                </Typography>
              </Box>
            }
            sx={{ alignItems: 'flex-start', m: 0 }}
          />
        </Box>
      </FormGroup>

      <Divider sx={{ my: 3 }} />

      {/* Delivery Settings */}
      <Typography variant="subtitle1" mb={2}>
        <EmailIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Delivery Method
      </Typography>

      <Stack spacing={2} mb={3}>
        {DELIVERY_OPTIONS.map(option => (
          <Paper
            key={option.value}
            sx={{
              p: 2,
              cursor: 'pointer',
              border: '2px solid',
              borderColor: settings.delivery_method === option.value ? 'secondary.main' : 'transparent',
              bgcolor: settings.delivery_method === option.value ? alpha('#9C27B0', 0.05) : 'background.default',
              transition: 'all 0.2s ease',
              '&:hover': {
                borderColor: alpha('#9C27B0', 0.5),
              },
            }}
            onClick={() => setSettings(prev => ({ ...prev, delivery_method: option.value as any }))}
          >
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography variant="subtitle2">{option.label}</Typography>
                <Typography variant="caption" color="text.secondary">{option.description}</Typography>
              </Box>
              {settings.delivery_method === option.value && (
                <CheckIcon color="secondary" />
              )}
            </Box>
          </Paper>
        ))}
      </Stack>

      <FormGroup>
        <Box sx={{ p: 2, borderRadius: 2, bgcolor: 'background.default' }}>
          <FormControlLabel
            control={
              <Switch
                checked={settings.email_notification}
                onChange={(e) => setSettings(prev => ({ ...prev, email_notification: e.target.checked }))}
              />
            }
            label={
              <Box>
                <Typography>Email Notification</Typography>
                <Typography variant="caption" color="text.secondary">
                  Receive an email when export is complete
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
          sx={{ bgcolor: '#9C27B0', '&:hover': { bgcolor: '#7B1FA2' } }}
        >
          {isSaving ? 'Saving...' : 'Save Settings'}
        </Button>
      </Box>
    </Box>
  );
};

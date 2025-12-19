/**
 * MTProto Media Download Service Configuration
 * 
 * Service: mtproto_media_download
 * Price: 75 credits/month
 * Daily Quota: 500 files
 * 
 * Allows users to configure:
 * - Media types to download (photos, videos, documents, etc.)
 * - Quality/size preferences
 * - Download location and organization
 * - Bandwidth limits
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
} from '@mui/material';
import {
  CloudDownload as DownloadIcon,
  Save as SaveIcon,
  Photo as PhotoIcon,
  VideoLibrary as VideoIcon,
  InsertDriveFile as FileIcon,
  Audiotrack as AudioIcon,
  Folder as FolderIcon,
  Speed as SpeedIcon,
  Storage as StorageIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { apiClient } from '@/api/client';

interface MediaDownloadSettings {
  enabled: boolean;
  download_photos: boolean;
  download_videos: boolean;
  download_documents: boolean;
  download_audio: boolean;
  download_voice: boolean;
  photo_size: 'thumbnail' | 'medium' | 'original';
  video_max_size_mb: number;
  document_max_size_mb: number;
  organize_by: 'channel' | 'date' | 'type' | 'flat';
  concurrent_downloads: number;
  bandwidth_limit_mbps: number | null;
  auto_resume: boolean;
  skip_duplicates: boolean;
}

interface UsageStats {
  files_today: number;
  files_month: number;
  daily_limit: number;
  monthly_limit: number;
  storage_used_mb: number;
  storage_limit_mb: number;
}

const PHOTO_SIZE_OPTIONS = [
  { value: 'thumbnail', label: 'Thumbnail (fast, small)', description: '< 100KB' },
  { value: 'medium', label: 'Medium quality', description: '~500KB' },
  { value: 'original', label: 'Original (full size)', description: 'Full resolution' },
];

const ORGANIZE_OPTIONS = [
  { value: 'channel', label: 'By Channel', description: 'Separate folder per channel' },
  { value: 'date', label: 'By Date', description: 'YYYY/MM/DD structure' },
  { value: 'type', label: 'By Type', description: 'photos/, videos/, docs/ folders' },
  { value: 'flat', label: 'Flat', description: 'All files in one folder' },
];

export const MediaDownloadConfig: React.FC = () => {
  const [settings, setSettings] = useState<MediaDownloadSettings>({
    enabled: true,
    download_photos: true,
    download_videos: true,
    download_documents: true,
    download_audio: true,
    download_voice: false,
    photo_size: 'original',
    video_max_size_mb: 100,
    document_max_size_mb: 50,
    organize_by: 'channel',
    concurrent_downloads: 3,
    bandwidth_limit_mbps: null,
    auto_resume: true,
    skip_duplicates: true,
  });

  const [usageStats, setUsageStats] = useState<UsageStats>({
    files_today: 0,
    files_month: 0,
    daily_limit: 500,
    monthly_limit: 10000,
    storage_used_mb: 0,
    storage_limit_mb: 5000,
  });

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        // Load saved settings
        const savedSettings = localStorage.getItem('mtproto_media_settings');
        if (savedSettings) {
          setSettings(prev => ({ ...prev, ...JSON.parse(savedSettings) }));
        }

        // Try to get usage stats
        try {
          const response = await apiClient.get('/user-mtproto/monitoring/overview') as Record<string, any>;
          if (response.storage_stats) {
            setUsageStats(prev => ({
              ...prev,
              storage_used_mb: response.storage_stats.used_mb || 0,
            }));
          }
        } catch {
          // Stats not available, use defaults
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
      localStorage.setItem('mtproto_media_settings', JSON.stringify(settings));
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

  const dailyUsagePercent = (usageStats.files_today / usageStats.daily_limit) * 100;
  const storageUsagePercent = (usageStats.storage_used_mb / usageStats.storage_limit_mb) * 100;

  return (
    <Box>
      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 3 }}>Settings saved successfully!</Alert>}

      {/* Service Header */}
      <Card sx={{ mb: 3, bgcolor: alpha('#4CAF50', 0.05), border: '1px solid', borderColor: alpha('#4CAF50', 0.2) }}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box display="flex" alignItems="center" gap={2}>
              <DownloadIcon sx={{ color: '#4CAF50', fontSize: 40 }} />
              <Box>
                <Typography variant="h6">MTProto Media Download</Typography>
                <Typography variant="body2" color="text.secondary">
                  Download photos, videos, and documents from your channels
                </Typography>
              </Box>
            </Box>
            <Stack direction="row" spacing={1}>
              <Chip 
                label="75 cr/month" 
                size="small"
                sx={{ bgcolor: alpha('#4CAF50', 0.1) }}
              />
              <Chip 
                label={`${usageStats.daily_limit} files/day`} 
                variant="outlined"
                size="small"
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
            Usage & Quota
          </Typography>

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Box>
                <Box display="flex" justifyContent="space-between" mb={0.5}>
                  <Typography variant="body2">Daily Downloads</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {usageStats.files_today} / {usageStats.daily_limit} files
                  </Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={Math.min(dailyUsagePercent, 100)} 
                  color={dailyUsagePercent > 80 ? 'warning' : 'success'}
                  sx={{ height: 8, borderRadius: 1 }}
                />
                {dailyUsagePercent > 80 && (
                  <Typography variant="caption" color="warning.main" display="flex" alignItems="center" mt={0.5}>
                    <WarningIcon sx={{ fontSize: 14, mr: 0.5 }} />
                    Approaching daily limit
                  </Typography>
                )}
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Box>
                <Box display="flex" justifyContent="space-between" mb={0.5}>
                  <Typography variant="body2">Storage Used</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {(usageStats.storage_used_mb / 1024).toFixed(2)} GB / {(usageStats.storage_limit_mb / 1024).toFixed(1)} GB
                  </Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={Math.min(storageUsagePercent, 100)} 
                  color={storageUsagePercent > 80 ? 'error' : 'primary'}
                  sx={{ height: 8, borderRadius: 1 }}
                />
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Media Type Selection */}
      <Typography variant="subtitle1" mb={2}>
        <PhotoIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Media Types
      </Typography>

      <Grid container spacing={2} mb={3}>
        <Grid item xs={12} sm={6} md={4}>
          <Card 
            sx={{ 
              p: 2, 
              cursor: 'pointer',
              border: '2px solid',
              borderColor: settings.download_photos ? 'success.main' : 'transparent',
              bgcolor: settings.download_photos ? alpha('#4CAF50', 0.05) : 'background.default',
            }}
            onClick={() => setSettings(prev => ({ ...prev, download_photos: !prev.download_photos }))}
          >
            <Box display="flex" alignItems="center" gap={2}>
              <PhotoIcon color={settings.download_photos ? 'success' : 'disabled'} />
              <Box flex={1}>
                <Typography variant="subtitle2">Photos</Typography>
                <Typography variant="caption" color="text.secondary">Images & stickers</Typography>
              </Box>
              <Switch checked={settings.download_photos} size="small" />
            </Box>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Card 
            sx={{ 
              p: 2, 
              cursor: 'pointer',
              border: '2px solid',
              borderColor: settings.download_videos ? 'success.main' : 'transparent',
              bgcolor: settings.download_videos ? alpha('#4CAF50', 0.05) : 'background.default',
            }}
            onClick={() => setSettings(prev => ({ ...prev, download_videos: !prev.download_videos }))}
          >
            <Box display="flex" alignItems="center" gap={2}>
              <VideoIcon color={settings.download_videos ? 'success' : 'disabled'} />
              <Box flex={1}>
                <Typography variant="subtitle2">Videos</Typography>
                <Typography variant="caption" color="text.secondary">Video files & GIFs</Typography>
              </Box>
              <Switch checked={settings.download_videos} size="small" />
            </Box>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Card 
            sx={{ 
              p: 2, 
              cursor: 'pointer',
              border: '2px solid',
              borderColor: settings.download_documents ? 'success.main' : 'transparent',
              bgcolor: settings.download_documents ? alpha('#4CAF50', 0.05) : 'background.default',
            }}
            onClick={() => setSettings(prev => ({ ...prev, download_documents: !prev.download_documents }))}
          >
            <Box display="flex" alignItems="center" gap={2}>
              <FileIcon color={settings.download_documents ? 'success' : 'disabled'} />
              <Box flex={1}>
                <Typography variant="subtitle2">Documents</Typography>
                <Typography variant="caption" color="text.secondary">PDFs, archives, etc.</Typography>
              </Box>
              <Switch checked={settings.download_documents} size="small" />
            </Box>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Card 
            sx={{ 
              p: 2, 
              cursor: 'pointer',
              border: '2px solid',
              borderColor: settings.download_audio ? 'success.main' : 'transparent',
              bgcolor: settings.download_audio ? alpha('#4CAF50', 0.05) : 'background.default',
            }}
            onClick={() => setSettings(prev => ({ ...prev, download_audio: !prev.download_audio }))}
          >
            <Box display="flex" alignItems="center" gap={2}>
              <AudioIcon color={settings.download_audio ? 'success' : 'disabled'} />
              <Box flex={1}>
                <Typography variant="subtitle2">Audio</Typography>
                <Typography variant="caption" color="text.secondary">Music & audio files</Typography>
              </Box>
              <Switch checked={settings.download_audio} size="small" />
            </Box>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Card 
            sx={{ 
              p: 2, 
              cursor: 'pointer',
              border: '2px solid',
              borderColor: settings.download_voice ? 'success.main' : 'transparent',
              bgcolor: settings.download_voice ? alpha('#4CAF50', 0.05) : 'background.default',
            }}
            onClick={() => setSettings(prev => ({ ...prev, download_voice: !prev.download_voice }))}
          >
            <Box display="flex" alignItems="center" gap={2}>
              <AudioIcon color={settings.download_voice ? 'success' : 'disabled'} />
              <Box flex={1}>
                <Typography variant="subtitle2">Voice Messages</Typography>
                <Typography variant="caption" color="text.secondary">Voice notes & rounds</Typography>
              </Box>
              <Switch checked={settings.download_voice} size="small" />
            </Box>
          </Card>
        </Grid>
      </Grid>

      <Divider sx={{ my: 3 }} />

      {/* Quality Settings */}
      <Typography variant="subtitle1" mb={2}>
        <StorageIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Quality & Size Limits
      </Typography>

      <Box mb={3}>
        <FormControl fullWidth sx={{ mb: 3 }}>
          <InputLabel>Photo Quality</InputLabel>
          <Select
            value={settings.photo_size}
            label="Photo Quality"
            onChange={(e) => setSettings(prev => ({ ...prev, photo_size: e.target.value as any }))}
          >
            {PHOTO_SIZE_OPTIONS.map(option => (
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
            Max Video Size: <strong>{settings.video_max_size_mb} MB</strong>
          </Typography>
          <Slider
            value={settings.video_max_size_mb}
            onChange={(_, value) => setSettings(prev => ({ ...prev, video_max_size_mb: value as number }))}
            min={10}
            max={500}
            step={10}
            marks={[
              { value: 10, label: '10MB' },
              { value: 100, label: '100MB' },
              { value: 250, label: '250MB' },
              { value: 500, label: '500MB' },
            ]}
            valueLabelDisplay="auto"
            valueLabelFormat={(value) => `${value}MB`}
          />
        </Box>

        <Box>
          <Typography variant="body2" gutterBottom>
            Max Document Size: <strong>{settings.document_max_size_mb} MB</strong>
          </Typography>
          <Slider
            value={settings.document_max_size_mb}
            onChange={(_, value) => setSettings(prev => ({ ...prev, document_max_size_mb: value as number }))}
            min={5}
            max={200}
            step={5}
            marks={[
              { value: 5, label: '5MB' },
              { value: 50, label: '50MB' },
              { value: 100, label: '100MB' },
              { value: 200, label: '200MB' },
            ]}
            valueLabelDisplay="auto"
            valueLabelFormat={(value) => `${value}MB`}
          />
        </Box>
      </Box>

      <Divider sx={{ my: 3 }} />

      {/* Organization Settings */}
      <Typography variant="subtitle1" mb={2}>
        <FolderIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        File Organization
      </Typography>

      <FormControl fullWidth sx={{ mb: 3 }}>
        <InputLabel>Organize Files By</InputLabel>
        <Select
          value={settings.organize_by}
          label="Organize Files By"
          onChange={(e) => setSettings(prev => ({ ...prev, organize_by: e.target.value as any }))}
        >
          {ORGANIZE_OPTIONS.map(option => (
            <MenuItem key={option.value} value={option.value}>
              <Box>
                <Typography>{option.label}</Typography>
                <Typography variant="caption" color="text.secondary">{option.description}</Typography>
              </Box>
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <FormGroup>
        <Box sx={{ p: 2, borderRadius: 2, bgcolor: 'background.default', mb: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={settings.skip_duplicates}
                onChange={(e) => setSettings(prev => ({ ...prev, skip_duplicates: e.target.checked }))}
              />
            }
            label={
              <Box>
                <Typography>Skip Duplicates</Typography>
                <Typography variant="caption" color="text.secondary">
                  Don't download files that already exist locally
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
                checked={settings.auto_resume}
                onChange={(e) => setSettings(prev => ({ ...prev, auto_resume: e.target.checked }))}
              />
            }
            label={
              <Box>
                <Typography>Auto-Resume Downloads</Typography>
                <Typography variant="caption" color="text.secondary">
                  Resume interrupted downloads automatically
                </Typography>
              </Box>
            }
            sx={{ alignItems: 'flex-start', m: 0 }}
          />
        </Box>
      </FormGroup>

      <Divider sx={{ my: 3 }} />

      {/* Performance Settings */}
      <Typography variant="subtitle1" mb={2}>
        <SpeedIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Performance
      </Typography>

      <Box mb={3}>
        <Typography variant="body2" gutterBottom>
          Concurrent Downloads: <strong>{settings.concurrent_downloads}</strong>
        </Typography>
        <Slider
          value={settings.concurrent_downloads}
          onChange={(_, value) => setSettings(prev => ({ ...prev, concurrent_downloads: value as number }))}
          min={1}
          max={5}
          step={1}
          marks={[
            { value: 1, label: '1' },
            { value: 3, label: '3' },
            { value: 5, label: '5' },
          ]}
          valueLabelDisplay="auto"
        />
        <Typography variant="caption" color="text.secondary">
          Higher values = faster but may cause rate limiting
        </Typography>
      </Box>

      {/* Save Button */}
      <Box mt={4} display="flex" justifyContent="flex-end">
        <Button
          variant="contained"
          startIcon={isSaving ? <CircularProgress size={20} color="inherit" /> : <SaveIcon />}
          onClick={handleSave}
          disabled={isSaving}
          size="large"
          sx={{ bgcolor: '#4CAF50', '&:hover': { bgcolor: '#388E3C' } }}
        >
          {isSaving ? 'Saving...' : 'Save Settings'}
        </Button>
      </Box>
    </Box>
  );
};

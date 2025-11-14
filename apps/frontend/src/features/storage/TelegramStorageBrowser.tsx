/**
 * Telegram Storage Browser
 *
 * Browse, upload, and manage files stored in user's Telegram channels.
 * Replaces server storage with zero-cost Telegram cloud storage.
 */

import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardMedia,
  CardContent,
  CardActions,
  Chip,
  Grid,
  IconButton,
  Menu,
  MenuItem,
  Stack,
  Typography,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Delete as DeleteIcon,
  Download as DownloadIcon,
  MoreVert as MoreIcon,
  Image as ImageIcon,
  VideoLibrary as VideoIcon,
  InsertDriveFile as FileIcon,
  AudioFile as AudioIcon,
} from '@mui/icons-material';
import { useTelegramStorageStore } from '@/store/slices/storage/useTelegramStorageStore';
import type { TelegramMedia } from '@/store/slices/storage/useTelegramStorageStore';

interface TelegramStorageBrowserProps {
  onSelectFile?: (file: TelegramMedia) => void;
  selectionMode?: boolean;
}

export const TelegramStorageBrowser: React.FC<TelegramStorageBrowserProps> = ({
  onSelectFile,
  selectionMode = false,
}) => {
  const {
    files: filesFromStore,
    totalFiles,
    isLoadingFiles,
    isUploading,
    error,
    fetchFiles,
    uploadFile,
    deleteFile,
    getFileUrl,
    clearError,
  } = useTelegramStorageStore();

  // Ensure files is always an array (defensive programming)
  const files = Array.isArray(filesFromStore) ? filesFromStore : [];

  const [currentTab, setCurrentTab] = useState<string>('all');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedFile, setSelectedFile] = useState<TelegramMedia | null>(null);

  useEffect(() => {
    const fileType = currentTab === 'all' ? undefined : currentTab;
    fetchFiles({ fileType });
  }, [currentTab, fetchFiles]);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: string) => {
    setCurrentTab(newValue);
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      await uploadFile(file);
    } catch (err) {
      console.error('Upload failed:', err);
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, file: TelegramMedia) => {
    setAnchorEl(event.currentTarget);
    setSelectedFile(file);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedFile(null);
  };

  const handleDownload = async () => {
    if (!selectedFile) return;
    try {
      const url = await getFileUrl(selectedFile.id);
      window.open(url, '_blank');
    } catch (err) {
      console.error('Download failed:', err);
    }
    handleMenuClose();
  };

  const handleDelete = async () => {
    if (!selectedFile) return;
    if (confirm(`Delete "${selectedFile.file_name}"?`)) {
      try {
        await deleteFile(selectedFile.id);
      } catch (err) {
        console.error('Delete failed:', err);
      }
    }
    handleMenuClose();
  };

  const handleSelect = (file: TelegramMedia) => {
    if (onSelectFile) {
      onSelectFile(file);
    }
  };

  const getFileIcon = (fileType: string) => {
    switch (fileType) {
      case 'photo':
        return <ImageIcon />;
      case 'video':
        return <VideoIcon />;
      case 'audio':
        return <AudioIcon />;
      default:
        return <FileIcon />;
    }
  };

  const filteredFiles = files;

  return (
    <Box>
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6">
          Telegram Storage ({totalFiles} files)
        </Typography>
        <Button
          variant="contained"
          component="label"
          startIcon={isUploading ? <CircularProgress size={20} /> : <UploadIcon />}
          disabled={isUploading}
        >
          {isUploading ? 'Uploading...' : 'Upload File'}
          <input type="file" hidden onChange={handleFileUpload} />
        </Button>
      </Stack>

      {/* Error Display */}
      {error && (
        <Alert severity="error" onClose={clearError} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* File Type Tabs */}
      <Tabs value={currentTab} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="All Files" value="all" />
        <Tab label="Photos" value="photo" icon={<ImageIcon />} iconPosition="start" />
        <Tab label="Videos" value="video" icon={<VideoIcon />} iconPosition="start" />
        <Tab label="Documents" value="document" icon={<FileIcon />} iconPosition="start" />
        <Tab label="Audio" value="audio" icon={<AudioIcon />} iconPosition="start" />
      </Tabs>

      {/* Loading State */}
      {isLoadingFiles ? (
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      ) : filteredFiles.length === 0 ? (
        <Card>
          <CardContent>
            <Box textAlign="center" py={4}>
              {getFileIcon(currentTab)}
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                No {currentTab === 'all' ? 'files' : `${currentTab}s`} found
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Upload files to get started
              </Typography>
            </Box>
          </CardContent>
        </Card>
      ) : (
        /* Files Grid */
        <Grid container spacing={2}>
          {filteredFiles.map((file) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={file.id}>
              <Card
                sx={{
                  cursor: selectionMode ? 'pointer' : 'default',
                  '&:hover': selectionMode
                    ? {
                        boxShadow: 3,
                        transform: 'translateY(-2px)',
                        transition: 'all 0.2s',
                      }
                    : {},
                }}
                onClick={() => selectionMode && handleSelect(file)}
              >
                {/* File Preview */}
                {file.file_type === 'photo' && file.preview_url && (
                  <CardMedia
                    component="img"
                    height="140"
                    image={file.preview_url}
                    alt={file.file_name}
                  />
                )}
                {file.file_type !== 'photo' && (
                  <Box
                    sx={{
                      height: 140,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      bgcolor: 'grey.100',
                    }}
                  >
                    {getFileIcon(file.file_type)}
                  </Box>
                )}

                <CardContent>
                  <Typography
                    variant="body2"
                    fontWeight="bold"
                    noWrap
                    title={file.file_name}
                  >
                    {file.file_name}
                  </Typography>
                  <Stack direction="row" spacing={1} mt={1} flexWrap="wrap">
                    <Chip label={file.file_type} size="small" />
                    <Chip label={file.file_size_formatted} size="small" variant="outlined" />
                  </Stack>
                  {file.caption && (
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }} noWrap>
                      {file.caption}
                    </Typography>
                  )}
                  <Typography variant="caption" color="text.secondary" display="block" mt={1}>
                    {new Date(file.uploaded_at).toLocaleDateString()}
                  </Typography>
                </CardContent>

                <CardActions>
                  {selectionMode ? (
                    <Button size="small" fullWidth onClick={() => handleSelect(file)}>
                      Select
                    </Button>
                  ) : (
                    <>
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleMenuOpen(e, file);
                        }}
                      >
                        <MoreIcon />
                      </IconButton>
                    </>
                  )}
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Context Menu */}
      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleMenuClose}>
        <MenuItem onClick={handleDownload}>
          <DownloadIcon fontSize="small" sx={{ mr: 1 }} />
          Download
        </MenuItem>
        <MenuItem onClick={handleDelete}>
          <DeleteIcon fontSize="small" sx={{ mr: 1 }} />
          Delete
        </MenuItem>
      </Menu>
    </Box>
  );
};

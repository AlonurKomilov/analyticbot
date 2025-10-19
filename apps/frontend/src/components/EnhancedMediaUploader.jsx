import React, { useState, useCallback, useRef } from 'react';
import {
    Box,
    Typography,
    LinearProgress,
    Alert,
    Chip,
    Paper,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Switch,
    FormControlLabel,
    Grid
} from '@mui/material';
import {
    CloudUpload as UploadIcon,
    Delete as DeleteIcon,
    Speed as SpeedIcon,
    Storage as StorageIcon,
    Refresh as RefreshIcon
} from '@mui/icons-material';
import { useMediaStore, useChannelStore } from '@/stores';
import { useTelegramWebApp } from '../hooks/index.js';

const EnhancedMediaUploader = React.memo(() => {
    const { uploadMediaDirect, pendingMedia, clearPendingMedia, isUploading } = useMediaStore();
    const { channels } = useChannelStore();

    const { hapticFeedback } = useTelegramWebApp();
    const fileInputRef = useRef(null);

    // Enhanced state management
    const [dragActive, setDragActive] = useState(false);
    const [selectedChannelId, setSelectedChannelId] = useState('');
    const [directToChannel, setDirectToChannel] = useState(false);
    const [uploadStats, setUploadStats] = useState(null);

    // File validation
    const validateFile = useCallback((file) => {
        const maxSize = 50 * 1024 * 1024; // 50MB
        const allowedTypes = [
            'image/jpeg', 'image/png', 'image/gif', 'image/webp',
            'video/mp4', 'video/webm', 'video/mov',
            'application/pdf', 'text/plain'
        ];

        if (file.size > maxSize) {
            throw new Error('File too large. Maximum size is 50MB.');
        }

        if (!allowedTypes.includes(file.type)) {
            throw new Error(`Unsupported file type: ${file.type}`);
        }

        return true;
    }, []);

    // Handle file upload
    const handleUpload = useCallback(async (file) => {
        if (!file) return;

        try {
            validateFile(file);
            hapticFeedback('light');

            const targetChannelId = directToChannel ? selectedChannelId : null;
            const startTime = Date.now();

            const response = await uploadMediaDirect(file, targetChannelId);

            // Set upload statistics
            setUploadStats({
                duration: response.upload_duration || (Date.now() - startTime),
                speed: response.upload_speed || (file.size / ((Date.now() - startTime) / 1000)),
                fileSize: file.size,
                uploadType: response.upload_type || (targetChannelId ? 'direct_channel' : 'storage')
            });

            hapticFeedback('success');
        } catch (error) {
            console.error('Upload failed:', error);
            hapticFeedback('error');
        }
    }, [uploadMediaDirect, validateFile, directToChannel, selectedChannelId, hapticFeedback]);

    // Handle file selection
    const handleFileSelect = useCallback((event) => {
        const file = event.target.files?.[0];
        if (file) {
            handleUpload(file);
        }
        // Reset input
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    }, [handleUpload]);

    // Drag and drop handlers
    const handleDrag = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    }, []);

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleUpload(e.dataTransfer.files[0]);
        }
    }, [handleUpload]);

    // Format file size
    const formatFileSize = (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    // Format upload speed
    const formatSpeed = (bytesPerSecond) => {
        return formatFileSize(bytesPerSecond) + '/s';
    };

    // Clear upload and stats
    const handleClear = useCallback(() => {
        clearPendingMedia();
        setUploadStats(null);
        hapticFeedback('light');
    }, [clearPendingMedia, hapticFeedback]);

    // Channel options
    const channelOptions = channels.map((channel) => ({
        value: channel.id,
        label: `${channel.title} (@${channel.username})`
    }));

    // Upload progress percentage
    const uploadProgress = pendingMedia.uploadProgress || 0;

    return (
        <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
                <span aria-hidden="true">📱</span> Enhanced Media Upload
            </Typography>

            {/* Upload Configuration */}
            <Box sx={{ mb: 2 }}>
                <FormControlLabel
                    control={
                        <Switch
                            checked={directToChannel}
                            onChange={(e) => setDirectToChannel(e.target.checked)}
                            disabled={isUploading}
                        />
                    }
                    label="Upload directly to channel"
                />

                {directToChannel && (
                    <FormControl fullWidth sx={{ mt: 1 }} disabled={isUploading}>
                        <InputLabel>Select Channel</InputLabel>
                        <Select
                            value={selectedChannelId}
                            label="Select Channel"
                            onChange={(e) => setSelectedChannelId(e.target.value)}
                        >
                            {channelOptions.map((option) => (
                                <MenuItem key={option.value} value={option.value}>
                                    {option.label}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                )}
            </Box>

            {/* Upload Area */}
            <Box
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                sx={{
                    border: '2px dashed',
                    borderColor: dragActive ? 'primary.main' : 'grey.300',
                    borderRadius: 1,
                    p: 3,
                    textAlign: 'center',
                    backgroundColor: dragActive ? 'primary.light' : 'grey.50',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                        borderColor: 'primary.main',
                        backgroundColor: 'primary.light'
                    }
                }}
                onClick={() => fileInputRef.current?.click()}
            >
                <input
                    ref={fileInputRef}
                    type="file"
                    onChange={handleFileSelect}
                    accept="image/*,video/*,.pdf,.txt"
                    style={{ display: 'none' }}
                    disabled={isUploading}
                />

                <UploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
                <Typography variant="h6" color="primary">
                    {dragActive ? 'Drop file here' : 'Click or drag file to upload'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    Supported: Images, Videos, PDF, Text (Max: 50MB)
                </Typography>
            </Box>

            {/* Upload Progress */}
            {isUploading && (
                <Box sx={{ mt: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <Typography variant="body2" sx={{ flex: 1 }}>
                            Uploading... {uploadProgress.toFixed(1)}%
                        </Typography>
                        {pendingMedia.uploadSpeed > 0 && (
                            <Chip
                                icon={<SpeedIcon />}
                                label={formatSpeed(pendingMedia.uploadSpeed)}
                                size="small"
                                color="primary"
                            />
                        )}
                    </Box>
                    <LinearProgress
                        variant="determinate"
                        value={uploadProgress}
                        sx={{ height: 8, borderRadius: 4 }}
                    />
                    {pendingMedia.bytesLoaded && pendingMedia.bytesTotal && (
                        <Typography variant="caption" color="text.secondary">
                            {formatFileSize(pendingMedia.bytesLoaded)} / {formatFileSize(pendingMedia.bytesTotal)}
                        </Typography>
                    )}
                </Box>
            )}

            {/* Upload Success & Stats */}
            {pendingMedia.file_id && !isUploading && (
                <Alert
                    severity="success"
                    sx={{ mt: 2 }}
                    action={
                        <IconButton
                            onClick={handleClear}
                            sx={{
                                minWidth: '44px',
                                minHeight: '44px',
                                '@media (hover: none)': {
                                    minWidth: '44px',
                                    minHeight: '44px'
                                }
                            }}
                            aria-label="Clear uploaded media"
                        >
                            <DeleteIcon />
                        </IconButton>
                    }
                >
                    <Typography variant="subtitle2">Upload Successful!</Typography>
                    {uploadStats && (
                        <Grid container spacing={1} sx={{ mt: 1 }}>
                            <Grid item xs={6}>
                                <Chip
                                    icon={<SpeedIcon />}
                                    label={`${formatSpeed(uploadStats.speed)}`}
                                    size="small"
                                    variant="outlined"
                                    sx={{
                                        minHeight: '32px',
                                        '@media (hover: none)': {
                                            minHeight: '36px'
                                        }
                                    }}
                                />
                            </Grid>
                            <Grid item xs={6}>
                                <Chip
                                    icon={<StorageIcon />}
                                    label={uploadStats.uploadType === 'direct_channel' ? 'Direct' : 'Storage'}
                                    size="small"
                                    variant="outlined"
                                    color={uploadStats.uploadType === 'direct_channel' ? 'primary' : 'default'}
                                    sx={{
                                        minHeight: '32px',
                                        '@media (hover: none)': {
                                            minHeight: '36px'
                                        }
                                    }}
                                />
                            </Grid>
                        </Grid>
                    )}
                </Alert>
            )}

            {/* Media Preview */}
            {pendingMedia.previewUrl && (
                <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>Preview:</Typography>
                    {pendingMedia.file_type?.startsWith('image/') ||
                     pendingMedia.metadata?.content_type?.startsWith('image/') ? (
                        <img
                            src={pendingMedia.previewUrl}
                            alt="Preview"
                            style={{
                                maxWidth: '100%',
                                maxHeight: '200px',
                                borderRadius: '8px',
                                objectFit: 'contain'
                            }}
                        />
                    ) : pendingMedia.file_type?.startsWith('video/') ||
                              pendingMedia.metadata?.content_type?.startsWith('video/') ? (
                        <video
                            src={pendingMedia.previewUrl}
                            controls
                            style={{
                                maxWidth: '100%',
                                maxHeight: '200px',
                                borderRadius: '8px'
                            }}
                        />
                    ) : (
                        <Box sx={{ p: 2, border: '1px solid #ddd', borderRadius: 1 }}>
                            <Typography variant="body2">
                                📄 File ready for upload
                            </Typography>
                        </Box>
                    )}
                </Box>
            )}
        </Paper>
    );
});

EnhancedMediaUploader.displayName = 'EnhancedMediaUploader';

export default EnhancedMediaUploader;

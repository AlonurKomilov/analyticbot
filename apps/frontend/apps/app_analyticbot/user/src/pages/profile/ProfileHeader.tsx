/**
 * Profile Header Component
 * Displays user avatar, name and status chips with photo change functionality
 */

import React, { useRef, useState } from 'react';
import { Box, Typography, Avatar, Chip, IconButton, CircularProgress, Tooltip, Snackbar, Alert } from '@mui/material';
import {
    Badge as BadgeIcon,
    CameraAlt as CameraIcon,
} from '@mui/icons-material';
import { apiClient } from '../../api/client';

interface ProfileHeaderProps {
    user: any;
    onPhotoUpdated?: () => void;
}

export const ProfileHeader: React.FC<ProfileHeaderProps> = ({ user, onPhotoUpdated }) => {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [uploading, setUploading] = useState(false);
    const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
        open: false,
        message: '',
        severity: 'success'
    });

    const showMessage = (message: string, severity: 'success' | 'error') => {
        setSnackbar({ open: true, message, severity });
    };

    const handlePhotoClick = () => {
        fileInputRef.current?.click();
    };

    const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        // Validate file type
        if (!file.type.startsWith('image/')) {
            showMessage('Please select an image file', 'error');
            return;
        }

        // Validate file size (max 2MB)
        if (file.size > 2 * 1024 * 1024) {
            showMessage('Image must be less than 2MB', 'error');
            return;
        }

        setUploading(true);
        try {
            // Convert to base64 data URL
            const reader = new FileReader();
            reader.onload = async (e) => {
                const dataUrl = e.target?.result as string;
                
                try {
                    await apiClient.put('/auth/profile', {
                        photo_url: dataUrl
                    });
                    showMessage('Profile photo updated!', 'success');
                    onPhotoUpdated?.();
                } catch (error: any) {
                    showMessage(error.response?.data?.detail || 'Failed to update photo', 'error');
                } finally {
                    setUploading(false);
                }
            };
            reader.onerror = () => {
                showMessage('Failed to read image file', 'error');
                setUploading(false);
            };
            reader.readAsDataURL(file);
        } catch (error) {
            showMessage('Failed to upload photo', 'error');
            setUploading(false);
        }

        // Reset input
        event.target.value = '';
    };

    // Get user initials for fallback
    const getInitials = () => {
        // Prefer first_name/last_name
        if (user?.first_name && user?.last_name) {
            return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase();
        }
        if (user?.first_name) {
            return user.first_name[0].toUpperCase();
        }
        // Fallback to full_name
        if (user?.full_name) {
            const parts = user.full_name.split(' ');
            if (parts.length >= 2) {
                return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
            }
            return user.full_name[0].toUpperCase();
        }
        if (user?.username) {
            return user.username[0].toUpperCase();
        }
        return 'U';
    };

    // Get display name
    const getDisplayName = () => {
        if (user?.first_name && user?.last_name) {
            return `${user.first_name} ${user.last_name}`;
        }
        if (user?.first_name) {
            return user.first_name;
        }
        return user?.full_name || user?.username || 'User';
    };

    return (
        <Box sx={{ mb: 4, textAlign: 'center' }}>
            <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                accept="image/*"
                style={{ display: 'none' }}
            />
            <Box sx={{ position: 'relative', display: 'inline-block' }}>
                <Avatar
                    src={user?.photo_url || undefined}
                    sx={{
                        width: 100,
                        height: 100,
                        mx: 'auto',
                        mb: 2,
                        bgcolor: 'primary.main',
                        fontSize: '2.5rem',
                        cursor: 'pointer',
                        transition: 'opacity 0.2s',
                        '&:hover': {
                            opacity: 0.8,
                        }
                    }}
                    onClick={handlePhotoClick}
                >
                    {uploading ? (
                        <CircularProgress size={40} color="inherit" />
                    ) : (
                        getInitials()
                    )}
                </Avatar>
                <Tooltip title="Change photo">
                    <IconButton
                        onClick={handlePhotoClick}
                        disabled={uploading}
                        sx={{
                            position: 'absolute',
                            bottom: 12,
                            right: -8,
                            bgcolor: 'background.paper',
                            boxShadow: 2,
                            '&:hover': {
                                bgcolor: 'background.paper',
                            }
                        }}
                        size="small"
                    >
                        <CameraIcon fontSize="small" />
                    </IconButton>
                </Tooltip>
            </Box>
            <Typography variant="h4" gutterBottom>
                {getDisplayName()}
            </Typography>
            <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1, mb: 2 }}>
                <Chip
                    label={user?.role || 'user'}
                    color="primary"
                    variant="outlined"
                    icon={<BadgeIcon />}
                />
                <Chip
                    label={user?.status || 'active'}
                    color="success"
                    variant="outlined"
                />
            </Box>

            {/* Snackbar for notifications */}
            <Snackbar
                open={snackbar.open}
                autoHideDuration={4000}
                onClose={() => setSnackbar({ ...snackbar, open: false })}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
            >
                <Alert
                    severity={snackbar.severity}
                    onClose={() => setSnackbar({ ...snackbar, open: false })}
                    sx={{ width: '100%' }}
                >
                    {snackbar.message}
                </Alert>
            </Snackbar>
        </Box>
    );
};

/**
 * Profile Information Tab Component
 * Form for editing user profile information
 */

import React from 'react';
import {
    Box,
    Typography,
    TextField,
    Button,
    Grid,
    CircularProgress
} from '@mui/material';
import {
    Person as PersonIcon,
    Edit as EditIcon,
    Save as SaveIcon,
    Cancel as CancelIcon,
    Email as EmailIcon
} from '@mui/icons-material';
import type { ProfileData } from './types';

interface ProfileInformationTabProps {
    profileData: ProfileData;
    editMode: boolean;
    loading: boolean;
    onProfileChange: (field: keyof ProfileData) => (event: React.ChangeEvent<HTMLInputElement>) => void;
    onEditClick: () => void;
    onSaveProfile: () => void;
    onCancelEdit: () => void;
}

export const ProfileInformationTab: React.FC<ProfileInformationTabProps> = ({
    profileData,
    editMode,
    loading,
    onProfileChange,
    onEditClick,
    onSaveProfile,
    onCancelEdit
}) => {
    return (
        <Box sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">
                    Profile Information
                </Typography>
                {!editMode ? (
                    <Button
                        startIcon={<EditIcon />}
                        onClick={onEditClick}
                        variant="outlined"
                    >
                        Edit Profile
                    </Button>
                ) : (
                    <Box sx={{ display: 'flex', gap: 1 }}>
                        <Button
                            startIcon={<SaveIcon />}
                            onClick={onSaveProfile}
                            variant="contained"
                            disabled={loading}
                        >
                            {loading ? <CircularProgress size={16} /> : 'Save'}
                        </Button>
                        <Button
                            startIcon={<CancelIcon />}
                            onClick={onCancelEdit}
                            variant="outlined"
                            disabled={loading}
                        >
                            Cancel
                        </Button>
                    </Box>
                )}
            </Box>

            <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                    <TextField
                        fullWidth
                        label="Username"
                        value={profileData.username}
                        onChange={onProfileChange('username')}
                        disabled={!editMode || loading}
                        InputProps={{
                            startAdornment: <PersonIcon sx={{ mr: 1, color: 'action.active' }} />
                        }}
                    />
                </Grid>
                <Grid item xs={12} sm={6}>
                    <TextField
                        fullWidth
                        label="Full Name"
                        value={profileData.fullName}
                        onChange={onProfileChange('fullName')}
                        disabled={!editMode || loading}
                    />
                </Grid>
                <Grid item xs={12}>
                    <TextField
                        fullWidth
                        label="Email Address"
                        value={profileData.email}
                        onChange={onProfileChange('email')}
                        disabled={!editMode || loading}
                        type="email"
                        InputProps={{
                            startAdornment: <EmailIcon sx={{ mr: 1, color: 'action.active' }} />
                        }}
                    />
                </Grid>
            </Grid>
        </Box>
    );
};

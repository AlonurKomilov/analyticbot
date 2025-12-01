/**
 * Security Tab Component
 * Password change and session management
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
    Lock as LockIcon,
    Security as SecurityIcon,
    Logout as LogoutIcon
} from '@mui/icons-material';
import type { PasswordData, PasswordErrors } from './types';

interface SecurityTabProps {
    passwordData: PasswordData;
    passwordErrors: PasswordErrors;
    loading: boolean;
    onPasswordChange: (field: keyof PasswordData) => (event: React.ChangeEvent<HTMLInputElement>) => void;
    onChangePassword: () => void;
    onLogout: () => void;
}

export const SecurityTab: React.FC<SecurityTabProps> = ({
    passwordData,
    passwordErrors,
    loading,
    onPasswordChange,
    onChangePassword,
    onLogout
}) => {
    return (
        <Box sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
                Change Password
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Ensure your account stays secure by using a strong password.
            </Typography>

            <Grid container spacing={3}>
                <Grid item xs={12}>
                    <TextField
                        fullWidth
                        type="password"
                        label="Current Password"
                        value={passwordData.currentPassword}
                        onChange={onPasswordChange('currentPassword')}
                        error={!!passwordErrors.currentPassword}
                        helperText={passwordErrors.currentPassword}
                        disabled={loading}
                        InputProps={{
                            startAdornment: <LockIcon sx={{ mr: 1, color: 'action.active' }} />
                        }}
                    />
                </Grid>
                <Grid item xs={12} sm={6}>
                    <TextField
                        fullWidth
                        type="password"
                        label="New Password"
                        value={passwordData.newPassword}
                        onChange={onPasswordChange('newPassword')}
                        error={!!passwordErrors.newPassword}
                        helperText={passwordErrors.newPassword}
                        disabled={loading}
                    />
                </Grid>
                <Grid item xs={12} sm={6}>
                    <TextField
                        fullWidth
                        type="password"
                        label="Confirm New Password"
                        value={passwordData.confirmPassword}
                        onChange={onPasswordChange('confirmPassword')}
                        error={!!passwordErrors.confirmPassword}
                        helperText={passwordErrors.confirmPassword}
                        disabled={loading}
                    />
                </Grid>
            </Grid>

            <Box sx={{ mt: 3 }}>
                <Button
                    variant="contained"
                    onClick={onChangePassword}
                    disabled={loading}
                    startIcon={loading ? <CircularProgress size={16} /> : <SecurityIcon />}
                >
                    Change Password
                </Button>
            </Box>

            {/* Logout Section */}
            <Box sx={{ mt: 6, pt: 4, borderTop: 1, borderColor: 'divider' }}>
                <Typography variant="h6" gutterBottom>
                    Session Management
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Sign out of your account on this device. You'll need to log in again to access your account.
                </Typography>
                <Button
                    variant="outlined"
                    color="error"
                    onClick={onLogout}
                    startIcon={<LogoutIcon />}
                >
                    Logout
                </Button>
            </Box>
        </Box>
    );
};

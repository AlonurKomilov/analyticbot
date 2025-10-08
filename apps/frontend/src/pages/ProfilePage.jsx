/**
 * 👤 User Profile Page
 *
 * Comprehensive user profile management with account settings,
 * password change, and profile information editing.
 */

import React, { useState } from 'react';
import {
    Box,
    Container,
    Paper,
    Typography,
    TextField,
    Button,
    Avatar,
    Chip,
    Grid,
    Divider,
    Alert,
    CircularProgress,
    Card,
    CardContent,
    CardActions,
    IconButton,
    Tooltip,
    Tab,
    Tabs
} from '@mui/material';
import {
    Person as PersonIcon,
    Edit as EditIcon,
    Save as SaveIcon,
    Cancel as CancelIcon,
    Lock as LockIcon,
    Email as EmailIcon,
    Badge as BadgeIcon,
    Security as SecurityIcon,
    Notifications as NotificationsIcon,
    Delete as DeleteIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { DESIGN_TOKENS } from '../theme/designTokens';

const ProfilePage = () => {
    const { user, updateUser } = useAuth();
    const [activeTab, setActiveTab] = useState(0);
    const [editMode, setEditMode] = useState(false);
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState('');
    const [error, setError] = useState('');

    // Profile form data
    const [profileData, setProfileData] = useState({
        username: user?.username || '',
        fullName: user?.full_name || '',
        email: user?.email || ''
    });

    // Password change data
    const [passwordData, setPasswordData] = useState({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
    });

    const [passwordErrors, setPasswordErrors] = useState({});

    // Handle tab change
    const handleTabChange = (event, newValue) => {
        setActiveTab(newValue);
        setError('');
        setSuccess('');
    };

    // Handle profile input changes
    const handleProfileChange = (field) => (event) => {
        setProfileData(prev => ({
            ...prev,
            [field]: event.target.value
        }));
    };

    // Handle password input changes
    const handlePasswordChange = (field) => (event) => {
        setPasswordData(prev => ({
            ...prev,
            [field]: event.target.value
        }));

        // Clear field-specific errors
        if (passwordErrors[field]) {
            setPasswordErrors(prev => ({
                ...prev,
                [field]: ''
            }));
        }
    };

    // Validate password form
    const validatePasswordForm = () => {
        const errors = {};

        if (!passwordData.currentPassword) {
            errors.currentPassword = 'Current password is required';
        }

        if (!passwordData.newPassword) {
            errors.newPassword = 'New password is required';
        } else if (passwordData.newPassword.length < 8) {
            errors.newPassword = 'Password must be at least 8 characters';
        }

        if (!passwordData.confirmPassword) {
            errors.confirmPassword = 'Please confirm your new password';
        } else if (passwordData.newPassword !== passwordData.confirmPassword) {
            errors.confirmPassword = 'Passwords do not match';
        }

        setPasswordErrors(errors);
        return Object.keys(errors).length === 0;
    };

    // Save profile changes
    const handleSaveProfile = async () => {
        setLoading(true);
        setError('');
        setSuccess('');

        try {
            // Simulate API call to update profile
            await new Promise(resolve => setTimeout(resolve, 1000));

            // Update user context
            updateUser({
                ...user,
                username: profileData.username,
                full_name: profileData.fullName,
                email: profileData.email
            });

            setSuccess('Profile updated successfully!');
            setEditMode(false);
        } catch (err) {
            setError('Failed to update profile. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    // Change password
    const handleChangePassword = async () => {
        if (!validatePasswordForm()) {
            return;
        }

        setLoading(true);
        setError('');
        setSuccess('');

        try {
            // Simulate API call to change password
            await new Promise(resolve => setTimeout(resolve, 1000));

            setSuccess('Password changed successfully!');
            setPasswordData({
                currentPassword: '',
                newPassword: '',
                confirmPassword: ''
            });
        } catch (err) {
            setError('Failed to change password. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    // Cancel edit mode
    const handleCancelEdit = () => {
        setProfileData({
            username: user?.username || '',
            fullName: user?.full_name || '',
            email: user?.email || ''
        });
        setEditMode(false);
        setError('');
        setSuccess('');
    };

    const TabPanel = ({ children, value, index, ...other }) => (
        <div
            role="tabpanel"
            hidden={value !== index}
            id={`profile-tabpanel-${index}`}
            aria-labelledby={`profile-tab-${index}`}
            {...other}
        >
            {value === index && (
                <Box sx={{ pt: 3 }}>
                    {children}
                </Box>
            )}
        </div>
    );

    return (
        <Container maxWidth="md" sx={{ py: 4 }}>
            {/* Header */}
            <Box sx={{ mb: 4, textAlign: 'center' }}>
                <Avatar
                    sx={{
                        width: 80,
                        height: 80,
                        mx: 'auto',
                        mb: 2,
                        bgcolor: 'primary.main',
                        fontSize: '2rem'
                    }}
                >
                    {user?.username ? user.username.charAt(0).toUpperCase() : <PersonIcon />}
                </Avatar>
                <Typography variant="h4" gutterBottom>
                    {user?.full_name || user?.username || 'User Profile'}
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1, mb: 2 }}>
                    <Chip
                        label={user?.role || 'User'}
                        color="primary"
                        variant="outlined"
                        icon={<BadgeIcon />}
                    />
                    <Chip
                        label={user?.status || 'Active'}
                        color="success"
                        variant="outlined"
                    />
                </Box>
            </Box>

            {/* Status Messages */}
            {success && (
                <Alert severity="success" sx={{ mb: 3 }}>
                    {success}
                </Alert>
            )}
            {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                    {error}
                </Alert>
            )}

            {/* Main Content */}
            <Paper sx={{ width: '100%' }}>
                {/* Tabs */}
                <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                    <Tabs value={activeTab} onChange={handleTabChange} aria-label="profile tabs">
                        <Tab label="Profile Information" icon={<PersonIcon />} />
                        <Tab label="Security" icon={<SecurityIcon />} />
                        <Tab label="Preferences" icon={<NotificationsIcon />} />
                    </Tabs>
                </Box>

                {/* Profile Information Tab */}
                <TabPanel value={activeTab} index={0}>
                    <Box sx={{ p: 3 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'between', alignItems: 'center', mb: 3 }}>
                            <Typography variant="h6">
                                Profile Information
                            </Typography>
                            {!editMode ? (
                                <Button
                                    startIcon={<EditIcon />}
                                    onClick={() => setEditMode(true)}
                                    variant="outlined"
                                >
                                    Edit Profile
                                </Button>
                            ) : (
                                <Box sx={{ display: 'flex', gap: 1 }}>
                                    <Button
                                        startIcon={<SaveIcon />}
                                        onClick={handleSaveProfile}
                                        variant="contained"
                                        disabled={loading}
                                    >
                                        {loading ? <CircularProgress size={16} /> : 'Save'}
                                    </Button>
                                    <Button
                                        startIcon={<CancelIcon />}
                                        onClick={handleCancelEdit}
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
                                    onChange={handleProfileChange('username')}
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
                                    onChange={handleProfileChange('fullName')}
                                    disabled={!editMode || loading}
                                />
                            </Grid>
                            <Grid item xs={12}>
                                <TextField
                                    fullWidth
                                    label="Email Address"
                                    value={profileData.email}
                                    onChange={handleProfileChange('email')}
                                    disabled={!editMode || loading}
                                    type="email"
                                    InputProps={{
                                        startAdornment: <EmailIcon sx={{ mr: 1, color: 'action.active' }} />
                                    }}
                                />
                            </Grid>
                        </Grid>
                    </Box>
                </TabPanel>

                {/* Security Tab */}
                <TabPanel value={activeTab} index={1}>
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
                                    onChange={handlePasswordChange('currentPassword')}
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
                                    onChange={handlePasswordChange('newPassword')}
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
                                    onChange={handlePasswordChange('confirmPassword')}
                                    error={!!passwordErrors.confirmPassword}
                                    helperText={passwordErrors.confirmPassword}
                                    disabled={loading}
                                />
                            </Grid>
                        </Grid>

                        <Box sx={{ mt: 3 }}>
                            <Button
                                variant="contained"
                                onClick={handleChangePassword}
                                disabled={loading}
                                startIcon={loading ? <CircularProgress size={16} /> : <SecurityIcon />}
                            >
                                Change Password
                            </Button>
                        </Box>
                    </Box>
                </TabPanel>

                {/* Preferences Tab */}
                <TabPanel value={activeTab} index={2}>
                    <Box sx={{ p: 3 }}>
                        <Typography variant="h6" gutterBottom>
                            Account Preferences
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                            Manage your account preferences and settings.
                        </Typography>

                        {/* Placeholder for future preferences */}
                        <Alert severity="info">
                            Additional preference settings will be available in a future update.
                        </Alert>
                    </Box>
                </TabPanel>
            </Paper>
        </Container>
    );
};

export default ProfilePage;

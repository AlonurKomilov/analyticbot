/**
 * 👤 User Profile Page
 *
 * Comprehensive user profile management with account settings,
 * password change, and profile information editing.
 *
 * Refactored from 490-line monolith into modular components:
 * - types.ts: TypeScript interfaces
 * - hooks.ts: Form state management hooks
 * - ProfileHeader.tsx: Avatar and status display
 * - ProfileInformationTab.tsx: Profile editing form
 * - SecurityTab.tsx: Password change and logout
 * - LoginMethodsTab.tsx: Account linking
 * - PreferencesTab.tsx: User preferences (placeholder)
 * - TabPanel.tsx: Reusable tab panel wrapper
 */

import React, { useState } from 'react';
import {
    Box,
    Container,
    Paper,
    Alert,
    Tab,
    Tabs
} from '@mui/material';
import {
    Person as PersonIcon,
    Security as SecurityIcon,
    Notifications as NotificationsIcon,
    Link as LinkIcon
} from '@mui/icons-material';
import { useAuth } from '@/contexts/AuthContext';

// Import sub-components
import { ProfileHeader } from './ProfileHeader';
import { ProfileInformationTab } from './ProfileInformationTab';
import { SecurityTab } from './SecurityTab';
import { LoginMethodsTab } from './LoginMethodsTab';
import { PreferencesTab } from './PreferencesTab';
import { TabPanel } from './TabPanel';
import { useProfileForm, usePasswordForm } from './hooks';

const ProfilePage: React.FC = () => {
    const { user, updateUser, logout } = useAuth();
    const [activeTab, setActiveTab] = useState(0);

    // Profile form hook
    const {
        profileData,
        editMode,
        loading: profileLoading,
        success: profileSuccess,
        error: profileError,
        handleProfileChange,
        handleSaveProfile,
        handleCancelEdit,
        handleEditClick,
        clearMessages: clearProfileMessages,
        setSuccess: setProfileSuccess
    } = useProfileForm({ user, updateUser });

    // Password form hook
    const {
        passwordData,
        passwordErrors,
        loading: passwordLoading,
        success: passwordSuccess,
        error: passwordError,
        handlePasswordChange,
        handleChangePassword
    } = usePasswordForm();

    // Combine loading and message states
    const loading = profileLoading || passwordLoading;
    const success = profileSuccess || passwordSuccess;
    const error = profileError || passwordError;

    // Handle tab change
    const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
        setActiveTab(newValue);
        clearProfileMessages();
    };

    // Handle login method update success
    const handleLoginMethodSuccess = () => {
        setProfileSuccess('Login method updated successfully!');
    };

    return (
        <Container maxWidth="md" sx={{ py: 4 }}>
            {/* Header */}
            <ProfileHeader user={user} />

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
                        <Tab label="Login Methods" icon={<LinkIcon />} />
                        <Tab label="Preferences" icon={<NotificationsIcon />} />
                    </Tabs>
                </Box>

                {/* Profile Information Tab */}
                <TabPanel value={activeTab} index={0}>
                    <ProfileInformationTab
                        profileData={profileData}
                        editMode={editMode}
                        loading={loading}
                        onProfileChange={handleProfileChange}
                        onEditClick={handleEditClick}
                        onSaveProfile={handleSaveProfile}
                        onCancelEdit={handleCancelEdit}
                    />
                </TabPanel>

                {/* Security Tab */}
                <TabPanel value={activeTab} index={1}>
                    <SecurityTab
                        passwordData={passwordData}
                        passwordErrors={passwordErrors}
                        loading={loading}
                        onPasswordChange={handlePasswordChange}
                        onChangePassword={handleChangePassword}
                        onLogout={logout}
                    />
                </TabPanel>

                {/* Login Methods Tab */}
                <TabPanel value={activeTab} index={2}>
                    <LoginMethodsTab
                        user={user}
                        onSuccess={handleLoginMethodSuccess}
                    />
                </TabPanel>

                {/* Preferences Tab */}
                <TabPanel value={activeTab} index={3}>
                    <PreferencesTab />
                </TabPanel>
            </Paper>
        </Container>
    );
};

export default ProfilePage;

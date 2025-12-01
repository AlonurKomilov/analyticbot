/**
 * Profile Page Hooks
 * Custom hooks for profile page state management
 */

import { useState, useCallback } from 'react';
import { apiClient } from '@/api/client';
import type { ProfileData, PasswordData, PasswordErrors } from './types';

// Use generic type for user to match AuthContext
interface UseProfileFormProps {
    user: any;
    updateUser: (user: any) => void;
}

export const useProfileForm = ({ user, updateUser }: UseProfileFormProps) => {
    const [editMode, setEditMode] = useState(false);
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState('');
    const [error, setError] = useState('');

    const [profileData, setProfileData] = useState<ProfileData>({
        username: user?.username || '',
        fullName: user?.full_name || '',
        email: user?.email || ''
    });

    const handleProfileChange = useCallback(
        (field: keyof ProfileData) =>
            (event: React.ChangeEvent<HTMLInputElement>) => {
                setProfileData(prev => ({
                    ...prev,
                    [field]: event.target.value
                }));
            },
        []
    );

    const handleSaveProfile = useCallback(async () => {
        setLoading(true);
        setError('');
        setSuccess('');

        try {
            const response = await apiClient.put<{ message: string; user: any }>('/auth/profile', {
                username: profileData.username,
                full_name: profileData.fullName,
                email: profileData.email
            });

            if (response && response.user && user) {
                updateUser({
                    ...user,
                    username: response.user.username,
                    full_name: response.user.full_name,
                    email: response.user.email
                });
            }

            setSuccess('Profile updated successfully!');
            setEditMode(false);
        } catch (err: any) {
            setError(err.message || 'Failed to update profile. Please try again.');
        } finally {
            setLoading(false);
        }
    }, [profileData, user, updateUser]);

    const handleCancelEdit = useCallback(() => {
        setProfileData({
            username: user?.username || '',
            fullName: user?.full_name || '',
            email: user?.email || ''
        });
        setEditMode(false);
        setError('');
        setSuccess('');
    }, [user]);

    const handleEditClick = useCallback(() => {
        setEditMode(true);
    }, []);

    const clearMessages = useCallback(() => {
        setError('');
        setSuccess('');
    }, []);

    return {
        profileData,
        editMode,
        loading,
        success,
        error,
        handleProfileChange,
        handleSaveProfile,
        handleCancelEdit,
        handleEditClick,
        clearMessages,
        setSuccess
    };
};

export const usePasswordForm = () => {
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState('');
    const [error, setError] = useState('');

    const [passwordData, setPasswordData] = useState<PasswordData>({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
    });

    const [passwordErrors, setPasswordErrors] = useState<PasswordErrors>({});

    const handlePasswordChange = useCallback(
        (field: keyof PasswordData) =>
            (event: React.ChangeEvent<HTMLInputElement>) => {
                setPasswordData(prev => ({
                    ...prev,
                    [field]: event.target.value
                }));

                if (passwordErrors[field]) {
                    setPasswordErrors(prev => ({
                        ...prev,
                        [field]: ''
                    }));
                }
            },
        [passwordErrors]
    );

    const validatePasswordForm = useCallback((): boolean => {
        const errors: PasswordErrors = {};

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
    }, [passwordData]);

    const handleChangePassword = useCallback(async () => {
        if (!validatePasswordForm()) {
            return;
        }

        setLoading(true);
        setError('');
        setSuccess('');

        try {
            // TODO: Replace with real API call
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
    }, [validatePasswordForm]);

    return {
        passwordData,
        passwordErrors,
        loading,
        success,
        error,
        handlePasswordChange,
        handleChangePassword
    };
};

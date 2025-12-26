/**
 * Register Form Fields Component
 * Form input fields for registration with real-time availability checks
 */

import React from 'react';
import { useTranslation } from 'react-i18next';
import {
    TextField,
    InputAdornment,
    IconButton,
    Typography,
    Box,
    CircularProgress,
    Grid
} from '@mui/material';
import {
    Email as EmailIcon,
    Lock as LockIcon,
    Person as PersonIcon,
    Visibility,
    VisibilityOff,
    CheckCircle as CheckIcon,
    Cancel as CancelIcon
} from '@mui/icons-material';
import type { FormData, FormErrors, PasswordStrength, AvailabilityStatus } from './types';
import { PasswordStrengthIndicator } from './PasswordStrengthIndicator';

interface RegisterFormFieldsProps {
    formData: FormData;
    errors: FormErrors;
    isSubmitting: boolean;
    showPassword: boolean;
    showConfirmPassword: boolean;
    showPasswordRequirements: boolean;
    passwordStrength: PasswordStrength;
    usernameStatus: AvailabilityStatus;
    emailStatus: AvailabilityStatus;
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    onTogglePassword: () => void;
    onToggleConfirmPassword: () => void;
    onTogglePasswordRequirements: () => void;
}

// Availability indicator component
const AvailabilityIndicator: React.FC<{ status: AvailabilityStatus }> = ({ status }) => {
    if (status.checking) {
        return (
            <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                <CircularProgress size={14} sx={{ mr: 1 }} />
                <Typography variant="caption" color="text.secondary">
                    Checking...
                </Typography>
            </Box>
        );
    }

    if (status.available === true) {
        return (
            <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                <CheckIcon sx={{ fontSize: 16, color: 'success.main', mr: 0.5 }} />
                <Typography variant="caption" color="success.main">
                    {status.message}
                </Typography>
            </Box>
        );
    }

    if (status.available === false) {
        return (
            <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                <CancelIcon sx={{ fontSize: 16, color: 'error.main', mr: 0.5 }} />
                <Typography variant="caption" color="error.main">
                    {status.message}
                </Typography>
            </Box>
        );
    }

    return null;
};

export const RegisterFormFields: React.FC<RegisterFormFieldsProps> = ({
    formData,
    errors,
    isSubmitting,
    showPassword,
    showConfirmPassword,
    showPasswordRequirements,
    passwordStrength,
    usernameStatus,
    emailStatus,
    onChange,
    onTogglePassword,
    onToggleConfirmPassword,
    onTogglePasswordRequirements
}) => {
    const { t } = useTranslation('auth');

    return (
        <>
            {/* Username Field with availability check */}
            <Box sx={{ mb: 2 }}>
                <TextField
                    fullWidth
                    name="username"
                    label={t('register.username', 'Username')}
                    placeholder="@username"
                    value={formData.username}
                    onChange={onChange}
                    error={!!errors.username || usernameStatus.available === false}
                    helperText={errors.username}
                    disabled={isSubmitting}
                    InputProps={{
                        startAdornment: (
                            <InputAdornment position="start">
                                <PersonIcon color="action" />
                            </InputAdornment>
                        ),
                        endAdornment: usernameStatus.checking ? (
                            <InputAdornment position="end">
                                <CircularProgress size={20} />
                            </InputAdornment>
                        ) : usernameStatus.available === true ? (
                            <InputAdornment position="end">
                                <CheckIcon color="success" />
                            </InputAdornment>
                        ) : usernameStatus.available === false ? (
                            <InputAdornment position="end">
                                <CancelIcon color="error" />
                            </InputAdornment>
                        ) : null
                    }}
                    autoComplete="username"
                    autoFocus
                />
                <AvailabilityIndicator status={usernameStatus} />
            </Box>

            {/* First Name and Last Name Fields */}
            <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={6}>
                    <TextField
                        fullWidth
                        name="firstName"
                        label={t('register.firstName', 'First Name')}
                        value={formData.firstName}
                        onChange={onChange}
                        error={!!errors.firstName}
                        helperText={errors.firstName}
                        disabled={isSubmitting}
                        autoComplete="given-name"
                    />
                </Grid>
                <Grid item xs={6}>
                    <TextField
                        fullWidth
                        name="lastName"
                        label={t('register.lastName', 'Last Name')}
                        value={formData.lastName}
                        onChange={onChange}
                        error={!!errors.lastName}
                        helperText={errors.lastName}
                        disabled={isSubmitting}
                        autoComplete="family-name"
                    />
                </Grid>
            </Grid>

            {/* Email Field with availability check */}
            <Box sx={{ mb: 2 }}>
                <TextField
                    fullWidth
                    name="email"
                    type="email"
                    label={t('register.email', 'Email Address')}
                    value={formData.email}
                    onChange={onChange}
                    error={!!errors.email || emailStatus.available === false}
                    helperText={errors.email}
                    disabled={isSubmitting}
                    InputProps={{
                        startAdornment: (
                            <InputAdornment position="start">
                                <EmailIcon color="action" />
                            </InputAdornment>
                        ),
                        endAdornment: emailStatus.checking ? (
                            <InputAdornment position="end">
                                <CircularProgress size={20} />
                            </InputAdornment>
                        ) : emailStatus.available === true ? (
                            <InputAdornment position="end">
                                <CheckIcon color="success" />
                            </InputAdornment>
                        ) : emailStatus.available === false ? (
                            <InputAdornment position="end">
                                <CancelIcon color="error" />
                            </InputAdornment>
                        ) : null
                    }}
                    autoComplete="email"
                />
                <AvailabilityIndicator status={emailStatus} />
            </Box>

            {/* Password Field */}
            <TextField
                fullWidth
                name="password"
                type={showPassword ? 'text' : 'password'}
                label={t('register.password', 'Password')}
                value={formData.password}
                onChange={onChange}
                error={!!errors.password}
                helperText={errors.password}
                disabled={isSubmitting}
                sx={{ mb: 1 }}
                InputProps={{
                    startAdornment: (
                        <InputAdornment position="start">
                            <LockIcon color="action" />
                        </InputAdornment>
                    ),
                    endAdornment: (
                        <InputAdornment position="end">
                            <IconButton
                                onClick={onTogglePassword}
                                edge="end"
                                disabled={isSubmitting}
                            >
                                {showPassword ? <VisibilityOff /> : <Visibility />}
                            </IconButton>
                        </InputAdornment>
                    )
                }}
                autoComplete="new-password"
            />

            {/* Password Strength Indicator */}
            <PasswordStrengthIndicator
                password={formData.password}
                passwordStrength={passwordStrength}
                showRequirements={showPasswordRequirements}
                onToggleRequirements={onTogglePasswordRequirements}
            />

            {/* Confirm Password Field */}
            <TextField
                fullWidth
                name="confirmPassword"
                type={showConfirmPassword ? 'text' : 'password'}
                label={t('register.confirmPassword', 'Confirm Password')}
                value={formData.confirmPassword}
                onChange={onChange}
                error={!!errors.confirmPassword}
                helperText={errors.confirmPassword}
                disabled={isSubmitting}
                sx={{ mb: 3 }}
                InputProps={{
                    startAdornment: (
                        <InputAdornment position="start">
                            <LockIcon color="action" />
                        </InputAdornment>
                    ),
                    endAdornment: (
                        <InputAdornment position="end">
                            <IconButton
                                onClick={onToggleConfirmPassword}
                                edge="end"
                                disabled={isSubmitting}
                            >
                                {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                            </IconButton>
                        </InputAdornment>
                    )
                }}
                autoComplete="new-password"
            />
        </>
    );
};

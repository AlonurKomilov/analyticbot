/**
 * Register Form Fields Component
 * Form input fields for registration
 */

import React from 'react';
import {
    TextField,
    InputAdornment,
    IconButton
} from '@mui/material';
import {
    Email as EmailIcon,
    Lock as LockIcon,
    Person as PersonIcon,
    Visibility,
    VisibilityOff
} from '@mui/icons-material';
import type { FormData, FormErrors, PasswordStrength } from './types';
import { PasswordStrengthIndicator } from './PasswordStrengthIndicator';

interface RegisterFormFieldsProps {
    formData: FormData;
    errors: FormErrors;
    isSubmitting: boolean;
    showPassword: boolean;
    showConfirmPassword: boolean;
    showPasswordRequirements: boolean;
    passwordStrength: PasswordStrength;
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    onTogglePassword: () => void;
    onToggleConfirmPassword: () => void;
    onTogglePasswordRequirements: () => void;
}

export const RegisterFormFields: React.FC<RegisterFormFieldsProps> = ({
    formData,
    errors,
    isSubmitting,
    showPassword,
    showConfirmPassword,
    showPasswordRequirements,
    passwordStrength,
    onChange,
    onTogglePassword,
    onToggleConfirmPassword,
    onTogglePasswordRequirements
}) => {
    return (
        <>
            {/* Username Field */}
            <TextField
                fullWidth
                name="username"
                label="Username"
                value={formData.username}
                onChange={onChange}
                error={!!errors.username}
                helperText={errors.username}
                disabled={isSubmitting}
                sx={{ mb: 2 }}
                InputProps={{
                    startAdornment: (
                        <InputAdornment position="start">
                            <PersonIcon color="action" />
                        </InputAdornment>
                    )
                }}
                autoComplete="username"
                autoFocus
            />

            {/* Full Name Field */}
            <TextField
                fullWidth
                name="fullName"
                label="Full Name"
                value={formData.fullName}
                onChange={onChange}
                error={!!errors.fullName}
                helperText={errors.fullName}
                disabled={isSubmitting}
                sx={{ mb: 2 }}
                autoComplete="name"
            />

            {/* Email Field */}
            <TextField
                fullWidth
                name="email"
                type="email"
                label="Email Address"
                value={formData.email}
                onChange={onChange}
                error={!!errors.email}
                helperText={errors.email}
                disabled={isSubmitting}
                sx={{ mb: 2 }}
                InputProps={{
                    startAdornment: (
                        <InputAdornment position="start">
                            <EmailIcon color="action" />
                        </InputAdornment>
                    )
                }}
                autoComplete="email"
            />

            {/* Password Field */}
            <TextField
                fullWidth
                name="password"
                type={showPassword ? 'text' : 'password'}
                label="Password"
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
                label="Confirm Password"
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

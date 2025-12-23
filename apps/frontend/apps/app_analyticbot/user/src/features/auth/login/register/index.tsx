/**
 * 📝 Registration Form Component
 *
 * Professional user registration form with validation, strength indicators, and error handling.
 * Integrates with AuthContext for JWT authentication and user creation.
 *
 * Refactored from 523-line monolith into modular components:
 * - types.ts: TypeScript interfaces
 * - passwordUtils.ts: Password strength calculation
 * - useRegisterForm.ts: Form state management hook
 * - PasswordStrengthIndicator.tsx: Visual password feedback
 * - RegisterFormFields.tsx: Form input fields
 */

import React from 'react';
import { useTranslation } from 'react-i18next';
import {
    Box,
    Card,
    CardContent,
    Button,
    Typography,
    Alert,
    CircularProgress,
    Link,
    Divider
} from '@mui/material';
import { PersonAdd as RegisterIcon } from '@mui/icons-material';
import { DESIGN_TOKENS } from '@/theme/designTokens';
import type { RegisterFormProps } from './types';
import { useRegisterForm } from './useRegisterForm';
import { RegisterFormFields } from './RegisterFormFields';

export const RegisterForm: React.FC<RegisterFormProps> = ({ onToggleMode = null }) => {
    const { t } = useTranslation('auth');
    const {
        formData,
        errors,
        registerError,
        isSubmitting,
        isLoading,
        showPassword,
        showConfirmPassword,
        showPasswordRequirements,
        passwordStrength,
        handleChange,
        handleSubmit,
        togglePasswordVisibility,
        toggleConfirmPasswordVisibility,
        togglePasswordRequirements
    } = useRegisterForm();

    return (
        <Box
            sx={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                minHeight: '100vh',
                backgroundColor: DESIGN_TOKENS.colors.background.secondary,
                padding: DESIGN_TOKENS.spacing.section.padding.md
            }}
        >
            <Card
                sx={{
                    width: '100%',
                    maxWidth: 500,
                    boxShadow: DESIGN_TOKENS.elevation.high,
                    borderRadius: DESIGN_TOKENS.layout.borderRadius.lg
                }}
            >
                <CardContent sx={{ p: 4 }}>
                    {/* Header */}
                    <Box sx={{ textAlign: 'center', mb: 3 }}>
                        <RegisterIcon
                            sx={{
                                fontSize: 48,
                                color: DESIGN_TOKENS.colors.primary.main,
                                mb: 1
                            }}
                        />
                        <Typography variant="h4" component="h1" gutterBottom>
                            {t('register.title')}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            {t('register.subtitle')}
                        </Typography>
                    </Box>

                    {/* Registration Error Alert */}
                    {registerError && (
                        <Alert severity="error" sx={{ mb: 2 }}>
                            {registerError}
                        </Alert>
                    )}

                    {/* Registration Form */}
                    <Box component="form" onSubmit={handleSubmit}>
                        <RegisterFormFields
                            formData={formData}
                            errors={errors}
                            isSubmitting={isSubmitting}
                            showPassword={showPassword}
                            showConfirmPassword={showConfirmPassword}
                            showPasswordRequirements={showPasswordRequirements}
                            passwordStrength={passwordStrength}
                            onChange={handleChange}
                            onTogglePassword={togglePasswordVisibility}
                            onToggleConfirmPassword={toggleConfirmPasswordVisibility}
                            onTogglePasswordRequirements={togglePasswordRequirements}
                        />

                        {/* Register Button */}
                        <Button
                            type="submit"
                            fullWidth
                            variant="contained"
                            size="large"
                            disabled={isSubmitting || isLoading}
                            sx={{
                                mb: 2,
                                height: 48,
                                fontSize: '1.1rem',
                                textTransform: 'none'
                            }}
                        >
                            {isSubmitting ? (
                                <>
                                    <CircularProgress size={20} sx={{ mr: 1 }} />
                                    {t('register.creatingAccount')}
                                </>
                            ) : (
                                t('register.createAccount')
                            )}
                        </Button>

                        {/* Login Link */}
                        {onToggleMode && (
                            <>
                                <Divider sx={{ my: 2 }}>
                                    <Typography variant="body2" color="text.secondary">
                                        {t('register.or')}
                                    </Typography>
                                </Divider>

                                <Box sx={{ textAlign: 'center' }}>
                                    <Typography variant="body2" color="text.secondary">
                                        {t('register.alreadyHaveAccount')}{' '}
                                        <Link
                                            href="#"
                                            onClick={(e) => {
                                                e.preventDefault();
                                                onToggleMode();
                                            }}
                                        >
                                            {t('register.signInHere')}
                                        </Link>
                                    </Typography>
                                </Box>
                            </>
                        )}
                    </Box>
                </CardContent>
            </Card>
        </Box>
    );
};

export default RegisterForm;

/**
 * 🔒 Login Form Component
 *
 * Professional login form with validation, loading states, and error handling.
 * Integrates with AuthContext for JWT authentication.
 */

import React, { useState } from 'react';
import {
    Box,
    Card,
    CardContent,
    TextField,
    Button,
    Typography,
    Alert,
    CircularProgress,
    InputAdornment,
    IconButton,
    Link,
    Divider
} from '@mui/material';
import {
    Email as EmailIcon,
    Lock as LockIcon,
    Visibility,
    VisibilityOff,
    Login as LoginIcon
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import { DESIGN_TOKENS } from '../../theme/designTokens';

const LoginForm = ({ onToggleMode = null, onForgotPassword = null }) => {
    const { login, isLoading } = useAuth();
    const [formData, setFormData] = useState({
        email: '',
        password: ''
    });
    const [showPassword, setShowPassword] = useState(false);
    const [errors, setErrors] = useState({});
    const [loginError, setLoginError] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Form validation
    const validateForm = () => {
        const newErrors = {};

        // Email validation
        if (!formData.email) {
            newErrors.email = 'Email is required';
        } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
            newErrors.email = 'Please enter a valid email address';
        }

        // Password validation
        if (!formData.password) {
            newErrors.password = 'Password is required';
        } else if (formData.password.length < 8) {
            newErrors.password = 'Password must be at least 8 characters';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    // Handle input changes
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));

        // Clear field error when user starts typing
        if (errors[name]) {
            setErrors(prev => ({
                ...prev,
                [name]: ''
            }));
        }

        // Clear login error
        if (loginError) {
            setLoginError('');
        }
    };

    // Handle form submission
    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        setIsSubmitting(true);
        setLoginError('');

        try {
            const result = await login(formData.email, formData.password);

            if (!result.success) {
                setLoginError(result.error || 'Login failed. Please try again.');
            }
            // Success is handled by AuthContext (redirects user)
        } catch (error) {
            setLoginError('Network error. Please check your connection and try again.');
        } finally {
            setIsSubmitting(false);
        }
    };

    const togglePasswordVisibility = () => {
        setShowPassword(!showPassword);
    };

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
                    maxWidth: 400,
                    boxShadow: DESIGN_TOKENS.elevation.high,
                    borderRadius: DESIGN_TOKENS.layout.borderRadius.lg
                }}
            >
                <CardContent sx={{ p: 4 }}>
                    {/* Header */}
                    <Box sx={{ textAlign: 'center', mb: 3 }}>
                        <LoginIcon
                            sx={{
                                fontSize: 48,
                                color: DESIGN_TOKENS.colors.primary.main,
                                mb: 1
                            }}
                        />
                        <Typography variant="h4" component="h1" gutterBottom>
                            Welcome Back
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            Sign in to your AnalyticBot account
                        </Typography>
                    </Box>

                    {/* Login Error Alert */}
                    {loginError && (
                        <Alert severity="error" sx={{ mb: 2 }}>
                            {loginError}
                        </Alert>
                    )}

                    {/* Login Form */}
                    <Box component="form" onSubmit={handleSubmit}>
                        {/* Email Field */}
                        <TextField
                            fullWidth
                            name="email"
                            type="email"
                            label="Email Address"
                            value={formData.email}
                            onChange={handleChange}
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
                            autoFocus
                        />

                        {/* Password Field */}
                        <TextField
                            fullWidth
                            name="password"
                            type={showPassword ? 'text' : 'password'}
                            label="Password"
                            value={formData.password}
                            onChange={handleChange}
                            error={!!errors.password}
                            helperText={errors.password}
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
                                            onClick={togglePasswordVisibility}
                                            edge="end"
                                            disabled={isSubmitting}
                                        >
                                            {showPassword ? <VisibilityOff /> : <Visibility />}
                                        </IconButton>
                                    </InputAdornment>
                                )
                            }}
                            autoComplete="current-password"
                        />

                        {/* Login Button */}
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
                                    Signing In...
                                </>
                            ) : (
                                'Sign In'
                            )}
                        </Button>

                        {/* Forgot Password Link */}
                        <Box sx={{ textAlign: 'center', mb: 2 }}>
                            <Link
                                href="#"
                                variant="body2"
                                onClick={(e) => {
                                    e.preventDefault();
                                    if (onForgotPassword) {
                                        onForgotPassword();
                                    } else {
                                        alert('Forgot password feature coming soon!');
                                    }
                                }}
                            >
                                Forgot your password?
                            </Link>
                        </Box>

                        {/* Divider */}
                        {onToggleMode && (
                            <>
                                <Divider sx={{ my: 2 }}>
                                    <Typography variant="body2" color="text.secondary">
                                        or
                                    </Typography>
                                </Divider>

                                {/* Register Link */}
                                <Box sx={{ textAlign: 'center' }}>
                                    <Typography variant="body2" color="text.secondary">
                                        Don't have an account?{' '}
                                        <Link
                                            href="#"
                                            onClick={(e) => {
                                                e.preventDefault();
                                                onToggleMode();
                                            }}
                                        >
                                            Sign up here
                                        </Link>
                                    </Typography>
                                </Box>
                            </>
                        )}
                    </Box>

                    {/* Demo Credentials (Development Only) */}
                    {process.env.NODE_ENV === 'development' && (
                        <Box sx={{ mt: 3, p: 2, backgroundColor: '#f5f5f5', borderRadius: 1 }}>
                            <Typography variant="caption" color="text.secondary" display="block">
                                Demo Credentials (Dev Only):
                            </Typography>
                            <Typography variant="caption" display="block">
                                Email: demo@analyticbot.com
                            </Typography>
                            <Typography variant="caption" display="block">
                                Password: demo123456
                            </Typography>
                        </Box>
                    )}
                </CardContent>
            </Card>
        </Box>
    );
};

export default LoginForm;

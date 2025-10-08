/**
 * 📝 Registration Form Component
 *
 * Professional user registration form with validation, strength indicators, and error handling.
 * Integrates with AuthContext for JWT authentication and user creation.
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
    Divider,
    LinearProgress,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Collapse
} from '@mui/material';
import {
    PersonAdd as RegisterIcon,
    Email as EmailIcon,
    Lock as LockIcon,
    Person as PersonIcon,
    Visibility,
    VisibilityOff,
    Check as CheckIcon,
    Close as CloseIcon,
    ExpandMore as ExpandMoreIcon,
    ExpandLess as ExpandLessIcon
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import { DESIGN_TOKENS } from '../../theme/designTokens';

const RegisterForm = ({ onToggleMode = null }) => {
    const { register, isLoading } = useAuth();
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        confirmPassword: '',
        username: '',
        fullName: ''
    });
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [errors, setErrors] = useState({});
    const [registerError, setRegisterError] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [showPasswordRequirements, setShowPasswordRequirements] = useState(false);

    // Password strength calculation
    const calculatePasswordStrength = (password) => {
        let score = 0;
        const requirements = {
            length: password.length >= 8,
            lowercase: /[a-z]/.test(password),
            uppercase: /[A-Z]/.test(password),
            number: /\d/.test(password),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
        };

        Object.values(requirements).forEach(met => {
            if (met) score += 20;
        });

        return { score, requirements };
    };

    const { score: passwordScore, requirements: passwordRequirements } = calculatePasswordStrength(formData.password);

    const getPasswordStrengthColor = (score) => {
        if (score < 40) return 'error';
        if (score < 80) return 'warning';
        return 'success';
    };

    const getPasswordStrengthLabel = (score) => {
        if (score < 40) return 'Weak';
        if (score < 80) return 'Good';
        return 'Strong';
    };

    // Form validation
    const validateForm = () => {
        const newErrors = {};

        // Username validation
        if (!formData.username.trim()) {
            newErrors.username = 'Username is required';
        } else if (formData.username.length < 3) {
            newErrors.username = 'Username must be at least 3 characters';
        } else if (formData.username.length > 50) {
            newErrors.username = 'Username must be less than 50 characters';
        }

        // Full name validation
        if (!formData.fullName.trim()) {
            newErrors.fullName = 'Full name is required';
        }

        // Email validation
        if (!formData.email) {
            newErrors.email = 'Email is required';
        } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
            newErrors.email = 'Please enter a valid email address';
        }

        // Password validation
        if (!formData.password) {
            newErrors.password = 'Password is required';
        } else if (passwordScore < 60) {
            newErrors.password = 'Password is too weak. Please follow the requirements below.';
        }

        // Confirm password validation
        if (!formData.confirmPassword) {
            newErrors.confirmPassword = 'Please confirm your password';
        } else if (formData.password !== formData.confirmPassword) {
            newErrors.confirmPassword = 'Passwords do not match';
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

        // Clear register error
        if (registerError) {
            setRegisterError('');
        }

        // Show password requirements when user starts typing password
        if (name === 'password' && value && !showPasswordRequirements) {
            setShowPasswordRequirements(true);
        }
    };

    // Handle form submission
    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        setIsSubmitting(true);
        setRegisterError('');

        try {
            const payload = {
                email: formData.email,
                password: formData.password,
                username: formData.username,
                full_name: formData.fullName
            };
            console.log('🚀 Registration payload:', payload);

            const result = await register(payload);

            if (!result.success) {
                setRegisterError(result.error || 'Registration failed. Please try again.');
            }
            // Success is handled by AuthContext (redirects user)
        } catch (error) {
            setRegisterError('Network error. Please check your connection and try again.');
        } finally {
            setIsSubmitting(false);
        }
    };

    const togglePasswordVisibility = () => {
        setShowPassword(!showPassword);
    };

    const toggleConfirmPasswordVisibility = () => {
        setShowConfirmPassword(!showConfirmPassword);
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
                            Create Account
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            Join AnalyticBot to start analyzing your social media
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
                        {/* Username Field */}
                        <TextField
                            fullWidth
                            name="username"
                            label="Username"
                            value={formData.username}
                            onChange={handleChange}
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
                            onChange={handleChange}
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
                                            onClick={togglePasswordVisibility}
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
                        {formData.password && (
                            <Box sx={{ mb: 2 }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                    <Typography variant="caption" sx={{ mr: 1 }}>
                                        Password strength:
                                    </Typography>
                                    <Typography variant="caption" color={`${getPasswordStrengthColor(passwordScore)}.main`}>
                                        {getPasswordStrengthLabel(passwordScore)}
                                    </Typography>
                                </Box>
                                <LinearProgress
                                    variant="determinate"
                                    value={passwordScore}
                                    color={getPasswordStrengthColor(passwordScore)}
                                    sx={{ height: 4, borderRadius: 2 }}
                                />

                                {/* Password Requirements */}
                                <Box sx={{ mt: 1 }}>
                                    <Button
                                        size="small"
                                        startIcon={showPasswordRequirements ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                                        onClick={() => setShowPasswordRequirements(!showPasswordRequirements)}
                                        sx={{ textTransform: 'none', fontSize: '0.75rem' }}
                                    >
                                        Password Requirements
                                    </Button>
                                    <Collapse in={showPasswordRequirements}>
                                        <List dense sx={{ py: 0 }}>
                                            {Object.entries({
                                                length: 'At least 8 characters',
                                                lowercase: 'Lowercase letter (a-z)',
                                                uppercase: 'Uppercase letter (A-Z)',
                                                number: 'Number (0-9)',
                                                special: 'Special character (!@#$%^&*)'
                                            }).map(([key, text]) => (
                                                <ListItem key={key} sx={{ py: 0, px: 1 }}>
                                                    <ListItemIcon sx={{ minWidth: 20 }}>
                                                        {passwordRequirements[key] ? (
                                                            <CheckIcon sx={{ fontSize: 16, color: 'success.main' }} />
                                                        ) : (
                                                            <CloseIcon sx={{ fontSize: 16, color: 'error.main' }} />
                                                        )}
                                                    </ListItemIcon>
                                                    <ListItemText
                                                        primary={text}
                                                        primaryTypographyProps={{
                                                            variant: 'caption',
                                                            color: passwordRequirements[key] ? 'success.main' : 'text.secondary'
                                                        }}
                                                    />
                                                </ListItem>
                                            ))}
                                        </List>
                                    </Collapse>
                                </Box>
                            </Box>
                        )}

                        {/* Confirm Password Field */}
                        <TextField
                            fullWidth
                            name="confirmPassword"
                            type={showConfirmPassword ? 'text' : 'password'}
                            label="Confirm Password"
                            value={formData.confirmPassword}
                            onChange={handleChange}
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
                                            onClick={toggleConfirmPasswordVisibility}
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
                                    Creating Account...
                                </>
                            ) : (
                                'Create Account'
                            )}
                        </Button>

                        {/* Login Link */}
                        {onToggleMode && (
                            <>
                                <Divider sx={{ my: 2 }}>
                                    <Typography variant="body2" color="text.secondary">
                                        or
                                    </Typography>
                                </Divider>

                                <Box sx={{ textAlign: 'center' }}>
                                    <Typography variant="body2" color="text.secondary">
                                        Already have an account?{' '}
                                        <Link
                                            href="#"
                                            onClick={(e) => {
                                                e.preventDefault();
                                                onToggleMode();
                                            }}
                                        >
                                            Sign in here
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

/**
 * 🔗 Account Linking Component
 *
 * Allows users to link/unlink authentication methods:
 * - Link Telegram account to email/password users
 * - Add email/password to Telegram-only users
 */

import React, { useState } from 'react';
import {
    Box,
    Paper,
    Typography,
    Button,
    TextField,
    Alert,
    CircularProgress,
    Divider,
    Chip
} from '@mui/material';
import {
    Telegram as TelegramIcon,
    Email as EmailIcon,
    Lock as LockIcon,
    CheckCircle as CheckCircleIcon,
    Link as LinkIcon
} from '@mui/icons-material';
import { apiClient } from '@/api/client';

interface AccountLinkingProps {
    user: any;
    onUpdate: () => void;
}

export const AccountLinking: React.FC<AccountLinkingProps> = ({ user, onUpdate }) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    // Email/Password form for Telegram users
    const [emailPassword, setEmailPassword] = useState({
        email: '',
        password: '',
        confirmPassword: ''
    });

    // Check login methods using API-provided fields
    const hasTelegram = user?.telegram_id || user?.telegram_username;
    // Use has_password from API (not hashed_password which is never sent to frontend)
    const hasEmailPassword = user?.has_password && user?.email && !user?.email?.includes('@telegram.local');
    const isTelegramOnly = hasTelegram && !hasEmailPassword;
    const isEmailOnly = !hasTelegram && hasEmailPassword;

    // Handle Telegram linking (for email users)
    const handleLinkTelegram = () => {
        // This will be handled by TelegramLoginButton component in linking mode
        setError('Please use the Telegram button below to link your account');
    };

    // Handle email/password addition (for Telegram users)
    const handleAddEmailPassword = async () => {
        setError('');
        setSuccess('');

        // Validation
        if (!emailPassword.email || !emailPassword.password || !emailPassword.confirmPassword) {
            setError('All fields are required');
            return;
        }

        if (emailPassword.password !== emailPassword.confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        if (emailPassword.password.length < 8) {
            setError('Password must be at least 8 characters');
            return;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(emailPassword.email)) {
            setError('Please enter a valid email address');
            return;
        }

        setLoading(true);

        try {
            await apiClient.put('/auth/profile', {
                email: emailPassword.email,
                password: emailPassword.password
            });

            setSuccess('Email and password added successfully! You can now login with either method.');
            setEmailPassword({ email: '', password: '', confirmPassword: '' });
            onUpdate();
        } catch (err: any) {
            setError(err.message || 'Failed to add email/password');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Box>
            {/* Current Login Methods */}
            <Paper sx={{ p: 3, mb: 3 }}>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CheckCircleIcon color="primary" />
                    Your Login Methods
                </Typography>
                <Divider sx={{ my: 2 }} />

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    {/* Email/Password Status */}
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <EmailIcon color={hasEmailPassword ? 'success' : 'disabled'} />
                            <Typography>
                                Email/Password Login
                            </Typography>
                        </Box>
                        {hasEmailPassword ? (
                            <Chip
                                label={`✓ Active: ${user?.email}`}
                                color="success"
                                size="small"
                            />
                        ) : (
                            <Chip
                                label="Not Set"
                                color="default"
                                size="small"
                            />
                        )}
                    </Box>

                    {/* Telegram Status */}
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <TelegramIcon color={hasTelegram ? 'success' : 'disabled'} />
                            <Typography>
                                Telegram Login
                            </Typography>
                        </Box>
                        {hasTelegram ? (
                            <Chip
                                label={`✓ Active: @${user?.telegram_username || 'linked'}`}
                                color="success"
                                size="small"
                            />
                        ) : (
                            <Chip
                                label="Not Linked"
                                color="default"
                                size="small"
                            />
                        )}
                    </Box>
                </Box>

                {(hasEmailPassword && hasTelegram) && (
                    <Alert severity="success" sx={{ mt: 2 }}>
                        🎉 You can use either method to sign in to your account!
                    </Alert>
                )}
            </Paper>

            {/* Add Email/Password (for Telegram users) */}
            {isTelegramOnly && (
                <Paper sx={{ p: 3, mb: 3 }}>
                    <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <EmailIcon color="primary" />
                        Add Email & Password Login
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        Enable login without Telegram. You'll be able to use either method.
                    </Typography>
                    <Divider sx={{ my: 2 }} />

                    {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
                    {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                        <TextField
                            fullWidth
                            label="Email Address"
                            type="email"
                            value={emailPassword.email}
                            onChange={(e) => setEmailPassword({ ...emailPassword, email: e.target.value })}
                            disabled={loading}
                            InputProps={{
                                startAdornment: <EmailIcon sx={{ mr: 1, color: 'action.active' }} />
                            }}
                        />
                        <TextField
                            fullWidth
                            label="Password"
                            type="password"
                            value={emailPassword.password}
                            onChange={(e) => setEmailPassword({ ...emailPassword, password: e.target.value })}
                            disabled={loading}
                            helperText="Minimum 8 characters"
                            InputProps={{
                                startAdornment: <LockIcon sx={{ mr: 1, color: 'action.active' }} />
                            }}
                        />
                        <TextField
                            fullWidth
                            label="Confirm Password"
                            type="password"
                            value={emailPassword.confirmPassword}
                            onChange={(e) => setEmailPassword({ ...emailPassword, confirmPassword: e.target.value })}
                            disabled={loading}
                            InputProps={{
                                startAdornment: <LockIcon sx={{ mr: 1, color: 'action.active' }} />
                            }}
                        />
                        <Button
                            fullWidth
                            variant="contained"
                            onClick={handleAddEmailPassword}
                            disabled={loading}
                            startIcon={loading ? <CircularProgress size={20} /> : <EmailIcon />}
                        >
                            {loading ? 'Adding...' : 'Add Email/Password Login'}
                        </Button>
                    </Box>
                </Paper>
            )}

            {/* Link Telegram Account (for email users) */}
            {isEmailOnly && (
                <Paper sx={{ p: 3 }}>
                    <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <TelegramIcon color="primary" />
                        Link Telegram Account
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        Enable faster login with Telegram. You'll be able to use either method.
                    </Typography>
                    <Divider sx={{ my: 2 }} />

                    <Alert severity="info" sx={{ mb: 2 }}>
                        Linking your Telegram account will allow you to sign in instantly without entering your password.
                    </Alert>

                    {/* This will be replaced with actual TelegramLoginButton in linking mode */}
                    <Button
                        fullWidth
                        variant="outlined"
                        startIcon={<LinkIcon />}
                        onClick={handleLinkTelegram}
                        sx={{
                            borderColor: '#0088cc',
                            color: '#0088cc',
                            '&:hover': {
                                backgroundColor: 'rgba(0, 136, 204, 0.08)',
                                borderColor: '#0088cc'
                            }
                        }}
                    >
                        Link Telegram Account
                    </Button>
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block', textAlign: 'center' }}>
                        You'll be redirected to Telegram to authorize the connection
                    </Typography>
                </Paper>
            )}
        </Box>
    );
};

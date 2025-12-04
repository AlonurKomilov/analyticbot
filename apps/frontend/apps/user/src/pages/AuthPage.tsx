/**
 * 🔐 Authentication Page
 *
 * Standalone authentication page that can be accessed via routes.
 * Handles both login and registration with URL-based state management.
 * Includes automatic Telegram Web App authentication.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, useSearchParams } from 'react-router-dom';
import { Box, Container, CircularProgress, Typography } from '@mui/material';
import { LoginForm, RegisterForm, ForgotPasswordForm } from '@features/auth';
import { useAuth } from '@/contexts/AuthContext';
import { DESIGN_TOKENS } from '@/theme/designTokens';
import { isTelegramWebApp, autoLoginFromTelegram } from '@/utils/telegramAuth';

type AuthMode = 'login' | 'register' | 'forgot-password';

const AuthPage: React.FC = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const [searchParams, setSearchParams] = useSearchParams();
    const { isAuthenticated } = useAuth();
    const [isTWALoading, setIsTWALoading] = useState(false);

    // Get mode from URL params, default to 'login'
    const mode = searchParams.get('mode') || 'login';
    const [authMode, setAuthMode] = useState<AuthMode>(mode as AuthMode);

    // Attempt TWA auto-login when the page loads
    useEffect(() => {
        const attemptTWALogin = async () => {
            // Only attempt if in Telegram WebApp and not already authenticated
            if (isTelegramWebApp() && !isAuthenticated) {
                console.log('🔐 AuthPage: Attempting TWA auto-login');
                setIsTWALoading(true);

                try {
                    const success = await autoLoginFromTelegram();
                    if (success) {
                        console.log('✅ AuthPage: TWA auto-login successful');
                        // The auth state should update via event,
                        // but let's also force a page reload to ensure proper state
                        window.location.href = '/';
                    } else {
                        console.log('⚠️ AuthPage: TWA auto-login failed, showing manual login');
                    }
                } catch (error) {
                    console.error('❌ AuthPage: TWA auto-login error:', error);
                } finally {
                    setIsTWALoading(false);
                }
            }
        };

        attemptTWALogin();
    }, []); // Only run once on mount

    // Redirect authenticated users to dashboard
    useEffect(() => {
        if (isAuthenticated) {
            const from = (location.state as any)?.from?.pathname || '/';
            navigate(from, { replace: true });
        }
    }, [isAuthenticated, navigate, location.state]);

    // Update URL when mode changes
    useEffect(() => {
        setSearchParams({ mode: authMode });
    }, [authMode, setSearchParams]);

    // Handle mode toggle
    const toggleAuthMode = (): void => {
        const newMode: AuthMode = authMode === 'login' ? 'register' : 'login';
        setAuthMode(newMode);
    };

    // Handle forgot password
    const handleForgotPassword = (): void => {
        setAuthMode('forgot-password');
    };

    // Handle back to login
    const handleBackToLogin = (): void => {
        setAuthMode('login');
    };

    return (
        <Box
            sx={{
                minHeight: '100vh',
                backgroundColor: DESIGN_TOKENS.colors.background.secondary,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
            }}
        >
            <Container maxWidth="sm">
                {isTWALoading ? (
                    <Box
                        sx={{
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            gap: 2,
                            py: 4
                        }}
                    >
                        <CircularProgress size={40} />
                        <Typography variant="body1" color="text.secondary">
                            Authenticating via Telegram...
                        </Typography>
                    </Box>
                ) : authMode === 'login' ? (
                    <LoginForm
                        onToggleMode={toggleAuthMode as any}
                        onForgotPassword={handleForgotPassword as any}
                    />
                ) : authMode === 'register' ? (
                    <RegisterForm onToggleMode={toggleAuthMode as any} />
                ) : authMode === 'forgot-password' ? (
                    <ForgotPasswordForm onBackToLogin={handleBackToLogin as any} />
                ) : (
                    <LoginForm
                        onToggleMode={toggleAuthMode as any}
                        onForgotPassword={handleForgotPassword as any}
                    />
                )}
            </Container>
        </Box>
    );
};

export default AuthPage;

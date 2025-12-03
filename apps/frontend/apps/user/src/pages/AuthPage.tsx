/**
 * 🔐 Authentication Page
 *
 * Standalone authentication page that can be accessed via routes.
 * Handles both login and registration with URL-based state management.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, useSearchParams } from 'react-router-dom';
import { Box, Container } from '@mui/material';
import { LoginForm, RegisterForm, ForgotPasswordForm } from '@features/auth';
import { useAuth } from '@/contexts/AuthContext';
import { DESIGN_TOKENS } from '@/theme/designTokens';

type AuthMode = 'login' | 'register' | 'forgot-password';

const AuthPage: React.FC = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const [searchParams, setSearchParams] = useSearchParams();
    const { isAuthenticated } = useAuth();

    // Get mode from URL params, default to 'login'
    const mode = searchParams.get('mode') || 'login';
    const [authMode, setAuthMode] = useState<AuthMode>(mode as AuthMode);

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
                {authMode === 'login' ? (
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

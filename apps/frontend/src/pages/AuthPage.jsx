/**
 * 🔐 Authentication Page
 *
 * Standalone authentication page that can be accessed via routes.
 * Handles both login and registration with URL-based state management.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, useSearchParams } from 'react-router-dom';
import { Box, Container } from '@mui/material';
import { LoginForm, RegisterForm } from '../components/auth';
import ForgotPasswordForm from '../components/auth/ForgotPasswordForm';
import { useAuth } from '../contexts/AuthContext';
import { DESIGN_TOKENS } from '../theme/designTokens';

const AuthPage = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const [searchParams, setSearchParams] = useSearchParams();
    const { isAuthenticated } = useAuth();

    // Get mode from URL params, default to 'login'
    const mode = searchParams.get('mode') || 'login';
    const [authMode, setAuthMode] = useState(mode);

    // Redirect authenticated users to dashboard
    useEffect(() => {
        if (isAuthenticated) {
            const from = location.state?.from?.pathname || '/';
            navigate(from, { replace: true });
        }
    }, [isAuthenticated, navigate, location.state]);

    // Update URL when mode changes
    useEffect(() => {
        setSearchParams({ mode: authMode });
    }, [authMode, setSearchParams]);

    // Handle mode toggle
    const toggleAuthMode = () => {
        const newMode = authMode === 'login' ? 'register' : 'login';
        setAuthMode(newMode);
    };

    // Handle forgot password
    const handleForgotPassword = () => {
        setAuthMode('forgot-password');
    };

    // Handle back to login
    const handleBackToLogin = () => {
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
                        onToggleMode={toggleAuthMode}
                        onForgotPassword={handleForgotPassword}
                    />
                ) : authMode === 'register' ? (
                    <RegisterForm onToggleMode={toggleAuthMode} />
                ) : authMode === 'forgot-password' ? (
                    <ForgotPasswordForm onBackToLogin={handleBackToLogin} />
                ) : (
                    <LoginForm
                        onToggleMode={toggleAuthMode}
                        onForgotPassword={handleForgotPassword}
                    />
                )}
            </Container>
        </Box>
    );
};

export default AuthPage;

/**
 * 🔐 Authentication Wrapper
 * 
 * Wraps the main application with authentication logic.
 * Shows login/register forms for unauthenticated users, main app for authenticated users.
 */

import React, { useState } from 'react';
import { Box, Container, Typography } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import { LoginForm, RegisterForm } from '../components/auth';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { DESIGN_TOKENS } from '../theme/designTokens';

const AuthenticationWrapper = ({ children }) => {
    const { user, isAuthenticated, isLoading } = useAuth();
    const [authMode, setAuthMode] = useState('login'); // 'login' or 'register'

    // Show loading spinner while checking authentication
    if (isLoading) {
        return (
            <Box
                sx={{
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    minHeight: '100vh',
                    flexDirection: 'column',
                    gap: 2
                }}
            >
                <LoadingSpinner size={40} />
                <Typography variant="body2" color="text.secondary">
                    Checking authentication...
                </Typography>
            </Box>
        );
    }

    // Show auth forms if not authenticated
    if (!isAuthenticated) {
        const toggleAuthMode = () => {
            setAuthMode(prev => prev === 'login' ? 'register' : 'login');
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
                        <LoginForm onToggleMode={toggleAuthMode} />
                    ) : (
                        <RegisterForm onToggleMode={toggleAuthMode} />
                    )}
                </Container>
            </Box>
        );
    }

    // Show authenticated app
    return children;
};

export default AuthenticationWrapper;
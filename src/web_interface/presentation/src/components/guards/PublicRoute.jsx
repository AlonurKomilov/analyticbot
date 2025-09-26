/**
 * 🚪 Public Route Component
 * 
 * Route guard for public routes (login, register) that redirects authenticated users
 * to the main application to prevent accessing auth pages when already logged in.
 */

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import LoadingSpinner from '../common/LoadingSpinner';
import { Box, Typography } from '@mui/material';

const PublicRoute = ({ 
    children, 
    redirectTo = '/',
    restricted = true // If true, redirect authenticated users away
}) => {
    const { isAuthenticated, isLoading } = useAuth();
    const location = useLocation();

    // Show loading while checking authentication
    if (isLoading) {
        return (
            <Box
                sx={{
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    minHeight: '50vh',
                    flexDirection: 'column',
                    gap: 2
                }}
            >
                <LoadingSpinner size={32} />
                <Typography variant="body2" color="text.secondary">
                    Loading...
                </Typography>
            </Box>
        );
    }

    // If route is restricted and user is authenticated, redirect to main app
    if (restricted && isAuthenticated) {
        // Redirect to intended destination or default
        const from = location.state?.from?.pathname || redirectTo;
        return <Navigate to={from} replace />;
    }

    // Render public content
    return children;
};

export default PublicRoute;
/**
 * 🛡️ Protected Route Component
 * 
 * Route guard that ensures only authenticated users can access protected routes.
 * Provides seamless redirects and loading states.
 */

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { Box, Typography } from '@mui/material';
import { useAuth } from '../../contexts/AuthContext';
import LoadingSpinner from '../common/LoadingSpinner';
import ProtectedLayout from '../layout/ProtectedLayout';

const ProtectedRoute = ({ 
    children, 
    redirectTo = '/login',
    requiredRole = null,
    fallbackComponent = null 
}) => {
    const { isAuthenticated, isLoading, user } = useAuth();
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
                    Verifying access...
                </Typography>
            </Box>
        );
    }

    // Redirect to login if not authenticated
    if (!isAuthenticated) {
        return <Navigate 
            to="/auth" 
            state={{ from: location }} 
            replace 
        />;
    }

    // Check role-based access if required
    if (requiredRole && user?.role !== requiredRole) {
        if (fallbackComponent) {
            return fallbackComponent;
        }
        
        return (
            <Box
                sx={{
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',  
                    minHeight: '50vh',
                    flexDirection: 'column',
                    gap: 2,
                    textAlign: 'center'
                }}
            >
                <Typography variant="h5" color="error">
                    Access Denied
                </Typography>
                <Typography variant="body1" color="text.secondary">
                    You don't have permission to access this page.
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    Required role: {requiredRole} | Your role: {user?.role || 'None'}
                </Typography>
            </Box>
        );
    }

    // Render protected content with layout
    return (
        <ProtectedLayout>
            {children}
        </ProtectedLayout>
    );
};

export default ProtectedRoute;
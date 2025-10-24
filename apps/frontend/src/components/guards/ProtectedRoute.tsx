/**
 * ProtectedRoute Component
 *
 * Route guard that checks authentication status and optional role requirements.
 * Redirects to login if not authenticated, shows fallback if role check fails.
 * 
 * Role checking uses hierarchy: higher roles (e.g., admin) can access 
 * routes requiring lower roles (e.g., moderator).
 */

import React, { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { hasRole, RoleType } from '../auth/RoleGuard'; // Import hierarchy checking function and type
import ProtectedLayout from '../layout/ProtectedLayout';
import LoadingSpinner from '../common/LoadingSpinner';

interface ProtectedRouteProps {
    children: ReactNode;
    redirectTo?: string;
    requiredRole?: RoleType; // Use RoleType instead of string
    fallbackComponent?: ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
    children,
    redirectTo = '/login',
    requiredRole,
    fallbackComponent
}) => {
    const { isAuthenticated, user, isLoading } = useAuth();
    const location = useLocation();

    // Show loading spinner while checking authentication
    if (isLoading) {
        return <LoadingSpinner />;
    }

    // Redirect to login if not authenticated
    if (!isAuthenticated) {
        return (
            <Navigate
                to={redirectTo}
                state={{ from: location }}
                replace
            />
        );
    }

    // Check role if required (uses hierarchy: higher roles pass lower role checks)
    if (requiredRole && !hasRole((user as any)?.role, requiredRole)) {
        // Show fallback component or redirect
        if (fallbackComponent) {
            return <>{fallbackComponent}</>;
        }

        // Default: redirect to dashboard
        return (
            <Navigate
                to="/dashboard"
                state={{
                    from: location,
                    error: 'Insufficient permissions'
                }}
                replace
            />
        );
    }

    // Wrap authenticated content in ProtectedLayout
    return (
        <ProtectedLayout>
            {children}
        </ProtectedLayout>
    );
};

export default ProtectedRoute;

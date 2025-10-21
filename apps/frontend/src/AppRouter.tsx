import React, { Suspense, useEffect, ReactNode } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Box } from '@mui/material';
import { ProtectedRoute, PublicRoute } from './components/guards';

// Import optimized lazy loading system
import {
    PageComponents,
    AdminComponents,
    ServiceComponents,
    UtilityComponents,
    preloadByRoute,
    initializePerformanceOptimizations
} from './utils/lazyLoading';

// Import navigation system from domain structure
import { NavigationProvider } from './components/common/NavigationProvider';
import { PageLoader } from './components/common/PageLoader';

const {
    DashboardPage,
    CreatePostPage,
    AnalyticsPage,
    AuthPage,
    ProfilePage,
    AdminDashboard,
    ResetPasswordForm
} = PageComponents;

const {
    SuperAdminDashboard
} = AdminComponents;

const {
    ServicesLayout,
    ContentOptimizerService,
    PredictiveAnalyticsService,
    ChurnPredictorService,
    SecurityMonitoringService
} = ServiceComponents;

const {
    DataTablesShowcase,
    SettingsPage,
    HelpPage,
    ServicesOverview
} = UtilityComponents;

interface OptimizedSuspenseProps {
    children: ReactNode;
    fallback?: ReactNode;
    skeletonType?: 'dashboard' | 'form' | 'list' | 'content';
}

/**
 * Performance-optimized loading component with skeleton UI
 */
const OptimizedSuspense: React.FC<OptimizedSuspenseProps> = ({
    children,
    fallback,
    skeletonType = 'dashboard'
}) => {
    return (
        <Suspense
            fallback={
                fallback || <PageLoader skeleton skeletonType={skeletonType} />
            }
        >
            {children}
        </Suspense>
    );
};

/**
 * Route-aware preloading component
 */
const RoutePreloader: React.FC = () => {
    const location = useLocation();

    useEffect(() => {
        // Preload components based on current route
        preloadByRoute(location.pathname);
    }, [location.pathname]);

    return null;
};

/**
 * Professional App Router with Performance Optimizations
 * Implements multi-page architecture with enterprise-grade navigation and smart preloading
 */
const AppRouter: React.FC = () => {
    useEffect(() => {
        // Initialize performance optimizations on app start
        initializePerformanceOptimizations();
    }, []);

    return (
        <Router
            future={{
                v7_startTransition: true,
                v7_relativeSplatPath: true
            }}
        >
            <NavigationProvider>
                <RoutePreloader />
                <Box sx={{ minHeight: '100vh' }}>
                    <OptimizedSuspense>
                            <Routes>
                                {/* Public Routes - Authentication */}
                                <Route
                                    path="/auth"
                                    element={
                                        <PublicRoute>
                                            <OptimizedSuspense skeletonType="form">
                                                <AuthPage />
                                            </OptimizedSuspense>
                                        </PublicRoute>
                                    }
                                />
                                <Route path="/login" element={<Navigate to="/auth?mode=login" replace />} />
                                <Route path="/register" element={<Navigate to="/auth?mode=register" replace />} />
                                <Route
                                    path="/reset-password"
                                    element={
                                        <PublicRoute>
                                            <OptimizedSuspense skeletonType="form">
                                                <ResetPasswordForm />
                                            </OptimizedSuspense>
                                        </PublicRoute>
                                    }
                                />

                                {/* Protected Routes - Main Application */}
                                <Route
                                    path="/"
                                    element={
                                        <ProtectedRoute>
                                            <OptimizedSuspense skeletonType="dashboard">
                                                <DashboardPage />
                                            </OptimizedSuspense>
                                        </ProtectedRoute>
                                    }
                                />
                                <Route path="/dashboard" element={<Navigate to="/" replace />} />

                                {/* Post Creation Route */}
                                <Route
                                    path="/create"
                                    element={
                                        <ProtectedRoute>
                                            <OptimizedSuspense skeletonType="form">
                                                <CreatePostPage />
                                            </OptimizedSuspense>
                                        </ProtectedRoute>
                                    }
                                />

                                {/* AI Services Routes */}
                                <Route
                                    path="/services"
                                    element={
                                        <ProtectedRoute>
                                            <ServicesLayout />
                                        </ProtectedRoute>
                                    }
                                >
                                    <Route index element={<Navigate to="/services/overview" replace />} />
                                    <Route path="overview" element={<ServicesOverview />} />
                                    <Route path="content-optimizer" element={<ContentOptimizerService />} />
                                    <Route path="predictive-analytics" element={<PredictiveAnalyticsService />} />
                                    <Route path="churn-predictor" element={<ChurnPredictorService />} />
                                    <Route path="security-monitoring" element={<SecurityMonitoringService />} />
                                </Route>

                                {/* Enhanced Data Tables Showcase */}
                                <Route
                                    path="/tables"
                                    element={
                                        <ProtectedRoute>
                                            <DataTablesShowcase />
                                        </ProtectedRoute>
                                    }
                                />

                                {/* Analytics Dashboard */}
                                <Route
                                    path="/analytics"
                                    element={
                                        <ProtectedRoute>
                                            <OptimizedSuspense skeletonType="dashboard">
                                                <AnalyticsPage />
                                            </OptimizedSuspense>
                                        </ProtectedRoute>
                                    }
                                />

                                {/* Admin Dashboard - Role-based protection */}
                                <Route
                                    path="/admin"
                                    element={
                                        <ProtectedRoute requiredRole="admin">
                                            <OptimizedSuspense skeletonType="dashboard">
                                                <AdminDashboard />
                                            </OptimizedSuspense>
                                        </ProtectedRoute>
                                    }
                                />

                                {/* SuperAdmin Dashboard - Highest level access */}
                                <Route
                                    path="/superadmin"
                                    element={
                                        <ProtectedRoute requiredRole="superadmin">
                                            <OptimizedSuspense skeletonType="dashboard">
                                                <SuperAdminDashboard />
                                            </OptimizedSuspense>
                                        </ProtectedRoute>
                                    }
                                />

                                {/* User Profile */}
                                <Route
                                    path="/profile"
                                    element={
                                        <ProtectedRoute>
                                            <OptimizedSuspense skeletonType="form">
                                                <ProfilePage />
                                            </OptimizedSuspense>
                                        </ProtectedRoute>
                                    }
                                />

                                {/* Settings */}
                                <Route
                                    path="/settings"
                                    element={
                                        <ProtectedRoute>
                                            <SettingsPage />
                                        </ProtectedRoute>
                                    }
                                />

                                {/* Help & Support */}
                                <Route
                                    path="/help"
                                    element={
                                        <ProtectedRoute>
                                            <HelpPage />
                                        </ProtectedRoute>
                                    }
                                />

                                {/* Fallback Routes */}
                                <Route path="*" element={<Navigate to="/auth" replace />} />
                            </Routes>
                        </OptimizedSuspense>
                </Box>
            </NavigationProvider>
        </Router>
    );
};

// ServicesOverview component moved to separate file - see /components/services/

// Placeholder components removed - using actual implementations from imports above

// Page components moved to separate files - see /components/pages/

export default AppRouter;

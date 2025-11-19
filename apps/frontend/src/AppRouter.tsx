import React, { Suspense, useEffect, ReactNode } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Box } from '@mui/material';
import { ProtectedRoute, PublicRoute } from '@features/auth/guards';
import { ROUTES } from '@config/routes';

// Import optimized lazy loading system
import {
    PageComponents,
    ServiceComponents,
    UtilityComponents,
    preloadByRoute,
    initializePerformanceOptimizations,
} from './utils/lazyLoading';

// Import navigation system from domain structure
import { NavigationProvider } from '@shared/components/navigation';
import { PageLoader } from '@shared/components/feedback';

const {
    DashboardPage,
    CreatePostPage,
    AnalyticsPage,
    AuthPage,
    ProfilePage,
    AdminDashboard,
    ResetPasswordForm
} = PageComponents;

// Lazy load additional pages
const ChannelsManagementPage = React.lazy(() => import('./pages/channels'));
const AIServicesPage = React.lazy(() => import('./pages/AIServicesPage'));
const PredictiveAnalyticsPage = React.lazy(() => import('./pages/PredictiveAnalyticsPage'));
const PaymentPage = React.lazy(() => import('./pages/PaymentPage'));
const SubscriptionPage = React.lazy(() => import('./pages/SubscriptionPage'));
const PaymentHistoryPage = React.lazy(() => import('./pages/PaymentHistoryPage'));
const InvoicesPage = React.lazy(() => import('./pages/InvoicesPage'));
const PostsPage = React.lazy(() => import('./pages/PostsPage'));
const PostDetailsPage = React.lazy(() => import('./pages/PostDetailsPage'));
const EditPostPage = React.lazy(() => import('./pages/EditPostPage'));
const ScheduledPostsPage = React.lazy(() => import('./pages/ScheduledPostsPage'));
const ChannelDetailsPage = React.lazy(() => import('./pages/channels/ChannelDetailsPage'));
const AddChannelPage = React.lazy(() => import('./pages/channels/AddChannelPage'));
const NotFoundPage = React.lazy(() => import('./pages/NotFoundPage'));
const UnauthorizedPage = React.lazy(() => import('./pages/UnauthorizedPage'));
const ServerErrorPage = React.lazy(() => import('./pages/ServerErrorPage'));

// Bot Management Pages
const BotSetupPage = React.lazy(() => import('./pages/BotSetupPage'));
const BotDashboardPage = React.lazy(() => import('./pages/BotDashboardPage'));
const AdminBotManagementPage = React.lazy(() => import('./pages/AdminBotManagementPage'));

// MTProto Setup Page
const MTProtoSetupPage = React.lazy(() => import('@features/mtproto-setup'));
const MTProtoMonitoringPage = React.lazy(() => import('./pages/MTProtoMonitoringPage'));

// Storage Channels Page
const StorageChannelsPage = React.lazy(() => import('./pages/StorageChannelsPage'));

// AdminComponents.SuperAdminDashboard archived - components moved to @features/admin
// const {
//     SuperAdminDashboard
// } = AdminComponents;

const {
    ServicesLayout,
    ContentOptimizerService,
    PredictiveAnalyticsService,
    ChurnPredictorService,
    SecurityMonitoringService
} = ServiceComponents;

const {
    // DataTablesShowcase and ServicesOverview archived
    SettingsPage,
    HelpPage,
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
            {...{
                future: {
                    v7_startTransition: true,
                    v7_relativeSplatPath: true
                }
            } as any}
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

                                {/* Channels Management Route */}
                                <Route
                                    path="/channels"
                                    element={
                                        <ProtectedRoute>
                                            <OptimizedSuspense skeletonType="dashboard">
                                                <ChannelsManagementPage />
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
                                    {/* ServicesOverview archived */}
                                    {/* <Route path="overview" element={<ServicesOverview />} /> */}
                                    <Route path="content-optimizer" element={<ContentOptimizerService />} />
                                    <Route path="predictive-analytics" element={<PredictiveAnalyticsService />} />
                                    <Route path="churn-predictor" element={<ChurnPredictorService />} />
                                    <Route path="security-monitoring" element={<SecurityMonitoringService />} />
                                </Route>

                                {/* Enhanced Data Tables Showcase - ARCHIVED */}
                                {/* <Route
                                    path="/tables"
                                    element={
                                        <ProtectedRoute>
                                            <DataTablesShowcase />
                                        </ProtectedRoute>
                                    }
                                /> */}

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

                                {/* Bot Management Routes */}
                                <Route
                                    path="/bot/setup"
                                    element={
                                        <ProtectedRoute>
                                            <OptimizedSuspense skeletonType="form">
                                                <BotSetupPage />
                                            </OptimizedSuspense>
                                        </ProtectedRoute>
                                    }
                                />
                                <Route
                                    path="/bot/dashboard"
                                    element={
                                        <ProtectedRoute>
                                            <OptimizedSuspense skeletonType="dashboard">
                                                <BotDashboardPage />
                                            </OptimizedSuspense>
                                        </ProtectedRoute>
                                    }
                                />
                                <Route
                                    path="/admin/bots"
                                    element={
                                        <ProtectedRoute requiredRole="admin">
                                            <OptimizedSuspense skeletonType="list">
                                                <AdminBotManagementPage />
                                            </OptimizedSuspense>
                                        </ProtectedRoute>
                                    }
                                />

                                {/* Owner Dashboard - ARCHIVED - Use /admin instead */}
                                {/* <Route
                                    path="/superadmin"
                                    element={
                                        <ProtectedRoute requiredRole="owner">
                                            <OptimizedSuspense skeletonType="dashboard">
                                                <SuperAdminDashboard />
                                            </OptimizedSuspense>
                                        </ProtectedRoute>
                                    }
                                /> */}

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

                                {/* MTProto Setup */}
                                <Route
                                    path="/settings/mtproto-setup"
                                    element={
                                        <ProtectedRoute>
                                            <OptimizedSuspense skeletonType="form">
                                                <MTProtoSetupPage />
                                            </OptimizedSuspense>
                                        </ProtectedRoute>
                                    }
                                />

                                {/* MTProto Monitoring */}
                                <Route
                                    path="/settings/mtproto-monitoring"
                                    element={
                                        <ProtectedRoute>
                                            <OptimizedSuspense skeletonType="dashboard">
                                                <MTProtoMonitoringPage />
                                            </OptimizedSuspense>
                                        </ProtectedRoute>
                                    }
                                />

                                {/* Storage Channels Settings */}
                                <Route
                                    path={ROUTES.SETTINGS_STORAGE}
                                    element={
                                        <ProtectedRoute>
                                            <OptimizedSuspense skeletonType="dashboard">
                                                <StorageChannelsPage />
                                            </OptimizedSuspense>
                                        </ProtectedRoute>
                                    }
                                />

                                {/* Help & Support */}
                                <Route
                                    path={ROUTES.HELP}
                                    element={
                                        <ProtectedRoute>
                                            <HelpPage />
                                        </ProtectedRoute>
                                    }
                                />

                                {/* AI Services Routes - New */}
                                <Route
                                    path={ROUTES.AI_SERVICES}
                                    element={
                                        <ProtectedRoute>
                                            <OptimizedSuspense skeletonType="dashboard">
                                                <AIServicesPage />
                                            </OptimizedSuspense>
                                        </ProtectedRoute>
                                    }
                                />
                                <Route
                                    path={ROUTES.PREDICTIVE_ANALYTICS}
                                    element={
                                        <ProtectedRoute>
                                            <OptimizedSuspense skeletonType="dashboard">
                                                <PredictiveAnalyticsPage />
                                            </OptimizedSuspense>
                                        </ProtectedRoute>
                                    }
                                />

                                {/* Payment & Subscription Routes */}
                                <Route
                                    path={ROUTES.PAYMENT}
                                    element={
                                        <ProtectedRoute>
                                            <OptimizedSuspense skeletonType="dashboard">
                                                <PaymentPage />
                                            </OptimizedSuspense>
                                        </ProtectedRoute>
                                    }
                                />
                                <Route
                                    path={ROUTES.SUBSCRIPTION}
                                    element={
                                        <ProtectedRoute>
                                            <OptimizedSuspense skeletonType="form">
                                                <SubscriptionPage />
                                            </OptimizedSuspense>
                                        </ProtectedRoute>
                                    }
                                />
                                <Route
                                    path={ROUTES.PAYMENT_HISTORY}
                                    element={
                                        <ProtectedRoute>
                                            <OptimizedSuspense skeletonType="list">
                                                <PaymentHistoryPage />
                                            </OptimizedSuspense>
                                        </ProtectedRoute>
                                    }
                                />
                                <Route
                                    path={ROUTES.INVOICES}
                                    element={
                                        <ProtectedRoute>
                                            <OptimizedSuspense skeletonType="list">
                                                <InvoicesPage />
                                            </OptimizedSuspense>
                                        </ProtectedRoute>
                                    }
                                />

                                {/* Posts Routes - IMPORTANT: Specific routes MUST come before parameterized routes */}

                                {/* Main posts hub */}
                                <Route
                                    path={ROUTES.POSTS}
                                    element={
                                        <ProtectedRoute>
                                            <OptimizedSuspense skeletonType="list">
                                                <PostsPage />
                                            </OptimizedSuspense>
                                        </ProtectedRoute>
                                    }
                                />

                                {/* Specific routes - MUST come before :id routes */}
                                <Route
                                    path={ROUTES.CREATE_POST}
                                    element={
                                        <ProtectedRoute>
                                            <OptimizedSuspense skeletonType="form">
                                                <CreatePostPage />
                                            </OptimizedSuspense>
                                        </ProtectedRoute>
                                    }
                                />
                                <Route
                                    path={ROUTES.SCHEDULED_POSTS}
                                    element={
                                        <ProtectedRoute>
                                            <OptimizedSuspense skeletonType="list">
                                                <ScheduledPostsPage />
                                            </OptimizedSuspense>
                                        </ProtectedRoute>
                                    }
                                />

                                {/* Parameterized routes - MUST come after specific routes */}
                                <Route
                                    path={ROUTES.EDIT_POST}
                                    element={
                                        <ProtectedRoute>
                                            <OptimizedSuspense skeletonType="form">
                                                <EditPostPage />
                                            </OptimizedSuspense>
                                        </ProtectedRoute>
                                    }
                                />
                                <Route
                                    path={ROUTES.POST_DETAILS}
                                    element={
                                        <ProtectedRoute>
                                            <OptimizedSuspense skeletonType="content">
                                                <PostDetailsPage />
                                            </OptimizedSuspense>
                                        </ProtectedRoute>
                                    }
                                />

                                {/* Channel Routes */}
                                <Route
                                    path={ROUTES.CHANNEL_DETAILS}
                                    element={
                                        <ProtectedRoute>
                                            <OptimizedSuspense skeletonType="dashboard">
                                                <ChannelDetailsPage />
                                            </OptimizedSuspense>
                                        </ProtectedRoute>
                                    }
                                />
                                <Route
                                    path={ROUTES.ADD_CHANNEL}
                                    element={
                                        <ProtectedRoute>
                                            <OptimizedSuspense skeletonType="form">
                                                <AddChannelPage />
                                            </OptimizedSuspense>
                                        </ProtectedRoute>
                                    }
                                />

                                {/* Error Pages */}
                                <Route
                                    path={ROUTES.NOT_FOUND}
                                    element={
                                        <OptimizedSuspense>
                                            <NotFoundPage />
                                        </OptimizedSuspense>
                                    }
                                />
                                <Route
                                    path={ROUTES.UNAUTHORIZED}
                                    element={
                                        <OptimizedSuspense>
                                            <UnauthorizedPage />
                                        </OptimizedSuspense>
                                    }
                                />
                                <Route
                                    path={ROUTES.SERVER_ERROR}
                                    element={
                                        <OptimizedSuspense>
                                            <ServerErrorPage />
                                        </OptimizedSuspense>
                                    }
                                />

                                {/* Fallback Routes */}
                                <Route path="*" element={<Navigate to={ROUTES.NOT_FOUND} replace />} />
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

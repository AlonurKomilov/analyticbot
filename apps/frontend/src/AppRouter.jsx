import React, { Suspense, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Box, CircularProgress, LinearProgress } from '@mui/material';

// Import optimized lazy loading system
import {
    CriticalComponents,
    AdminComponents,
    ServiceComponents,
    UtilityComponents,
    preloadByRoute,
    initializePerformanceOptimizations
} from './utils/lazyLoading';

// Import new page components
import DashboardPage from './components/pages/DashboardPage.jsx';
import CreatePostPage from './components/pages/CreatePostPage.jsx';
import AnalyticsPage from './components/pages/AnalyticsPage.jsx';

// Destructure components for cleaner code
const {
    MainDashboard,
    AnalyticsDashboard
} = CriticalComponents;

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

// Import navigation system from domain structure
import { NavigationProvider } from './components/common/NavigationProvider';
import NavigationBar from './components/domains/navigation/NavigationBar';

/**
 * Performance-optimized loading component
 */
const OptimizedSuspense = ({ children, fallback }) => {
    return (
        <Suspense 
            fallback={
                fallback || (
                    <Box sx={{ 
                        minHeight: '400px',
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'center',
                        alignItems: 'center',
                        gap: 2
                    }}>
                        <CircularProgress size={40} />
                        <LinearProgress 
                            sx={{ width: '200px', borderRadius: 1 }}
                            variant="indeterminate"
                        />
                        <Box sx={{ 
                            fontSize: '0.875rem', 
                            color: 'text.secondary',
                            fontWeight: 500
                        }}>
                            Loading component...
                        </Box>
                    </Box>
                )
            }
        >
            {children}
        </Suspense>
    );
};

/**
 * Route-aware preloading component
 */
const RoutePreloader = () => {
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
const AppRouter = () => {
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
                    {/* Global Navigation Bar */}
                    <NavigationBar />
                    
                    {/* Main Content Area */}
                    <Box sx={{ pt: { xs: 7, sm: 8 } }}>
                        <OptimizedSuspense>
                            <Routes>
                                {/* Main Dashboard Routes */}
                                <Route path="/" element={<DashboardPage />} />
                                <Route path="/dashboard" element={<Navigate to="/" replace />} />
                                
                                {/* Post Creation Route */}
                                <Route path="/create" element={<CreatePostPage />} />
                                
                                {/* AI Services Routes */}
                                <Route path="/services" element={<ServicesLayout />}>
                                <Route index element={<Navigate to="/services/overview" replace />} />
                                <Route path="overview" element={<ServicesOverview />} />
                                <Route path="content-optimizer" element={<ContentOptimizerService />} />
                                <Route path="predictive-analytics" element={<PredictiveAnalyticsService />} />
                                <Route path="churn-predictor" element={<ChurnPredictorService />} />
                                <Route path="security-monitoring" element={<SecurityMonitoringService />} />
                            </Route>
                            
                            {/* Enhanced Data Tables Showcase */}
                            <Route path="/tables" element={<DataTablesShowcase />} />
                            
                            {/* Analytics Dashboard */}
                            <Route path="/analytics" element={<AnalyticsPage />} />
                            
                            {/* Super Admin Dashboard */}
                            <Route path="/admin" element={<SuperAdminDashboard />} />
                            
                            {/* Settings */}
                            <Route path="/settings" element={<SettingsPage />} />
                            
                            {/* Help & Support */}
                            <Route path="/help" element={<HelpPage />} />
                            
                                {/* Redirect old routes */}
                                <Route path="*" element={<Navigate to="/" replace />} />
                            </Routes>
                        </OptimizedSuspense>
                    </Box>
                </Box>
            </NavigationProvider>
        </Router>
    );
};

// ServicesOverview component moved to separate file - see /components/services/

// Placeholder components removed - using actual implementations from imports above

// Page components moved to separate files - see /components/pages/

export default AppRouter;
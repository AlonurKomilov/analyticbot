import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Box } from '@mui/material';

// Import main app components
import MainDashboard from './MainDashboard';
import ServicesLayout from './services/ServicesLayout';
import ContentOptimizerService from './services/ContentOptimizerService';
import PredictiveAnalyticsService from './services/PredictiveAnalyticsService';
import ChurnPredictorService from './services/ChurnPredictorService';
import SecurityMonitoringService from './services/SecurityMonitoringService';
import DataTablesShowcase from './components/DataTablesShowcase';

// Import navigation system
import { NavigationProvider } from './components/common/NavigationProvider';
import NavigationBar from './components/common/NavigationBar';

/**
 * Professional App Router
 * Implements multi-page architecture with enterprise-grade navigation
 */
const AppRouter = () => {
    return (
        <Router>
            <NavigationProvider>
                <Box sx={{ minHeight: '100vh' }}>
                    {/* Global Navigation Bar */}
                    <NavigationBar />
                    
                    {/* Main Content Area */}
                    <Box sx={{ pt: { xs: 7, sm: 8 } }}>
                        <Routes>
                            {/* Main Dashboard Routes */}
                            <Route path="/" element={<MainDashboard />} />
                            <Route path="/dashboard" element={<Navigate to="/" replace />} />
                            
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
                            <Route path="/analytics" element={<AnalyticsDashboard />} />
                            
                            {/* Super Admin Dashboard */}
                            <Route path="/admin" element={<SuperAdminDashboard />} />
                            
                            {/* Settings */}
                            <Route path="/settings" element={<SettingsPage />} />
                            
                            {/* Help & Support */}
                            <Route path="/help" element={<HelpPage />} />
                            
                            {/* Redirect old routes */}
                            <Route path="*" element={<Navigate to="/" replace />} />
                        </Routes>
                    </Box>
                </Box>
            </NavigationProvider>
        </Router>
    );
};

// Services Overview Component
const ServicesOverview = () => {
    return (
        <Box sx={{ p: 3 }}>
            <h2>AI Services Overview</h2>
            <p>Select a service from the sidebar to get started.</p>
        </Box>
    );
};

// Analytics Dashboard Component (placeholder)
const AnalyticsDashboard = () => {
    return (
        <Box sx={{ p: 3 }}>
            <h2>Analytics Dashboard</h2>
            <p>Advanced analytics and reporting tools.</p>
        </Box>
    );
};

// Super Admin Dashboard Component (placeholder)
const SuperAdminDashboard = () => {
    return (
        <Box sx={{ p: 3 }}>
            <h2>Super Admin Dashboard</h2>
            <p>Advanced administrative controls and monitoring.</p>
        </Box>
    );
};

// Settings Page Component
const SettingsPage = () => {
    return (
        <Box sx={{ p: 3 }}>
            <h2>Settings</h2>
            <p>Configure your preferences and account settings.</p>
        </Box>
    );
};

// Help Page Component
const HelpPage = () => {
    return (
        <Box sx={{ p: 3 }}>
            <h2>Help & Support</h2>
            <p>Find answers to frequently asked questions and get support.</p>
        </Box>
    );
};

export default AppRouter;
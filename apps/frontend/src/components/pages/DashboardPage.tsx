/**
 * DashboardPage Component
 *
 * Main dashboard orchestrator with enhanced features and legacy fallback.
 * Integrates multiple stores and displays comprehensive analytics.
 */

import React from 'react';
import { Box, Container } from '@mui/material';
import { TouchTargetProvider } from '../common/TouchTargetCompliance';
import EnhancedDashboardPage from './EnhancedDashboardPage';
import BestTimeRecommender from '../analytics/BestTimeRecommender/BestTimeRecommender';
import SmartAlertsPanel from '../analytics/AdvancedAnalyticsDashboard/SmartAlertsPanel';

const DashboardPage: React.FC = () => {
    const showEnhancedDashboard = false;

    // Use enhanced dashboard if enabled
    if (showEnhancedDashboard) {
        return (
            <TouchTargetProvider>
                <EnhancedDashboardPage />
            </TouchTargetProvider>
        );
    }

    // Legacy dashboard layout
    return (
        <Container maxWidth="xl">
            <Box sx={{ py: 3 }}>
                {/* Best Time Recommender */}
                <Box sx={{ mt: 3 }}>
                    <BestTimeRecommender />
                </Box>

                {/* Smart Alerts Panel */}
                <Box sx={{ mt: 3 }}>
                    <SmartAlertsPanel />
                </Box>
            </Box>
        </Container>
    );
};

export default DashboardPage;

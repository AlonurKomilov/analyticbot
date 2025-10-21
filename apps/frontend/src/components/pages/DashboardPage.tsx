/**
 * DashboardPage Component
 *
 * Main dashboard orchestrator with comprehensive analytics.
 * Uses full-featured AnalyticsDashboard with tab navigation.
 *
 * Updated: October 2025
 * - Switched from minimal dashboard to comprehensive AnalyticsDashboard
 * - Provides better analytics overview with KPIs, charts, and insights
 * - Enhanced dashboard available via feature flag if needed
 */

import React from 'react';
import { TouchTargetProvider } from '../common/TouchTargetCompliance';
import AnalyticsDashboard from '../dashboard/AnalyticsDashboard/AnalyticsDashboard';
import EnhancedDashboardPage from './EnhancedDashboardPage';

const DashboardPage: React.FC = () => {
    // Feature flag: Set to true to enable premium enhanced dashboard with animations
    const showEnhancedDashboard = false;

    // Enhanced dashboard with micro-interactions and advanced features
    if (showEnhancedDashboard) {
        return (
            <TouchTargetProvider>
                <EnhancedDashboardPage />
            </TouchTargetProvider>
        );
    }

    // Standard comprehensive analytics dashboard (recommended for most users)
    return (
        <TouchTargetProvider>
            <AnalyticsDashboard />
        </TouchTargetProvider>
    );
};

export default DashboardPage;
